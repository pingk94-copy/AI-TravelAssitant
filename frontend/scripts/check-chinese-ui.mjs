import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const rootDir = dirname(dirname(fileURLToPath(import.meta.url)))

const filesToCheck = [
  'src/App.vue',
  'src/views/DashboardView.vue',
  'src/views/AuthView.vue',
  'src/views/ChatView.vue',
  'src/views/TripsView.vue',
]

const forbiddenVisibleText = [
  'AI Travel Assistant',
  'Vue 3 + FastAPI</span>',
  '>Dashboard<',
  '>Chat<',
  '>Trips<',
  '>Login<',
  '>Register<',
  '>Send<',
  '>Start<',
  '>Origin<',
  '>Destination<',
  '>Days<',
  '>Budget<',
  '>Preferences<',
  'Weather-aware planning',
  'POI search',
  'Stay strategy',
  'Phase 1 skeleton',
  'Sign in',
  'Create account',
  'Chat Sessions',
  'New Session',
  'AI Travel Chat',
  'SSE stream is connected',
  'Create a session',
  'Ask for travel ideas',
  'Trip Planner',
  'Async task itinerary',
  'Start date',
  'Generate itinerary',
  'No itinerary yet',
  'Route tips',
  'Notes',
]

const failures = []

for (const file of filesToCheck) {
  const content = readFileSync(join(rootDir, file), 'utf8')
  for (const text of forbiddenVisibleText) {
    if (content.includes(text)) {
      failures.push(`${file}: ${text}`)
    }
  }
}

if (failures.length > 0) {
  console.error('以下前端用户可见英文文案仍未中文化：')
  for (const failure of failures) {
    console.error(`- ${failure}`)
  }
  process.exit(1)
}

console.log('前端核心页面中文化检查通过。')
