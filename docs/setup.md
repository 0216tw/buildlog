# BuildLog 개발 환경 기준

## 1. 문서 목적

이 문서는 Phase 0부터 Phase 3까지의 결과와 이후 개발에서 사용할 환경 기준을 기록합니다.

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
| `backend/` | FastAPI 기본 구조와 테스트 생성 | 정상 |
| `frontend/` | React 기본 구조와 테스트 생성 | 정상 |
| `database/` | 기존 `buildlog.sqlite3` 보존, Git 제외 | 이전하지 않음 |
| Python 가상환경 | `backend/.venv` | 생성 완료, Git 제외 |
| `node_modules` | `frontend/node_modules` | 생성 완료, Git 제외 |
| 실제 `.env` | `backend/.env` | 생성 완료, 내용은 Git 제외·비공개 |
| Git 저장소 | `main` 브랜치와 `origin` 연결 | 사용 가능 |

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

현재 기술 구성은 React, FastAPI, 실행용 Supabase PostgreSQL, 테스트용 메모리 SQLite3입니다. 기존 SQLite3 파일은 보존하지만 실행 시 자동으로 사용하거나 데이터를 이전하지 않습니다.

## 4. 사용할 버전 기준

현재 설치된 환경과 2026년 10월 14일의 공식 배포 정보를 기준으로 다음 버전을 첫 설치 기준으로 사용합니다. 실제 설치는 Phase 1과 Phase 2에서 나누어 진행하고 설치 후 정확한 버전을 파일에 고정합니다.

| 도구 | 기준 버전 | 판단 |
| --- | --- | --- |
| Python | 3.12.7 | 현재 설치 버전 유지 |
| FastAPI | 0.143.0 | Python 3.12 지원 확인 |
| Uvicorn | 0.54.0 | FastAPI 개발 서버로 설치 |
| React | 19.3.0 | 공식 최신 안정 버전 |
| Vite | 8.3.4 | Node.js 24.14.0이 요구 조건을 충족 |
| Vite React 플러그인 | 6.1.2 | React 개발 화면에 사용 |
| pytest | 9.1.1 | 백엔드 자동 테스트에 사용 |
| httpx2 | 2.13.1 | FastAPI 테스트 요청에 사용 |
| SQLAlchemy | 2.0.54 | SQLite3 연결과 모델에 설치 |
| Alembic | 1.20.0 | SQLite3 변경 이력에 설치 |
| pwdlib | 0.3.1 | 비밀번호를 Argon2 방식으로 안전하게 처리 |
| email-validator | 2.3.0 | 이메일 형식 확인 |
| psycopg | 3.3.6 | FastAPI와 Alembic의 PostgreSQL 연결 |
| python-dotenv | 1.2.4 | `backend/.env` 읽기 |

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
| `DATABASE_URL` | FastAPI·Alembic | Supabase Session pooler PostgreSQL 연결 주소 |
| `TEST_DATABASE_URL` | 백엔드 테스트 | 테스트용 메모리 SQLite3 연결 주소 |
| `FRONTEND_ORIGIN` | FastAPI | 요청을 허용할 React 주소 |
| `VITE_API_BASE_URL` | React | 호출할 FastAPI API 기본 주소 |
| `SESSION_COOKIE_SECURE` | FastAPI | HTTPS 환경에서 로그인 쿠키를 HTTPS로만 보낼지 결정 |

백엔드 설정은 `backend/.env.example`을 복사해 `backend/.env`에 작성합니다. 실제 연결값은 문서나 Git에 기록하지 않습니다.

```text
DATABASE_URL=postgresql+psycopg://postgres.PROJECT_REF:URL_ENCODED_PASSWORD@aws-POOLER_INDEX-REGION.pooler.supabase.com:5432/postgres?sslmode=require
FRONTEND_ORIGIN=http://localhost:5173
SESSION_COOKIE_SECURE=false
```

