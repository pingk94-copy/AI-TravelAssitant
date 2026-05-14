<script setup lang="ts">
import { LogIn, UserPlus } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAppStore } from '../stores/app'

const router = useRouter()
const appStore = useAppStore()
const mode = ref<'login' | 'register'>('login')
const username = ref('traveler')
const email = ref('traveler@example.com')
const password = ref('StrongPass123')
const errorMessage = ref('')
const isSubmitting = ref(false)

const title = computed(() => (mode.value === 'login' ? '登录账号' : '创建账号'))

async function submitAuth() {
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
  <main class="mx-auto grid min-h-[calc(100vh-73px)] max-w-7xl items-center px-5 py-10 lg:grid-cols-[0.9fr_1.1fr]">
    <section class="hidden pr-10 lg:block">
      <p class="mb-4 text-sm font-semibold tracking-[0.18em] text-[#c75532]">账号中心</p>
      <h1 class="text-5xl font-semibold leading-tight">
        让每一次对话、工具查询和行程规划都沉淀到你的专属工作区。
      </h1>
      <p class="mt-5 max-w-xl text-sm leading-7 text-[#5e675b]">
        登录后，聊天记录、行程规划和后续收藏能力都会与当前用户绑定，方便继续追踪和复盘。
      </p>
    </section>

    <section class="mx-auto w-full max-w-md border border-[#d9d0bd] bg-[#f8f5ed] p-6">
      <div class="mb-6 flex gap-2 rounded bg-[#e7dfcf] p-1">
        <button
          class="flex-1 rounded px-4 py-2 text-sm font-semibold"
          :class="mode === 'login' ? 'bg-white text-[#17201a]' : 'text-[#5e675b]'"
          type="button"
          @click="mode = 'login'"
        >
          登录
        </button>
        <button
          class="flex-1 rounded px-4 py-2 text-sm font-semibold"
          :class="mode === 'register' ? 'bg-white text-[#17201a]' : 'text-[#5e675b]'"
          type="button"
          @click="mode = 'register'"
        >
          注册
        </button>
      </div>

      <h2 class="text-2xl font-semibold">{{ title }}</h2>

      <form class="mt-6 grid gap-4" @submit.prevent="submitAuth">
        <label v-if="mode === 'register'" class="grid gap-2 text-sm font-medium">
          用户名
          <input v-model="username" class="auth-input" type="text" />
        </label>
        <label class="grid gap-2 text-sm font-medium">
          邮箱
          <input v-model="email" class="auth-input" type="email" />
        </label>
        <label class="grid gap-2 text-sm font-medium">
          密码
          <input v-model="password" class="auth-input" type="password" />
        </label>

        <button
          class="mt-2 inline-flex h-12 items-center justify-center gap-2 rounded bg-[#1d3b2a] px-5 font-semibold text-white disabled:opacity-60"
          :disabled="isSubmitting"
          type="submit"
        >
          <UserPlus v-if="mode === 'register'" :size="18" />
          <LogIn v-else :size="18" />
          {{ title }}
        </button>
      </form>

      <p v-if="errorMessage" class="mt-4 text-sm text-[#b4442a]">{{ errorMessage }}</p>
    </section>
  </main>
</template>

<style scoped>
.auth-input {
  height: 2.75rem;
  border: 1px solid #d9d0bd;
  border-radius: 6px;
  background: #fff;
  padding: 0 0.75rem;
  outline: none;
}

.auth-input:focus {
  border-color: #1d3b2a;
}
</style>
