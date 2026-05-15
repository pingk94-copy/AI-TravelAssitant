<script setup lang="ts">
import {
  CalendarDays,
  CheckCircle2,
  CloudSun,
  Hotel,
  MapPinned,
  MessageSquareText,
  Route,
  Sparkles,
} from 'lucide-vue-next'
import { RouterLink } from 'vue-router'

const capabilityCards = [
  { title: '天气辅助规划', text: '根据目的地天气安排户外景点、室内备选和每日节奏。', icon: CloudSun },
  { title: '路线与景点检索', text: '结合景点、区域和交通锚点，生成更顺路的游玩顺序。', icon: MapPinned },
  { title: '住宿区域建议', text: '先判断适合落脚的商圈，再安排通勤和返程策略。', icon: Hotel },
]

const previewDays = [
  { time: '09:30', title: '抵达核心景区', text: '优先安排步行距离短、排队压力低的入口。' },
  { time: '13:00', title: '午餐与短休', text: '选择靠近下午路线的餐饮区域，减少折返。' },
  { time: '16:30', title: '城市漫游', text: '把拍照点、咖啡店和夜景动线串联起来。' },
]
</script>

<template>
  <main class="mx-auto grid max-w-[112rem] gap-6 px-4 py-5 md:px-6 md:py-8">
    <section class="home-hero">
      <div class="hero-copy">
        <p class="hero-badge">
          <Sparkles :size="16" />
          AI 旅行规划助手
        </p>
        <h1>把一句旅行想法，整理成清晰可执行的行程。</h1>
        <p class="hero-lead">
          输入出发地、目的地、天数和偏好后，系统会生成按天拆分的路线、天气参考、住宿区域和出行提醒。
        </p>

        <div class="hero-actions">
          <RouterLink class="home-action primary" to="/trips">
            <Route :size="18" />
            开始规划行程
          </RouterLink>
          <RouterLink class="home-action secondary" to="/chat">
            <MessageSquareText :size="18" />
            进入 AI 对话
          </RouterLink>
        </div>

        <div class="hero-notes">
          <span>
            <CheckCircle2 :size="15" />
            自动保存历史行程
          </span>
          <span>
            <CheckCircle2 :size="15" />
            支持收藏常用方案
          </span>
        </div>
      </div>

      <div class="itinerary-preview" aria-label="行程预览">
        <div class="preview-header">
          <div>
            <p>杭州两日慢旅行</p>
            <span>周末 · 轻松节奏 · 美食优先</span>
          </div>
          <CalendarDays :size="22" />
        </div>

        <div class="preview-map">
          <span class="map-pin start">西湖</span>
          <span class="map-pin middle">南宋御街</span>
          <span class="map-pin end">河坊街</span>
        </div>

        <div class="preview-list">
          <div v-for="item in previewDays" :key="item.time" class="preview-item">
            <span>{{ item.time }}</span>
            <div>
              <p>{{ item.title }}</p>
              <small>{{ item.text }}</small>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="capability-grid" aria-label="核心能力">
      <article v-for="card in capabilityCards" :key="card.title" class="capability-card">
        <span class="capability-icon">
          <component :is="card.icon" :size="22" />
        </span>
        <div>
          <h2>{{ card.title }}</h2>
          <p>{{ card.text }}</p>
        </div>
      </article>
    </section>
  </main>
</template>

<style scoped>
.home-hero {
  display: grid;
  min-height: min(680px, calc(100vh - 145px));
  grid-template-columns: minmax(0, 1.02fr) minmax(420px, 0.98fr);
  gap: 1.5rem;
  align-items: stretch;
}

.hero-copy {
  display: flex;
  min-height: 520px;
  flex-direction: column;
  justify-content: center;
  border: 1px solid #d9d0bd;
  background: #fbfaf6;
  padding: clamp(2rem, 4vw, 4.25rem);
  box-shadow: 0 20px 60px rgb(29 59 42 / 0.08);
}

.hero-badge {
  display: inline-flex;
  width: fit-content;
  align-items: center;
  gap: 0.5rem;
  border: 1px solid #d7e3d3;
  border-radius: 999px;
  background: #eef5eb;
  color: #1d3b2a;
  font-size: 0.9rem;
  font-weight: 700;
  padding: 0.45rem 0.85rem;
}

.hero-copy h1 {
  max-width: 12em;
  margin: 1.5rem 0 0;
  color: #17201a;
  font-size: clamp(2.7rem, 4.8vw, 5.7rem);
  font-weight: 800;
  line-height: 1.08;
}

