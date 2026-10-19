import assert from 'node:assert/strict'
import test from 'node:test'

import { fetchApiHealth } from '../src/api/health.js'


test('정상 상태 응답을 반환한다', async () => {
  const fakeFetch = async (url) => {
    assert.equal(url, 'http://127.0.0.1:8000/api/health')
    return {
      ok: true,
      json: async () => ({ status: 'ok', service: 'buildlog-api' }),
    }
  }

  const result = await fetchApiHealth(
    'http://127.0.0.1:8000/api',
    fakeFetch,
  )

  assert.deepEqual(result, { status: 'ok', service: 'buildlog-api' })
})


test('서버가 실패 상태를 반환하면 오류를 알린다', async () => {
  const fakeFetch = async () => ({
    ok: false,
    json: async () => ({}),
  })

  await assert.rejects(
    () => fetchApiHealth('http://127.0.0.1:8000/api', fakeFetch),
    /상태 확인 요청에 실패했습니다/,
  )
})
