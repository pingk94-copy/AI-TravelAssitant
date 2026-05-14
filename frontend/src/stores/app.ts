import { defineStore } from 'pinia'

import {
  type AuthUser,
  type LoginPayload,
  type RegisterPayload,
  getCurrentUser,
  login,
  register,
} from '../api/auth'

export const useAppStore = defineStore('app', {
  state: () => ({
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
    currentTaskId: '',
    token: localStorage.getItem('access_token') ?? '',
    user: null as AuthUser | null,
    authReady: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token && state.user),
  },
  actions: {
    setCurrentTask(taskId: string) {
      this.currentTaskId = taskId
    },
    setAuth(token: string, user: AuthUser) {
      this.token = token
      this.user = user
      localStorage.setItem('access_token', token)
    },
    async register(payload: RegisterPayload) {
      const response = await register(payload)
      this.setAuth(response.access_token, response.user)
      return response.user
    },
    async login(payload: LoginPayload) {
      const response = await login(payload)
      this.setAuth(response.access_token, response.user)
      return response.user
    },
    async restoreUser() {
      if (!this.token) {
        this.authReady = true
        return
      }
      try {
        this.user = await getCurrentUser(this.token)
      } catch {
        this.logout()
      } finally {
        this.authReady = true
      }
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('access_token')
    },
  },
})
