import assert from 'node:assert/strict'
import test from 'node:test'

import { createStudy, listErrors, listPublicRecords, toggleTodo } from '../src/api/records.js'

function response(data, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: async () => data })
}

test('study creation sends JSON and keeps cookies enabled', async () => {
  let request
  await createStudy({ title: '제목', content: '내용', is_public: false }, async (url, options) => {
    request = { url, options }
    return response({ id: 1 }, 201)
  })
  assert.match(request.url, /\/studies$/)
  assert.equal(request.options.method, 'POST')
  assert.equal(request.options.credentials, 'include')
  assert.equal(JSON.parse(request.options.body).title, '제목')
})

test('todo completion and error search use their documented endpoints', async () => {
  const urls = []
  const fetchImpl = async (url) => { urls.push(url); return response([]) }
  await toggleTodo(7, true, fetchImpl)
  await listErrors('unresolved', 'timeout 오류', fetchImpl)
  assert.match(urls[0], /\/todos\/7\/completion$/)
  assert.match(urls[1], /state=unresolved&q=timeout%20%EC%98%A4%EB%A5%98/)
})

test('public list sends type and encoded query', async () => {
  let url
  await listPublicRecords('study', '리액트 상태', async (nextUrl) => { url = nextUrl; return response([]) })
  assert.match(url, /record_type=study/)
  assert.match(url, /q=%EB%A6%AC%EC%95%A1%ED%8A%B8%20%EC%83%81%ED%83%9C/)
})
