<script setup lang="ts">
import { AlertTriangle, LoaderCircle, MessageSquarePlus, SendHorizontal, Trash2, X } from 'lucide-vue-next'
import { computed, nextTick, onMounted, ref } from 'vue'

import {
  type ChatMessage,
  type ChatSession,
  type LlmHealth,
  createChatSession,
  deleteChatSession,
  getLlmHealth,
  listChatMessages,
  listChatSessions,
  streamChatReply,
} from '../api/chat'
import { useAppStore } from '../stores/app'

type RenderBlock = {
  type: 'heading' | 'list' | 'paragraph'
  text?: string
  items?: string[]
}

const appStore = useAppStore()
const sessions = ref<ChatSession[]>([])
const activeSession = ref<ChatSession | null>(null)
const pendingDeleteSession = ref<ChatSession | null>(null)
const messages = ref<ChatMessage[]>([])
const draft = ref('')
const sessionTitle = ref('')
const isStreaming = ref(false)
const isDeleting = ref(false)
const errorMessage = ref('')
const llmHealth = ref<LlmHealth | null>(null)
const llmHealthError = ref('')
const messageList = ref<HTMLElement | null>(null)

const canSend = computed(() => Boolean(activeSession.value && draft.value.trim() && !isStreaming.value))
const llmStatusText = computed(() => {
  if (llmHealthError.value) return '模型状态获取失败'
  if (!llmHealth.value) return '正在检查模型状态'
  return llmHealth.value.enabled ? '大模型已配置' : '大模型未配置'
})
const llmStatusClass = computed(() => {
  if (llmHealth.value?.enabled) return 'border-[#b8d8bf] bg-[#eef8ef] text-[#1d5a2c]'
  if (llmHealthError.value) return 'border-[#edc7b8] bg-[#fff4ef] text-[#9d3d20]'
  return 'border-[#d9d0bd] bg-[#f8f5ed] text-[#5e675b]'
})

async function scrollToBottom() {
  await nextTick()
  if (messageList.value) {
    messageList.value.scrollTop = messageList.value.scrollHeight
  }
}

async function refreshSessions() {
  if (!appStore.token) return
  sessions.value = await listChatSessions(appStore.token)
  if (!activeSession.value && sessions.value.length > 0) {
    await selectSession(sessions.value[0])
  }
}

async function refreshLlmHealth() {
  try {
    llmHealth.value = await getLlmHealth()
    llmHealthError.value = ''
  } catch (error) {
    llmHealthError.value = error instanceof Error ? error.message : '模型状态检查失败。'
  }
}

async function selectSession(session: ChatSession) {
  if (!appStore.token) return
  activeSession.value = session
  messages.value = await listChatMessages(appStore.token, session.id)
  await scrollToBottom()
}

async function startSession() {
  if (!appStore.token) {
    errorMessage.value = '请先登录，再开始新的旅行对话。'
    return
  }

  const title = sessionTitle.value.trim() || '新的旅行对话'
  const session = await createChatSession(appStore.token, title)
  sessions.value = [session, ...sessions.value]
  activeSession.value = session
  messages.value = []
  sessionTitle.value = ''
  errorMessage.value = ''
}

function requestDeleteSession(session: ChatSession) {
  if (isStreaming.value) return
  pendingDeleteSession.value = session
}

function cancelDeleteSession() {
  if (isDeleting.value) return
  pendingDeleteSession.value = null
}

async function confirmDeleteSession() {
  if (!appStore.token || !pendingDeleteSession.value) return
  const session = pendingDeleteSession.value
  isDeleting.value = true
  errorMessage.value = ''

  try {
    await deleteChatSession(appStore.token, session.id)
    sessions.value = sessions.value.filter((item) => item.id !== session.id)
    if (activeSession.value?.id === session.id) {
      activeSession.value = sessions.value[0] ?? null
      messages.value = []
      if (activeSession.value) {
        await selectSession(activeSession.value)
      }
    }
    pendingDeleteSession.value = null
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '删除会话失败，请稍后重试。'
  } finally {
    isDeleting.value = false
  }
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
  await scrollToBottom()

  try {
    await streamChatReply(appStore.token, activeSession.value.id, userText, async (token) => {
      assistantMessage.content += token
      await scrollToBottom()
    })
    messages.value = await listChatMessages(appStore.token, activeSession.value.id)
    await scrollToBottom()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'AI 回复生成失败，请稍后重试。'
  } finally {
    isStreaming.value = false
  }
}

