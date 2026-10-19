import { useEffect, useState } from 'react'

import { listPublicRecords } from '../api/records.js'
import AppLayout from '../components/AppLayout.jsx'
import ReportForm from '../components/ReportForm.jsx'

export default function PublicRecordsPage({ navigate }) {
  const [items, setItems] = useState([])
  const [type, setType] = useState('all')
  const [query, setQuery] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    listPublicRecords(type, query).then(setItems).catch((requestError) => setError(requestError.message)).finally(() => setLoading(false))
  }, [type, query])

  return <AppLayout navigate={navigate}>
    <section className="page-heading"><p className="eyebrow">COMMUNITY</p><h1>공개 기록</h1><p>로그인한 회원이 공개한 기록만 볼 수 있습니다.</p></section>
    <section className="list-tools"><input aria-label="공개 기록 검색" placeholder="검색어" value={query} onChange={(event) => setQuery(event.target.value)} /><select value={type} onChange={(event) => setType(event.target.value)}><option value="all">전체</option><option value="study">공부 기록</option><option value="todo">할 일</option><option value="error">오류 기록</option></select></section>
    {error && <p className="form-message form-message--error" role="alert">{error}</p>}
    {loading ? <p role="status">공개 기록을 불러오는 중입니다.</p> : <div className="card-grid">{items.map((item) => <article className="card record-card" key={`${item.type}-${item.id}`}>
      <div className="card-title-row"><h2>{item.title}</h2><span className="badge">{item.type}</span></div>
      {item.content && <p className="pre-wrap">{item.content}</p>} {item.status && <p><strong>{item.status}</strong></p>}
      <p className="meta">작성자 {item.author_nickname} · {new Date(item.created_at).toLocaleString()}</p>
      <div className="button-row">{item.type !== 'todo' && <button className="secondary-button" onClick={() => navigate(`/public/${item.type}/${item.id}`)}>자세히 보기</button>}<ReportForm targetType={item.type} targetId={item.id} /></div>
    </article>)}</div>}
  </AppLayout>
}
