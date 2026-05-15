import { apiRequest, getApiBaseUrl } from './http'

export type ChatSession = {
  id: number
  title: string
  created_at: string
}

export type ChatMessage = {
  id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at: string
}

export type LlmHealth = {
  status: 'configured' | 'disabled'
  enabled: boolean
  api_key_configured: boolean
  base_url: string
  model: string
  timeout_seconds: number
}

export async function getLlmHealth() {
  return apiRequest<LlmHealth>('/api/health/llm')
}

export async function createChatSession(token: string, title: string) {
  return apiRequest<ChatSession>('/api/chat/sessions', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ title }),
  })
}

export async function listChatSessions(token: string) {
  return apiRequest<ChatSession[]>('/api/chat/sessions', {
    headers: { Authorization: `Bearer ${token}` },
  })
}

export async function listChatMessages(token: string, sessionId: number) {
  return apiRequest<ChatMessage[]>(`/api/chat/sessions/${sessionId}/messages`, {
    headers: { Authorization: `Bearer ${token}` },
  })
}

export async function deleteChatSession(token: string, sessionId: number) {
  return apiRequest<void>(`/api/chat/sessions/${sessionId}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  })
}

export async function streamChatReply(
  token: string,
  sessionId: number,
  message: string,
  onToken: (token: string) => void,
) {
  const response = await fetch(`${getApiBaseUrl()}/api/chat/sessions/${sessionId}/stream`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  })

  if (!response.ok || response.body === null) {
    throw new Error(`AI 回复请求失败，状态码 ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const events = buffer.split('\n\n')
    buffer = events.pop() ?? ''

    for (const event of events) {
      const dataLine = event.split('\n').find((line) => line.startsWith('data: '))
      const data = dataLine?.slice(6)
      if (data && data !== '[DONE]') {
        onToken(data)
      }
    }
  }
}
