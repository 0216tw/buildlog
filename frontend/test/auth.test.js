import assert from 'node:assert/strict'
import test from 'node:test'

import {
  ApiError,
  getCurrentUser,
  loginUser,
  signupUser,
  updateNickname,
} from '../src/api/auth.js'


function successfulFetch(data) {
  return async () => ({ ok: true, status: 200, json: async () => data })
}


test('회원가입 요청은 입력값을 JSON으로 보내고 쿠키를 포함한다', async () => {
  const input = {
    email: 'learner@example.com',
    password: 'password123',
    nickname: '학습자_1',
  }
  let captured
  const fakeFetch = async (url, options) => {
    captured = { url, options }
    return { ok: true, status: 201, json: async () => ({ id: 1, ...input }) }
  }

  await signupUser(input, fakeFetch)

  assert.equal(captured.url, 'http://localhost:8000/api/auth/signup')
  assert.equal(captured.options.method, 'POST')
  assert.equal(captured.options.credentials, 'include')
  assert.deepEqual(JSON.parse(captured.options.body), input)
})


test('로그인과 보호된 요청은 쿠키를 포함한다', async () => {
  const calls = []
  const fakeFetch = async (url, options) => {
    calls.push({ url, options })
    return {
      ok: true,
      status: 200,
      json: async () => ({ id: 1, nickname: '학습자_1' }),
    }
  }

  await loginUser({ email: 'learner@example.com', password: 'password123' }, fakeFetch)
  const currentUser = await getCurrentUser(fakeFetch)
  await updateNickname('새닉네임', fakeFetch)

  assert.equal(calls[1].url, 'http://localhost:8000/api/auth/me')
  assert.equal(currentUser.nickname, '학습자_1')
  assert.deepEqual(calls.map((call) => call.options.credentials), [
    'include',
    'include',
    'include',
  ])
  assert.deepEqual(calls.map((call) => call.options.method), ['POST', 'GET', 'PATCH'])
})


test('서버 오류 메시지와 상태 코드를 전달한다', async () => {
  const fakeFetch = async () => ({
    ok: false,
    status: 401,
    json: async () => ({ detail: '로그인이 필요합니다.' }),
  })

  await assert.rejects(
    () => getCurrentUser(fakeFetch),
    (error) => {
      assert.ok(error instanceof ApiError)
      assert.equal(error.status, 401)
      assert.equal(error.message, '로그인이 필요합니다.')
      return true
    },
  )
})


test('응답 본문이 없어도 공통 실패 문구를 보여준다', async () => {
  const fakeFetch = async () => ({
    ok: false,
    status: 500,
    json: async () => { throw new Error('invalid json') },
  })

  await assert.rejects(
    () => signupUser({}, fakeFetch),
    /요청을 처리하지 못했습니다/,
  )
})
