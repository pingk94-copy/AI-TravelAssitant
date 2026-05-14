import { apiRequest } from './http'
import type { TripResponse } from './trips'

export type TaskResponse = {
  id: number
  task_type: string
  status: 'pending' | 'running' | 'success' | 'failed'
  input: Record<string, unknown>
  output: null | {
    trip?: TripResponse
  }
  error_message: string | null
  created_at: string
  updated_at: string
}

export function getTask(token: string, taskId: number) {
  return apiRequest<TaskResponse>(`/api/tasks/${taskId}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
}
