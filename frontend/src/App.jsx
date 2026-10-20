import { useCallback, useEffect, useState } from 'react'

import AccountSettingsPage from './pages/AccountSettingsPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import HomePage from './pages/HomePage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import MaterialsPage from './pages/MaterialsPage.jsx'
import AdminReportsPage from './pages/AdminReportsPage.jsx'
import PublicDetailPage from './pages/PublicDetailPage.jsx'
import PublicRecordsPage from './pages/PublicRecordsPage.jsx'
import RecordsPage from './pages/RecordsPage.jsx'
import SignupPage from './pages/SignupPage.jsx'

function App() {
  const [path, setPath] = useState(window.location.pathname)
  const [message, setMessage] = useState('')

  useEffect(() => {
    const handlePopState = () => {
      setPath(window.location.pathname)
      setMessage('')
    }
    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  const navigate = useCallback((nextPath, nextMessage = '') => {
    window.history.pushState({}, '', nextPath)
    setPath(nextPath)
    setMessage(nextMessage)
  }, [])

  if (path === '/signup') return <SignupPage navigate={navigate} />
  if (path === '/login') return <LoginPage navigate={navigate} message={message} />
  if (path === '/settings') return <AccountSettingsPage navigate={navigate} />
  if (path === '/dashboard') return <DashboardPage navigate={navigate} />
  if (path === '/materials') return <MaterialsPage navigate={navigate} />
  if (path === '/studies') return <RecordsPage kind="studies" navigate={navigate} />
  if (path === '/todos') return <RecordsPage kind="todos" navigate={navigate} />
  if (path === '/errors') return <RecordsPage kind="errors" navigate={navigate} />
  if (path === '/public') return <PublicRecordsPage navigate={navigate} />
  if (path === '/admin/reports') return <AdminReportsPage navigate={navigate} />
  const detailMatch = path.match(/^\/public\/(study|error)\/(\d+)$/)
  if (detailMatch) return <PublicDetailPage type={detailMatch[1]} id={detailMatch[2]} navigate={navigate} />
  return <HomePage navigate={navigate} />
}

export default App
