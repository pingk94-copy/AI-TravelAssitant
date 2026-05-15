<script setup lang="ts">
import { CheckCircle2, KeyRound, LogIn, ShieldCheck, UserPlus } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAppStore } from '../stores/app'

const router = useRouter()
const appStore = useAppStore()
const mode = ref<'login' | 'register'>('login')
const username = ref('')
const email = ref('')
const password = ref('')
const errorMessage = ref('')
const isSubmitting = ref(false)

const title = computed(() => (mode.value === 'login' ? '登录账号' : '创建账号'))
const canSubmit = computed(() => {
  const hasAccount = email.value.trim() && password.value
  return mode.value === 'login' ? Boolean(hasAccount && !isSubmitting.value) : Boolean(hasAccount && username.value.trim() && !isSubmitting.value)
})

function switchMode(nextMode: 'login' | 'register') {
  mode.value = nextMode
  errorMessage.value = ''
}

async function submitAuth() {
  if (!canSubmit.value) {
    errorMessage.value = mode.value === 'login' ? '请输入邮箱和密码。' : '请输入用户名、邮箱和密码。'
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    if (mode.value === 'register') {
      await appStore.register({
        username: username.value,
        email: email.value,
        password: password.value,
      })
    } else {
      await appStore.login({
        email: email.value,
        password: password.value,
      })
    }
    await router.push('/trips')
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '认证失败，请检查账号信息后重试。'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="mx-auto grid min-h-[calc(100vh-73px)] max-w-[112rem] items-center gap-6 px-4 py-6 md:px-6 md:py-8 lg:grid-cols-[1fr_480px]">
    <section class="app-surface hidden min-h-[560px] flex-col justify-between p-10 lg:flex">
      <div>
        <p class="inline-flex items-center gap-2 rounded-full border border-[#d7e3d3] bg-[#eef5eb] px-3 py-1 text-sm font-bold text-[#1d3b2a]">
          <ShieldCheck :size="16" />
          账号中心
        </p>
        <h1 class="mt-6 max-w-4xl text-5xl font-extrabold leading-tight">
          把对话、行程和收藏，都沉淀到你的专属旅行工作区。
        </h1>
        <p class="mt-5 max-w-2xl text-base leading-8 text-[#5e675b]">
          登录后可以保存每一次 AI 对话、结构化行程和收藏方案。下次继续规划时，不用从零开始。
        </p>
      </div>

      <div class="grid gap-3">
        <div class="app-card grid grid-cols-[auto_1fr] gap-3 p-4">
          <span class="app-icon"><CheckCircle2 :size="20" /></span>
          <div>
            <p class="font-bold">历史记录自动归档</p>
            <p class="mt-1 text-sm leading-6 text-[#5e675b]">对话和行程都会绑定到当前账号，方便复盘和继续修改。</p>
          </div>
        </div>
        <div class="app-card grid grid-cols-[auto_1fr] gap-3 p-4">
          <span class="app-icon app-icon-warm"><KeyRound :size="20" /></span>
          <div>
            <p class="font-bold">本地开发安全配置</p>
            <p class="mt-1 text-sm leading-6 text-[#5e675b]">API Key 留在后端环境文件中，不会暴露到前端页面。</p>
          </div>
        </div>
      </div>
    </section>

    <section class="app-surface mx-auto w-full max-w-md p-6 md:p-7">
      <div class="mb-6">
        <p class="text-sm font-bold text-[#c75532]">欢迎回来</p>
        <h2 class="mt-2 text-2xl font-extrabold">{{ title }}</h2>
        <p class="mt-2 text-sm leading-6 text-[#5e675b]">
          {{ mode === 'login' ? '登录后继续管理你的旅行计划。' : '创建账号后即可保存行程和对话。' }}
        </p>
      </div>

      <div class="mb-6 flex gap-2 rounded-lg bg-[#e7dfcf] p-1">
        <button
          class="flex-1 rounded-md px-4 py-2 text-sm font-bold"
          :class="mode === 'login' ? 'bg-white text-[#17201a]' : 'text-[#5e675b]'"
          type="button"
          @click="switchMode('login')"
        >
          登录
        </button>
        <button
          class="flex-1 rounded-md px-4 py-2 text-sm font-bold"
          :class="mode === 'register' ? 'bg-white text-[#17201a]' : 'text-[#5e675b]'"
          type="button"
          @click="switchMode('register')"
        >
          注册
        </button>
      </div>

      <form class="mt-6 grid gap-4" @submit.prevent="submitAuth">
        <label v-if="mode === 'register'" class="grid gap-2 text-sm font-medium">
          用户名
          <input v-model="username" autocomplete="username" class="app-input" placeholder="请输入用户名" type="text" />
        </label>
        <label class="grid gap-2 text-sm font-medium">
          邮箱
          <input v-model="email" autocomplete="email" class="app-input" placeholder="请输入邮箱" type="email" />
        </label>
        <label class="grid gap-2 text-sm font-medium">
          密码
          <input
            v-model="password"
            :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
            class="app-input"
            placeholder="请输入密码"
            type="password"
          />
        </label>

        <button
          class="app-button-primary mt-2 h-12 px-5 disabled:opacity-60"
          :disabled="!canSubmit"
          type="submit"
        >
          <UserPlus v-if="mode === 'register'" :size="18" />
          <LogIn v-else :size="18" />
          {{ title }}
        </button>
      </form>

      <div v-if="errorMessage" class="app-alert mt-4 p-3 text-sm leading-6">
        {{ errorMessage }}
      </div>
    </section>
  </main>
</template>