.hero-lead {
  max-width: 42rem;
  margin: 1.5rem 0 0;
  color: #465144;
  font-size: 1.05rem;
  line-height: 1.9;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  margin-top: 2.2rem;
}

.home-action {
  display: inline-flex;
  min-height: 3.2rem;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  border-radius: 8px;
  padding: 0 1.25rem;
  font-weight: 800;
  text-decoration: none;
  transition:
    transform 160ms ease,
    box-shadow 160ms ease,
    border-color 160ms ease;
}

.home-action:hover {
  transform: translateY(-1px);
}

.home-action.primary {
  background: #c75532;
  box-shadow: 0 12px 24px rgb(199 85 50 / 0.22);
  color: white;
}

.home-action.secondary {
  border: 1px solid #cfc4ae;
  background: white;
  color: #1d3b2a;
}

.hero-notes {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem 1.2rem;
  margin-top: 1.25rem;
  color: #5e675b;
  font-size: 0.9rem;
}

.hero-notes span {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.itinerary-preview {
  display: flex;
  min-height: 520px;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
  border: 1px solid #cfc4ae;
  background: #1d3b2a;
  color: white;
  padding: clamp(1.5rem, 3vw, 2.4rem);
  box-shadow: 0 20px 60px rgb(29 59 42 / 0.16);
}

.preview-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.preview-header p {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 800;
}

.preview-header span {
  display: block;
  margin-top: 0.35rem;
  color: #d9ead5;
  font-size: 0.9rem;
}

.preview-map {
  position: relative;
  min-height: 210px;
  margin: 2rem 0;
  border: 1px solid rgb(255 255 255 / 0.18);
  background:
    linear-gradient(90deg, rgb(255 255 255 / 0.08) 1px, transparent 1px),
    linear-gradient(rgb(255 255 255 / 0.08) 1px, transparent 1px),
    #244c36;
  background-size: 42px 42px;
}

.preview-map::before {
  position: absolute;
  inset: 28% 12% auto 16%;
  height: 2px;
  background: #f1b797;
  content: '';
  transform: rotate(14deg);
  transform-origin: left center;
}

.preview-map::after {
  position: absolute;
  inset: auto 16% 35% 34%;
  height: 2px;
  background: #f1b797;
  content: '';
  transform: rotate(-11deg);
  transform-origin: left center;
}

.map-pin {
  position: absolute;
  border-radius: 999px;
  background: white;
  color: #1d3b2a;
  font-size: 0.78rem;
  font-weight: 800;
  padding: 0.42rem 0.65rem;
  box-shadow: 0 10px 24px rgb(0 0 0 / 0.18);
  white-space: nowrap;
}

.map-pin.start {
  left: 10%;
  top: 22%;
}

.map-pin.middle {
  left: 40%;
  top: 43%;
}

.map-pin.end {
  bottom: 20%;
  right: 12%;
}

.preview-list {
  display: grid;
  gap: 0.75rem;
}

.preview-item {
  display: grid;
  grid-template-columns: 4.5rem minmax(0, 1fr);
  gap: 0.85rem;
  border: 1px solid rgb(255 255 255 / 0.16);
  background: rgb(255 255 255 / 0.08);
  padding: 0.9rem;
}

.preview-item > span {
  color: #f1b797;
  font-weight: 800;
}

.preview-item p {
  margin: 0;
  font-weight: 800;
}

.preview-item small {
  display: block;
  margin-top: 0.25rem;
  color: #d9ead5;
  line-height: 1.6;
}

.capability-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.capability-card {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 1rem;
  align-items: start;
  border: 1px solid #d9d0bd;
  background: #f8f5ed;
  padding: 1.25rem;
}

.capability-icon {
  display: grid;
  width: 2.7rem;
  height: 2.7rem;
  place-items: center;
  border-radius: 8px;
  background: #fff4ef;
  color: #c75532;
}

.capability-card h2 {
  margin: 0;
  color: #17201a;
  font-size: 1.05rem;
  font-weight: 800;
}

.capability-card p {
  margin: 0.45rem 0 0;
  color: #5e675b;
  font-size: 0.92rem;
  line-height: 1.7;
}

@media (max-width: 1100px) {
  .home-hero {
    grid-template-columns: 1fr;
  }

  .itinerary-preview {
    min-height: auto;
  }

  .capability-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .hero-copy,
  .itinerary-preview {
    min-height: auto;
    padding: 1.35rem;
  }

  .hero-copy h1 {
    font-size: 2.45rem;
  }

  .home-action {
    width: 100%;
  }

  .preview-item {
    grid-template-columns: 1fr;
  }
}
</style>
