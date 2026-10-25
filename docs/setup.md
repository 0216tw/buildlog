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
| React가 호출하는 FastAPI API 기본 경로 | `http://localhost:8000/api` |
| FastAPI 상태 확인 경로 | `http://localhost:8000/api/health` |

FastAPI의 CORS 설정에서는 개발 중 React 주소인 `http://localhost:5173`만 허용합니다. 모든 주소를 무조건 허용하지 않습니다.

FastAPI 프로세스는 `127.0.0.1:8000`에서 실행해도 되지만, 브라우저의 React 화면과 API 요청은 모두 `localhost` 호스트를 사용합니다. `localhost:5173`에서 `127.0.0.1:8000`으로 요청하면 브라우저가 로그인 쿠키를 보내지 않아 보호 API가 `401 Unauthorized`를 반환할 수 있습니다.

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

## 16. Figma 대시보드 예시 화면 추가 (2026-10-20)

- Figma의 `Dashboard · Desktop · 1440` 노드를 React 요소와 전용 CSS로 구현했습니다.
- 기존 화면을 바꾸지 않고 `/dashboard` 경로에 별도 예시 페이지를 추가했습니다.
- 공부 기록·할 일·오류 기록·공개 기록·계정 설정 버튼은 기존 화면 경로로 연결했습니다.
- 할 일 체크는 화면의 React 상태만 변경하며 새로고침하면 Figma 예시 상태로 돌아갑니다.
- 백엔드, 데이터베이스, 환경 변수, 기존 로그인·기록 기능은 변경하지 않았습니다.
- 대시보드 예시 데이터 테스트와 프론트엔드 전체 테스트 11개, 프로덕션 빌드를 통과했습니다.
- 2026-10-20 Figma 재확인 결과에 맞춰 `공부 기록 쓰기` 버튼 배경색만 빨간색(`#D92D20`)으로 갱신했습니다. 기존 화면 동작과 데이터 값은 변경하지 않았습니다.
- `/dashboard`가 기존 `GET /api/auth/me`를 호출해 로그인 사용자의 실제 닉네임과 첫 글자를 인사말·사이드바에 표시하도록 변경했습니다. 비로그인 상태는 로그인 화면으로 이동하며, 사용자 조회 중에는 예시 닉네임을 표시하지 않습니다.
- 닉네임 연동 변경 후 프론트엔드 테스트 11개, 프로덕션 빌드, 백엔드 인증 테스트 14개를 통과했습니다. 실제 로그인 계정으로 브라우저에 표시되는 흐름은 아직 직접 확인하지 않았습니다.
- `/auth/me`의 반복적인 401 원인은 React가 `localhost`, API가 `127.0.0.1`을 사용해 세션 쿠키가 요청에 포함되지 않은 것이었습니다. React의 기본 API 주소와 `.env.example`을 `http://localhost:8000/api`로 통일했습니다. 변경 후 프론트엔드 테스트 11개, 빌드, 백엔드 인증 테스트 14개와 실제 CORS 응답을 확인했습니다. 로그인 화면에서 한 번 다시 로그인하는 브라우저 확인은 남아 있습니다.
- 현재 자동 브라우저가 제공되지 않아 실제 렌더링 캡처 비교는 확인하지 못했습니다.

다음 작업은 사용자가 `frontend`에서 개발 서버를 실행하고 `http://localhost:5173/dashboard`를 열어 화면을 직접 확인하는 것입니다.

## 17. 비공개 학습 자료함 확장 문서 준비 (2026-10-20)

- 현재 `/materials`는 Figma 기반 React 화면과 디자인 확인용 예시 데이터까지만 준비되어 있습니다.
- 실제 기능 범위를 제목, 선택 메모, 파일 한 개, 등록, 내 목록, 원본 보기와 삭제로 확정해 `PRD.md`와 `spec.md`에 추가했습니다.
- 실제 파일은 `backend/uploads`, 메타정보는 Supabase PostgreSQL의 `materials` 테이블에 저장하는 구조로 정했습니다.
- 기존 쿠키 로그인과 FastAPI의 `get_current_user`를 모든 자료 API에서 재사용하고, 자료는 작성자 본인만 접근하도록 정했습니다.
- 개발 순서를 M1 파일 선택 → M2 테이블 준비 → M3 업로드 API → M4 조회·삭제 API → M5 화면 연결로 `plan.md`에 나눴습니다.
- 이번 작업은 문서만 변경했으며 API, 테이블, 파일 저장, 패키지와 현재 React 동작은 구현하거나 변경하지 않았습니다.

