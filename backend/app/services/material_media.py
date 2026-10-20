import base64
from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from collections.abc import Iterator

import imageio_ffmpeg
from PIL import Image, ImageOps, UnidentifiedImageError


IMAGE_MAX_DIMENSION = 2048
IMAGE_MAX_PIXELS = 50_000_000
VIDEO_FRAME_MAX_DIMENSION = 1280
VIDEO_MAX_FRAMES = 8
VIDEO_AUDIO_MAX_SECONDS = 15 * 60
VIDEO_AUDIO_SEGMENT_SECONDS = 5 * 60
TRANSCRIPTION_FILE_LIMIT_BYTES = 24 * 1024 * 1024


class MediaProcessingError(RuntimeError):
    pass


@dataclass(frozen=True)
class VideoInfo:
    duration_seconds: float
    has_video: bool
    has_audio: bool


@dataclass(frozen=True)
class PreparedVideo:
    frame_data_urls: tuple[str, ...]
    audio_files: tuple[Path, ...]
    transcript_expected: bool


def _data_url(payload: bytes, content_type: str) -> str:
    encoded = base64.b64encode(payload).decode("ascii")
    return f"data:{content_type};base64,{encoded}"


def image_to_data_url(
    path: Path,
    content_type: str,
    *,
    max_dimension: int = IMAGE_MAX_DIMENSION,
) -> str:
    try:
        with Image.open(path) as source:
            if source.width * source.height > IMAGE_MAX_PIXELS:
                raise MediaProcessingError("이미지 해상도가 너무 큽니다.")
            source.load()
            image = ImageOps.exif_transpose(source)
            image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            output = BytesIO()
            if content_type == "image/png":
                image.save(output, format="PNG", optimize=True)
            elif content_type == "image/jpeg":
                if image.mode not in {"RGB", "L"}:
                    image = image.convert("RGB")
                image.save(output, format="JPEG", quality=85, optimize=True)
            else:
                raise MediaProcessingError("지원하지 않는 이미지 형식입니다.")
    except (OSError, UnidentifiedImageError, ValueError) as error:
        raise MediaProcessingError("이미지를 해석하지 못했습니다.") from error
    return _data_url(output.getvalue(), content_type)


def _ffmpeg_command(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    command = [imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", *arguments]
    creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    try:
        return subprocess.run(
            command,
            capture_output=True,
            check=False,
            timeout=180,
            creationflags=creation_flags,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise MediaProcessingError("영상을 처리하지 못했습니다.") from error


def inspect_video(path: Path) -> VideoInfo:
    result = _ffmpeg_command("-i", str(path))
    details = result.stderr.decode("utf-8", errors="replace")
    duration_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", details)
    duration = 0.0
    if duration_match:
        hours, minutes, seconds = duration_match.groups()
        duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    has_video = re.search(r"Stream #.*Video:", details) is not None
    has_audio = re.search(r"Stream #.*Audio:", details) is not None
    if not has_video or duration <= 0:
        raise MediaProcessingError("영상 화면을 해석하지 못했습니다.")
    return VideoInfo(duration_seconds=duration, has_video=has_video, has_audio=has_audio)


def representative_timestamps(duration_seconds: float) -> tuple[float, ...]:
    if duration_seconds <= 1:
        return (0.0,)
    count = min(VIDEO_MAX_FRAMES, max(2, int(duration_seconds // 5) + 1))
    end = max(0.0, duration_seconds - 0.05)
    if count == 1:
        return (0.0,)
    return tuple((end * index) / (count - 1) for index in range(count))


def _extract_frames(path: Path, output_dir: Path, duration_seconds: float) -> tuple[str, ...]:
    frames: list[str] = []
    fingerprints: set[str] = set()
    for index, timestamp in enumerate(representative_timestamps(duration_seconds), start=1):
        output_path = output_dir / f"frame-{index:02d}.jpg"
        result = _ffmpeg_command(
            "-loglevel",
            "error",
            "-ss",
            f"{timestamp:.3f}",
            "-i",
            str(path),
            "-frames:v",
            "1",
            "-vf",
            f"scale={VIDEO_FRAME_MAX_DIMENSION}:{VIDEO_FRAME_MAX_DIMENSION}:force_original_aspect_ratio=decrease",
            "-q:v",
            "3",
            "-y",
            str(output_path),
        )
        if result.returncode != 0 or not output_path.is_file():
            continue
        payload = output_path.read_bytes()
        fingerprint = sha256(payload).hexdigest()
        if fingerprint in fingerprints:
            output_path.unlink(missing_ok=True)
            continue
        fingerprints.add(fingerprint)
        frames.append(_data_url(payload, "image/jpeg"))
    if not frames:
        raise MediaProcessingError("영상 화면을 추출하지 못했습니다.")
    return tuple(frames)


def _audio_ranges(duration_seconds: float) -> tuple[tuple[float, float], ...]:
    if duration_seconds <= VIDEO_AUDIO_MAX_SECONDS:
        return ((0.0, duration_seconds),)
    segment = float(VIDEO_AUDIO_SEGMENT_SECONDS)
    middle = max(0.0, (duration_seconds - segment) / 2)
    end = max(0.0, duration_seconds - segment)
    return ((0.0, segment), (middle, segment), (end, segment))


def _extract_audio(path: Path, output_dir: Path, duration_seconds: float) -> tuple[Path, ...]:
    audio_files: list[Path] = []
    for index, (start, length) in enumerate(_audio_ranges(duration_seconds), start=1):
        output_path = output_dir / f"audio-{index:02d}.mp3"
        result = _ffmpeg_command(
            "-loglevel",
            "error",
            "-ss",
            f"{start:.3f}",
            "-t",
            f"{length:.3f}",
            "-i",
            str(path),
            "-map",
            "0:a:0",
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-b:a",
            "48k",
            "-y",
            str(output_path),
        )
        if result.returncode != 0 or not output_path.is_file() or output_path.stat().st_size == 0:
            raise MediaProcessingError("영상 음성을 추출하지 못했습니다.")
        if output_path.stat().st_size > TRANSCRIPTION_FILE_LIMIT_BYTES:
            raise MediaProcessingError("전사용 음성 파일 크기 제한을 넘었습니다.")
        audio_files.append(output_path)
    return tuple(audio_files)


@contextmanager
def prepare_video(path: Path, analysis_root: Path, material_id: int) -> Iterator[PreparedVideo]:
    analysis_root.mkdir(parents=True, exist_ok=True)
    temporary_directory = Path(
        tempfile.mkdtemp(prefix=f"{material_id}-", dir=analysis_root)
    ).resolve()
    try:
        info = inspect_video(path)
        frames = _extract_frames(path, temporary_directory, info.duration_seconds)
        audio_files: tuple[Path, ...] = ()
        if info.has_audio:
            try:
                audio_files = _extract_audio(path, temporary_directory, info.duration_seconds)
            except MediaProcessingError:
                audio_files = ()
        yield PreparedVideo(
            frame_data_urls=frames,
            audio_files=audio_files,
            transcript_expected=info.has_audio,
        )
    finally:
        shutil.rmtree(temporary_directory, ignore_errors=True)
