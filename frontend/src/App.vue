<script setup lang="ts">
import { Compass, LogOut, MapPinned, MessageSquareText, Route, UserRound } from 'lucide-vue-next'
import { RouterLink, RouterView } from 'vue-router'

import { useAppStore } from './stores/app'

const appStore = useAppStore()
</script>

<template>
  <div class="min-h-screen bg-[#f4f0e7] pb-24 text-[#17201a] md:pb-0">
    <header class="border-b border-[#d9d0bd] bg-[#f8f5ed]/90 backdrop-blur">
      <div class="mx-auto flex max-w-[112rem] items-center justify-between px-5 py-4 md:px-6">
        <RouterLink to="/" class="flex min-w-0 items-center gap-3">
          <span class="grid h-10 w-10 place-items-center rounded bg-[#1d3b2a] text-white">
            <Compass :size="21" />
          </span>
          <span class="min-w-0">
            <span class="block truncate text-base font-semibold">AI 智能旅行助手</span>
            <span class="hidden text-xs text-[#6d746a] sm:block">Vue 3 + FastAPI 全栈项目</span>
          </span>
        </RouterLink>

        <nav class="hidden items-center gap-1 md:flex">
          <RouterLink class="nav-link" to="/">
            <MapPinned :size="17" />
            首页
          </RouterLink>
          <RouterLink class="nav-link" to="/chat">
            <MessageSquareText :size="17" />
            AI 对话
          </RouterLink>
          <RouterLink class="nav-link" to="/trips">
            <Route :size="17" />
            行程规划
          </RouterLink>
        </nav>

        <div class="flex items-center gap-2">
          <RouterLink
            v-if="!appStore.isAuthenticated"
            class="inline-flex h-10 items-center justify-center gap-2 rounded border border-[#cfc4ae] bg-white px-3 text-sm font-semibold text-[#1d3b2a]"
            to="/auth"
          >
            <UserRound :size="17" />
            登录
          </RouterLink>
          <template v-else>
            <span class="hidden text-sm text-[#465144] sm:inline">{{ appStore.user?.username }}</span>
            <button
              aria-label="退出登录"
              class="inline-flex h-10 w-10 items-center justify-center rounded border border-[#cfc4ae] bg-white text-[#1d3b2a]"
              type="button"
              @click="appStore.logout()"
            >
              <LogOut :size="18" />
            </button>
          </template>
        </div>
      </div>
    </header>

    <RouterView />

    <nav class="fixed inset-x-0 bottom-0 z-40 border-t border-[#d9d0bd] bg-[#f8f5ed]/95 px-3 py-2 shadow-[0_-10px_24px_rgba(23,32,26,0.08)] backdrop-blur md:hidden">
      <div class="mx-auto grid max-w-md grid-cols-3 gap-2">
        <RouterLink class="mobile-nav-link" to="/">
          <MapPinned :size="19" />
          首页
        </RouterLink>
        <RouterLink class="mobile-nav-link" to="/chat">
          <MessageSquareText :size="19" />
          对话
        </RouterLink>
        <RouterLink class="mobile-nav-link" to="/trips">
          <Route :size="19" />
          行程
        </RouterLink>
      </div>
    </nav>
  </div>
</template>

<style scoped>
.nav-link {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  border-radius: 6px;
  padding: 0.55rem 0.75rem;
  color: #465144;
  font-size: 0.9rem;
  text-decoration: none;
}

.nav-link.router-link-active {
  background: #e7dfcf;
  color: #17201a;
}

.mobile-nav-link {
  display: inline-flex;
  min-height: 3.25rem;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  border-radius: 6px;
  color: #465144;
  font-size: 0.82rem;
  font-weight: 700;
  text-decoration: none;
}

.mobile-nav-link.router-link-active {
  background: #e7dfcf;
  color: #17201a;
}
</style>
