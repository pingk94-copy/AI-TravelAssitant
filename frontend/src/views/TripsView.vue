<script setup lang="ts">
import {
  AlertTriangle,
  CalendarDays,
  CloudSun,
  LoaderCircle,
  MapPinned,
  RefreshCw,
  Sparkles,
  Star,
  Trash2,
  WalletCards,
  X,
} from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'

import { getTask } from '../api/tasks'
import {
  type TripFavoriteResponse,
  type TripResponse,
  deleteTrip,
  favoriteTrip,
  listFavoriteTrips,
  listTrips,
  planTripAsync,
  unfavoriteTrip,
} from '../api/trips'
import { useAppStore } from '../stores/app'

const appStore = useAppStore()
const form = ref({
  origin: '',
  destination: '',
  start_date: '',
  days: 2,
  budget: '',
  preferences: '',
})
const trips = ref<TripResponse[]>([])
const favoriteTrips = ref<TripFavoriteResponse[]>([])
const activeTrip = ref<TripResponse | null>(null)
const pendingDeleteTrip = ref<TripResponse | null>(null)
const isPlanning = ref(false)
const isDeleting = ref(false)
const favoriteBusyId = ref<number | null>(null)
const errorMessage = ref('')
const taskStatus = ref('')
const lastPayload = ref<{
  origin: string
  destination: string
  start_date: string
  days: number
  budget?: string
  preferences: string[]
} | null>(null)

const canSubmit = computed(() => {
  return Boolean(form.value.origin.trim() && form.value.destination.trim() && form.value.start_date && !isPlanning.value)
})
const favoriteTripIds = computed(() => new Set(favoriteTrips.value.map((favorite) => favorite.target_id)))
const activeTripFavorited = computed(() => Boolean(activeTrip.value && favoriteTripIds.value.has(activeTrip.value.id)))

async function refreshTrips() {
  if (!appStore.token) return
  const [tripItems, favoriteItems] = await Promise.all([listTrips(appStore.token), listFavoriteTrips(appStore.token)])
  trips.value = tripItems
  favoriteTrips.value = favoriteItems
  activeTrip.value = activeTrip.value ?? trips.value[0] ?? null
}

function selectTrip(trip: TripResponse) {
  activeTrip.value = trip
  errorMessage.value = ''
  taskStatus.value = ''
}

function preferencesList() {
  return form.value.preferences
    .split(/[,，、\s]+/)
    .map((item) => item.trim())
    .filter(Boolean)
}

async function submitPlan(useLastPayload = false) {
  if (!appStore.token) {
    errorMessage.value = '请先登录，再提交行程规划。'
    return
  }
  if (!useLastPayload && !canSubmit.value) {
    errorMessage.value = '请至少填写出发地、目的地和出发日期。'
    return
  }
  const payload = useLastPayload && lastPayload.value
    ? lastPayload.value
    : {
        origin: form.value.origin.trim(),
        destination: form.value.destination.trim(),
        start_date: form.value.start_date,
        days: Number(form.value.days),
        budget: form.value.budget.trim() || undefined,
        preferences: preferencesList(),
      }
  lastPayload.value = payload

  isPlanning.value = true
  errorMessage.value = ''
  taskStatus.value = '正在整理城市、天气、路线和偏好信息...'

  try {
    const task = await planTripAsync(appStore.token, payload)
    taskStatus.value = `任务 #${task.task_id} 已提交，正在生成可执行行程...`
    const taskResult = await getTask(appStore.token, task.task_id)
    const trip = taskResult.output?.trip
    if (!trip) {
      throw new Error(taskResult.error_message ?? '行程规划任务没有返回可展示的结果。')
    }
    activeTrip.value = trip
    trips.value = [trip, ...trips.value.filter((item) => item.id !== trip.id)]
    taskStatus.value = `任务 #${task.task_id} 已完成，已保存到历史行程。`
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '行程规划失败，请稍后重试。'
  } finally {
    isPlanning.value = false
  }
}

