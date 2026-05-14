<script setup lang="ts">
import { LoaderCircle, MessageSquarePlus, SendHorizontal } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'

import {
  type ChatMessage,
  type ChatSession,
  createChatSession,
  listChatMessages,
  listChatSessions,
  streamChatReply,
} from '../api/chat'
import { useAppStore } from '../stores/app'

const appStore = useAppStore()
const sessions = ref<ChatSession[]>([])
const activeSession = ref<ChatSession | null>(null)
const messages = ref<ChatMessage[]>([])
const draft = ref('帮我规划一次杭州慢旅行')
const sessionTitle = ref('新的旅行对话')
const isStreaming = ref(false)
const errorMessage = ref('')

async function refreshSessions() {
  if (!appStore.token) return
  sessions.value = await listChatSessions(appStore.token)
  if (!activeSession.value && sessions.value.length > 0) {
    await selectSession(sessions.value[0])
  }
}

async function selectSession(session: ChatSession) {
  if (!appStore.token) return
  activeSession.value = session
  messages.value = await listChatMessages(appStore.token, session.id)
}

async function startSession() {
  if (!appStore.token) {
    errorMessage.value = '请先登录，再开始新的旅行对话。'
    return
  }

  const session = await createChatSession(appStore.token, sessionTitle.value)
  sessions.value = [session, ...sessions.value]
  activeSession.value = session
  messages.value = []
}

async function sendMessage() {
  if (!appStore.token || !activeSession.value || !draft.value.trim()) return

  const userText = draft.value.trim()
  draft.value = ''
  errorMessage.value = ''
  isStreaming.value = true
  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: userText,
    created_at: new Date().toISOString(),
  })
  const assistantMessage: ChatMessage = {
    id: Date.now() + 1,
    role: 'assistant',
    content: '',
    created_at: new Date().toISOString(),
  }
  messages.value.push(assistantMessage)

  try {
    await streamChatReply(appStore.token, activeSession.value.id, userText, (token) => {
      assistantMessage.content += token
    })
    messages.value = await listChatMessages(appStore.token, activeSession.value.id)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'AI 回复生成失败，请稍后重试。'
  } finally {
    isStreaming.value = false
  }
}

onMounted(() => {
  refreshSessions().catch((error) => {
    errorMessage.value = error instanceof Error ? error.message : '会话列表加载失败，请刷新页面重试。'
  })
})
</script>

<template>
  <main class="mx-auto grid max-w-7xl gap-5 px-5 py-8 lg:grid-cols-[300px_1fr]">
    <aside class="border border-[#d9d0bd] bg-[#f8f5ed] p-5">
      <h1 class="text-lg font-semibold">旅行会话</h1>

      <div class="mt-5 grid gap-3">
        <input
          v-model="sessionTitle"
          class="h-11 rounded border border-[#d9d0bd] bg-white px-3 text-sm outline-none focus:border-[#1d3b2a]"
          type="text"
        />
        <button
          class="inline-flex h-11 items-center justify-center gap-2 rounded bg-[#1d3b2a] px-4 text-sm font-semibold text-white"
          type="button"
          @click="startSession"
        >
          <MessageSquarePlus :size="17" />
          新建会话
        </button>
      </div>

      <div class="mt-6 grid gap-2">
        <button
          v-for="session in sessions"
          :key="session.id"
          class="rounded border px-3 py-3 text-left text-sm"
          :class="
            activeSession?.id === session.id
              ? 'border-[#1d3b2a] bg-[#e7dfcf] text-[#17201a]'
              : 'border-[#d9d0bd] bg-white text-[#5e675b]'
          "
          type="button"
          @click="selectSession(session)"
        >
          {{ session.title }}
        </button>
      </div>
    </aside>

    <section class="flex min-h-[620px] flex-col border border-[#d9d0bd] bg-white">
      <div class="border-b border-[#d9d0bd] p-5">
        <h2 class="text-xl font-semibold">{{ activeSession?.title ?? 'AI 旅行对话' }}</h2>
        <p class="mt-1 text-sm text-[#5e675b]">通过 SSE 流式接收 FastAPI 后端返回的 AI 回复。</p>
      </div>

      <div class="flex-1 space-y-4 overflow-y-auto p-5">
        <div v-if="!activeSession" class="flex h-full items-center justify-center text-center text-[#5e675b]">
          先新建一个会话，就可以开始和 AI 讨论旅行计划。
        </div>

        <article
          v-for="message in messages"
          :key="message.id"
          class="max-w-[82%] rounded px-4 py-3 text-sm leading-6"
          :class="
            message.role === 'user'
              ? 'ml-auto bg-[#1d3b2a] text-white'
              : 'mr-auto border border-[#d9d0bd] bg-[#f8f5ed] text-[#17201a]'
          "
        >
          {{ message.content }}
        </article>
      </div>

      <p v-if="errorMessage" class="border-t border-[#d9d0bd] px-5 py-3 text-sm text-[#b4442a]">
        {{ errorMessage }}
      </p>

      <form class="grid gap-3 border-t border-[#d9d0bd] p-5 md:grid-cols-[1fr_auto]" @submit.prevent="sendMessage">
        <input
          v-model="draft"
          :disabled="!activeSession || isStreaming"
          class="h-12 rounded border border-[#d9d0bd] bg-white px-4 outline-none focus:border-[#1d3b2a] disabled:bg-[#eee8dc]"
          placeholder="输入你的旅行想法，例如：杭州两日慢旅行怎么安排？"
          type="text"
        />
        <button
          class="inline-flex h-12 items-center justify-center gap-2 rounded bg-[#c75532] px-5 font-semibold text-white disabled:opacity-60"
          :disabled="!activeSession || isStreaming"
          type="submit"
        >
          <LoaderCircle v-if="isStreaming" class="animate-spin" :size="18" />
          <SendHorizontal v-else :size="18" />
          发送
        </button>
      </form>
    </section>
  </main>
</template>
