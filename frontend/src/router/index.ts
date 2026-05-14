import { createRouter, createWebHistory } from 'vue-router'

import { useAppStore } from '../stores/app'
import AuthView from '../views/AuthView.vue'
import ChatView from '../views/ChatView.vue'
import DashboardView from '../views/DashboardView.vue'
import TripsView from '../views/TripsView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: DashboardView },
    { path: '/auth', name: 'auth', component: AuthView },
    { path: '/chat', name: 'chat', component: ChatView, meta: { requiresAuth: true } },
    { path: '/trips', name: 'trips', component: TripsView, meta: { requiresAuth: true } },
  ],
})

router.beforeEach(async (to) => {
  const appStore = useAppStore()
  if (!appStore.authReady) {
    await appStore.restoreUser()
  }
  if (to.meta.requiresAuth && !appStore.isAuthenticated) {
    return { name: 'auth' }
  }
})
