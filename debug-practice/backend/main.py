import logging

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware


logger = logging.getLogger(__name__)
app = FastAPI(title="독립 오류 확인 실습")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5176"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"message": "실습 서버 실행 중"}


@app.get("/hello")
def hello() -> dict[str, str]:
    return {"message": "프론트와 백엔드가 정상적으로 연결되었습니다."}


@app.get("/server-error")
def server_error() -> dict[str, str]:
    study_records = []

    if not study_records:
        return {"message": "저장된 공부 기록이 없습니다."}

    return {"message": study_records[0]["title"]}