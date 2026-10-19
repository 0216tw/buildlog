import { useEffect, useState } from 'react'

import { ApiError, getCurrentUser, updateNickname } from '../api/auth.js'


function AccountSettingsPage({ navigate }) {
  const [nickname, setNickname] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    let active = true

    getCurrentUser()
      .then((user) => {
        if (active) setNickname(user.nickname)
      })
      .catch((requestError) => {
        if (!active) return
        if (requestError instanceof ApiError && requestError.status === 401) {
          navigate('/login', '로그인이 필요합니다.')
          return
        }
        setError(requestError.message)
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [navigate])

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setMessage('')
    setSubmitting(true)

    try {
      const user = await updateNickname(nickname)
      setNickname(user.nickname)
      setMessage('닉네임을 변경했습니다.')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="page-shell">
      <section className="form-card" aria-labelledby="settings-title">
        <p className="eyebrow">BUILDLOG</p>
        <h1 id="settings-title">계정 설정</h1>
        <p className="description">내 닉네임을 변경할 수 있습니다.</p>

        {loading ? (
          <p role="status">계정 정보를 불러오고 있습니다.</p>
        ) : (
          <form className="auth-form" onSubmit={handleSubmit}>
            <label>
              새 닉네임
              <input
                type="text"
                minLength="2"
                maxLength="20"
                value={nickname}
                onChange={(event) => setNickname(event.target.value)}
                required
              />
            </label>

            {error && <p className="form-message form-message--error" role="alert">{error}</p>}
            {message && <p className="form-message form-message--success" role="status">{message}</p>}

            <button className="primary-button" type="submit" disabled={submitting}>
              {submitting ? '변경하는 중...' : '닉네임 변경'}
            </button>
          </form>
        )}

        <button className="link-button" type="button" onClick={() => navigate('/')}>
          내 기록 홈으로 돌아가기
        </button>
      </section>
    </main>
  )
}

export default AccountSettingsPage
