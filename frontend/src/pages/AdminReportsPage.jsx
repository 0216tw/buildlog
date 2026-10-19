import { useEffect, useState } from 'react'

import { listReports } from '../api/records.js'
import AppLayout from '../components/AppLayout.jsx'

export default function AdminReportsPage({ navigate }) {
  const [reports, setReports] = useState([])
  const [error, setError] = useState('')
  useEffect(() => { listReports().then(setReports).catch((requestError) => setError(requestError.message)) }, [])
  return <AppLayout navigate={navigate}><section className="page-heading"><p className="eyebrow">ADMIN</p><h1>신고 관리</h1><p>신고는 내용을 숨기거나 삭제하지 않고 운영자 확인용으로 보관됩니다.</p></section>{error && <p className="form-message form-message--error" role="alert">{error}</p>}<div className="card-grid">{reports.map((report) => <article className="card" key={report.id}><h2>{report.target_type} #{report.target_id}</h2><p>{report.reason}</p><p className="meta">신고자 {report.reporter_nickname} · {new Date(report.created_at).toLocaleString()}</p></article>)}</div></AppLayout>
}