function renderBlocks(content: string): RenderBlock[] {
  const normalized = content
    .replace(/\r/g, '')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/#{1,6}\s*/g, '\n## ')
    .replace(/\s+-\s+/g, '\n- ')
    .replace(/\s+(\d+[.、])\s+/g, '\n$1 ')
    .replace(/([。！？；])\s*/g, '$1\n')
  const lines = normalized
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
  const blocks: RenderBlock[] = []
  let listItems: string[] = []

  function flushList() {
    if (listItems.length > 0) {
      blocks.push({ type: 'list', items: listItems })
      listItems = []
    }
  }

  for (const line of lines) {
    if (line.startsWith('## ')) {
      flushList()
      blocks.push({ type: 'heading', text: line.replace(/^##\s*/, '') })
    } else if (/^[-*]\s+/.test(line)) {
      listItems.push(line.replace(/^[-*]\s+/, ''))
    } else if (/^\d+[.、]\s+/.test(line)) {
      listItems.push(line.replace(/^\d+[.、]\s+/, ''))
    } else {
      flushList()
      blocks.push({ type: 'paragraph', text: line })
    }
  }
  flushList()
  return blocks.length > 0 ? blocks : [{ type: 'paragraph', text: content }]
}

onMounted(() => {
  refreshLlmHealth()
  refreshSessions().catch((error) => {
    errorMessage.value = error instanceof Error ? error.message : '会话列表加载失败，请刷新页面重试。'
  })
})
</script>

<template>
  <main class="mx-auto grid max-w-7xl gap-5 px-4 py-5 md:h-[calc(100vh-73px)] md:px-5 md:py-6 lg:grid-cols-[320px_1fr]">
    <aside class="flex min-h-0 flex-col border border-[#d9d0bd] bg-[#f8f5ed] p-5">
      <div class="shrink-0">
        <h1 class="text-lg font-semibold">旅行会话</h1>

        <div class="mt-5 grid gap-3">
          <input
            v-model="sessionTitle"
            class="h-11 rounded border border-[#d9d0bd] bg-white px-3 text-sm outline-none focus:border-[#1d3b2a]"
            placeholder="会话标题，例如：西安三日游"
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
      </div>

      <div class="mt-6 grid gap-2 overflow-y-auto pr-1 md:min-h-0">
        <div
          v-for="session in sessions"
          :key="session.id"
          class="group grid grid-cols-[1fr_auto] items-center gap-2 rounded border px-3 py-3 text-sm"
          :class="
            activeSession?.id === session.id
              ? 'border-[#1d3b2a] bg-[#e7dfcf] text-[#17201a]'
              : 'border-[#d9d0bd] bg-white text-[#5e675b]'
          "
        >
          <button class="truncate text-left" type="button" @click="selectSession(session)">
            {{ session.title }}
          </button>
          <button
            class="inline-flex h-8 w-8 items-center justify-center rounded text-[#8b4a36] hover:bg-white"
            title="删除会话"
            type="button"
            @click="requestDeleteSession(session)"
          >
            <Trash2 :size="15" />
          </button>
        </div>
      </div>
    </aside>

    <section class="flex min-h-[620px] flex-col border border-[#d9d0bd] bg-white md:min-h-0">
      <div class="shrink-0 border-b border-[#d9d0bd] p-5">
        <h2 class="text-xl font-semibold">{{ activeSession?.title ?? 'AI 旅行对话' }}</h2>
        <p class="mt-1 text-sm text-[#5e675b]">回复会按标题、段落和清单拆开显示，方便阅读和复查。</p>
        <div class="mt-4 rounded border px-4 py-3 text-sm" :class="llmStatusClass">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <span class="font-semibold">{{ llmStatusText }}</span>
            <button class="text-xs font-semibold underline-offset-4 hover:underline" type="button" @click="refreshLlmHealth">
              重新检查
            </button>
          </div>
          <p v-if="llmHealth" class="mt-2 leading-6">
            当前模型：{{ llmHealth.model }} · 接口：{{ llmHealth.base_url }} · 超时：{{ llmHealth.timeout_seconds }} 秒
          </p>
          <p v-if="llmHealth && !llmHealth.enabled" class="mt-2 leading-6">
            请在 backend\.env 填入真实 OPENAI_API_KEY 后，重新执行一键启动脚本。
          </p>
          <p v-if="llmHealthError" class="mt-2 leading-6">
            {{ llmHealthError }}
          </p>
        </div>
      </div>

      <div ref="messageList" class="min-h-0 flex-1 space-y-5 overflow-y-auto p-5">
        <div v-if="!activeSession" class="flex h-full items-center justify-center text-center text-[#5e675b]">
          先新建一个会话，就可以开始和 AI 讨论旅行计划。
        </div>

        <article
          v-for="message in messages"
          :key="message.id"
          class="rounded px-4 py-3 text-sm leading-7"
          :class="
            message.role === 'user'
              ? 'ml-auto max-w-[92%] bg-[#1d3b2a] text-white md:max-w-[78%]'
              : 'mr-auto max-w-[860px] border border-[#d9d0bd] bg-[#f8f5ed] text-[#17201a]'
          "
        >
          <template v-if="message.role === 'assistant'">
            <div class="grid gap-3">
              <template v-for="(block, index) in renderBlocks(message.content)" :key="`${message.id}-${index}`">
                <h3 v-if="block.type === 'heading'" class="text-base font-semibold text-[#1d3b2a]">
                  {{ block.text }}
                </h3>
                <ul v-else-if="block.type === 'list'" class="grid gap-2 pl-4">
                  <li v-for="item in block.items" :key="item" class="list-disc">
                    {{ item }}
                  </li>
                </ul>
                <p v-else>
                  {{ block.text }}
                </p>
              </template>
            </div>
          </template>
          <template v-else>
            {{ message.content }}
          </template>
        </article>
      </div>

      <p v-if="errorMessage" class="shrink-0 border-t border-[#d9d0bd] px-5 py-3 text-sm text-[#b4442a]">
        {{ errorMessage }}
      </p>

      <form class="grid shrink-0 gap-3 border-t border-[#d9d0bd] p-5 md:grid-cols-[1fr_auto]" @submit.prevent="sendMessage">
        <input
          v-model="draft"
          :disabled="!activeSession || isStreaming"
          class="h-12 rounded border border-[#d9d0bd] bg-white px-4 outline-none focus:border-[#1d3b2a] disabled:bg-[#eee8dc]"
          placeholder="输入你的旅行想法，例如：杭州两日慢旅行怎么安排？"
          type="text"
        />
        <button
          class="inline-flex h-12 items-center justify-center gap-2 rounded bg-[#c75532] px-5 font-semibold text-white disabled:opacity-60"
          :disabled="!canSend"
          type="submit"
        >
          <LoaderCircle v-if="isStreaming" class="animate-spin" :size="18" />
          <SendHorizontal v-else :size="18" />
          发送
        </button>
      </form>
    </section>

    <Teleport to="body">
      <div
        v-if="pendingDeleteSession"
        class="fixed inset-0 z-50 grid place-items-center bg-[#17201a]/45 px-4 backdrop-blur-sm"
        @click.self="cancelDeleteSession"
      >
        <section class="w-full max-w-md border border-[#d9d0bd] bg-white shadow-2xl">
          <div class="flex items-start justify-between gap-4 border-b border-[#eadfca] p-5">
            <div class="flex gap-3">
              <span class="grid h-10 w-10 shrink-0 place-items-center rounded bg-[#f7dfd6] text-[#b4442a]">
                <AlertTriangle :size="20" />
              </span>
              <div>
                <h2 class="text-lg font-semibold">删除这个会话？</h2>
                <p class="mt-1 text-sm leading-6 text-[#5e675b]">
                  删除后，会话和其中的聊天记录都会被移除，无法在页面中恢复。
                </p>
              </div>
            </div>
            <button
              class="grid h-8 w-8 place-items-center rounded text-[#5e675b] hover:bg-[#f4f0e7]"
              type="button"
              @click="cancelDeleteSession"
            >
              <X :size="18" />
            </button>
          </div>

          <div class="grid gap-2 p-5">
            <p class="text-sm text-[#5e675b]">即将删除</p>
            <p class="rounded border border-[#eadfca] bg-[#f8f5ed] px-3 py-3 font-semibold">
              {{ pendingDeleteSession.title }}
            </p>
          </div>

          <div class="flex justify-end gap-3 border-t border-[#eadfca] p-5">
            <button
              class="h-10 rounded border border-[#cfc4ae] bg-white px-4 text-sm font-semibold text-[#465144] hover:bg-[#f8f5ed]"
              :disabled="isDeleting"
              type="button"
              @click="cancelDeleteSession"
            >
              取消
            </button>
            <button
              class="inline-flex h-10 items-center justify-center gap-2 rounded bg-[#b4442a] px-4 text-sm font-semibold text-white disabled:opacity-60"
              :disabled="isDeleting"
              type="button"
              @click="confirmDeleteSession"
            >
              <LoaderCircle v-if="isDeleting" class="animate-spin" :size="16" />
              <Trash2 v-else :size="16" />
              确认删除
            </button>
          </div>
        </section>
      </div>
    </Teleport>
  </main>
</template>
