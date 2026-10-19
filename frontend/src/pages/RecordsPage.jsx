import { useCallback, useEffect, useMemo, useState } from 'react'

import {
  createErrorLog, createStudy, createTodo, deleteErrorLog, deleteStudy, deleteTodo,
  listErrors, listStudies, listTodos, setVisibility, toggleTodo, updateErrorLog,
  updateStudy, updateTodo,
} from '../api/records.js'
import AppLayout from '../components/AppLayout.jsx'

const settings = {
  studies: { label: '공부 기록', singular: '공부 기록', list: (filter, q) => listStudies(q), create: createStudy, update: updateStudy, remove: deleteStudy },
  todos: { label: '할 일', singular: '할 일', list: (filter) => listTodos(filter), create: createTodo, update: updateTodo, remove: deleteTodo },
  errors: { label: '오류 기록', singular: '오류 기록', list: (filter, q) => listErrors(filter, q), create: createErrorLog, update: updateErrorLog, remove: deleteErrorLog },
}

const emptyForm = (kind) => ({ title: '', content: '', resolution: '', is_resolved: false, is_public: false, ...(kind === 'todos' ? {} : {}) })

export default function RecordsPage({ kind, navigate }) {
  const config = settings[kind]
  const [items, setItems] = useState([])
  const [form, setForm] = useState(emptyForm(kind))
  const [editingId, setEditingId] = useState(null)
  const [filter, setFilter] = useState('all')
  const [query, setQuery] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try { setItems(await config.list(filter, query)) }
    catch (requestError) { setError(requestError.message) }
    finally { setLoading(false) }
  }, [config, filter, query])

  useEffect(() => { load() }, [load])

  const payload = useMemo(() => {
    if (kind === 'todos') return { title: form.title, is_public: form.is_public }
    if (kind === 'errors') return { title: form.title, content: form.content, resolution: form.resolution || null, is_resolved: form.is_resolved, is_public: form.is_public }
    return { title: form.title, content: form.content, is_public: form.is_public }
  }, [form, kind])

  async function submit(event) {
    event.preventDefault()
    setError('')
    setSaving(true)
    try {
      if (editingId) await config.update(editingId, payload)
      else await config.create(payload)
      setEditingId(null)
      setForm(emptyForm(kind))
      await load()
    } catch (requestError) { setError(requestError.message) }
    finally { setSaving(false) }
  }

  function startEdit(item) {
    setEditingId(item.id)
    setForm({ title: item.title, content: item.content ?? '', resolution: item.resolution ?? '', is_resolved: item.is_resolved ?? false, is_public: item.is_public })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  async function remove(item) {
    if (!window.confirm(`이 ${config.singular}을(를) 삭제할까요?`)) return
    try { await config.remove(item.id); await load() }
    catch (requestError) { setError(requestError.message) }
  }

  async function changeVisibility(item) {
    try { await setVisibility(kind, item.id, !item.is_public); await load() }
    catch (requestError) { setError(requestError.message) }
  }

  async function changeCompletion(item) {
    try { await toggleTodo(item.id, !item.is_completed); await load() }
    catch (requestError) { setError(requestError.message) }
  }

  return (
    <AppLayout navigate={navigate}>
      <section className="page-heading"><p className="eyebrow">MY BUILDLOG</p><h1>{config.label}</h1><p>기록은 기본 비공개로 저장됩니다.</p></section>
      <form className="record-form card" onSubmit={submit}>
        <h2>{editingId ? '기록 수정' : '새 기록 작성'}</h2>
        <label>제목 <input maxLength="100" value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} required /></label>
        {kind !== 'todos' && <label>내용 <textarea maxLength="5000" rows="7" value={form.content} onChange={(event) => setForm({ ...form, content: event.target.value })} required /></label>}
        {kind === 'errors' && <>
          <label>해결 방법 <textarea maxLength="5000" rows="5" value={form.resolution} onChange={(event) => setForm({ ...form, resolution: event.target.value })} /></label>
          <label className="check-row"><input type="checkbox" checked={form.is_resolved} onChange={(event) => setForm({ ...form, is_resolved: event.target.checked })} /> 해결됨</label>
        </>}
        <label className="check-row"><input type="checkbox" checked={form.is_public} onChange={(event) => setForm({ ...form, is_public: event.target.checked })} /> 다른 회원에게 공개</label>
        {error && <p className="form-message form-message--error" role="alert">{error}</p>}
        <div className="button-row"><button className="primary-button" disabled={saving}>{saving ? '저장 중...' : '저장'}</button>{editingId && <button type="button" className="secondary-button" onClick={() => { setEditingId(null); setForm(emptyForm(kind)) }}>수정 취소</button>}</div>
      </form>

      <section className="list-tools" aria-label="목록 도구">
        {kind !== 'todos' && <input aria-label="검색어" placeholder="검색어" value={query} onChange={(event) => setQuery(event.target.value)} />}
        {kind !== 'studies' && <select aria-label="상태 필터" value={filter} onChange={(event) => setFilter(event.target.value)}>
          <option value="all">전체</option>
          <option value={kind === 'todos' ? 'pending' : 'unresolved'}>{kind === 'todos' ? '미완료' : '미해결'}</option>
          <option value={kind === 'todos' ? 'completed' : 'resolved'}>{kind === 'todos' ? '완료' : '해결'}</option>
        </select>}
      </section>

      {loading ? <p role="status">목록을 불러오는 중입니다.</p> : items.length === 0 ? <p className="empty-state">아직 기록이 없습니다.</p> : <div className="card-grid">
        {items.map((item) => <article className="card record-card" key={item.id}>
          <div className="card-title-row">
            {kind === 'todos' && <input aria-label={`${item.title} 완료`} type="checkbox" checked={item.is_completed} onChange={() => changeCompletion(item)} />}
            <h2>{item.title}</h2><span className="badge">{item.is_public ? '공개' : '비공개'}</span>
          </div>
          {item.content && <p className="pre-wrap">{item.content}</p>}
          {kind === 'errors' && <p><strong>{item.is_resolved ? '해결' : '미해결'}</strong>{item.resolution ? ` · ${item.resolution}` : ''}</p>}
          <p className="meta">수정: {new Date(item.updated_at).toLocaleString()}</p>
          <div className="button-row"><button className="secondary-button" onClick={() => startEdit(item)}>수정</button><button className="secondary-button" onClick={() => changeVisibility(item)}>{item.is_public ? '비공개로' : '공개로'}</button><button className="danger-button" onClick={() => remove(item)}>삭제</button></div>
        </article>)}
      </div>}
    </AppLayout>
  )
}