`DATABASE_URL`은 Supabase Dashboard의 **Connect → Session pooler**에서 복사합니다. 포트는 `5432`를 사용하며 예약 문자가 포함된 비밀번호는 URL 인코딩합니다. 실제 값은 `backend/.env`에만 저장하고 채팅, React 코드, 문서, Git 기록에 넣지 않습니다.

실행용 `DATABASE_URL`이 없거나 SQLite3이면 서버와 Alembic은 시작하지 않습니다. 자동 테스트만 명시적으로 메모리 SQLite3를 사용하며 PostgreSQL에 접속하지 않습니다.

## 7. Supabase PostgreSQL 연결 기준

- 새 데이터는 Supabase PostgreSQL에 저장합니다.
- React는 PostgreSQL에 직접 연결하지 않고 FastAPI API만 호출합니다.
- FastAPI와 Alembic은 SQLAlchemy와 psycopg를 통해 연결합니다.
- Session pooler 주소와 포트 `5432`를 사용합니다.
- 연결에는 `sslmode=require`를 적용합니다.
- 데이터 구조 변경은 Alembic으로 기록합니다.
- 같은 명령을 다시 실행해도 적용된 Alembic 변경 이력은 다시 실행되지 않습니다.
- 자동 테스트는 메모리 SQLite3를 사용해 Supabase 데이터를 건드리지 않습니다.
- 기존 SQLite3 파일과 데이터는 삭제하거나 이전하지 않습니다.

## 8. 앞으로 사용할 명령 기준

다음은 각 Phase에서 프로젝트 파일이 만들어진 뒤 사용할 명령의 형태입니다. Phase 0에서는 실행하지 않았습니다.

### 백엔드

`backend` 폴더에서 실행합니다.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
.\.venv\Scripts\python.exe -m pytest
```

### 프론트엔드

Windows PowerShell에서는 `npm` 대신 `npm.cmd`를 사용합니다.

`frontend` 폴더에서 실행합니다.

```powershell
npm.cmd install
npm.cmd run dev
npm.cmd test
npm.cmd run build
```

## 9. 사용자가 준비할 항목

### Phase 1 전

사용자가 별도로 준비할 값이나 설정은 없습니다.

### Supabase 연결 전

- Supabase 프로젝트의 Connect 화면에서 Session pooler 연결 주소를 복사합니다.
- `backend/.env.example`을 참고해 `backend/.env`를 만들고 `DATABASE_URL`을 입력합니다.
- 포트가 `5432`인지 확인합니다. `6543`은 Transaction pooler이므로 사용하지 않습니다.
- 비밀번호의 예약 문자는 URL 인코딩합니다.
- 연결 정보를 입력하기 전에는 실제 DB 연결과 테이블 생성이 완료되지 않습니다.

## 10. Phase 0 결론

- 문서 범위 충돌: 없음
- Python·Node.js 실행 문제: 없음
- SQLite3 사용 문제: 없음
- React·FastAPI 개발을 시작할 환경 차단 요소: 없음
- 지금 필요한 사용자 비밀값: 없음
- 다음 단계: Phase 1 `FastAPI와 React 프로젝트 뼈대 만들기`

## 11. Phase 1 실행 결과

### 만든 항목

- FastAPI 애플리케이션 시작점
- `GET /api/health` 상태 확인 API
- React 기본 화면과 FastAPI 연결 상태 안내
- React에서 사용하는 상태 확인 요청 모듈
- 허용된 React 주소만 받는 CORS 설정
- 백엔드와 프론트엔드 자동 테스트
- 비밀값이 없는 `.env.example`
- Python, Node.js, 테스트, 빌드, SQLite3 생성물을 제외하는 `.gitignore`
- 정확한 패키지 버전을 기록한 Python 요구사항과 npm 잠금 파일

### 자동 확인 결과

| 확인 항목 | 결과 |
| --- | --- |
| FastAPI 상태 API 테스트 | 2개 통과 |
| React API 호출 모듈 테스트 | 2개 통과 |
| React 프로덕션 빌드 | 통과 |
| FastAPI 실제 실행 | `127.0.0.1:8000`에서 정상 |
| React 실제 실행 | `localhost:5173`에서 HTTP 200 응답 |
| React 출처 CORS 요청 | 허용 및 응답 헤더 확인 |
| 허용하지 않은 출처 CORS 요청 | HTTP 400으로 차단 확인 |
| npm 보안 검사 | 알려진 취약점 0개 |

### 남은 직접 확인

자동 브라우저 연결 기능의 초기화 오류로 렌더링된 React 화면을 직접 보지는 못했습니다. 서버 응답, React 빌드, API 호출 코드와 CORS 통신은 모두 확인했습니다.

사용자는 다음 두 서버를 실행한 뒤 `http://localhost:5173`에서 아래 문구가 보이는지만 확인하면 됩니다.

