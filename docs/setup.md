# BuildLog 개발 환경 기준

## 1. 문서 목적

이 문서는 2026년 10월 14일 수행한 Phase 0 확인 결과와 이후 개발에서 사용할 환경 기준을 기록합니다.

Phase 0에서는 프로그램 코드 작성, 패키지 설치, 데이터베이스 생성, Git 초기화를 하지 않았습니다.

## 2. 확인한 로컬 환경

| 항목 | 확인 결과 | 상태 |
| --- | --- | --- |
| 작업 폴더 | `C:\Users\xodn_\Desktop\buildlog` | 사용 가능 |
| Python | 3.12.7 | 사용 가능 |
| Python SQLite3 모듈 | 정상 로드 | 사용 가능 |
| SQLite 라이브러리 | 3.45.3 | 사용 가능 |
| Node.js | 24.14.0 | 사용 가능 |
| npm | 11.9.0 | 사용 가능 |
| `backend/` | 비어 있음 | 정상 |
| `frontend/` | 비어 있음 | 정상 |
| `database/` | 비어 있음 | 정상 |
| Python 가상환경 | 없음 | Phase 1에서 생성 예정 |
| `node_modules` | 없음 | Phase 1에서 생성 예정 |
| 실제 `.env` | 없음 | 필요한 Phase에서 생성 예정 |
| Git 저장소 | 초기화되지 않음 | 요청대로 유지 |

## 3. 문서와 기능 범위 확인

`PRD.md`, `spec.md`, `plan.md`를 비교한 결과 첫 MVP의 기능 범위는 서로 일치합니다.

포함하는 기능은 다음과 같습니다.

- 회원가입, 로그인, 닉네임 변경
- 공부 기록
- 할 일
- 오류 기록
- 공개·비공개 설정과 공개 기록 검색
- 댓글과 좋아요
- 신고와 운영자 확인
- 반응형 화면과 공통 실패 처리

첫 버전에 포함하지 않는 기능도 세 문서에서 일치합니다.

- 이메일 확인
- 비밀번호 찾기
- 할 일 마감일
- 할 일 중요도
- 내 할 일 검색
- 댓글 답글

기술 구성은 React, FastAPI, Supabase PostgreSQL, 테스트용 SQLite3로 통일되어 있으며 Django를 전제로 한 내용은 남아 있지 않습니다.

## 4. 사용할 버전 기준

현재 설치된 환경과 2026년 10월 14일의 공식 배포 정보를 기준으로 다음 버전을 첫 설치 기준으로 사용합니다. 실제 설치는 Phase 1과 Phase 2에서 나누어 진행하고 설치 후 정확한 버전을 파일에 고정합니다.

| 도구 | 기준 버전 | 판단 |
| --- | --- | --- |
| Python | 3.12.7 | 현재 설치 버전 유지 |
| FastAPI | 0.143.0 | Python 3.12 지원 확인 |
| React | 19.3.0 | 공식 최신 안정 버전 |
| Vite | 8.3.4 | Node.js 24.14.0이 요구 조건을 충족 |
| SQLAlchemy | 2.1.4 | Python 3.12용 배포 파일 확인 |
| Alembic | 1.19.2 | 1.20.0은 배포 철회 표시가 있어 제외 |

참고한 공식 자료:

- FastAPI: <https://pypi.org/project/fastapi/>
- React 버전: <https://react.dev/versions>
- Vite 시작 안내: <https://vite.dev/guide/>
- SQLAlchemy: <https://pypi.org/project/SQLAlchemy/>
- Alembic: <https://pypi.org/project/alembic/>
- Supabase 데이터베이스 연결: <https://supabase.com/docs/guides/database/connecting-to-postgres>

## 5. 개발 주소

| 역할 | 주소 |
| --- | --- |
| React 개발 서버 | `http://localhost:5173` |
| FastAPI 개발 서버 | `http://127.0.0.1:8000` |
| FastAPI API 기본 경로 | `http://127.0.0.1:8000/api` |
| FastAPI 상태 확인 경로 | `http://127.0.0.1:8000/api/health` |

