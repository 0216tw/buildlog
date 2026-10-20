import assert from 'node:assert/strict'
import test from 'node:test'

import {
  dashboardSummary,
  initialDashboardTasks,
  recentStudies,
  toggleExampleTask,
} from '../src/pages/dashboardData.js'


test('dashboard example data matches the Figma summary', () => {
  assert.deepEqual(
    dashboardSummary.map(({ label, value }) => [label, value]),
    [['공부 기록', 24], ['남은 할 일', 4], ['미해결 오류', 2]],
  )
  assert.equal(recentStudies.length, 3)
  assert.equal(initialDashboardTasks.length, 4)
})


test('dashboard task checks only update local example state', () => {
  const updated = toggleExampleTask(initialDashboardTasks, 2)

  assert.equal(initialDashboardTasks[1].completed, false)
  assert.equal(updated[1].completed, true)
  assert.equal(updated[0].completed, false)
})
