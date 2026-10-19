import { useCallback, useEffect, useState } from 'react'

import { addLike, createComment, deleteComment, getLike, getRecord, listComments, removeLike, updateComment } from '../api/records.js'
import { getCurrentUser } from '../api/auth.js'
import AppLayout from '../components/AppLayout.jsx'
import ReportForm from '../components/ReportForm.jsx'

export default function PublicDetailPage({ type, id, navigate }) {
  const pluralType = type === 'study' ? 'studies' : 'errors'
  const [record, setRecord] = useState(null)
  const [comments, setComments] = useState([])
  const [like, setLike] = useState({ liked: false, count: 0 })
  const [me, setMe] = useState(null)
  const [comment, setComment] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [editingContent, setEditingContent] = useState('')
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    try {
      const [nextRecord, nextComments, nextLike, user] = await Promise.all([getRecord(pluralType, id), listComments(pluralType, id), getLike(pluralType, id), getCurrentUser()])
      setRecord(nextRecord); setComments(nextComments); setLike(nextLike); setMe(user)
    } catch (requestError) { setError(requestError.message) }
  }, [id, pluralType])
  useEffect(() => { load() }, [load])

  async function submitComment(event) {
    event.preventDefault(); setError('')
    try { await createComment(pluralType, id, comment); setComment(''); await load() }
    catch (requestError) { setError(requestError.message) }
  }
  async function saveEdit(event) {
    event.preventDefault()
    try { await updateComment(editingId, editingContent); setEditingId(null); setEditingContent(''); await load() }
    catch (requestError) { setError(requestError.message) }
  }
  async function remove(item) {
    if (!window.confirm('이 댓글을 삭제할까요?')) return
    try { await deleteComment(item.id); await load() } catch (requestError) { setError(requestError.message) }
  }
  async function toggleLike() {
    try { setLike(like.liked ? await removeLike(pluralType, id) : await addLike(pluralType, id)) } catch (requestError) { setError(requestError.message) }
  }
  return <AppLayout navigate={navigate}>
    {error && <p className="form-message form-message--error" role="alert">{error}</p>}
    {!record ? <p role="status">기록을 불러오는 중입니다.</p> : <>
      <article className="card detail-card"><p className="eyebrow">PUBLIC RECORD</p><h1>{record.title}</h1><p className="pre-wrap">{record.content}</p>{record.resolution && <section><h2>해결 방법</h2><p className="pre-wrap">{record.resolution}</p></section>}<div className="button-row"><button className="primary-button" onClick={toggleLike}>{like.liked ? '좋아요 취소' : '좋아요'} {like.count}</button><ReportForm targetType={type} targetId={Number(id)} /></div></article>
      <section className="comments"><h2>댓글</h2><form className="comment-form" onSubmit={submitComment}><textarea maxLength="500" value={comment} onChange={(event) => setComment(event.target.value)} required /><button className="primary-button">댓글 작성</button></form>
        {comments.map((item) => <article className="card comment-card" key={item.id}><p className="meta">{item.author_nickname}</p>{editingId === item.id ? <form className="inline-form" onSubmit={saveEdit}><textarea maxLength="500" value={editingContent} onChange={(event) => setEditingContent(event.target.value)} required /><div className="button-row"><button className="primary-button">수정 저장</button><button type="button" className="secondary-button" onClick={() => setEditingId(null)}>취소</button></div></form> : <p className="pre-wrap">{item.content}</p>}<div className="button-row">{me?.id === item.author_id && editingId !== item.id && <button className="secondary-button" onClick={() => { setEditingId(item.id); setEditingContent(item.content) }}>수정</button>}{(me?.id === item.author_id || me?.id === record.user_id) && <button className="danger-button" onClick={() => remove(item)}>삭제</button>}<ReportForm targetType="comment" targetId={item.id} /></div></article>)}
      </section>
    </>}
  </AppLayout>
}