다음 작업은 Phase M1만 진행해 파일 선택과 브라우저 입력 검사를 준비하는 것입니다.

### 학습 자료함 SDD 추가 (2026-10-20)

- `docs/sdd.md`에 학습 자료함의 데이터 모델, 파일 저장 구조, API 계약, 인증·소유권 검사, 실패 복구, React 상태와 테스트 기준을 상세히 정리했습니다.
- 실행 기준은 React + FastAPI + Supabase PostgreSQL이며, 자동 테스트만 기존 방식대로 메모리 SQLite3를 사용합니다.
- 파일 시스템과 PostgreSQL이 하나의 트랜잭션이 아니라는 점을 반영해 임시 업로드, 최종 이동, 삭제 격리와 실패 복구 순서를 정했습니다.
- 이번 작업은 설계 문서만 추가했으며 테이블, migration, API, 업로드 폴더, 패키지와 React 동작은 변경하지 않았습니다.

다음 작업은 SDD의 Phase M1 범위에 따라 파일 선택과 브라우저 입력 검사만 구현하는 것입니다.

## 18. 비공개 학습 자료함 구현 결과 (2026-10-20)

### Phase별 완료 내용

- M1: 제목·메모 상태, 파일 한 개 선택, PNG·JPG·MP4 형식과 크기 검사를 `/materials`에 연결했습니다.
- M2: `Material` 모델과 `20261020_04_create_materials` migration을 만들고 업로드 파일의 Git 제외 규칙을 추가했습니다.
- M3: 임시 파일 스트리밍, 실제 형식 검사, UUID 저장 이름과 DB 실패 정리를 포함한 `POST /api/materials`를 구현했습니다.
- M4: 작성자 전용 목록, 원본 보기와 삭제 API를 구현하고 다른 사용자 자료는 동일한 `404`로 숨겼습니다.
- M5: 예시 자료를 제거하고 실제 등록·목록·필터·원본 보기·삭제 흐름을 React 화면에 연결했습니다.

### 확인 완료

| 확인 항목 | 결과 |
| --- | --- |
| 백엔드 전체 테스트 | 36개 통과 |
| 제목·메모·이미지·영상 경계값 | 자동 테스트 통과 |
| 프론트엔드 전체 테스트 | 19개 통과 |
| 프론트엔드 프로덕션 빌드 | 통과 |
| Supabase Alembic 적용 | `20261020_04 (head)` |
| Alembic 모델 차이 검사 | 새 변경 없음 |
| Supabase 실제 API 스모크 테스트 | 회원가입·로그인·업로드·목록·원본·삭제 통과 |
| 스모크 테스트 임시 사용자·자료 정리 | 완료 |
| 실행 중 `/materials` 화면 HTTP 응답 | `200 OK` |
| 비로그인 자료 API 접근 | `401 Unauthorized` |
| 비밀번호·연결 문자열 출력 | 하지 않음 |

### 직접 확인이 남은 항목

- 실제 브라우저에서 PNG·JPG·MP4 선택과 오류 안내 확인
- 원본 파일 새 창 표시와 브라우저 새 창 차단 안내 확인
- 삭제 확인창의 취소·동의 흐름 확인
- 서버 재시작 전후 목록과 원본 유지 확인
- 너비 360px 이상의 실제 모바일 또는 브라우저 반응형 조작 확인
- 현재 실행 환경에 제어 가능한 브라우저가 없어 자동 화면 조작은 확인하지 못함

다음 작업은 백엔드와 프론트엔드를 실행하고 `http://localhost:5173/materials`에서 실제 브라우저 흐름을 확인하는 것입니다.

### 학습 자료 이미지 표시 수정 (2026-10-20)

- 원인: 목록 카드가 저장된 이미지 파일을 사용하지 않고 `PNG` 또는 `JPG` 글자만 표시하는 고정 자리 표시자를 렌더링하고 있었습니다.
- 확인: Supabase의 이미지 자료 2건과 연결된 `backend/uploads` 원본 파일 2개가 모두 존재했습니다.
- 수정: 이미지 자료는 작성자 인증을 거치는 `GET /api/materials/{id}/file` 주소를 `<img>`에 연결해 실제 원본을 카드 안에 표시합니다.
- 보안: `backend/uploads`를 공개 경로로 열지 않았으며 기존 쿠키 로그인과 자료 소유권 검사를 그대로 통과해야 이미지를 볼 수 있습니다.
- 실패 처리: 원본 요청이 실패하면 깨진 이미지 대신 `이미지를 불러오지 못했습니다` 안내를 표시합니다.
- 검증: 프론트엔드 전체 테스트 20개와 프로덕션 빌드를 통과했습니다.

