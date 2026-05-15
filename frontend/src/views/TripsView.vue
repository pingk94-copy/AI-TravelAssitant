<script setup lang="ts">
import { AlertTriangle, CalendarDays, LoaderCircle, MapPinned, Sparkles, Trash2, X } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'

import { getTask } from '../api/tasks'
import { type TripResponse, deleteTrip, listTrips, planTripAsync } from '../api/trips'
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
const activeTrip = ref<TripResponse | null>(null)
const pendingDeleteTrip = ref<TripResponse | null>(null)
const isPlanning = ref(false)
const isDeleting = ref(false)
const errorMessage = ref('')
const taskStatus = ref('')

const canSubmit = computed(() => {
  return Boolean(form.value.origin.trim() && form.value.destination.trim() && form.value.start_date && !isPlanning.value)
})

async function refreshTrips() {
  if (!appStore.token) return
  trips.value = await listTrips(appStore.token)
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

async function submitPlan() {
  if (!appStore.token) {
    errorMessage.value = '请先登录，再提交行程规划。'
    return
  }
  if (!canSubmit.value) {
    errorMessage.value = '请至少填写出发地、目的地和出发日期。'
    return
  }

  isPlanning.value = true
  errorMessage.value = ''
  taskStatus.value = '正在提交行程规划任务...'

  try {
    const task = await planTripAsync(appStore.token, {
      origin: form.value.origin.trim(),
      destination: form.value.destination.trim(),
      start_date: form.value.start_date,
      days: Number(form.value.days),
      budget: form.value.budget.trim() || undefined,
      preferences: preferencesList(),
    })
    taskStatus.value = `任务 #${task.task_id} 已提交，正在获取规划结果...`
    const taskResult = await getTask(appStore.token, task.task_id)
    const trip = taskResult.output?.trip
    if (!trip) {
      throw new Error(taskResult.error_message ?? '行程规划任务没有返回可展示的结果。')
    }
    activeTrip.value = trip
    trips.value = [trip, ...trips.value.filter((item) => item.id !== trip.id)]
    taskStatus.value = `任务 #${task.task_id} 已完成。`
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '行程规划失败，请稍后重试。'
  } finally {
    isPlanning.value = false
  }
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

onMounted(() => {
  refreshTrips().catch((error) => {
    errorMessage.value = error instanceof Error ? error.message : '历史行程加载失败，请刷新页面重试。'
  })
})
</script>

<template>
  <main class="mx-auto grid max-w-7xl gap-5 px-5 py-8 lg:grid-cols-[380px_1fr]">
    <aside class="grid gap-5">
      <section class="border border-[#d9d0bd] bg-[#f8f5ed] p-6">
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

        <p v-if="errorMessage" class="mt-4 text-sm text-[#b4442a]">{{ errorMessage }}</p>
        <p v-if="taskStatus" class="mt-3 text-sm text-[#5e675b]">{{ taskStatus }}</p>
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
    </aside>

    <section class="border border-[#d9d0bd] bg-white">
      <div class="border-b border-[#d9d0bd] p-6">
        <h2 class="text-xl font-semibold">{{ activeTrip?.title ?? '暂无行程' }}</h2>
        <p v-if="activeTrip" class="mt-1 flex items-center gap-2 text-sm text-[#5e675b]">
          <CalendarDays :size="16" />
          {{ activeTrip.start_date }} · {{ activeTrip.days }} 天 · {{ activeTrip.status }}
        </p>
      </div>

      <div v-if="!activeTrip" class="flex min-h-[520px] items-center justify-center p-8 text-center text-[#5e675b]">
        填写真实出发地、目的地和日期后，这里会展示按天拆分的结构化行程。
      </div>

      <div v-else class="grid gap-6 p-6">
        <p class="rounded border border-[#d9d0bd] bg-[#f8f5ed] p-4 text-sm leading-7 text-[#465144]">
          {{ activeTrip.result.summary }}
        </p>

        <article v-for="day in activeTrip.result.days" :key="day.day" class="border border-[#d9d0bd] p-5">
          <h3 class="text-lg font-semibold">第 {{ day.day }} 天 · {{ day.theme }}</h3>
          <div class="mt-4 grid gap-3">
            <div
              v-for="item in day.schedule"
              :key="`${day.day}-${item.time}-${item.title}`"
              class="grid gap-1 rounded bg-[#fbfaf6] p-3"
            >
              <p class="text-sm font-semibold text-[#c75532]">{{ item.time }} · {{ item.title }}</p>
              <p class="text-sm leading-7 text-[#465144]">{{ item.description }}</p>
            </div>
          </div>
        </article>

        <section v-if="activeTrip.result.route_tips.length" class="grid gap-2">
          <h3 class="font-semibold">路线建议</h3>
          <ul class="grid gap-2 pl-5 text-sm leading-7 text-[#5e675b]">
            <li v-for="tip in activeTrip.result.route_tips" :key="tip" class="list-disc">
              {{ tip }}
            </li>
          </ul>
        </section>

        <section v-if="activeTrip.result.tips.length" class="grid gap-2">
          <h3 class="font-semibold">出行提醒</h3>
          <ul class="grid gap-2 pl-5 text-sm leading-7 text-[#5e675b]">
            <li v-for="tip in activeTrip.result.tips" :key="tip" class="list-disc">
              {{ tip }}
            </li>
          </ul>
        </section>
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
