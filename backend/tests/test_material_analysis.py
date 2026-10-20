import subprocess
from pathlib import Path
from types import SimpleNamespace

import imageio_ffmpeg
from PIL import Image
import pytest
from sqlalchemy import select

from app.db.database import SessionLocal
from app.models import Material, User
from app.services.material_analysis import (
    AnalysisFailure,
    AnalysisResult,
    MaterialAnalysisInput,
    MaterialSummaryOutput,
    OpenAIMaterialAnalyzer,
    mask_secrets,
)
from app.services.material_analysis_worker import MaterialAnalysisCoordinator
from app.services.material_media import image_to_data_url, prepare_video, representative_timestamps
from app.services.material_storage import MaterialStorage


VALID_SUMMARY = "핵심 내용: API 요청 흐름\n중요 키워드: HTTP\n복습할 점: 상태 코드"


class FakeResponses:
    def __init__(self, summary: str = VALID_SUMMARY):
        self.summary = summary
        self.requests = []

    def parse(self, **kwargs):
        self.requests.append(kwargs)
        return SimpleNamespace(output_parsed=MaterialSummaryOutput(summary=self.summary))


class FakeTranscriptions:
    def __init__(self, text: str = "API 요청과 응답을 설명합니다."):
        self.text = text
        self.requests = []

    def create(self, **kwargs):
        self.requests.append(kwargs)
        return SimpleNamespace(text=self.text)


class FakeOpenAIClient:
    def __init__(self, summary: str = VALID_SUMMARY):
        self.responses = FakeResponses(summary)
        self.audio = SimpleNamespace(transcriptions=FakeTranscriptions())


class SequenceAnalyzer:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    def analyze(self, _material):
        outcome = self.outcomes[self.calls]
        self.calls += 1
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _create_image(path: Path, size=(64, 32)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color=(30, 100, 220)).save(path, format="PNG")


def _create_pending_material(storage: MaterialStorage) -> tuple[int, Path]:
    source_path = storage.upload_root / "1" / "material.png"
    _create_image(source_path)
    with SessionLocal() as database:
        user = User(
            email="analysis@example.com",
            password_hash="hash",
            nickname="분석사용자",
        )
        database.add(user)
        database.flush()
        material = Material(
            user_id=user.id,
            title="분석 자료",
            memo="요청 흐름",
            original_filename="material.png",
            stored_path="1/material.png",
            media_type="image",
            content_type="image/png",
            size_bytes=source_path.stat().st_size,
            ai_status="pending",
        )
        database.add(material)
        database.commit()
        return material.id, source_path


def test_image_preprocessing_resizes_without_changing_original(tmp_path: Path):
    source = tmp_path / "large.png"
    _create_image(source, size=(2400, 1200))
    original = source.read_bytes()

    data_url = image_to_data_url(source, "image/png")

    assert data_url.startswith("data:image/png;base64,")
    assert source.read_bytes() == original


def test_analyzer_requires_only_the_named_api_key(tmp_path: Path):
    with pytest.raises(AnalysisFailure) as captured:
        OpenAIMaterialAnalyzer("   ", tmp_path / ".analysis")
    assert captured.value.code == "configuration_missing"


def test_image_analyzer_uses_private_data_url_and_structured_output(tmp_path: Path):
    source = tmp_path / "note.png"
    _create_image(source)
    client = FakeOpenAIClient()
    analyzer = OpenAIMaterialAnalyzer("test-key", tmp_path / ".analysis", client=client)

    result = analyzer.analyze(
        MaterialAnalysisInput(
            material_id=1,
            title="REST API",
            memo="요청 흐름",
            media_type="image",
            content_type="image/png",
            source_path=source,
        )
    )

    assert result.summary == VALID_SUMMARY
    request = client.responses.requests[0]
    assert request["model"] == "gpt-6-luna"
    assert request["reasoning"] == {"effort": "none"}
    assert request["store"] is False
    assert request["text_format"] is MaterialSummaryOutput
    image_input = request["input"][0]["content"][1]
    assert image_input["image_url"].startswith("data:image/png;base64,")
    assert image_input["detail"] == "auto"
    assert str(source) not in str(request)


def test_summary_validation_and_secret_masking():
    assert "sk-example" not in mask_secrets(f"{VALID_SUMMARY}\nsk-example12345678")
    with pytest.raises(ValueError, match="요약 형식"):
        MaterialSummaryOutput(summary="제목 없는 요약")
    with pytest.raises(ValueError, match="요약 길이"):
        MaterialSummaryOutput(
            summary="핵심 내용: " + "가" * 1000 + "\n중요 키워드: 키\n복습할 점: 복습"
        )


