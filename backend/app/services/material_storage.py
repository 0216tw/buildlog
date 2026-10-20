from dataclasses import dataclass
import os
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


IMAGE_LIMIT_BYTES = 5 * 1024 * 1024
VIDEO_LIMIT_BYTES = 30 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class FileRule:
    extension: str
    content_type: str
    media_type: str
    limit: int


@dataclass(frozen=True)
class StoredUpload:
    original_filename: str
    stored_path: str
    media_type: str
    content_type: str
    size_bytes: int


@dataclass(frozen=True)
class QuarantinedFile:
    original_path: Path
    quarantine_path: Path


class MaterialValidationError(ValueError):
    pass


class MaterialStorageError(RuntimeError):
    pass


FILE_RULES = {
    "png": FileRule("png", "image/png", "image", IMAGE_LIMIT_BYTES),
    "jpg": FileRule("jpg", "image/jpeg", "image", IMAGE_LIMIT_BYTES),
    "jpeg": FileRule("jpg", "image/jpeg", "image", IMAGE_LIMIT_BYTES),
    "mp4": FileRule("mp4", "video/mp4", "video", VIDEO_LIMIT_BYTES),
}


def _has_valid_signature(rule: FileRule, header: bytes) -> bool:
    if rule.content_type == "image/png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    if rule.content_type == "image/jpeg":
        return header.startswith(b"\xff\xd8\xff")
    if rule.content_type == "video/mp4":
        return len(header) >= 12 and header[4:8] == b"ftyp"
    return False


class MaterialStorage:
    def __init__(self, upload_root: Path):
        self.upload_root = upload_root.resolve()

    def _safe_path(self, relative_path: str) -> Path:
        candidate = (self.upload_root / relative_path).resolve()
        try:
            candidate.relative_to(self.upload_root)
        except ValueError as error:
            raise MaterialStorageError("저장 파일 경로가 올바르지 않습니다.") from error
        return candidate

    @staticmethod
    def _original_filename(filename: str | None) -> str:
        if not filename:
            raise MaterialValidationError("파일을 선택해 주세요.")
        basename = filename.replace("\\", "/").rsplit("/", 1)[-1].strip()
        if not basename or any(ord(character) < 32 for character in basename):
            raise MaterialValidationError("파일 이름을 확인해 주세요.")
        return basename

    @staticmethod
    def _rule_for(filename: str, content_type: str | None) -> FileRule:
        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        rule = FILE_RULES.get(extension)
        if rule is None or content_type != rule.content_type:
            raise MaterialValidationError("PNG, JPG 또는 MP4 파일만 등록할 수 있습니다.")
        return rule

    def store(self, upload: UploadFile, user_id: int) -> StoredUpload:
        temporary_path: Path | None = None

        try:
            upload_id = uuid4().hex
            temporary_path = self._safe_path(f".tmp/{upload_id}.part")
            original_filename = self._original_filename(upload.filename)
            rule = self._rule_for(original_filename, upload.content_type)
            relative_path = f"{user_id}/{upload_id}.{rule.extension}"
            final_path = self._safe_path(relative_path)
            size_bytes = 0
            header = bytearray()
            temporary_path.parent.mkdir(parents=True, exist_ok=True)
            final_path.parent.mkdir(parents=True, exist_ok=True)
            with temporary_path.open("xb") as destination:
                while chunk := upload.file.read(CHUNK_SIZE):
                    size_bytes += len(chunk)
                    if size_bytes > rule.limit:
                        limit_label = "5MiB" if rule.media_type == "image" else "30MiB"
                        raise MaterialValidationError(
                            f"{('이미지' if rule.media_type == 'image' else '영상')} 파일은 {limit_label} 이하로 등록해 주세요."
                        )
                    if len(header) < 32:
                        header.extend(chunk[: 32 - len(header)])
                    destination.write(chunk)

            if size_bytes == 0:
                raise MaterialValidationError("내용이 있는 파일을 선택해 주세요.")
            if not _has_valid_signature(rule, bytes(header)):
                raise MaterialValidationError("파일의 실제 형식이 확장자와 일치하지 않습니다.")

            os.replace(temporary_path, final_path)
            return StoredUpload(
                original_filename=original_filename,
                stored_path=relative_path,
                media_type=rule.media_type,
                content_type=rule.content_type,
                size_bytes=size_bytes,
            )
        except MaterialValidationError:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise
        except OSError as error:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise MaterialStorageError("파일을 저장하지 못했습니다.") from error
        finally:
            upload.file.close()

    def resolve_existing(self, relative_path: str) -> Path:
        path = self._safe_path(relative_path)
        if not path.is_file() or path.is_symlink():
            raise MaterialStorageError("저장된 원본 파일을 찾을 수 없습니다.")
        return path

    def remove_stored(self, relative_path: str) -> None:
        path = self._safe_path(relative_path)
        try:
            path.unlink(missing_ok=True)
        except OSError as error:
            raise MaterialStorageError("저장 파일을 정리하지 못했습니다.") from error

    def quarantine(self, relative_path: str) -> QuarantinedFile:
        original_path = self.resolve_existing(relative_path)
        quarantine_path = self._safe_path(f".trash/{uuid4().hex}.deleted")
        try:
            quarantine_path.parent.mkdir(parents=True, exist_ok=True)
            os.replace(original_path, quarantine_path)
        except OSError as error:
            raise MaterialStorageError("파일을 삭제할 준비를 하지 못했습니다.") from error
        return QuarantinedFile(original_path, quarantine_path)

    @staticmethod
    def restore(quarantined: QuarantinedFile) -> None:
        try:
            quarantined.original_path.parent.mkdir(parents=True, exist_ok=True)
            os.replace(quarantined.quarantine_path, quarantined.original_path)
        except OSError as error:
            raise MaterialStorageError("삭제 중인 파일을 복구하지 못했습니다.") from error

    @staticmethod
    def purge(quarantined: QuarantinedFile) -> None:
        try:
            quarantined.quarantine_path.unlink()
        except OSError as error:
            raise MaterialStorageError("격리한 파일을 최종 삭제하지 못했습니다.") from error

    def clear_empty_directories(self, relative_path: str) -> None:
        path = self._safe_path(relative_path).parent
        if path == self.upload_root:
            return
        try:
            path.rmdir()
        except OSError:
            pass