FastAPI의 CORS 설정에서는 개발 중 React 주소인 `http://localhost:5173`만 허용합니다. 모든 주소를 무조건 허용하지 않습니다.

## 6. 환경 변수 기준

| 이름 | 사용하는 곳 | 용도 |
| --- | --- | --- |
| `DATABASE_URL` | FastAPI | Supabase PostgreSQL 연결 주소 |
| `TEST_DATABASE_URL` | 백엔드 테스트 | SQLite3 테스트 연결 주소 |
| `SECRET_KEY` | FastAPI | 로그인 정보를 안전하게 서명하는 비밀값 |
| `FRONTEND_ORIGIN` | FastAPI | 요청을 허용할 React 주소 |
| `VITE_API_BASE_URL` | React | 호출할 FastAPI API 기본 주소 |

기본값으로 공유할 수 있는 항목은 다음과 같습니다.

```text
TEST_DATABASE_URL=sqlite:///../database/buildlog-test.sqlite3
FRONTEND_ORIGIN=http://localhost:5173
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

`DATABASE_URL`과 `SECRET_KEY`에는 실제 값이 필요하므로 `.env.example`에는 예시나 빈칸만 기록합니다. 실제 값은 `.env`에만 저장하고 채팅, React 코드, 문서, Git 기록에 넣지 않습니다.

자동 테스트는 `TEST_DATABASE_URL`만 사용하게 만들고, Supabase의 `DATABASE_URL`로 테스트가 실행되지 않도록 서버 코드에서 한 번 더 차단합니다.

## 7. Supabase 연결 기준

- Supabase는 PostgreSQL 데이터베이스로만 사용합니다.
- 회원가입과 로그인은 FastAPI에서 처리하며 Supabase Auth는 사용하지 않습니다.
- React는 Supabase에 직접 연결하지 않습니다.
- FastAPI가 SQLAlchemy를 통해 Supabase에 연결합니다.
- 연결 주소는 Supabase Dashboard의 Connect 화면에서 가져옵니다.
- 실제 연결 방식은 FastAPI를 배포할 환경의 IPv4·IPv6 및 서버 실행 방식에 맞춰 Phase 2에서 결정합니다.
- 데이터베이스 연결에는 SSL을 사용합니다.
- Alembic 변경 이력 적용은 테스트 실행과 분리합니다.

## 8. 앞으로 사용할 명령 기준

다음은 각 Phase에서 프로젝트 파일이 만들어진 뒤 사용할 명령의 형태입니다. Phase 0에서는 실행하지 않았습니다.

### 백엔드

```powershell
py -3.12 -m venv .venv
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
python -m pytest
```

### 프론트엔드

Windows PowerShell에서는 `npm` 대신 `npm.cmd`를 사용합니다.

```powershell
npm.cmd run dev
npm.cmd test
npm.cmd run build
```

## 9. 사용자가 준비할 항목

### Phase 1 전

사용자가 별도로 준비할 값이나 설정은 없습니다.

### Phase 2 전

- Supabase 계정과 프로젝트를 준비합니다.
- 프로젝트의 PostgreSQL 연결 주소를 확인합니다.
- 데이터베이스 비밀번호를 확인합니다.
- 비밀값은 채팅으로 전달하지 않고 안내에 따라 로컬 `.env`에 직접 입력합니다.

Supabase 프로젝트가 아직 없어도 Phase 1까지는 진행할 수 있습니다.

## 10. Phase 0 결론

- 문서 범위 충돌: 없음
- Python·Node.js 실행 문제: 없음
- SQLite3 사용 문제: 없음
- React·FastAPI 개발을 시작할 환경 차단 요소: 없음
- 지금 필요한 사용자 비밀값: 없음
- 다음 단계: Phase 1 `FastAPI와 React 프로젝트 뼈대 만들기`
