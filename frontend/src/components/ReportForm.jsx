import { useState } from 'react'

import { createReport } from '../api/records.js'

export default function ReportForm({ targetType, targetId }) {
  const [open, setOpen] = useState(false)
  const [reason, setReason] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setError(''); setMessage(''); setSaving(true)
    try {
      await createReport(targetType, targetId, reason)
      setReason(''); setOpen(false); setMessage('신고를 접수했습니다.')
    } catch (requestError) { setError(requestError.message) }
    finally { setSaving(false) }
  }

  return <div className="report-box">
    <button className="secondary-button" type="button" onClick={() => setOpen(!open)}>신고</button>
    {open && <form className="inline-form" onSubmit={submit}><label>신고 이유<textarea maxLength="500" value={reason} onChange={(event) => setReason(event.target.value)} required /></label>{error && <p className="form-message form-message--error" role="alert">{error}</p>}<div className="button-row"><button className="primary-button" disabled={saving}>{saving ? '접수 중...' : '신고 접수'}</button><button className="secondary-button" type="button" onClick={() => setOpen(false)}>취소</button></div></form>}
    {message && <p className="form-message form-message--success" role="status">{message}</p>}
  </div>
}
