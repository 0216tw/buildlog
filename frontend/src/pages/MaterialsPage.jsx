import { useCallback, useEffect, useRef, useState } from 'react'

import { ApiError, getCurrentUser } from '../api/auth.js'
import {
  createMaterial,
  deleteMaterial,
  fetchMaterialFile,
  getMaterialFileUrl,
  listMaterials,
} from '../api/materials.js'
import {
  filterMaterials,
  formatFileSize,
  formatMaterialDate,
  getMaterialCounts,
  getMaterialFormat,
  getMaterialAIView,
  hasActiveMaterialAnalysis,
  validateMaterialFile,
  validateMaterialText,
} from './materialsData.js'
import '../styles/materials.css'


const navigationItems = [
  { label: '대시보드', path: '/dashboard' },
  { label: '공부 기록', path: '/studies' },
  { label: '할 일', path: '/todos' },
  { label: '오류 기록', path: '/errors' },
  { label: '학습 자료함', path: '/materials' },
  { label: '공개 기록', path: '/public' },
]

const filters = [
  { key: 'all', label: '전체' },
  { key: 'image', label: '이미지' },
  { key: 'video', label: '영상' },
]


function MaterialsPage({ navigate }) {
  const [user, setUser] = useState(null)
  const [userLoading, setUserLoading] = useState(true)
  const [userError, setUserError] = useState('')
  const [title, setTitle] = useState('')
  const [memo, setMemo] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [formErrors, setFormErrors] = useState({})
  const [isUploading, setIsUploading] = useState(false)
  const [materials, setMaterials] = useState([])
  const [listStatus, setListStatus] = useState('loading')
  const [listError, setListError] = useState('')
  const [activeFilter, setActiveFilter] = useState('all')
  const [openingId, setOpeningId] = useState(null)
  const [deletingId, setDeletingId] = useState(null)
  const [failedPreviewIds, setFailedPreviewIds] = useState(() => new Set())
  const [pageMessage, setPageMessage] = useState({ type: '', text: '' })
  const fileInputRef = useRef(null)
  const refreshInFlightRef = useRef(false)

  const handleApiError = useCallback((requestError, fallback) => {
    if (requestError instanceof ApiError && requestError.status === 401) {
      navigate('/login', '로그인이 필요합니다.')
      return true
    }
    setPageMessage({ type: 'error', text: requestError.message || fallback })
    return false
  }, [navigate])

  const refreshMaterials = useCallback(async ({ silent = false } = {}) => {
    if (refreshInFlightRef.current) return
    refreshInFlightRef.current = true
    if (!silent) {
      setListStatus('loading')
      setListError('')
    }
    try {
      const items = await listMaterials()
      setMaterials(items)
      setListStatus(items.length ? 'success' : 'empty')
      setListError('')
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        navigate('/login', '로그인이 필요합니다.')
        return
      }
      setListError(requestError.message)
      if (!silent) setListStatus('error')
    } finally {
      refreshInFlightRef.current = false
    }
  }, [navigate])

  useEffect(() => {
    let active = true

    getCurrentUser()
      .then((currentUser) => {
        if (active) setUser(currentUser)
      })
      .catch((requestError) => {
        if (!active) return
        if (requestError instanceof ApiError && requestError.status === 401) {
          navigate('/login', '로그인이 필요합니다.')
          return
        }
        setUserError(requestError.message)
      })
      .finally(() => {
        if (active) setUserLoading(false)
      })

    return () => {
      active = false
    }
  }, [navigate])

  useEffect(() => {
    if (user) refreshMaterials()
  }, [refreshMaterials, user])

  const analysisActive = hasActiveMaterialAnalysis(materials)

  useEffect(() => {
    if (!user || !analysisActive) return undefined
    let cancelled = false
    let timerId = window.setTimeout(async function poll() {
      await refreshMaterials({ silent: true })
      if (!cancelled) timerId = window.setTimeout(poll, 3000)
    }, 3000)
    return () => {
      cancelled = true
      window.clearTimeout(timerId)
    }
  }, [analysisActive, refreshMaterials, user])

  const handleFileChange = (event) => {
    const file = event.target.files?.[0] ?? null
    const result = validateMaterialFile(file)
    if (!result.valid) {
      setSelectedFile(null)
      setFormErrors((current) => ({ ...current, file: result.message }))
      event.target.value = ''
      return
    }
    setSelectedFile(file)
    setFormErrors((current) => ({ ...current, file: '' }))
    setPageMessage({ type: '', text: '' })
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    const textResult = validateMaterialText(title, memo)
    const fileResult = validateMaterialFile(selectedFile)
    const nextErrors = {
      ...textResult.errors,
      ...(!fileResult.valid ? { file: fileResult.message } : {}),
    }
    setFormErrors(nextErrors)
    setPageMessage({ type: '', text: '' })
    if (Object.keys(nextErrors).length) return

    setIsUploading(true)
    try {
      await createMaterial({
        title: textResult.values.title,
        memo: textResult.values.memo,
        file: selectedFile,
      })
      setTitle('')
      setMemo('')
      setSelectedFile(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
      setFormErrors({})
      setPageMessage({ type: 'success', text: '학습 자료를 등록했습니다. AI 분석을 시작합니다.' })
      await refreshMaterials()
    } catch (requestError) {
      handleApiError(requestError, '자료를 등록하지 못했습니다.')
    } finally {
      setIsUploading(false)
    }
  }

  const handleOpen = async (material) => {
    const previewWindow = window.open('', '_blank')
    if (!previewWindow) {
      setPageMessage({ type: 'error', text: '원본을 보려면 브라우저에서 새 창을 허용해 주세요.' })
      return
    }
    previewWindow.opener = null
    setOpeningId(material.id)
    setPageMessage({ type: '', text: '' })
    try {
      const { blob } = await fetchMaterialFile(material.id)
      const url = URL.createObjectURL(blob)
      previewWindow.location.replace(url)
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000)
    } catch (requestError) {
      previewWindow?.close()
      handleApiError(requestError, '원본 파일을 열지 못했습니다.')
    } finally {
      setOpeningId(null)
    }
  }

  const handleDelete = async (material) => {
    if (!window.confirm(`'${material.title}' 자료를 삭제할까요?`)) return
    setDeletingId(material.id)
    setPageMessage({ type: '', text: '' })
    try {
      await deleteMaterial(material.id)
      setMaterials((current) => {
        const nextMaterials = current.filter((item) => item.id !== material.id)
        setListStatus(nextMaterials.length ? 'success' : 'empty')
        return nextMaterials
      })
      setPageMessage({ type: 'success', text: '학습 자료를 삭제했습니다.' })
    } catch (requestError) {
      handleApiError(requestError, '자료를 삭제하지 못했습니다.')
    } finally {
      setDeletingId(null)
    }
  }

  if (userLoading) {
    return <main className="page-shell"><p role="status">로그인 정보를 확인하고 있습니다.</p></main>
  }

  if (userError) {
    return <main className="page-shell"><p className="form-message form-message--error" role="alert">{userError}</p></main>
  }

  if (!user) return null

  const counts = getMaterialCounts(materials)
  const visibleMaterials = filterMaterials(materials, activeFilter)

  return (
    <div className="materials-page">
      <aside className="materials-page__sidebar" aria-label="BuildLog 메뉴">
        <button className="materials-page__brand" type="button" onClick={() => navigate('/dashboard')}>
          <span>b</span> BuildLog
        </button>
        <p className="materials-page__workspace-label">MY WORKSPACE</p>

        <nav className="materials-page__nav" aria-label="학습 자료함 메뉴">
          {navigationItems.map((item) => (
            <button
              className={`materials-page__nav-item${item.path === '/materials' ? ' materials-page__nav-item--active' : ''}`}
              type="button"
              key={item.path}
              aria-current={item.path === '/materials' ? 'page' : undefined}
              onClick={() => navigate(item.path)}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <section className="materials-page__private-note" aria-label="공개 범위 안내">
          <strong>나만의 학습 공간</strong>
          <p>올린 자료는<br />나에게만 보여요.</p>
        </section>

        <button className="materials-page__account" type="button" onClick={() => navigate('/settings')}>
          {user.nickname}님&nbsp; · &nbsp;내 계정
        </button>
      </aside>

      <main className="materials-page__main">
        <header className="materials-page__heading">
          <p>MY LEARNING LIBRARY</p>
          <h1>학습 자료함</h1>
          <span>캡처부터 실습 영상까지, 배운 순간을 한곳에 모아보세요.</span>
        </header>

        {pageMessage.text && (
          <p
            className={`materials-page__message materials-page__message--${pageMessage.type}`}
            role={pageMessage.type === 'error' ? 'alert' : 'status'}
          >
            {pageMessage.text}
          </p>
        )}

        <div className="materials-page__workspace">
          <form className="materials-page__upload-card" aria-labelledby="materials-upload-title" onSubmit={handleSubmit}>
            <h2 id="materials-upload-title">새 자료 등록</h2>
            <p className="materials-page__upload-copy">기억하고 싶은 자료를 남겨보세요.</p>

            <label className="materials-page__field">
              <span>자료 제목</span>
              <input
                type="text"
                placeholder="예: REST API 수업 정리"
                value={title}
                maxLength={101}
                onChange={(event) => setTitle(event.target.value)}
                aria-invalid={Boolean(formErrors.title)}
              />
              {formErrors.title && <small className="materials-page__field-error" role="alert">{formErrors.title}</small>}
            </label>

            <label className="materials-page__field">
              <span>메모&nbsp; · &nbsp;선택</span>
              <textarea
                placeholder="어떤 내용인지 간단히 적어주세요."
                value={memo}
                maxLength={1001}
                onChange={(event) => setMemo(event.target.value)}
                aria-invalid={Boolean(formErrors.memo)}
              />
              {formErrors.memo && <small className="materials-page__field-error" role="alert">{formErrors.memo}</small>}
            </label>

            <div className="materials-page__file-box">
              <span className="materials-page__upload-icon" aria-hidden="true">↑</span>
              <strong>이미지 또는 영상을 선택하세요</strong>
              <p>PNG · JPG&nbsp; 5MiB / MP4&nbsp; 30MiB</p>
              <input
                ref={fileInputRef}
                className="materials-page__file-input"
                type="file"
                accept=".png,.jpg,.jpeg,.mp4,image/png,image/jpeg,video/mp4"
                onChange={handleFileChange}
              />
              <button type="button" onClick={() => fileInputRef.current?.click()} disabled={isUploading}>파일 선택</button>
              {selectedFile && (
                <p className="materials-page__selected-file">
                  {selectedFile.name} · {formatFileSize(selectedFile.size)}
                </p>
              )}
              {formErrors.file && <small className="materials-page__field-error" role="alert">{formErrors.file}</small>}
            </div>

            <p className="materials-page__privacy-copy">자료당 파일 1개 · BuildLog에서는 나만 볼 수 있어요</p>
            <p className="materials-page__ai-notice">등록한 파일은 AI 요약을 위해 OpenAI로 전송됩니다.</p>
            <button className="materials-page__upload-button" type="submit" disabled={isUploading}>
              {isUploading ? '등록하는 중...' : '자료 업로드'}
            </button>
          </form>

          <section className="materials-page__library" aria-labelledby="materials-library-title">
            <header className="materials-page__library-header">
              <h2 id="materials-library-title">내 자료 <span>{counts.all}</span></h2>
            </header>

            <div className="materials-page__filters" aria-label="자료 종류 필터">
              {filters.map((filter) => (
                <button
                  className={activeFilter === filter.key ? 'materials-page__filter--active' : ''}
                  type="button"
                  key={filter.key}
                  aria-pressed={activeFilter === filter.key}
                  onClick={() => setActiveFilter(filter.key)}
                >
                  {filter.label} {counts[filter.key]}
                </button>
              ))}
            </div>

            {listError && listStatus !== 'error' && (
              <p className="materials-page__message materials-page__message--error" role="alert">
                최신 분석 상태를 불러오지 못했습니다. 기존 목록은 그대로 표시합니다.
              </p>
            )}

            {listStatus === 'loading' && <p className="materials-page__list-state" role="status">자료를 불러오고 있습니다.</p>}
            {listStatus === 'error' && (
              <div className="materials-page__list-state materials-page__list-state--error" role="alert">
                <p>{listError || '자료를 불러오지 못했습니다.'}</p>
                <button type="button" onClick={refreshMaterials}>다시 불러오기</button>
              </div>
            )}
            {listStatus === 'empty' && <p className="materials-page__list-state">아직 등록한 학습 자료가 없습니다.</p>}
            {listStatus !== 'loading' && listStatus !== 'error' && visibleMaterials.length === 0 && materials.length > 0 && (
              <p className="materials-page__list-state">이 종류의 자료가 없습니다.</p>
            )}

            <div className="materials-page__list">
              {visibleMaterials.map((material) => {
                const isVideo = material.media_type === 'video'
                const previewFailed = failedPreviewIds.has(material.id)
                const aiView = getMaterialAIView(material)
                return (
                  <article className="materials-page__item" key={material.id}>
                    <div className={`materials-page__thumbnail materials-page__thumbnail--${isVideo ? 'dark' : 'blue'}`}>
                      {!isVideo && !previewFailed ? (
                        <img
                          src={getMaterialFileUrl(material.id)}
                          alt={`${material.title} 미리보기`}
                          onError={() => {
                            setFailedPreviewIds((current) => {
                              const next = new Set(current)
                              next.add(material.id)
                              return next
                            })
                          }}
                        />
                      ) : (
                        <>
                          <strong aria-hidden="true">{isVideo ? '▶' : getMaterialFormat(material)}</strong>
                          <span>{isVideo ? '실습 영상' : '이미지를 불러오지 못했습니다'}</span>
                        </>
                      )}
                    </div>
                    <div className="materials-page__item-copy">
                      <h3>{material.title}</h3>
                      {material.memo && <p className="materials-page__item-memo">{material.memo}</p>}
                      <p>{material.original_filename} · {getMaterialFormat(material)} · {formatFileSize(material.size_bytes)}</p>
                      <div className="materials-page__item-actions">
                        <time dateTime={material.created_at}>{formatMaterialDate(material.created_at)}</time>
                        <span aria-hidden="true">·</span>
                        <button type="button" disabled={openingId === material.id} onClick={() => handleOpen(material)}>
                          {openingId === material.id ? '여는 중...' : '원본 보기'}
                        </button>
                        <span aria-hidden="true">·</span>
                        <button
                          className="materials-page__delete-button"
                          type="button"
                          disabled={deletingId === material.id}
                          onClick={() => handleDelete(material)}
                        >
                          {deletingId === material.id ? '삭제 중...' : '삭제'}
                        </button>
                      </div>
                      <div className={`materials-page__summary materials-page__summary--${material.ai_status || 'not_requested'}`}>
                        <strong>{aiView.label}</strong>
                        {material.ai_status === 'completed' && material.ai_summary ? (
                          <p>{material.ai_summary}</p>
                        ) : (
                          <p>{aiView.message}</p>
                        )}
                      </div>
                    </div>
                  </article>
                )
              })}
            </div>

            <p className="materials-page__library-help">차곡차곡 쌓인 자료가 나만의 복습 노트가 됩니다.</p>
          </section>
        </div>

        <section className="materials-page__ai" aria-labelledby="materials-ai-title">
          <div>
            <h2 id="materials-ai-title">AI 학습 요약</h2>
            <p>새로 등록한 이미지와 영상을 분석해 핵심 내용, 중요 키워드와 복습할 점을 정리합니다.</p>
            <span>AI 분석이 실패해도 원본 자료는 그대로 보거나 삭제할 수 있습니다.</span>
          </div>
        </section>
      </main>
    </div>
  )
}

export default MaterialsPage
