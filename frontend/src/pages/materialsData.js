export const IMAGE_LIMIT_BYTES = 5 * 1024 * 1024
export const VIDEO_LIMIT_BYTES = 30 * 1024 * 1024

const FILE_RULES = {
  png: { contentType: 'image/png', mediaType: 'image', limit: IMAGE_LIMIT_BYTES },
  jpg: { contentType: 'image/jpeg', mediaType: 'image', limit: IMAGE_LIMIT_BYTES },
  jpeg: { contentType: 'image/jpeg', mediaType: 'image', limit: IMAGE_LIMIT_BYTES },
  mp4: { contentType: 'video/mp4', mediaType: 'video', limit: VIDEO_LIMIT_BYTES },
}


export function validateMaterialText(title, memo) {
  const normalizedTitle = title.trim()
  const normalizedMemo = memo.trim()
  const errors = {}

  if (!normalizedTitle) {
    errors.title = '자료 제목을 입력해 주세요.'
  } else if (normalizedTitle.length > 100) {
    errors.title = '자료 제목은 100자 이하로 입력해 주세요.'
  }

  if (normalizedMemo.length > 1000) {
    errors.memo = '메모는 1,000자 이하로 입력해 주세요.'
  }

  return {
    values: { title: normalizedTitle, memo: normalizedMemo },
    errors,
  }
}


export function validateMaterialFile(file) {
  if (!file) return { valid: false, message: '파일을 선택해 주세요.' }

  const extension = file.name.split('.').pop()?.toLowerCase() ?? ''
  const rule = FILE_RULES[extension]
  if (!rule || file.type !== rule.contentType) {
    return { valid: false, message: 'PNG, JPG 또는 MP4 파일만 선택할 수 있습니다.' }
  }
  if (file.size <= 0) {
    return { valid: false, message: '내용이 있는 파일을 선택해 주세요.' }
  }
  if (file.size > rule.limit) {
    return {
      valid: false,
      message: rule.mediaType === 'image'
        ? '이미지 파일은 5MiB 이하로 선택해 주세요.'
        : '영상 파일은 30MiB 이하로 선택해 주세요.',
    }
  }
  return { valid: true, mediaType: rule.mediaType }
}


export function formatFileSize(sizeBytes) {
  if (sizeBytes < 1024) return `${sizeBytes} B`
  const units = ['KiB', 'MiB']
  let size = sizeBytes / 1024
  let unit = units[0]
  if (size >= 1024) {
    size /= 1024
    unit = units[1]
  }
  return `${size.toFixed(size >= 10 ? 1 : 2)} ${unit}`
}


export function getMaterialCounts(materials) {
  return {
    all: materials.length,
    image: materials.filter((material) => material.media_type === 'image').length,
    video: materials.filter((material) => material.media_type === 'video').length,
  }
}


export function filterMaterials(materials, filter) {
  if (filter === 'all') return materials
  return materials.filter((material) => material.media_type === filter)
}


export function formatMaterialDate(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}.${month}.${day}`
}


export function getMaterialFormat(material) {
  if (material.content_type === 'image/png') return 'PNG'
  if (material.content_type === 'image/jpeg') return 'JPG'
  if (material.content_type === 'video/mp4') return 'MP4'
  return ''
}


const AI_VIEW = {
  not_requested: {
    label: 'AI 요약 없음',
    message: 'AI 기능 도입 전에 등록한 자료입니다.',
  },
  pending: {
    label: '분석 대기',
    message: 'AI 분석을 준비하고 있습니다.',
  },
  processing: {
    label: '분석 중',
    message: '이미지 또는 영상을 분석하고 있습니다.',
  },
  completed: {
    label: '요약 완료',
    message: '',
  },
  failed: {
    label: '요약 실패',
    message: '원본 자료는 정상적으로 저장되었습니다.',
  },
}


export function getMaterialAIView(material) {
  return AI_VIEW[material.ai_status] ?? AI_VIEW.not_requested
}


export function hasActiveMaterialAnalysis(materials) {
  return materials.some((material) => ['pending', 'processing'].includes(material.ai_status))
}
