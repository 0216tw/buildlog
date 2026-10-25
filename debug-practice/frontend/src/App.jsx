import { useState } from 'react'

const API_URL = 'http://127.0.0.1:8012'

function App() {
  const [result, setResult] = useState('아직 실행하지 않았습니다.')

async function runPractice() {
  const response = await fetch(`${API_URL}/server-error`)
  const data = await response.json().catch(() => ({}))

  setResult(
    `${response.status} ${response.statusText}: ${data.message ?? data.detail ?? '응답 내용 없음'}`,
  )
}
  return (
    <main>
      <h1>오류 확인 실습</h1>
      <button type="button" onClick={runPractice}>실행하기</button>
      <hr />
      <strong>실행 결과</strong>
      <pre>{result}</pre>
    </main>
  )
}

export default App