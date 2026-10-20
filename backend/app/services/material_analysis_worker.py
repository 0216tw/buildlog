from datetime import UTC, datetime
import logging
from queue import Empty, Queue
from threading import Event, Lock, Thread
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.models import Material
from app.services.material_analysis import (
    AnalysisFailure,
    AnalysisResult,
    MaterialAnalysisInput,
    MaterialAnalyzer,
)
from app.services.material_storage import MaterialStorage, MaterialStorageError


logger = logging.getLogger(__name__)
MAX_ANALYSIS_ATTEMPTS = 3
MAX_RETRY_DELAY_SECONDS = 30.0


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class MaterialAnalysisCoordinator:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        analyzer: MaterialAnalyzer,
        storage: MaterialStorage,
        *,
        poll_interval_seconds: float = 3.0,
    ) -> None:
        self.session_factory = session_factory
        self.analyzer = analyzer
        self.storage = storage
        self.poll_interval_seconds = poll_interval_seconds
        self._queue: Queue[int] = Queue()
        self._stop_event = Event()
        self._thread: Thread | None = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self.recover_interrupted()
        self.enqueue_pending()
        self._thread = Thread(
            target=self._run,
            name="material-analysis-worker",
            daemon=True,
        )
        self._thread.start()

    def stop(self, timeout: float = 5.0) -> None:
        self._stop_event.set()
        self._queue.put(-1)
        if self._thread is not None:
            self._thread.join(timeout=timeout)
        self._thread = None

    def enqueue(self, material_id: int) -> None:
        if material_id > 0:
            self._queue.put(material_id)

    def enqueue_pending(self) -> None:
        try:
            with self.session_factory() as database:
                material_ids = list(
                    database.scalars(
                        select(Material.id)
                        .where(Material.ai_status == "pending")
                        .order_by(Material.created_at, Material.id)
                    )
                )
        except SQLAlchemyError:
            logger.exception("material analysis pending scan failed")
            return
        for material_id in material_ids:
            self.enqueue(material_id)

    def recover_interrupted(self) -> None:
        try:
            with self.session_factory() as database:
                interrupted = list(
                    database.scalars(
                        select(Material).where(Material.ai_status == "processing")
                    )
                )
                for material in interrupted:
                    material.ai_started_at = None
                    material.ai_summary = None
                    material.ai_model = None
                    material.ai_prompt_version = None
                    material.ai_analyzed_at = None
                    if material.ai_attempt_count >= MAX_ANALYSIS_ATTEMPTS:
                        material.ai_status = "failed"
                        material.ai_error_code = "retry_exhausted"
                    else:
                        material.ai_status = "pending"
                        material.ai_error_code = None
                database.commit()
        except SQLAlchemyError:
            logger.exception("material analysis recovery failed")
            raise

    def process_now(self, material_id: int) -> None:
        claimed = self._claim(material_id)
        if claimed is None:
            return

        analysis_input, attempt_count = claimed
        while True:
            try:
                result = self.analyzer.analyze(analysis_input)
            except AnalysisFailure as error:
                logger.warning(
                    "material analysis failed material_id=%s code=%s attempt=%s request_id=%s",
                    material_id,
                    error.code,
                    attempt_count,
                    error.request_id or "none",
                )
                if error.retryable and attempt_count < MAX_ANALYSIS_ATTEMPTS:
                    delay = error.retry_after if error.retry_after is not None else 2 ** (attempt_count - 1)
                    if delay > MAX_RETRY_DELAY_SECONDS:
                        self._mark_failed(material_id, "rate_limited")
                        return
                    if self._stop_event.wait(max(0.0, delay)):
                        return
                    next_attempt = self._advance_retry(material_id)
                    if next_attempt is None:
                        return
                    attempt_count = next_attempt
                    continue
                self._mark_failed(material_id, error.code)
                return
            except Exception:
                logger.exception("material analysis unexpected failure material_id=%s", material_id)
                self._mark_failed(material_id, "internal_error")
                return

            self._mark_completed(material_id, result)
            return

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                material_id = self._queue.get(timeout=self.poll_interval_seconds)
            except Empty:
                self.enqueue_pending()
                continue
            if material_id < 0:
                continue
            try:
                self.process_now(material_id)
            finally:
                self._queue.task_done()

    def _claim(self, material_id: int) -> tuple[MaterialAnalysisInput, int] | None:
        try:
            with self.session_factory() as database:
                material = database.scalar(
                    select(Material).where(
                        Material.id == material_id,
                        Material.ai_status == "pending",
                    )
                )
                if material is None:
                    return None
                if material.ai_attempt_count >= MAX_ANALYSIS_ATTEMPTS:
                    material.ai_status = "failed"
                    material.ai_error_code = "retry_exhausted"
                    material.ai_started_at = None
                    database.commit()
                    return None
                material.ai_status = "processing"
                material.ai_attempt_count += 1
                material.ai_started_at = _utc_now()
                material.ai_error_code = None
                database.commit()
                stored_path = material.stored_path
                snapshot = {
                    "material_id": material.id,
                    "title": material.title,
                    "memo": material.memo,
                    "media_type": material.media_type,
                    "content_type": material.content_type,
                }
                attempt_count = material.ai_attempt_count
        except SQLAlchemyError:
            logger.exception("material analysis claim failed material_id=%s", material_id)
            return None

        try:
            source_path = self.storage.resolve_existing(stored_path)
        except MaterialStorageError:
            self._mark_failed(material_id, "source_missing")
            return None
        return MaterialAnalysisInput(source_path=source_path, **snapshot), attempt_count

    def _advance_retry(self, material_id: int) -> int | None:
        try:
            with self.session_factory() as database:
                material = database.scalar(
                    select(Material).where(
                        Material.id == material_id,
                        Material.ai_status == "processing",
                    )
                )
                if material is None:
                    return None
                if material.ai_attempt_count >= MAX_ANALYSIS_ATTEMPTS:
                    material.ai_status = "failed"
                    material.ai_error_code = "retry_exhausted"
                    material.ai_started_at = None
                    database.commit()
                    return None
                material.ai_attempt_count += 1
                material.ai_started_at = _utc_now()
                database.commit()
                return material.ai_attempt_count
        except SQLAlchemyError:
            logger.exception("material analysis retry update failed material_id=%s", material_id)
            return None

    def _mark_completed(self, material_id: int, result: AnalysisResult) -> None:
        try:
            with self.session_factory() as database:
                statement = (
                    update(Material)
                    .where(
                        Material.id == material_id,
                        Material.ai_status == "processing",
                    )
                    .values(
                        ai_status="completed",
                        ai_summary=result.summary,
                        ai_model=result.model,
                        ai_prompt_version=result.prompt_version,
                        ai_analyzed_at=_utc_now(),
                        ai_started_at=None,
                        ai_error_code=None,
                    )
                )
                database.execute(statement)
                database.commit()
        except SQLAlchemyError:
            logger.exception("material analysis result save failed material_id=%s", material_id)

    def _mark_failed(self, material_id: int, error_code: str) -> None:
        try:
            with self.session_factory() as database:
                statement = (
                    update(Material)
                    .where(
                        Material.id == material_id,
                        Material.ai_status == "processing",
                    )
                    .values(
                        ai_status="failed",
                        ai_summary=None,
                        ai_model=None,
                        ai_prompt_version=None,
                        ai_analyzed_at=None,
                        ai_started_at=None,
                        ai_error_code=error_code,
                    )
                )
                database.execute(statement)
                database.commit()
        except SQLAlchemyError:
            logger.exception("material analysis failure save failed material_id=%s", material_id)


_coordinator: MaterialAnalysisCoordinator | None = None
_coordinator_lock = Lock()


def set_material_analysis_coordinator(
    coordinator: MaterialAnalysisCoordinator | None,
) -> None:
    global _coordinator
    with _coordinator_lock:
        _coordinator = coordinator


def enqueue_material_analysis(material_id: int) -> bool:
    with _coordinator_lock:
        coordinator = _coordinator
    if coordinator is None:
        return False
    coordinator.enqueue(material_id)
    return True
