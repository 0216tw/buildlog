import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import BACKEND_ROOT
from app.db.database import get_db
from app.models import Material, User
from app.schemas import MaterialResponse, MaterialText
from app.services import MaterialStorage, MaterialStorageError, MaterialValidationError
from app.services.material_analysis_worker import enqueue_material_analysis


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/materials", tags=["materials"])
default_material_storage = MaterialStorage(BACKEND_ROOT / "uploads")


def get_material_storage() -> MaterialStorage:
    return default_material_storage


def _validation_detail(error: ValidationError) -> str:
    errors = error.errors()
    if not errors:
        return "입력값을 확인해 주세요."
    message = str(errors[0].get("msg", "입력값을 확인해 주세요."))
    return message.removeprefix("Value error, ")


def _owned_material(database: Session, material_id: int, user_id: int) -> Material:
    material = database.scalar(
        select(Material).where(
            Material.id == material_id,
            Material.user_id == user_id,
        )
    )
    if material is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="자료를 찾을 수 없습니다.",
        )
    return material


@router.post("", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
def create_material(
    title: str = Form(...),
    memo: str | None = Form(default=None),
    files: list[UploadFile] = File(..., alias="file"),
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
    storage: MaterialStorage = Depends(get_material_storage),
) -> Material:
    if len(files) != 1:
        for upload in files:
            upload.file.close()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="파일은 한 개만 선택해 주세요.",
        )
    try:
        text = MaterialText(title=title, memo=memo)
        stored = storage.store(files[0], current_user.id)
    except ValidationError as error:
        files[0].file.close()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=_validation_detail(error),
        ) from error
    except MaterialValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    except MaterialStorageError as error:
        logger.exception("material upload storage failure user_id=%s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="파일을 저장하지 못했습니다. 잠시 후 다시 시도해 주세요.",
        ) from error

    material = Material(
        user_id=current_user.id,
        title=text.title,
        memo=text.memo,
        original_filename=stored.original_filename,
        stored_path=stored.stored_path,
        media_type=stored.media_type,
        content_type=stored.content_type,
        size_bytes=stored.size_bytes,
        ai_status="pending",
    )
    database.add(material)
    try:
        database.commit()
    except SQLAlchemyError as error:
        database.rollback()
        try:
            storage.remove_stored(stored.stored_path)
        except MaterialStorageError:
            logger.exception("material upload cleanup failure user_id=%s", current_user.id)
        logger.exception("material metadata commit failure user_id=%s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="자료를 등록하지 못했습니다. 잠시 후 다시 시도해 주세요.",
        ) from error
    database.refresh(material)
    enqueue_material_analysis(material.id)
    return material


@router.get("", response_model=list[MaterialResponse])
def list_materials(
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
) -> list[Material]:
    statement = (
        select(Material)
        .where(Material.user_id == current_user.id)
        .order_by(Material.created_at.desc(), Material.id.desc())
    )
    return list(database.scalars(statement))


@router.get("/{material_id}/file")
def read_material_file(
    material_id: int,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
    storage: MaterialStorage = Depends(get_material_storage),
) -> FileResponse:
    material = _owned_material(database, material_id, current_user.id)
    try:
        path = storage.resolve_existing(material.stored_path)
    except MaterialStorageError as error:
        logger.exception(
            "material file read failure material_id=%s user_id=%s",
            material.id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="원본 파일을 열지 못했습니다. 잠시 후 다시 시도해 주세요.",
        ) from error
    return FileResponse(
        path,
        media_type=material.content_type,
        filename=material.original_filename,
        content_disposition_type="inline",
        headers={
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(
    material_id: int,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
    storage: MaterialStorage = Depends(get_material_storage),
) -> Response:
    material = _owned_material(database, material_id, current_user.id)
    snapshot = {
        "id": material.id,
        "user_id": material.user_id,
        "title": material.title,
        "memo": material.memo,
        "original_filename": material.original_filename,
        "stored_path": material.stored_path,
        "media_type": material.media_type,
        "content_type": material.content_type,
        "size_bytes": material.size_bytes,
        "ai_summary": material.ai_summary,
        "ai_status": material.ai_status,
        "ai_model": material.ai_model,
        "ai_prompt_version": material.ai_prompt_version,
        "ai_attempt_count": material.ai_attempt_count,
        "ai_started_at": material.ai_started_at,
        "ai_analyzed_at": material.ai_analyzed_at,
        "ai_error_code": material.ai_error_code,
        "created_at": material.created_at,
    }
    try:
        quarantined = storage.quarantine(material.stored_path)
    except MaterialStorageError as error:
        logger.exception(
            "material delete quarantine failure material_id=%s user_id=%s",
            material.id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="자료를 삭제하지 못했습니다. 잠시 후 다시 시도해 주세요.",
        ) from error

    database.delete(material)
    try:
        database.commit()
    except SQLAlchemyError as error:
        database.rollback()
        try:
            storage.restore(quarantined)
        except MaterialStorageError:
            logger.exception(
                "material delete restore failure material_id=%s user_id=%s",
                material_id,
                current_user.id,
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="자료를 삭제하지 못했습니다. 잠시 후 다시 시도해 주세요.",
        ) from error

    try:
        storage.purge(quarantined)
    except MaterialStorageError as error:
        logger.exception(
            "material delete purge failure material_id=%s user_id=%s",
            material_id,
            current_user.id,
        )
        try:
            storage.restore(quarantined)
            database.add(Material(**snapshot))
            database.commit()
        except (MaterialStorageError, SQLAlchemyError):
            database.rollback()
            logger.exception(
                "material delete compensation failure material_id=%s user_id=%s",
                material_id,
                current_user.id,
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="자료를 삭제하지 못했습니다. 잠시 후 다시 시도해 주세요.",
        ) from error

    storage.clear_empty_directories(snapshot["stored_path"])
    return Response(status_code=status.HTTP_204_NO_CONTENT)
