export async function fetchApiHealth(apiBaseUrl, fetchImplementation = fetch) {
  const response = await fetchImplementation(`${apiBaseUrl}/health`)

  if (!response.ok) {
    throw new Error('상태 확인 요청에 실패했습니다.')
  }

  const data = await response.json()
  if (data.status !== 'ok') {
    throw new Error('서버가 준비되지 않았습니다.')
  }

  return data
}
