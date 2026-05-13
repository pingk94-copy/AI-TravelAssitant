import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
    currentTaskId: '',
    token: localStorage.getItem('access_token') ?? '',
    user: null as null | {
      id: number
      username: string
      email: string
      is_guest: boolean
    },
  }),
  actions: {
    setCurrentTask(taskId: string) {
      this.currentTaskId = taskId
    },
    setToken(token: string) {
      this.token = token
      localStorage.setItem('access_token', token)
    },
    clearToken() {
      this.token = ''
      this.user = null
      localStorage.removeItem('access_token')
    },
  },
})