```text
개발 준비가 완료되었습니다.
React와 FastAPI가 정상적으로 연결되었습니다.
```

### 다음 단계

직접 화면 확인까지 끝나면 Phase 2 `데이터베이스 연결과 사용자 데이터 구조`를 시작합니다.

## 12. Phase 2 최초 SQLite3 구현 결과 이력

아래 내용은 Supabase 전환 전의 최초 구현 이력입니다. 현재 실행 DB 기준은 14장의 Supabase 전환 내용을 따릅니다.

### 만든 항목

- SQLAlchemy SQLite3 연결과 요청별 데이터베이스 세션
- 사용자와 로그인 세션 모델
- 이메일·비밀번호·닉네임 입력 규칙
- 사용자와 로그인 세션을 만드는 첫 Alembic 변경 이력
- 개발용 SQLite3와 테스트용 메모리 SQLite3 분리

### 확인 결과

- Alembic 변경 이력을 개발용 SQLite3에 적용했습니다.
- 현재 변경 이력이 최신 상태이며 모델과 차이가 없음을 확인했습니다.
- 자동 테스트가 SQLite3가 아닌 연결 주소를 거부하도록 설정했습니다.
- 실제 SQLite3 파일은 `.gitignore` 규칙으로 Git에서 제외됩니다.

## 13. Phase 3 실행 결과

### 만든 항목

- 이메일·비밀번호·닉네임 회원가입 API와 화면
- 이메일·비밀번호 로그인 API와 화면
- JavaScript에서 읽을 수 없는 HttpOnly 로그인 쿠키와 DB 세션 저장
- 로그인 사용자 확인과 비로그인 접근 차단
- 내 닉네임 변경 API와 계정 설정 화면
- 로그인 성공 후 내 기록 홈 화면 이동

### 자동 확인 결과

| 확인 항목 | 결과 |
| --- | --- |
| 백엔드 전체 테스트 | 16개 통과 |
| 프론트엔드 전체 테스트 | 6개 통과 |
| React 프로덕션 빌드 | 통과 |
| Alembic 변경 이력 적용 | `20261016_01` 적용 |
| 모델과 변경 이력 차이 검사 | 차이 없음 |

### 확인하지 못한 항목

- 실제 브라우저에서 회원가입부터 닉네임 변경까지 직접 조작하는 화면 확인은 아직 하지 못했습니다.

### 다음 작업

- 브라우저 직접 확인을 마치고 Phase 4 `공부 기록·할 일·오류 기록의 데이터 구조`를 진행합니다.

## 14. Supabase PostgreSQL 전환 준비 결과

### 변경한 항목

- `backend/.env`의 `DATABASE_URL`을 필수로 읽도록 변경했습니다.
- Supabase Session pooler 호스트와 포트 `5432`를 확인하고 PostgreSQL이 아니면 실행을 중단합니다.
- SQLite3로 자동 대체하는 동작을 제거했습니다.
- psycopg PostgreSQL 드라이버와 python-dotenv를 설치하고 버전을 고정했습니다.
- 기존 사용자·로그인 세션 모델과 첫 Alembic 변경 이력을 PostgreSQL에서도 동작하도록 조정했습니다.
- 기존 SQLite3 파일은 삭제하거나 수정하지 않았습니다.

### 확인한 항목

