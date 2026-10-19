import { useState } from 'react'

import { loginUser } from '../api/auth.js'


function LoginPage({ navigate, message }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)

    try {
      await loginUser({ email, password })
      navigate('/')
    } catch (requestError) {
      setError(requestError.message)
      setPassword('')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="page-shell">
      <section className="form-card" aria-labelledby="login-title">
        <p className="eyebrow">BUILDLOG</p>
        <h1 id="login-title">로그인</h1>
        <p className="description">내 공부 기록을 이어서 작성해 보세요.</p>

        {message && <p className="form-message form-message--success" role="status">{message}</p>}

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            이메일
            <input
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>
          <label>
            비밀번호
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>

          {error && <p className="form-message form-message--error" role="alert">{error}</p>}

          <button className="primary-button" type="submit" disabled={submitting}>
            {submitting ? '로그인하는 중...' : '로그인'}
          </button>
        </form>

        <button className="link-button" type="button" onClick={() => navigate('/signup')}>
          계정이 없나요? 회원가입
        </button>
      </section>
    </main>
  )
}

export default LoginPage
