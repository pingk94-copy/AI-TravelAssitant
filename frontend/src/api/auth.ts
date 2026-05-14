import { apiRequest } from './http'

export type AuthUser = {
  id: number
  username: string
  email: string
  is_guest: boolean
}

export type AuthResponse = {
  access_token: string
  token_type: 'bearer'
  user: AuthUser
}

export type RegisterPayload = {
  username: string
  email: string
  password: string
}

export type LoginPayload = {
  email: string
  password: string
}

export function register(payload: RegisterPayload) {
  return apiRequest<AuthResponse>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function login(payload: LoginPayload) {
  return apiRequest<AuthResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getCurrentUser(token: string) {
  return apiRequest<AuthUser>('/api/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  })
}
