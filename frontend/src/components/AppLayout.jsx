import { useEffect, useState } from 'react'

import { ApiError, getCurrentUser } from '../api/auth.js'

export default function AppLayout({ navigate, children }) {
  const [user, setUser] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getCurrentUser().then(setUser).catch((requestError) => {
      if (requestError instanceof ApiError && requestError.status === 401) navigate('/login', '로그인이 필요합니다.')
      else setError(requestError.message)
    })
  }, [navigate])

  if (!user && !error) return <main className="page-shell"><p role="status">로그인 상태를 확인하고 있습니다.</p></main>

  return (
    <div className="app-shell">
      <header className="app-header">
        <button className="brand-button" onClick={() => navigate('/')}>BuildLog</button>
        <nav aria-label="주요 메뉴">
          <button onClick={() => navigate('/studies')}>공부 기록</button>
          <button onClick={() => navigate('/todos')}>할 일</button>
          <button onClick={() => navigate('/errors')}>오류 기록</button>
          <button onClick={() => navigate('/materials')}>학습 자료함</button>
          <button onClick={() => navigate('/public')}>공개 기록</button>
          {user?.is_admin && <button onClick={() => navigate('/admin/reports')}>신고 관리</button>}
          <button onClick={() => navigate('/settings')}>설정</button>
        </nav>
      </header>
      <main className="content-shell">
        {error ? <p className="form-message form-message--error" role="alert">{error}</p> : children}
      </main>
    </div>
  )
}