def test_worker_completes_and_retries_transient_failures(tmp_path: Path):
    storage = MaterialStorage(tmp_path / "uploads")
    material_id, _source = _create_pending_material(storage)
    analyzer = SequenceAnalyzer(
        [
            AnalysisFailure("rate_limited", retryable=True, retry_after=0),
            AnalysisFailure("provider_unavailable", retryable=True, retry_after=0),
            AnalysisResult(summary=VALID_SUMMARY),
        ]
    )
    coordinator = MaterialAnalysisCoordinator(SessionLocal, analyzer, storage)

    coordinator.process_now(material_id)

    with SessionLocal() as database:
        material = database.get(Material, material_id)
        assert material.ai_status == "completed"
        assert material.ai_summary == VALID_SUMMARY
        assert material.ai_attempt_count == 3
        assert material.ai_model == "gpt-6-luna"
        assert material.ai_error_code is None
    assert analyzer.calls == 3


def test_worker_preserves_source_when_analysis_fails(tmp_path: Path):
    storage = MaterialStorage(tmp_path / "uploads")
    material_id, source = _create_pending_material(storage)
    coordinator = MaterialAnalysisCoordinator(
        SessionLocal,
        SequenceAnalyzer([AnalysisFailure("authentication_failed")]),
        storage,
    )

    coordinator.process_now(material_id)

    with SessionLocal() as database:
        material = database.get(Material, material_id)
        assert material.ai_status == "failed"
        assert material.ai_summary is None
        assert material.ai_error_code == "authentication_failed"
    assert source.is_file()


def test_worker_recovers_interrupted_rows(tmp_path: Path):
    storage = MaterialStorage(tmp_path / "uploads")
    material_id, _source = _create_pending_material(storage)
    with SessionLocal() as database:
        material = database.get(Material, material_id)
        material.ai_status = "processing"
        material.ai_attempt_count = 1
        database.commit()

    coordinator = MaterialAnalysisCoordinator(
        SessionLocal,
        SequenceAnalyzer([AnalysisResult(summary=VALID_SUMMARY)]),
        storage,
    )
    coordinator.recover_interrupted()

    with SessionLocal() as database:
        assert database.get(Material, material_id).ai_status == "pending"


def test_worker_lifecycle_processes_pending_queue(tmp_path: Path):
    storage = MaterialStorage(tmp_path / "uploads")
    material_id, _source = _create_pending_material(storage)
    coordinator = MaterialAnalysisCoordinator(
        SessionLocal,
        SequenceAnalyzer([AnalysisResult(summary=VALID_SUMMARY)]),
        storage,
        poll_interval_seconds=0.01,
    )

    coordinator.start()
    try:
        coordinator._queue.join()
    finally:
        coordinator.stop()

    with SessionLocal() as database:
        assert database.get(Material, material_id).ai_status == "completed"


def test_video_preparation_extracts_frames_audio_and_cleans_temp_files(tmp_path: Path):
    video_path = tmp_path / "lesson.mp4"
    executable = imageio_ffmpeg.get_ffmpeg_exe()
    command = [
        executable,
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "lavfi",
        "-i",
        "color=c=blue:s=320x240:d=1",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=440:duration=1",
        "-shortest",
        "-c:v",
        "mpeg4",
        "-c:a",
        "aac",
        "-y",
        str(video_path),
    ]
    subprocess.run(command, check=True, capture_output=True)
    analysis_root = tmp_path / ".analysis"

    with prepare_video(video_path, analysis_root, 7) as prepared:
        assert 1 <= len(prepared.frame_data_urls) <= 8
        assert all(value.startswith("data:image/jpeg;base64,") for value in prepared.frame_data_urls)
        assert prepared.audio_files
        assert all(path.stat().st_size < 24 * 1024 * 1024 for path in prepared.audio_files)
        temporary_directories = list(analysis_root.iterdir())
        assert len(temporary_directories) == 1

    assert list(analysis_root.iterdir()) == []
    assert representative_timestamps(0.5) == (0.0,)

    client = FakeOpenAIClient()
    analyzer = OpenAIMaterialAnalyzer("test-key", analysis_root, client=client)
    result = analyzer.analyze(
        MaterialAnalysisInput(
            material_id=7,
            title="영상 자료",
            memo=None,
            media_type="video",
            content_type="video/mp4",
            source_path=video_path,
        )
    )

    assert result.summary == VALID_SUMMARY
    assert client.audio.transcriptions.requests
    summary_content = client.responses.requests[0]["input"][0]["content"]
    assert any("음성 자막" in item.get("text", "") for item in summary_content)
    assert all(
        item["detail"] == "low"
        for item in summary_content
        if item["type"] == "input_image"
    )
    assert list(analysis_root.iterdir()) == []
