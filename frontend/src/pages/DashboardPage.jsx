import { useEffect, useState } from 'react'

import { ApiError, getCurrentUser } from '../api/auth.js'
import {
  dashboardSummary,
  initialDashboardTasks,
  recentStudies,
  toggleExampleTask,
} from './dashboardData.js'
import '../styles/dashboard.css'


const navigationItems = [
  { icon: '▦', label: '대시보드', path: '/dashboard' },
  { icon: '▤', label: '공부 기록', path: '/studies' },
  { icon: '✓', label: '할 일', path: '/todos' },
  { icon: '!', label: '오류 기록', path: '/errors' },
  { icon: '▣', label: '학습 자료함', path: '/materials' },
  { icon: '↗', label: '공개 기록', path: '/public' },
]


function DashboardPage({ navigate }) {
  const [user, setUser] = useState(null)
  const [userLoading, setUserLoading] = useState(true)
  const [userError, setUserError] = useState('')
  const [tasks, setTasks] = useState(initialDashboardTasks)
  const newlyCompleted = tasks.filter((task) => task.completed).length
  const remainingTasks = tasks.length - newlyCompleted
  const completedCount = 8 + newlyCompleted
  const totalTasks = 12
  const completionRate = Math.round((completedCount / totalTasks) * 100)

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

  function handleTaskChange(taskId) {
    setTasks((currentTasks) => toggleExampleTask(currentTasks, taskId))
  }

  if (userLoading) {
    return <main className="page-shell"><p role="status">로그인 정보를 확인하고 있습니다.</p></main>
  }

  if (userError) {
    return <main className="page-shell"><p className="form-message form-message--error" role="alert">{userError}</p></main>
  }

  if (!user) return null

  const nicknameInitial = Array.from(user.nickname)[0] ?? ''

  return (
    <div className="figma-dashboard">
      <aside className="figma-dashboard__sidebar" aria-label="BuildLog 메뉴">
        <button className="figma-dashboard__brand" type="button" onClick={() => navigate('/dashboard')}>
          <span className="figma-dashboard__brand-mark">b</span>
          <span>BuildLog</span>
        </button>

        <p className="figma-dashboard__workspace-label">MY WORKSPACE</p>
        <nav className="figma-dashboard__nav" aria-label="대시보드 메뉴">
          {navigationItems.map((item) => (
            <button
              className={`figma-dashboard__nav-item${item.path === '/dashboard' ? ' figma-dashboard__nav-item--active' : ''}`}
              type="button"
              key={item.path}
              aria-current={item.path === '/dashboard' ? 'page' : undefined}
              onClick={() => navigate(item.path)}
            >
              <span className="figma-dashboard__nav-icon" aria-hidden="true">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="figma-dashboard__account">
          <span className="figma-dashboard__avatar" aria-hidden="true">{nicknameInitial}</span>
          <button
            className="figma-dashboard__account-link"
            type="button"
            aria-label={`${user.nickname} 계정 설정`}
            onClick={() => navigate('/settings')}
          >
            <strong title={user.nickname}>{user.nickname}</strong>
            <span>계정 설정&nbsp; ›</span>
          </button>
        </div>
      </aside>

      <main className="figma-dashboard__main">
        <div className="figma-dashboard__topbar">
          <p>내 학습 한눈에 보기</p>
          <time dateTime="2026-10-20">2026. 10. 20&nbsp;&nbsp;화요일</time>
        </div>

        <section className="figma-dashboard__greeting" aria-labelledby="dashboard-title">
          <div>
            <h1 id="dashboard-title">{user.nickname}님, 차곡차곡 쌓이고 있어요</h1>
            <p>오늘의 배움도 기록으로 남겨보세요.</p>
          </div>
          <button className="figma-dashboard__primary-action" type="button" onClick={() => navigate('/studies')}>
            +&nbsp; 공부 기록 쓰기
          </button>
        </section>

        <section className="figma-dashboard__summary-grid" aria-label="학습 요약">
          {dashboardSummary.map((item) => (
            <article className="figma-dashboard__summary-card" key={item.label}>
              <p className="figma-dashboard__summary-label">{item.label}</p>
              <strong>{item.label === '남은 할 일' ? remainingTasks : item.value}</strong>
              <p className="figma-dashboard__summary-hint">{item.hint}</p>
            </article>
          ))}
        </section>

        <section className="figma-dashboard__content-grid">
          <article className="figma-dashboard__panel figma-dashboard__studies">
            <header className="figma-dashboard__panel-header">
              <h2>최근 공부 기록</h2>
              <button type="button" onClick={() => navigate('/studies')}>전체 보기&nbsp; ›</button>
            </header>
            <div className="figma-dashboard__study-list">
              {recentStudies.map((study) => (
                <article className="figma-dashboard__study-item" key={study.title}>
                  <div>
                    <h3>{study.title}</h3>
                    <time>{study.date}</time>
                  </div>
                  <p>{study.description}</p>
                </article>
              ))}
            </div>
          </article>

          <article className="figma-dashboard__panel figma-dashboard__tasks">
            <header className="figma-dashboard__task-header">
              <h2>남은 할 일</h2>
              <span>{remainingTasks}개</span>
            </header>
            <p className="figma-dashboard__task-copy">작은 완료가 모여 큰 성장이 돼요.</p>
            <div className="figma-dashboard__task-list">
              {tasks.map((task) => (
                <label className={`figma-dashboard__task${task.completed ? ' figma-dashboard__task--completed' : ''}`} key={task.id}>
                  <input
                    type="checkbox"
                    checked={task.completed}
                    onChange={() => handleTaskChange(task.id)}
                  />
                  <span>{task.title}</span>
                </label>
              ))}
            </div>
            <button className="figma-dashboard__task-footer" type="button" onClick={() => navigate('/todos')}>
              할 일 관리하기&nbsp; →
            </button>
          </article>
        </section>

        <section className="figma-dashboard__progress" aria-label="할 일 완료율">
          <div className="figma-dashboard__progress-copy">
            <h2>잘하고 있어요. 벌써 {completedCount}개 완료!</h2>
            <p>전체 할 일 {totalTasks}개 중 {completedCount}개를 마쳤어요.</p>
          </div>
          <div className="figma-dashboard__progress-visual">
            <div className="figma-dashboard__progress-labels">
              <span>할 일 완료율</span>
              <strong>{completionRate}%</strong>
            </div>
            <div
              className="figma-dashboard__progress-track"
              role="progressbar"
              aria-valuemin="0"
              aria-valuemax={totalTasks}
              aria-valuenow={completedCount}
            >
              <span style={{ width: `${completionRate}%` }} />
            </div>
          </div>
          <strong className="figma-dashboard__progress-total">{completedCount} / {totalTasks}</strong>
        </section>

        <footer className="figma-dashboard__footer">
          <span>매일의 작은 기록, 내일의 큰 변화.</span>
          <span>수업용 예시 데이터</span>
        </footer>
      </main>
    </div>
  )
}

export default DashboardPage