실제 브라우저에서는 `/materials`를 새로고침한 뒤 이미지가 표시되는지 확인해야 합니다.

## 19. 학습 자료 AI 분석·요약 개발 계획 (2026-10-20)

- 현재 자료 등록 API, `materials` 테이블, `backend/uploads` 저장, 작성자 전용 조회·삭제와 `/materials` 화면 연결 상태를 확인했습니다.
- OpenAI 공식 문서를 확인해 이미지는 Responses API로 직접 분석하고, MP4는 대표 프레임과 선택적 음성 자막으로 나눠 분석하는 계획을 `docs/plan.md` 9장에 추가했습니다.
- 기본 요약 모델은 비용에 민감한 이미지 작업용 `gpt-6-luna`, 영상 음성 전사는 `gpt-4o-mini-transcribe`로 계획했습니다. 구현 시작 시 공식 지원과 가격을 다시 확인합니다.
- 사용자가 넣을 새 환경변수는 백엔드의 `OPENAI_API_KEY` 하나이며, 모델과 처리 제한에는 코드 기본값을 둘 계획입니다.
- AI 실패가 원본 등록을 취소하지 않도록 `pending`, `processing`, `completed`, `failed` 상태와 요약을 기존 `materials` 행에 저장하는 구조로 계획했습니다.
- 개발 순서는 AI0 문서 정합성 → AI1 설정·클라이언트 → AI2 DB migration → AI3 이미지 분석 → AI4 영상 분석 → AI5 백그라운드 처리·복구 → AI6 화면 연결 → AI7 전체 검증입니다.
- 이번 작업에서는 계획 문서만 변경했고 코드, DB, migration, 패키지, `.env`와 실제 OpenAI 호출은 변경하거나 실행하지 않았습니다.

다음 작업은 Phase AI0 하나만 진행해 PRD·SPEC·SDD의 기존 `AI 제외` 범위를 새 요구사항과 일치시키는 것입니다.

## 20. 학습 자료 AI 분석·요약 상세 SDD (2026-10-20)

- `docs/sdd.md`에 AI 확장의 전체 구조, 환경설정, DB 열, 상태 머신, 이미지·영상 전처리, OpenAI 요청, 프롬프트, 백그라운드 작업자, 화면 상태, 실패 복구와 테스트 기준을 추가했습니다.
- OpenAI 공식 문서를 다시 확인해 이미지 Base64 입력, Structured Outputs, `store=False`, 음성 파일 25MB 한도와 429 재시도 규칙을 설계에 반영했습니다.
- MP4는 직접 요약 모델에 보내지 않고 최대 8개 대표 프레임과 최대 15분의 선택적 음성 자막으로 분석하도록 구체화했습니다.
- 외부 큐 없이 현재 단일 FastAPI 인스턴스에서 동작하도록 DB 상태를 최종 기준으로 삼는 복구 가능한 작업자를 설계했습니다.
- 기존 자료는 `not_requested`, 새 자료는 `pending`으로 구분하고 AI 실패가 원본 저장·조회·삭제를 취소하지 않게 했습니다.
- 현재 PRD와 SPEC에는 AI가 제외 범위로 남아 있다는 문서 불일치를 명시했습니다.
- 이번 작업은 SDD와 진행 기록만 변경했으며 코드, DB, migration, 패키지, `.env`와 실제 OpenAI 호출은 변경하거나 실행하지 않았습니다.

다음 작업은 Phase AI0 하나만 진행해 `PRD.md`와 `spec.md`의 AI 제외 문구를 새 확장 요구사항으로 갱신하는 것입니다.

## 21. 학습 자료 AI 기능 Phase별 실행 구분 (2026-10-20)

- `docs/sdd.md` 42장에 AI0부터 AI7까지 각 Phase의 목표, 작업 범위, 확인 방법과 완료 조건을 상세히 나눴습니다.
- 개발 순서는 AI0 문서 정합성 → AI1 환경설정·OpenAI 호출 경계 → AI2 DB·migration → AI3 이미지 분석 → AI4 영상 분석 → AI5 자동 실행·복구 → AI6 화면 연결 → AI7 전체 검증입니다.
- 각 Phase의 완료 조건을 확인한 뒤 다음 단계로 이동하며, 앞 단계에서 뒤 단계의 코드나 DB를 함께 변경하지 않습니다.
- 사용자가 미리 준비할 값은 없습니다. 실제 API 확인을 진행하는 AI7에서만 `backend/.env`에 `OPENAI_API_KEY`를 직접 입력하면 됩니다.
- 이번 작업에서는 Phase 구분 문서만 변경했습니다. 코드, DB, migration, 패키지, `.env`와 실제 OpenAI 호출은 변경하거나 실행하지 않았습니다.

