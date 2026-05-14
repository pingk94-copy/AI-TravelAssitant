<script setup lang="ts">
import { CalendarDays, LoaderCircle, MapPinned, Sparkles } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'

import { type TripResponse, listTrips, planTrip } from '../api/trips'
import { useAppStore } from '../stores/app'

const appStore = useAppStore()
const form = ref({
  origin: 'Shanghai',
  destination: 'Hangzhou',
  start_date: '2026-06-01',
  days: 2,
  budget: '3000',
  preferences: 'food, relaxed, scenic',
})
const trips = ref<TripResponse[]>([])
const activeTrip = ref<TripResponse | null>(null)
const isPlanning = ref(false)
const errorMessage = ref('')

async function refreshTrips() {
  if (!appStore.token) return
  trips.value = await listTrips(appStore.token)
  activeTrip.value = activeTrip.value ?? trips.value[0] ?? null
}

async function submitPlan() {
  if (!appStore.token) {
    errorMessage.value = 'Set a token in the store after logging in before planning trips.'
    return
  }

  isPlanning.value = true
  errorMessage.value = ''

  try {
    const trip = await planTrip(appStore.token, {
      origin: form.value.origin,
      destination: form.value.destination,
      start_date: form.value.start_date,
      days: Number(form.value.days),
      budget: form.value.budget,
      preferences: form.value.preferences
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean),
    })
    activeTrip.value = trip
    trips.value = [trip, ...trips.value.filter((item) => item.id !== trip.id)]
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Failed to plan trip.'
  } finally {
    isPlanning.value = false
  }
}

onMounted(() => {
  refreshTrips().catch((error) => {
    errorMessage.value = error instanceof Error ? error.message : 'Failed to load trips.'
  })
})
</script>

<template>
  <main class="mx-auto grid max-w-7xl gap-5 px-5 py-8 lg:grid-cols-[360px_1fr]">
    <section class="border border-[#d9d0bd] bg-[#f8f5ed] p-6">
      <div class="mb-6 flex items-center gap-3">
        <span class="grid h-10 w-10 place-items-center rounded bg-[#1d3b2a] text-white">
          <MapPinned :size="20" />
        </span>
        <div>
          <h1 class="text-2xl font-semibold">Trip Planner</h1>
          <p class="text-sm text-[#5e675b]">MVP structured itinerary</p>
        </div>
      </div>

      <form class="grid gap-4" @submit.prevent="submitPlan">
        <label class="grid gap-2 text-sm font-medium">
          Origin
          <input v-model="form.origin" class="form-input" type="text" />
        </label>
        <label class="grid gap-2 text-sm font-medium">
          Destination
          <input v-model="form.destination" class="form-input" type="text" />
        </label>
        <label class="grid gap-2 text-sm font-medium">
          Start date
          <input v-model="form.start_date" class="form-input" type="date" />
        </label>
        <label class="grid gap-2 text-sm font-medium">
          Days
          <input v-model="form.days" class="form-input" max="5" min="1" type="number" />
        </label>
        <label class="grid gap-2 text-sm font-medium">
          Budget
          <input v-model="form.budget" class="form-input" type="text" />
        </label>
        <label class="grid gap-2 text-sm font-medium">
          Preferences
          <input v-model="form.preferences" class="form-input" type="text" />
        </label>

        <button
          class="mt-2 inline-flex h-12 items-center justify-center gap-2 rounded bg-[#c75532] px-5 font-semibold text-white disabled:opacity-60"
          :disabled="isPlanning"
          type="submit"
        >
          <LoaderCircle v-if="isPlanning" class="animate-spin" :size="18" />
          <Sparkles v-else :size="18" />
          Generate itinerary
        </button>
      </form>

      <p v-if="errorMessage" class="mt-4 text-sm text-[#b4442a]">{{ errorMessage }}</p>
    </section>

    <section class="border border-[#d9d0bd] bg-white">
      <div class="border-b border-[#d9d0bd] p-6">
        <h2 class="text-xl font-semibold">{{ activeTrip?.title ?? 'No itinerary yet' }}</h2>
        <p v-if="activeTrip" class="mt-1 flex items-center gap-2 text-sm text-[#5e675b]">
          <CalendarDays :size="16" />
          {{ activeTrip.start_date }} · {{ activeTrip.days }} days · {{ activeTrip.status }}
        </p>
      </div>

      <div v-if="!activeTrip" class="flex min-h-[520px] items-center justify-center p-8 text-center text-[#5e675b]">
        Generate your first itinerary to see structured daily plans here.
      </div>

      <div v-else class="grid gap-6 p-6">
        <p class="rounded border border-[#d9d0bd] bg-[#f8f5ed] p-4 text-sm leading-6 text-[#465144]">
          {{ activeTrip.result.summary }}
        </p>

        <article
          v-for="day in activeTrip.result.days"
          :key="day.day"
          class="border border-[#d9d0bd] p-5"
        >
          <h3 class="text-lg font-semibold">Day {{ day.day }} · {{ day.theme }}</h3>
          <div class="mt-4 grid gap-3">
            <div v-for="item in day.schedule" :key="`${day.day}-${item.time}-${item.title}`" class="grid gap-1">
              <p class="text-sm font-semibold text-[#c75532]">{{ item.time }} · {{ item.title }}</p>
              <p class="text-sm leading-6 text-[#5e675b]">{{ item.description }}</p>
            </div>
          </div>
        </article>

        <section class="grid gap-2">
          <h3 class="font-semibold">Route tips</h3>
          <p v-for="tip in activeTrip.result.route_tips" :key="tip" class="text-sm leading-6 text-[#5e675b]">
            {{ tip }}
          </p>
        </section>

        <section class="grid gap-2">
          <h3 class="font-semibold">Notes</h3>
          <p v-for="tip in activeTrip.result.tips" :key="tip" class="text-sm leading-6 text-[#5e675b]">
            {{ tip }}
          </p>
        </section>
      </div>
    </section>
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
