export const dashboardSummary = [
  { label: '공부 기록', value: 24, hint: '쌓아온 배움의 순간' },
  { label: '남은 할 일', value: 4, hint: '하나씩 완료해보세요' },
  { label: '미해결 오류', value: 2, hint: '해결 과정도 소중한 기록이에요' },
]

export const recentStudies = [
  {
    title: 'React 컴포넌트, 이제 조금 알 것 같아요',
    description: '화면을 작은 조각으로 나누고 다시 조합하는 방법을 배웠어요.',
    date: '오늘',
  },
  {
    title: 'FastAPI로 첫 API 만들기',
    description: 'GET과 POST의 차이를 직접 요청하며 확인했어요.',
    date: '어제',
  },
  {
    title: 'Supabase 연결 성공!',
    description: '내가 쓴 기록이 새로고침 후에도 그대로 남아 있어요.',
    date: '10월 18일',
  },
]

export const initialDashboardTasks = [
  { id: 1, title: 'Figma 대시보드 디자인 살펴보기', completed: false },
  { id: 2, title: 'MCP로 디자인 정보 읽어오기', completed: false },
  { id: 3, title: 'React 화면으로 구현하기', completed: false },
  { id: 4, title: '실제 데이터 연결해보기', completed: false },
]

export function toggleExampleTask(tasks, taskId) {
  return tasks.map((task) => (
    task.id === taskId ? { ...task, completed: !task.completed } : task
  ))
}