다음 작업은 Phase AI0 하나만 진행해 `docs/PRD.md`와 `docs/spec.md`의 기존 AI 제외 범위를 현재 요구사항과 일치시키는 것입니다.

## 22. 학습 자료 AI 분석·요약 구현 결과 (2026-10-20)

### 완료한 작업

- AI0부터 AI7까지 문서 정합성, 설정, DB, 이미지·영상 분석, 백그라운드 처리, 화면 연결과 자동 검증을 순서대로 수행했습니다.
- OpenAI SDK `3.35.1`, Pillow `13.0.0`, imageio-ffmpeg `0.6.0`을 백엔드 요구사항에 추가하고 현재 가상환경에 설치했습니다.
- `materials` 테이블에 AI 상태, 요약, 모델, 프롬프트 버전, 시도 횟수, 처리 시각과 안전한 오류 코드를 저장하도록 확장했습니다.
- Supabase PostgreSQL에 `20261020_05` migration을 적용했고 현재 Alembic head와 모델이 일치합니다.
- 기능 배포 전 자료는 `not_requested`, 새 자료는 `pending`으로 구분합니다.
- 새 자료 등록은 AI 완료를 기다리지 않고 `201`을 반환하며, 작업자가 이미지 또는 영상을 분석합니다.
- AI 실패가 원본 등록을 취소하지 않으며 원본 보기와 삭제를 계속 사용할 수 있습니다.
- `/materials`에 분석 대기, 분석 중, 요약 완료, 요약 실패와 실제 요약을 표시하고 처리 중일 때만 목록을 갱신합니다.

### 사용자가 입력할 값

`backend/.env`에 다음 한 줄을 추가합니다. 실제 키는 답변, 문서와 Git에 넣지 않습니다.

```dotenv
OPENAI_API_KEY=본인의_OpenAI_API_키
```

다른 AI 설정은 입력하지 않아도 됩니다. 요약 모델, 전사 모델, 프레임 수, 처리 시간과 재시도 횟수에는 코드 기본값이 있습니다.

키를 넣지 않으면 서버 시작 시 `OPENAI_API_KEY`를 확인하라는 안전한 오류가 표시됩니다. 키가 잘못됐거나 권한·결제·사용 한도 문제가 있으면 원본은 유지되고 해당 자료만 `요약 실패`로 표시됩니다.

### 실행 방법

백엔드 터미널:

```powershell
cd C:\Users\xodn_\Desktop\buildlog\backend
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

현재 로컬 파일 작업자는 한 프로세스에서 실행하므로 `--workers` 옵션은 추가하지 않습니다.

프론트엔드 터미널:

```powershell
cd C:\Users\xodn_\Desktop\buildlog\frontend
npm.cmd install
npm.cmd run dev
```

브라우저에서 `http://localhost:5173/materials`를 엽니다. 로그인 후 작은 PNG를 등록하고 `분석 대기` → `분석 중` → `요약 완료`로 바뀌는지 확인합니다. 그다음 짧은 무음 MP4와 음성이 있는 MP4를 각각 확인합니다.

### 확인 결과

| 확인 항목 | 결과 |
| --- | --- |
| 백엔드 전체 테스트 | 45개 통과 |
| Python 구문·import compileall | 통과 |
| 이미지 Base64·Structured Outputs 요청 구성 | 가짜 OpenAI 클라이언트 테스트 통과 |
| 영상 프레임·음성 추출과 임시 파일 정리 | 실제 FFmpeg 기반 자동 테스트 통과 |
| 백그라운드 상태·재시도·시작 복구 | 자동 테스트 통과 |
| 임시 placeholder 키로 앱 시작·health 확인 | 통과, OpenAI 호출은 하지 않음 |
| 프론트엔드 전체 테스트 | 21개 통과 |
| 프론트엔드 프로덕션 빌드 | 통과 |
| Supabase Alembic 적용 | `20261020_05 (head)` |
| Alembic 모델 차이 검사 | 새 변경 없음 |
| `.env`와 업로드·분석 임시 파일 Git 제외 | 확인 |