| 확인 항목 | 결과 |
| --- | --- |
| 백엔드 전체 자동 테스트 | 21개 통과 |
| PostgreSQL용 Alembic SQL 생성 | 통과 |
| 생성 예정 테이블 | `alembic_version`, `users`, `user_sessions` |
| `backend/.env` Git 제외 | 확인 완료 |
| `backend/.env.example` Git 기록 가능 | 확인 완료 |

### 아직 확인하지 못한 항목

- 실제 Supabase 연결 정보가 없으므로 DB 연결은 확인하지 않았습니다.
- 실제 Supabase 테이블 생성은 실행하지 않았습니다.
- Supabase 환경에서 회원가입·로그인은 아직 확인하지 않았습니다.
- 공부 기록·할 일·오류 기록 테이블은 아직 구현되지 않았으므로 이번 변경 이력에 포함되지 않습니다.

### 설정 오류 확인 순서

1. `backend/.env` 파일 이름과 위치를 확인합니다.
2. Supabase Dashboard의 Connect 화면에서 **Session pooler** 주소를 복사했는지 확인합니다.
3. 호스트, 사용자 이름, 프로젝트 참조값을 직접 추측하지 않고 복사했는지 확인합니다.
4. 포트가 `5432`인지 확인합니다.
5. 데이터베이스 비밀번호가 맞는지 확인하고 예약 문자를 URL 인코딩했는지 확인합니다.
6. 연결 주소에 `sslmode=require`가 있는지 확인합니다.

## 15. Phase 4~13 완료 결과 (2026-10-20)

14장의 “아직 확인하지 못한 항목”은 전환 준비 당시의 기록입니다. 이후 사용자가 연결 정보를 입력했고, 아래와 같이 실제 연결과 기능을 확인했습니다.

### 구현한 기능

- 공부 기록·할 일·오류 기록 테이블과 작성·조회·수정·삭제
- 제목·내용·해결 방법 길이와 공백 검증
- 할 일 완료 전환과 미완료 우선 정렬
- 오류 해결 전환과 해결 날짜 관리
- 기본 비공개, 작성자 공개 전환, 공개 기록 통합 목록·필터·검색
- 공개 공부 기록·오류 기록의 댓글 작성·수정·삭제
- 공개 공부 기록·오류 기록의 좋아요·취소·개수
- 공개 공부 기록·할 일·오류 기록·댓글 신고
- 운영자 전용 신고 목록·상세 API와 화면
- 360px 이상 화면을 위한 반응형 React 레이아웃과 공통 오류 안내

### 자동·연결 확인 결과

| 확인 항목 | 결과 |
| --- | --- |
| 백엔드 전체 SQLite3 자동 테스트 | 26개 통과 |
| 프론트엔드 전체 자동 테스트 | 9개 통과 |
| React 프로덕션 빌드 | 통과 |
| PostgreSQL용 Alembic SQL 생성 | 통과 |
| Supabase Alembic 적용 | `20261020_03 (head)` |
| SQLAlchemy 모델과 Supabase 구조 비교 | 추가 변경 없음 |
| Supabase 필수 테이블 존재 | 확인 완료 |
| Supabase 실제 API 스모크 테스트 | 회원가입·로그인·세 기록·공개 검색·댓글·좋아요·신고·완료·해결 통과 |
| Supabase 임시 테스트 데이터 정리 | 완료 |
| 기존 SQLite 파일 보존 | 확인 완료 |
| 실제 비밀 설정의 Git 제외 | 확인 완료 |

### 직접 확인이 남은 항목

- Chrome과 Edge에서 전체 사용자 흐름을 마우스와 키보드로 직접 조작하는 확인
- Windows 환경에서 실행할 수 없는 Safari 최신 두 버전 확인
- 실제 배포 주소에서 HTTPS 쿠키와 모바일 실기기 화면 확인

### 현재 다음 작업

기능 구현 Phase는 모두 끝났습니다. 두 서버를 실행한 뒤 브라우저 직접 확인을 수행하고, 발견되는 문제만 별도 작업으로 수정합니다.
