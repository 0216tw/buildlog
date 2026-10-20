import assert from 'node:assert/strict'
import test from 'node:test'

import {
  createMaterial,
  deleteMaterial,
  fetchMaterialFile,
  getMaterialFileUrl,
  listMaterials,
} from '../src/api/materials.js'
import {
  filterMaterials,
  formatFileSize,
  formatMaterialDate,
  getMaterialFormat,
  getMaterialCounts,
  getMaterialAIView,
  hasActiveMaterialAnalysis,
  IMAGE_LIMIT_BYTES,
  validateMaterialFile,
  validateMaterialText,
  VIDEO_LIMIT_BYTES,
} from '../src/pages/materialsData.js'


const materials = [
  { id: 1, media_type: 'image', content_type: 'image/png' },
  { id: 2, media_type: 'video', content_type: 'video/mp4' },
  { id: 3, media_type: 'image', content_type: 'image/jpeg' },
]


test('학습 자료함 개수와 필터는 실제 API 형태를 사용한다', () => {
  assert.deepEqual(getMaterialCounts(materials), { all: 3, image: 2, video: 1 })
  assert.deepEqual(
    filterMaterials(materials, 'image').map((material) => material.media_type),
    ['image', 'image'],
  )
  assert.deepEqual(
    filterMaterials(materials, 'video').map((material) => material.media_type),
    ['video'],
  )
  assert.equal(filterMaterials(materials, 'all').length, 3)
})


test('자료 제목과 선택 메모의 공백과 길이를 검사한다', () => {
  assert.deepEqual(
    validateMaterialText('  REST API 정리  ', '  요청 흐름  '),
    { values: { title: 'REST API 정리', memo: '요청 흐름' }, errors: {} },
  )
  assert.match(validateMaterialText('   ', '').errors.title, /제목/)
  assert.match(validateMaterialText('가'.repeat(101), '').errors.title, /100자/)
  assert.match(validateMaterialText('제목', '가'.repeat(1001)).errors.memo, /1,000자/)
})


test('이미지와 영상 파일 형식 및 크기를 검사한다', () => {
  assert.equal(validateMaterialFile({ name: 'note.png', type: 'image/png', size: IMAGE_LIMIT_BYTES }).valid, true)
  assert.equal(validateMaterialFile({ name: 'note.jpeg', type: 'image/jpeg', size: IMAGE_LIMIT_BYTES }).valid, true)
  assert.equal(validateMaterialFile({ name: 'lesson.mp4', type: 'video/mp4', size: VIDEO_LIMIT_BYTES }).valid, true)
  assert.match(validateMaterialFile({ name: 'note.png', type: 'image/png', size: IMAGE_LIMIT_BYTES + 1 }).message, /5MiB/)
  assert.match(validateMaterialFile({ name: 'lesson.mp4', type: 'video/mp4', size: VIDEO_LIMIT_BYTES + 1 }).message, /30MiB/)
  assert.equal(validateMaterialFile({ name: 'fake.png', type: 'text/plain', size: 100 }).valid, false)
  assert.equal(validateMaterialFile({ name: 'empty.jpg', type: 'image/jpeg', size: 0 }).valid, false)
})


test('파일 크기를 읽기 쉬운 단위로 표시한다', () => {
  assert.equal(formatFileSize(512), '512 B')
  assert.equal(formatFileSize(1024), '1.00 KiB')
  assert.equal(formatFileSize(5 * 1024 * 1024), '5.00 MiB')
})


test('자료 형식과 등록 날짜를 화면용으로 표시한다', () => {
  assert.equal(getMaterialFormat(materials[0]), 'PNG')
  assert.equal(getMaterialFormat(materials[1]), 'MP4')
  assert.equal(getMaterialFormat(materials[2]), 'JPG')
  assert.equal(formatMaterialDate('2026-10-20T10:30:00'), '2026.10.20')
  assert.equal(formatMaterialDate('invalid'), '')
})


test('자료 등록은 FormData와 쿠키를 사용하고 multipart 헤더를 직접 지정하지 않는다', async () => {
  let captured
  const fakeFetch = async (url, options) => {
    captured = { url, options }
    return { ok: true, status: 201, json: async () => ({ id: 1 }) }
  }
  const file = new Blob([new Uint8Array([1, 2, 3])], { type: 'image/png' })

  await createMaterial({ title: '자료', memo: '메모', file }, fakeFetch)

  assert.equal(captured.url, 'http://localhost:8000/api/materials')
  assert.equal(captured.options.credentials, 'include')
  assert.ok(captured.options.body instanceof FormData)
  assert.equal(captured.options.body.get('title'), '자료')
  assert.equal(captured.options.body.get('memo'), '메모')
  assert.equal(captured.options.headers['Content-Type'], undefined)
})


test('자료 목록과 삭제는 정해진 API 경로를 호출한다', async () => {
  const calls = []
  const fakeFetch = async (url, options) => {
    calls.push({ url, options })
    if (options.method === 'DELETE') {
      return { ok: true, status: 204, json: async () => ({}) }
    }
    return { ok: true, status: 200, json: async () => materials }
  }

  assert.equal((await listMaterials(fakeFetch)).length, 3)
  assert.equal(await deleteMaterial(7, fakeFetch), null)
  assert.equal(calls[0].url, 'http://localhost:8000/api/materials')
  assert.equal(calls[1].url, 'http://localhost:8000/api/materials/7')
  assert.deepEqual(calls.map(({ options }) => options.credentials), ['include', 'include'])
})


test('원본 요청은 성공 응답만 Blob으로 반환한다', async () => {
  const expected = new Blob(['file'], { type: 'image/png' })
  const fakeFetch = async (_url, options) => ({
    ok: true,
    status: 200,
    headers: { get: () => "inline; filename*=UTF-8''note.png" },
    blob: async () => expected,
    options,
  })

  const result = await fetchMaterialFile(3, fakeFetch)
  assert.equal(result.blob, expected)
  assert.equal(result.filename, 'note.png')
})


test('이미지 미리보기는 작성자 인증 원본 API 주소를 사용한다', () => {
  assert.equal(
    getMaterialFileUrl(7),
    'http://localhost:8000/api/materials/7/file',
  )
})


test('AI 상태별 안내와 폴링 대상 여부를 구분한다', () => {
  assert.deepEqual(getMaterialAIView({ ai_status: 'pending' }), {
    label: '분석 대기',
    message: 'AI 분석을 준비하고 있습니다.',
  })
  assert.equal(getMaterialAIView({ ai_status: 'completed' }).label, '요약 완료')
  assert.equal(getMaterialAIView({ ai_status: 'failed' }).label, '요약 실패')
  assert.equal(hasActiveMaterialAnalysis([{ ai_status: 'completed' }]), false)
  assert.equal(hasActiveMaterialAnalysis([{ ai_status: 'processing' }]), true)
})
