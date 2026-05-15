<script setup lang="ts">
import { CalendarDays, CloudSun, Hotel, MapPinned, MessageSquareText, Route } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'

const capabilityCards = [
  { title: '天气辅助规划', text: '先查询目的地天气，再安排户外景点、室内备选和每日节奏。', icon: CloudSun },
  { title: '景点与路线检索', text: '通过地图工具收集景点、周边区域和路线锚点，为 Agent 规划提供依据。', icon: MapPinned },
  { title: '住宿区域建议', text: '在接入真实酒店预订前，先给出适合落脚的商圈和通勤策略。', icon: Hotel },
]
</script>

<template>
  <main class="mx-auto grid max-w-7xl gap-8 px-5 py-8 lg:grid-cols-[1.05fr_0.95fr]">
    <section class="flex min-h-[520px] flex-col justify-between bg-[#1d3b2a] p-8 text-white">
      <div class="max-w-2xl">
        <p class="mb-5 inline-flex items-center gap-2 rounded bg-white/10 px-3 py-1 text-sm text-[#d9ead5]">
          <CalendarDays :size="16" />
          可交互演示版
        </p>
        <h1 class="max-w-3xl text-4xl font-semibold leading-tight md:text-6xl">
          用 AI Agent 把旅行想法拆成可执行的行程方案。
        </h1>
      </div>

      <div class="mt-10 grid gap-3 rounded bg-[#f8f5ed] p-3 text-[#17201a] sm:grid-cols-2">
        <RouterLink class="home-action bg-[#c75532] text-white" to="/trips">
          <Route :size="18" />
          开始规划行程
        </RouterLink>
        <RouterLink class="home-action border border-[#d9d0bd] bg-white text-[#1d3b2a]" to="/chat">
          <MessageSquareText :size="18" />
          进入 AI 对话
        </RouterLink>
      </div>
    </section>

    <section class="grid content-start gap-4">
      <article
        v-for="card in capabilityCards"
        :key="card.title"
        class="border border-[#d9d0bd] bg-[#f8f5ed] p-6"
      >
        <component :is="card.icon" class="mb-5 text-[#c75532]" :size="26" />
        <h2 class="mb-2 text-xl font-semibold">{{ card.title }}</h2>
        <p class="text-sm leading-6 text-[#5e675b]">{{ card.text }}</p>
      </article>
    </section>
  </main>
</template>

<style scoped>
.home-action {
  display: inline-flex;
  min-height: 3rem;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border-radius: 6px;
  padding: 0 1rem;
  font-weight: 700;
  text-decoration: none;
}
</style>
