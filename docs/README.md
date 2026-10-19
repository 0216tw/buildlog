BuildLog
학습한 내용과 해결한 오류를 기록하는 서비스입니다.
git으로 변경이력을 관리합니다

# BuildLog 실행 안내

BuildLog는 공부 기록, 할 일, 오류와 해결 방법을 한곳에 저장하고 필요한 기록을 다른 회원과 공유하는 서비스입니다. React 화면과 FastAPI 서버를 사용하며, 실행 데이터는 Supabase PostgreSQL에 저장합니다. 자동 테스트는 별도의 메모리 SQLite3를 사용합니다.

## 처음 한 번 준비하기

### 1. 백엔드 준비

PowerShell에서 `backend` 폴더로 이동해 실행합니다.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

`backend/.env`의 `DATABASE_URL`에 Supabase Dashboard의 **Connect → Session pooler** 주소를 입력합니다. 포트는 `5432`를 사용합니다. 실제 연결 주소와 비밀번호는 Git이나 문서에 넣지 않습니다.

테이블을 준비합니다.

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

이미 적용된 변경은 다시 실행되지 않습니다.

### 2. 프론트엔드 준비

새 PowerShell에서 `frontend` 폴더로 이동해 실행합니다.

```powershell
npm.cmd install
```

## 프로그램 실행하기

첫 번째 PowerShell의 `backend` 폴더에서 FastAPI를 실행합니다.

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

두 번째 PowerShell의 `frontend` 폴더에서 React를 실행합니다.

```powershell
npm.cmd run dev
```

브라우저에서 `http://localhost:5173`을 엽니다. API 상태는 `http://127.0.0.1:8000/api/health`, API 문서는 `http://127.0.0.1:8000/docs`에서 확인할 수 있습니다.

## 제공하는 기능

- 회원가입, 로그인, 닉네임 변경
- 공부 기록 작성·검색·수정·삭제
- 할 일 작성·완료 체크·필터·수정·삭제
- 오류 기록 작성·검색·해결 처리·수정·삭제
- 기록 공개·비공개 전환과 공개 기록 검색
- 공개 공부 기록·오류 기록의 댓글과 좋아요
- 공개 기록·댓글 신고와 운영자 확인
- 너비 360px 이상의 반응형 화면

기록은 처음 만들 때 비공개입니다. 공개 기록은 로그인한 다른 회원이 볼 수 있습니다. 댓글과 좋아요는 공개 공부 기록과 공개 오류 기록에서만 사용합니다.

## 테스트하기

백엔드 테스트는 Supabase가 아닌 메모리 SQLite3만 사용합니다.

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

프론트엔드는 다음과 같이 테스트하고 빌드합니다.

```powershell
cd frontend
npm.cmd test
npm.cmd run build
```

## 설정 문제 확인하기

- `DATABASE_URL이 없습니다`: `backend/.env`가 있는지 확인합니다.
- Session pooler 오류: Supabase Connect 화면에서 주소를 다시 복사하고 포트가 `5432`인지 확인합니다.
- 비밀번호 연결 오류: 비밀번호가 맞는지, 예약 문자가 URL 인코딩되었는지 확인합니다.
- React에서 API 호출 실패: FastAPI가 실행 중인지와 `FRONTEND_ORIGIN=http://localhost:5173`인지 확인합니다.
- 로그인 쿠키 문제: 로컬에서는 `SESSION_COOKIE_SECURE=false`, HTTPS 배포에서는 `true`를 사용합니다.

기존 `database/buildlog.sqlite3`는 삭제하지 않았으며, 현재 실행 DB로 자동 선택되거나 Supabase로 이전되지 않습니다.