### 확인하지 못한 항목

- 현재 `OPENAI_API_KEY`가 설정되지 않아 실제 OpenAI 이미지·영상 호출은 실행하지 않았습니다.
- 실제 API 호출 비용, 현재 계정의 모델 접근 권한, 결제·사용 한도는 확인하지 않았습니다.
- 실제 브라우저에서 업로드 후 상태가 바뀌고 요약이 표시되는 흐름은 키 입력 후 확인해야 합니다.

다음 작업은 사용자가 `backend/.env`에 `OPENAI_API_KEY`를 입력한 뒤 서버를 다시 켜고 실제 PNG 한 건으로 연결을 확인하는 것입니다.

## 23. 09 교안 오류 확인 실습과 캡처 준비 (2026-10-21)

### 추가한 실습 기능

- 기존 기능과 분리된 React `/debug-practice` 화면을 추가했습니다.
- 프론트 `ReferenceError`, 잘못된 API 경로의 `404`, FastAPI의 `ZeroDivisionError`와 `500`을 의도적으로 재현합니다.
- 실습 API는 DB, 업로드 파일과 OpenAI를 사용하지 않습니다.
- 수업이 끝나면 실습 화면과 API만 따로 제거할 수 있도록 파일을 분리했습니다.

### 독립 캡처 방식

- 사용자가 작업 중인 Chrome, VS Code, `5173`·`8000` 서버를 조작하지 않았습니다.
- 테스트용 메모리 SQLite를 사용하는 FastAPI를 `8010`, React를 `5174`에서 일시적으로 실행했습니다.
- 임시 폴더의 `playwright-core`와 별도 Headless Chrome으로 실제 Console, Network, FastAPI 로그를 수집했습니다.
- 캡처가 끝난 뒤 두 임시 서버와 Headless Chrome을 종료했습니다.
- 캡처 파일은 `docs/assets/09-debugging/`에 저장했습니다.

### 확인 결과

| 확인 항목 | 결과 |
| --- | --- |
| 프론트 전체 테스트 | 23개 통과 |
| 프론트 프로덕션 빌드 | 통과 |
| 백엔드 전체 테스트 | 47개 통과 |
| 프론트 ReferenceError 재현 | 실제 Console 증거 수집 완료 |
| 잘못된 `/pingg` 요청 | 실제 `404 Not Found` 수집 완료 |
| 서버의 `1 / 0` 실행 | 실제 `500`과 `ZeroDivisionError` 로그 수집 완료 |
| Notion 09 교안 | 1.1 이전 유지, 1.1~1.4 재구성 및 캡처 7장 첨부 |
| 429 오류 재발 | npm 설치·독립 캡처·Notion 업로드와 수정에서 재발하지 않음 |

### 다음 작업

- 사용자가 09 교안의 1.1~1.4 설명과 이미지 배치를 읽고 수정할 부분을 지정합니다.
- 수업용 `/debug-practice` 코드는 교안 실습을 마친 뒤 제거 여부를 결정합니다.

## 24. 09 교안 단계별 오류 재현 방식으로 재구성 (2026-10-21)

### 완료한 내용

- Notion 09 교안의 큰 목차를 `오류를 직접 만들고 확인하는 법`, `확인한 내용으로 AI에게 효율적으로 질문하는 법` 두 개로 정리했습니다.
- 학생이 `DebugPracticePage.jsx`와 `debug_practice.py`를 직접 만들고 코드를 단계별로 바꾸도록 전체 흐름을 다시 작성했습니다.
- 프론트 정상 동작과 `ReferenceError`, API 미작성 `404`, 주소 오타 `404`, 잘못된 요청 데이터 `422`, backend 내부 `IndexError`와 `500`을 순서대로 실습하도록 구성했습니다.
- 각 단계에 복사 가능한 코드, Console·Network·backend 터미널 확인 방법, 진단용·수정용 AI 질문 예시를 넣었습니다.
- 기존 실습 화면과 API를 정상 결과와 오류 결과를 비교할 수 있는 형태로 확장했습니다.

### 독립 캡처와 확인 결과