async function toggleFavoriteTrip(trip: TripResponse) {
  if (!appStore.token || favoriteBusyId.value === trip.id) return
  favoriteBusyId.value = trip.id
  errorMessage.value = ''

  try {
    if (favoriteTripIds.value.has(trip.id)) {
      await unfavoriteTrip(appStore.token, trip.id)
      favoriteTrips.value = favoriteTrips.value.filter((favorite) => favorite.target_id !== trip.id)
    } else {
      const favorite = await favoriteTrip(appStore.token, trip.id)
      favoriteTrips.value = [favorite, ...favoriteTrips.value.filter((item) => item.target_id !== trip.id)]
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '收藏操作失败，请稍后重试。'
  } finally {
    favoriteBusyId.value = null
  }
}

function retryLastPlan() {
  if (!lastPayload.value || isPlanning.value) return
  submitPlan(true)
}

function requestDeleteTrip(trip: TripResponse) {
  pendingDeleteTrip.value = trip
}

function cancelDeleteTrip() {
  if (isDeleting.value) return
  pendingDeleteTrip.value = null
}

async function confirmDeleteTrip() {
  if (!appStore.token || !pendingDeleteTrip.value) return
  const trip = pendingDeleteTrip.value
  isDeleting.value = true
  errorMessage.value = ''

  try {
    await deleteTrip(appStore.token, trip.id)
    trips.value = trips.value.filter((item) => item.id !== trip.id)
    favoriteTrips.value = favoriteTrips.value.filter((favorite) => favorite.target_id !== trip.id)
    if (activeTrip.value?.id === trip.id) {
      activeTrip.value = trips.value[0] ?? null
    }
    pendingDeleteTrip.value = null
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '删除行程失败，请稍后重试。'
  } finally {
    isDeleting.value = false
  }
}

function formatCreatedAt(value: string) {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function statusLabel(status: string) {
  return status === 'success' ? '已生成' : status
}

onMounted(() => {
  refreshTrips().catch((error) => {
    errorMessage.value = error instanceof Error ? error.message : '历史行程加载失败，请刷新页面重试。'
  })
})
</script>

<template>
  <main class="mx-auto grid max-w-7xl gap-5 px-4 py-5 md:px-5 md:py-8 lg:h-[calc(100vh-73px)] lg:grid-cols-[380px_1fr] lg:py-6">
    <aside class="grid min-h-0 gap-5 overflow-y-auto pr-0 lg:pr-1">
      <section class="border border-[#d9d0bd] bg-[#f8f5ed] p-5 md:p-6">
        <div class="mb-6 flex items-center gap-3">
          <span class="grid h-10 w-10 place-items-center rounded bg-[#1d3b2a] text-white">
            <MapPinned :size="20" />
          </span>
          <div>
            <h1 class="text-2xl font-semibold">行程规划</h1>
            <p class="text-sm text-[#5e675b]">调用大模型生成结构化行程，失败时使用本地兜底。</p>
          </div>
        </div>

        <form class="grid gap-4" @submit.prevent="submitPlan">
          <label class="grid gap-2 text-sm font-medium">
            出发地
            <input v-model="form.origin" class="form-input" placeholder="例如：上海" type="text" />
          </label>
          <label class="grid gap-2 text-sm font-medium">
            目的地
            <input v-model="form.destination" class="form-input" placeholder="例如：西安" type="text" />
          </label>
          <label class="grid gap-2 text-sm font-medium">
            出发日期
            <input v-model="form.start_date" class="form-input" type="date" />
          </label>
          <label class="grid gap-2 text-sm font-medium">
            游玩天数
            <input v-model="form.days" class="form-input" max="5" min="1" type="number" />
          </label>
          <label class="grid gap-2 text-sm font-medium">
            预算
            <input v-model="form.budget" class="form-input" placeholder="例如：3000 元/人" type="text" />
          </label>
          <label class="grid gap-2 text-sm font-medium">
            偏好
            <input v-model="form.preferences" class="form-input" placeholder="例如：历史、美食、慢节奏" type="text" />
          </label>

          <button
            class="mt-2 inline-flex h-12 items-center justify-center gap-2 rounded bg-[#c75532] px-5 font-semibold text-white disabled:opacity-60"
            :disabled="!canSubmit"
            type="submit"
          >
            <LoaderCircle v-if="isPlanning" class="animate-spin" :size="18" />
            <Sparkles v-else :size="18" />
            生成行程
          </button>
        </form>

        <div v-if="errorMessage" class="mt-4 rounded border border-[#edc7b8] bg-[#fff4ef] p-3 text-sm leading-6 text-[#9d3d20]">
          <p class="font-semibold">生成失败</p>
          <p>{{ errorMessage }}</p>
          <button
            v-if="lastPayload"
            class="mt-3 inline-flex h-9 items-center justify-center gap-2 rounded border border-[#d9a08a] bg-white px-3 text-xs font-semibold"
            type="button"
            @click="retryLastPlan"
          >
            <RefreshCw :size="14" />
            重新生成
          </button>
        </div>
        <div v-if="taskStatus" class="mt-4 rounded border border-[#d9d0bd] bg-white p-3 text-sm leading-6 text-[#5e675b]">
          <div class="flex items-center gap-2">
            <LoaderCircle v-if="isPlanning" class="animate-spin text-[#c75532]" :size="16" />
            <Sparkles v-else class="text-[#c75532]" :size="16" />
            <span>{{ taskStatus }}</span>
          </div>
        </div>
      </section>

      <section class="border border-[#d9d0bd] bg-white p-5">
        <div class="mb-4 flex items-center justify-between gap-3">
          <h2 class="font-semibold">历史行程</h2>
          <span class="text-xs text-[#5e675b]">{{ trips.length }} 条</span>
        </div>
        <div v-if="trips.length === 0" class="rounded border border-dashed border-[#d9d0bd] p-4 text-sm leading-6 text-[#5e675b]">
          还没有历史行程。生成后会自动保存到这里。
        </div>
        <div v-else class="grid max-h-[420px] gap-2 overflow-y-auto pr-1">
          <div
            v-for="trip in trips"
            :key="trip.id"
            class="grid grid-cols-[1fr_auto] items-start gap-2 rounded border px-3 py-3 text-sm transition"
            :class="
              activeTrip?.id === trip.id
                ? 'border-[#1d3b2a] bg-[#e7dfcf] text-[#17201a]'
                : 'border-[#d9d0bd] bg-white text-[#5e675b] hover:border-[#b9ad96] hover:bg-[#fbfaf6]'
            "
          >
            <button class="grid min-w-0 gap-1 text-left" type="button" @click="selectTrip(trip)">
              <span class="truncate font-semibold">{{ trip.title }}</span>
              <span class="truncate text-xs">{{ trip.origin }} → {{ trip.destination }} · {{ trip.days }} 天</span>
              <span class="text-xs text-[#7a8175]">{{ trip.start_date }} 出发 · {{ formatCreatedAt(trip.created_at) }} 保存</span>
            </button>
            <button
              class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded text-[#8b4a36] hover:bg-[#f8f5ed]"
              title="删除行程"
              type="button"
              @click="requestDeleteTrip(trip)"
            >
              <Trash2 :size="15" />
            </button>
          </div>
        </div>
      </section>

      <section class="border border-[#d9d0bd] bg-white p-5">
        <div class="mb-4 flex items-center justify-between gap-3">
          <h2 class="font-semibold">收藏行程</h2>
          <span class="text-xs text-[#5e675b]">{{ favoriteTrips.length }} 条</span>
        </div>
        <div v-if="favoriteTrips.length === 0" class="rounded border border-dashed border-[#d9d0bd] p-4 text-sm leading-6 text-[#5e675b]">
          还没有收藏。打开行程后点击星标，就能把常用方案留在这里。
        </div>
        <div v-else class="grid max-h-[260px] gap-2 overflow-y-auto pr-1">
          <button
            v-for="favorite in favoriteTrips"
            :key="favorite.id"
            class="grid gap-1 rounded border border-[#d9d0bd] bg-[#fbfaf6] px-3 py-3 text-left text-sm text-[#5e675b] hover:border-[#1d3b2a]"
            type="button"
            @click="selectTrip(favorite.trip)"
          >
            <span class="truncate font-semibold text-[#17201a]">{{ favorite.trip.title }}</span>
            <span class="truncate text-xs">{{ favorite.trip.origin }} → {{ favorite.trip.destination }} · {{ favorite.trip.days }} 天</span>
          </button>
        </div>
      </section>
    </aside>

    <section class="flex min-h-[620px] flex-col border border-[#d9d0bd] bg-white lg:min-h-0">
      <div class="shrink-0 flex flex-wrap items-start justify-between gap-4 border-b border-[#d9d0bd] p-6">
        <div>
          <h2 class="text-xl font-semibold">{{ activeTrip?.title ?? '暂无行程' }}</h2>
          <p v-if="activeTrip" class="mt-1 flex items-center gap-2 text-sm text-[#5e675b]">
            <CalendarDays :size="16" />
            {{ activeTrip.start_date }} · {{ activeTrip.days }} 天 · {{ statusLabel(activeTrip.status) }}
          </p>
        </div>
        <button
          v-if="activeTrip"
          class="inline-flex h-10 items-center justify-center gap-2 rounded border px-4 text-sm font-semibold"
          :class="
            activeTripFavorited
              ? 'border-[#c75532] bg-[#fff4ef] text-[#b4442a]'
              : 'border-[#cfc4ae] bg-white text-[#465144] hover:bg-[#f8f5ed]'
          "
          :disabled="favoriteBusyId === activeTrip.id"
          type="button"
          @click="toggleFavoriteTrip(activeTrip)"
        >
          <LoaderCircle v-if="favoriteBusyId === activeTrip.id" class="animate-spin" :size="16" />
          <Star v-else :size="16" />
          {{ activeTripFavorited ? '已收藏' : '收藏行程' }}
        </button>
      </div>

      <div v-if="isPlanning" class="grid min-h-[460px] flex-1 place-items-center overflow-y-auto p-6 text-center md:min-h-[520px] md:p-8 lg:min-h-0">
        <div class="max-w-md">
          <span class="mx-auto grid h-14 w-14 place-items-center rounded bg-[#f7dfd6] text-[#c75532]">
            <LoaderCircle class="animate-spin" :size="28" />
          </span>
          <h3 class="mt-5 text-xl font-semibold">正在生成行程</h3>
          <p class="mt-3 text-sm leading-7 text-[#5e675b]">
            正在结合出发城市、目的地、天气、路线和你的偏好生成结构化安排。完成后会自动展示并保存到历史行程。
          </p>
          <div class="mt-5 grid gap-2 text-left text-sm text-[#5e675b]">
            <p class="rounded border border-[#d9d0bd] bg-[#f8f5ed] px-3 py-2">1. 收集路线和天气上下文</p>
            <p class="rounded border border-[#d9d0bd] bg-[#f8f5ed] px-3 py-2">2. 生成每日时间表和路线建议</p>
            <p class="rounded border border-[#d9d0bd] bg-[#f8f5ed] px-3 py-2">3. 保存到你的历史行程</p>
          </div>
        </div>
      </div>

      <div v-else-if="!activeTrip" class="grid min-h-[460px] flex-1 place-items-center overflow-y-auto p-6 text-center text-[#5e675b] md:min-h-[520px] md:p-8 lg:min-h-0">
        <div class="max-w-md">
          <span class="mx-auto grid h-14 w-14 place-items-center rounded bg-[#e7dfcf] text-[#1d3b2a]">
            <MapPinned :size="26" />
          </span>
          <h3 class="mt-5 text-xl font-semibold text-[#17201a]">从一份真实需求开始</h3>
          <p class="mt-3 text-sm leading-7">
            填写出发地、目的地和日期后，这里会展示按天拆分的行程、路线建议、天气参考和出行提醒。
          </p>
        </div>
      </div>

      <div v-else class="grid min-h-0 flex-1 gap-6 overflow-y-auto p-5 md:p-6">
        <div class="grid gap-4 rounded border border-[#d9d0bd] bg-[#f8f5ed] p-5">
          <p class="text-sm leading-7 text-[#465144]">{{ activeTrip.result.summary }}</p>
          <div class="grid gap-3 text-sm md:grid-cols-3">
            <div class="rounded border border-[#eadfca] bg-white p-3">
              <p class="text-xs text-[#7a8175]">路线</p>
              <p class="mt-1 font-semibold">{{ activeTrip.origin }} → {{ activeTrip.destination }}</p>
            </div>
            <div class="rounded border border-[#eadfca] bg-white p-3">
              <p class="text-xs text-[#7a8175]">预算</p>
              <p class="mt-1 font-semibold">{{ activeTrip.budget || '未填写' }}</p>
            </div>
            <div class="rounded border border-[#eadfca] bg-white p-3">
              <p class="text-xs text-[#7a8175]">偏好</p>
              <p class="mt-1 truncate font-semibold">
                {{ activeTrip.preferences.length ? activeTrip.preferences.join('、') : '经典景点、在地体验' }}
              </p>
            </div>
          </div>
        </div>

        <section v-if="activeTrip.result.weather.length" class="grid gap-3">
          <h3 class="flex items-center gap-2 font-semibold">
            <CloudSun :size="18" />
            天气参考
          </h3>
          <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            <div
              v-for="(weather, index) in activeTrip.result.weather.slice(0, activeTrip.days)"
              :key="`${weather.date ?? index}-${weather.weather ?? ''}`"
              class="rounded border border-[#d9d0bd] bg-[#fbfaf6] p-3 text-sm"
            >
              <p class="font-semibold">{{ weather.date ?? `第 ${index + 1} 天` }}</p>
              <p class="mt-1 text-[#5e675b]">
                {{ weather.weather ?? '天气待确认' }} · {{ weather.temperature ?? '温度待确认' }}
              </p>
            </div>
          </div>
        </section>

        <article v-for="day in activeTrip.result.days" :key="day.day" class="border border-[#d9d0bd] p-5">
          <h3 class="text-lg font-semibold">第 {{ day.day }} 天 · {{ day.theme }}</h3>
          <div class="mt-4 grid gap-3">
            <div
              v-for="item in day.schedule"
              :key="`${day.day}-${item.time}-${item.title}`"
              class="grid gap-1 rounded border border-[#eadfca] bg-[#fbfaf6] p-3"
            >
              <p class="text-sm font-semibold text-[#c75532]">{{ item.time }} · {{ item.title }}</p>
              <p class="text-sm leading-7 text-[#465144]">{{ item.description }}</p>
            </div>
          </div>
        </article>

        <div class="grid gap-4 lg:grid-cols-2">
          <section v-if="activeTrip.result.route_tips.length" class="grid gap-2 rounded border border-[#d9d0bd] p-5">
            <h3 class="flex items-center gap-2 font-semibold">
              <MapPinned :size="18" />
              路线建议
            </h3>
            <ul class="grid gap-2 pl-5 text-sm leading-7 text-[#5e675b]">
              <li v-for="tip in activeTrip.result.route_tips" :key="tip" class="list-disc">
                {{ tip }}
              </li>
            </ul>
          </section>

          <section v-if="activeTrip.result.tips.length" class="grid gap-2 rounded border border-[#d9d0bd] p-5">
            <h3 class="flex items-center gap-2 font-semibold">
              <WalletCards :size="18" />
              出行提醒
            </h3>
            <ul class="grid gap-2 pl-5 text-sm leading-7 text-[#5e675b]">
              <li v-for="tip in activeTrip.result.tips" :key="tip" class="list-disc">
                {{ tip }}
              </li>
            </ul>
          </section>
        </div>
      </div>
    </section>

    <Teleport to="body">
      <div
        v-if="pendingDeleteTrip"
        class="fixed inset-0 z-50 grid place-items-center bg-[#17201a]/45 px-4 backdrop-blur-sm"
        @click.self="cancelDeleteTrip"
      >
        <section class="w-full max-w-md border border-[#d9d0bd] bg-white shadow-2xl">
          <div class="flex items-start justify-between gap-4 border-b border-[#eadfca] p-5">
            <div class="flex gap-3">
              <span class="grid h-10 w-10 shrink-0 place-items-center rounded bg-[#f7dfd6] text-[#b4442a]">
                <AlertTriangle :size="20" />
              </span>
              <div>
                <h2 class="text-lg font-semibold">删除这个行程？</h2>
                <p class="mt-1 text-sm leading-6 text-[#5e675b]">
                  删除后，这份行程规划会从历史列表移除，页面中无法恢复。
                </p>
              </div>
            </div>
            <button
              class="grid h-8 w-8 place-items-center rounded text-[#5e675b] hover:bg-[#f4f0e7]"
              type="button"
              @click="cancelDeleteTrip"
            >
              <X :size="18" />
            </button>
          </div>

          <div class="grid gap-2 p-5">
            <p class="text-sm text-[#5e675b]">即将删除</p>
            <p class="rounded border border-[#eadfca] bg-[#f8f5ed] px-3 py-3 font-semibold">
              {{ pendingDeleteTrip.title }}
            </p>
          </div>

          <div class="flex justify-end gap-3 border-t border-[#eadfca] p-5">
            <button
              class="h-10 rounded border border-[#cfc4ae] bg-white px-4 text-sm font-semibold text-[#465144] hover:bg-[#f8f5ed]"
              :disabled="isDeleting"
              type="button"
              @click="cancelDeleteTrip"
            >
              取消
            </button>
            <button
              class="inline-flex h-10 items-center justify-center gap-2 rounded bg-[#b4442a] px-4 text-sm font-semibold text-white disabled:opacity-60"
              :disabled="isDeleting"
              type="button"
              @click="confirmDeleteTrip"
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

<style scoped>
.form-input {
  height: 2.75rem;
  border: 1px solid #d9d0bd;
  border-radius: 6px;
  background: #fff;
  padding: 0 0.75rem;
  outline: none;
}

.form-input:focus {
  border-color: #1d3b2a;
}
</style>
