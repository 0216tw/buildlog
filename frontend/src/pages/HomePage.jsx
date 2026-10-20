import { useEffect, useState } from 'react'

import { ApiError, getCurrentUser } from '../api/auth.js'


function HomePage({ navigate }) {
  const [user, setUser] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    getCurrentUser()
      .then((currentUser) => {
        if (active) setUser(currentUser)
      })
      .catch((requestError) => {
        if (!active) return
        if (requestError instanceof ApiError && requestError.status === 401) {
          navigate('/login', '로그인이 필요합니다.')
          return
        }
        setError(requestError.message)
      })

    return () => {
      active = false
    }
  }, [navigate])

  if (!user && !error) {
    return <main className="page-shell"><p role="status">로그인 상태를 확인하고 있습니다.</p></main>
  }

  return (
    <main className="page-shell">
      <section className="welcome-card" aria-labelledby="home-title">
        <p className="eyebrow">BUILDLOG</p>
        <h1 id="home-title">내 기록 홈</h1>
        {error ? (
          <p className="form-message form-message--error" role="alert">{error}</p>
        ) : (
          <>
            <p className="description"><strong>{user.nickname}</strong>님, 반갑습니다.</p>
            <div className="home-actions">
              <button className="primary-button" type="button" onClick={() => navigate('/studies')}>공부 기록</button>
              <button className="secondary-button" type="button" onClick={() => navigate('/todos')}>할 일</button>
              <button className="secondary-button" type="button" onClick={() => navigate('/errors')}>오류 기록</button>
              <button className="secondary-button" type="button" onClick={() => navigate('/materials')}>학습 자료함</button>
              <button className="secondary-button" type="button" onClick={() => navigate('/public')}>공개 기록</button>
              <button className="secondary-button" type="button" onClick={() => navigate('/settings')}>계정 설정</button>
            </div>
          </>
        )}
      </section>
    </main>
  )
}

export default HomePage