- 사용자의 Chrome과 기존 서버를 조작하지 않고 테스트용 FastAPI `8011`, React `5175`, 별도 Headless Chrome을 사용했습니다.
- 정상·오류·수정 결과와 Network·backend 로그 캡처 13장을 `docs/assets/09-debugging-v2/`에 만들었습니다.
- 교안에는 중복을 제외한 실제 캡처 8장을 첨부했고, 다시 읽어 두 개의 큰 목차와 8개 이미지가 모두 남아 있음을 확인했습니다.
- 실습용 backend 테스트 5개, frontend 전체 테스트 23개, frontend 프로덕션 빌드가 통과했습니다.
- backend 전체 테스트는 50개 중 49개가 통과했고 기존 AI 자료 분석 작업자 테스트 1개가 전체 실행에서 실패했습니다. 해당 테스트는 단독 실행하면 통과하며, 이번 실습 코드와 무관한 테스트 간 상태 공유 문제로 확인이 필요합니다.
- 임시 설치와 캡처, Notion 파일 업로드와 본문 수정에서 `429`는 재발하지 않았습니다.
- 캡처가 끝난 뒤 `8011`, `5175` 포트가 모두 종료된 것을 확인했습니다.

### 다음 작업

- 사용자가 새 교안을 읽고 설명 순서, 코드 분량, 캡처 배치에서 수정할 부분을 지정합니다.
- 필요하면 기존 AI 자료 분석 작업자 테스트의 전체 실행 시 상태 공유 문제를 별도 작업으로 진단합니다.

## 25. 09 교안 실습용 코드 제거 (2026-10-21)

### 완료한 내용

- 학생이 교안을 따라 처음부터 직접 만들 수 있도록 `/debug-practice` React 화면과 전용 CSS를 제거했습니다.
- frontend의 실습 화면 연결 코드와 실습 전용 테스트를 제거했습니다.
- FastAPI의 `/api/debug-practice` 라우터와 실습 전용 테스트를 제거했습니다.
- 교안 캡처 자동화 스크립트와 프로젝트 안의 로컬 캡처 파일을 제거했습니다.
- Notion 09 교안에 업로드된 설명과 이미지는 유지했습니다.

### 확인 결과

- frontend와 backend에서 `debug-practice`, `DebugPractice` 참조가 남지 않았습니다.
- frontend 전체 테스트 21개와 프로덕션 빌드가 통과했습니다.
- AI 자료 분석 작업자 테스트가 같은 메모리 SQLite 연결을 동시에 조회하지 않도록 작업 큐 완료 후 상태를 확인하게 안정화했습니다.
- backend 전체 테스트 45개를 연속 두 번 실행했고 모두 통과했습니다.

### 다음 작업

- 사용자가 Notion 09 교안의 1-1부터 순서대로 실습 파일을 직접 만듭니다.

## 26. 09 교안 독립 실습 구조로 재작성 (2026-10-21)

### 완료한 내용

- Notion 09 교안의 실습 코드를 기존 BuildLog의 React 라우팅, API 클라이언트, FastAPI 라우터와 완전히 분리했습니다.
- 모든 실습 파일을 프로젝트 최상위의 `debug-practice/frontend`, `debug-practice/backend` 안에서만 만들도록 교안을 다시 작성했습니다.
- 실습 frontend는 별도 `package.json`과 `5176` 포트, 실습 backend는 별도 `requirements.txt`, 가상환경, FastAPI 앱과 `8012` 포트를 사용합니다.
- 기존 `frontend/`, `backend/`, 로그인, DB, `.env`, 디자인을 사용하거나 수정하지 않는다고 명시했습니다.
- 프론트 `ReferenceError`, API 미작성 `404`, 주소 오타 `404`, 잘못된 데이터 `422`, backend `IndexError`와 `500`을 순서대로 만들고 고치는 코드와 AI 질문 예시를 넣었습니다.
- 독립 환경에서 다시 만든 정상·오류 캡처 10장으로 기존 교안 이미지를 교체했습니다.

### 확인 결과

| 확인 항목 | 결과 |
| --- | --- |
| 독립 frontend 프로덕션 빌드 | 통과 |
| 독립 backend API 확인 | 8개 통과 (`200`, `404`, `422`, `500` 포함) |
| 독립 브라우저 캡처 | 10장 생성 및 육안 확인 |
| Notion 교안 이미지 | 새 캡처 10장 첨부 확인 |
| 기존 프로젝트 의존 표현 | `../api/client.js`, `DebugPracticePage`, `app.include_router`가 남지 않음을 확인 |
| 기존 BuildLog 실행 코드 | 변경하지 않음 |

### 다음 작업

- 사용자가 Notion 교안의 `debug-practice/` 생성 단계부터 직접 실습합니다.
- 실습이 끝나면 학생은 `debug-practice/` 폴더만 제거하고 기존 BuildLog는 그대로 유지합니다.
