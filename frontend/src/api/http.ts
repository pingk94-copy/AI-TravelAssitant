const defaultApiBaseUrl = 'http://127.0.0.1:8000'

export function getApiBaseUrl() {
  return import.meta.env.VITE_API_BASE_URL ?? defaultApiBaseUrl
}

function formatValidationError(detail: unknown) {
  if (!Array.isArray(detail)) return ''

  const messages = detail
    .map((item) => {
      if (!item || typeof item !== 'object') return ''
      const error = item as { loc?: unknown[]; msg?: string; type?: string }
      const field = Array.isArray(error.loc) ? String(error.loc[error.loc.length - 1] ?? '') : ''

      if (field === 'email') return '邮箱格式不正确，请输入类似 name@example.com 的邮箱。'
      if (field === 'password' && error.type?.includes('too_short')) return '密码至少需要 8 位。'
      if (field === 'username' && error.type?.includes('too_short')) return '用户名至少需要 2 个字符。'
      return error.msg ?? ''
    })
    .filter(Boolean)

  return messages.join(' ')
}

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (!response.ok) {
    let message = `请求失败，状态码 ${response.status}`
    try {
      const body = await response.json()
      if (typeof body.detail === 'string') {
        message = body.detail
      } else {
        message = formatValidationError(body.detail) || message
      }
    } catch {
      // Keep the status-based message when the backend returns no JSON body.
    }
    throw new Error(message)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}
