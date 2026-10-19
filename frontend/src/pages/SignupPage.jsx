import { useState } from 'react'

import { signupUser } from '../api/auth.js'


function SignupPage({ navigate }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [nickname, setNickname] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)

    try {
      await signupUser({ email, password, nickname })
      navigate('/login', '회원가입이 완료되었습니다. 로그인해 주세요.')
    } catch (requestError) {
      setError(requestError.message)
      setPassword('')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="page-shell">
      <section className="form-card" aria-labelledby="signup-title">
        <p className="eyebrow">BUILDLOG</p>
        <h1 id="signup-title">회원가입</h1>
        <p className="description">공부 기록을 안전하게 보관할 계정을 만드세요.</p>

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
              autoComplete="new-password"
              minLength="8"
              maxLength="64"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
            <span className="field-help">8~64자로 입력해 주세요.</span>
          </label>
          <label>
            닉네임
            <input
              type="text"
              autoComplete="nickname"
              minLength="2"
              maxLength="20"
              value={nickname}
              onChange={(event) => setNickname(event.target.value)}
              required
            />
            <span className="field-help">한글, 영문, 숫자, 밑줄만 사용할 수 있어요.</span>
          </label>

          {error && <p className="form-message form-message--error" role="alert">{error}</p>}

          <button className="primary-button" type="submit" disabled={submitting}>
            {submitting ? '가입하는 중...' : '회원가입'}
          </button>
        </form>

        <button className="link-button" type="button" onClick={() => navigate('/login')}>
          이미 계정이 있나요? 로그인
        </button>
      </section>
    </main>
  )
}

export default SignupPage
