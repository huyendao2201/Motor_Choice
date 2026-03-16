<template>
  <div class="sensitivity-wrap glass-card">
    <div class="section-sub-header">
      <h3>📊 Sensitivity Analysis – Phân Tích Độ Nhạy</h3>
      <p>Kéo thanh trọng số để xem ranking thay đổi <strong>real-time</strong> (không cần gọi lại AI)</p>
    </div>

    <div class="sens-layout">
      <!-- Controls -->
      <div class="sens-controls">
        <div class="sens-weight-items">
          <div v-for="item in items" :key="item.key" class="sens-weight-item">
            <div class="sw-header">
              <span class="sw-label">{{ item.icon }} {{ item.label }}</span>
              <span class="sw-value" :style="{ color: item.color }">{{ localWeights[item.key] }}%</span>
            </div>
            <div class="sw-track">
              <div class="sw-fill" :style="{ width: localWeights[item.key] + '%', background: item.color }"></div>
              <input
                type="range" min="0" max="100" step="1"
                v-model.number="localWeights[item.key]"
                class="sw-range overlay-range"
                @input="onWeightChange"
              />
            </div>
          </div>
        </div>

        <div class="sens-total" :class="totalClass">
          ⚡ Tổng trọng số: <strong>{{ totalPct }}%</strong>
          <span v-if="Math.abs(totalPct - 100) > 15" class="total-warn"> (nên = 100%)</span>
        </div>
        <button class="btn btn-ghost btn-sm" @click="resetWeights">↺ Khôi phục trọng số AI</button>
      </div>

      <!-- Ranking Result -->
      <div class="sens-ranking">
        <div v-if="!rankedBikes.length" class="sens-empty">Chưa có dữ liệu</div>
        <transition-group name="rank-item" tag="div" class="rank-list">
          <div
            v-for="(bike, i) in rankedBikes"
            :key="bike.brand + bike.model"
            class="rank-row"
            :class="{ 'rank-top': i === 0 }"
          >
            <div class="rank-num" :class="{ gold: i === 0 }">{{ i === 0 ? '🥇' : i + 1 }}</div>
            <div class="rank-info">
              <div class="rank-model">{{ bike.model }}</div>
              <div class="rank-brand">{{ bike.brand }} · {{ bike.vehicle_type }}</div>
            </div>
            <div v-if="bike._delta !== 0 && bike._delta !== null" class="rank-delta">
              <span v-if="bike._delta > 0" class="delta-up">▲{{ bike._delta }}</span>
              <span v-else-if="bike._delta < 0" class="delta-down">▼{{ Math.abs(bike._delta) }}</span>
            </div>
            <div class="rank-score-wrap">
              <span class="rank-score">{{ bike.sens_score }}</span>
              <div class="rank-bar">
                <div class="rank-bar-fill" :style="{ width: barWidth(bike.sens_score) + '%' }"></div>
              </div>
            </div>
          </div>
        </transition-group>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'

const props = defineProps({
  bikes: Array,
  initialWeights: Object
})

const CRITERIA = [
  { key: 'price_million_vnd', wKey: 'w_price', type: 'cost' },
  { key: 'fuel_consumption_l_per_100km', wKey: 'w_fuel', type: 'cost' },
  { key: 'performance_score', wKey: 'w_performance', type: 'benefit' },
  { key: 'design_score', wKey: 'w_design', type: 'benefit' },
  { key: 'brand_score', wKey: 'w_brand', type: 'benefit' },
]

const items = [
  { key: 'w_price', icon: '💰', label: 'Giá thành', color: '#f59e0b' },
  { key: 'w_fuel', icon: '⛽', label: 'Tiêu thụ xăng', color: '#10b981' },
  { key: 'w_performance', icon: '⚡', label: 'Hiệu năng', color: '#6366f1' },
  { key: 'w_design', icon: '🎨', label: 'Thiết kế', color: '#ec4899' },
  { key: 'w_brand', icon: '🏅', label: 'Thương hiệu', color: '#8b5cf6' },
]

// Local weights (in %)
const localWeights = reactive({
  w_price: 0, w_fuel: 0, w_performance: 0, w_design: 0, w_brand: 0
})

let prevRanking = []
const rankedBikes = ref([])

const totalPct = computed(() =>
  Object.values(localWeights).reduce((a, b) => a + b, 0)
)
const totalClass = computed(() => ({
  'total-ok': Math.abs(totalPct.value - 100) <= 15,
  'total-warn-class': Math.abs(totalPct.value - 100) > 15
}))

function onWeightChange() { computeRanking() }

// Watch both initialWeights and bikes to sync and recompute
watch([() => props.initialWeights, () => props.bikes], ([w, bikes]) => {
  if (!w) return
  items.forEach(item => {
    localWeights[item.key] = Math.round((w[item.key] || 0) * 100)
  })
  if (bikes && bikes.length) {
    computeRanking()
  }
}, { immediate: true })

function computeRanking() {
  if (!props.bikes || !props.bikes.length) return

  const rawSum = totalPct.value
  if (rawSum <= 0) return

  try {
    const normW = {}
    items.forEach(item => { normW[item.key] = localWeights[item.key] / rawSum })

    // Compute ranges from bikes
    const ranges = {}
    CRITERIA.forEach(c => {
      const vals = props.bikes.map(b => Number(b[c.key]) || 0)
      const min = Math.min(...vals)
      const max = Math.max(...vals)
      ranges[c.key] = { min, max }
    })

    // Score each bike
    const scored = props.bikes.map(bike => {
      let score = 0
      CRITERIA.forEach(c => {
        const { min, max } = ranges[c.key]
        const val = Number(bike[c.key]) || 0
        const norm = max === min ? 1 : c.type === 'cost'
          ? (max - val) / (max - min)
          : (val - min) / (max - min)
        score += (normW[c.wKey] || 0) * norm
      })
      return { ...bike, sens_score: parseFloat(score.toFixed(4)) }
    })

    const sorted = [...scored].sort((a, b) => b.sens_score - a.sens_score)

    // Compute delta vs previous ranking
    sorted.forEach((bike, i) => {
      const prevIdx = prevRanking.findIndex(b => b.brand === bike.brand && b.model === bike.model)
      bike._delta = prevIdx !== -1 && prevIdx !== i ? prevIdx - i : null
    })

    prevRanking = sorted.map(b => ({ brand: b.brand, model: b.model }))
    rankedBikes.value = sorted.slice(0, 6)
  } catch (e) {
    console.warn('SensitivityPanel: computeRanking error', e)
    rankedBikes.value = []
  }
}

function resetWeights() {
  if (!props.initialWeights) return
  items.forEach(item => {
    localWeights[item.key] = Math.round((props.initialWeights[item.key] || 0) * 100)
  })
  computeRanking()
}

const maxScore = computed(() => rankedBikes.value[0]?.sens_score || 1)
function barWidth(score) {
  return ((score / maxScore.value) * 100).toFixed(1)
}
</script>

<style scoped>
.sensitivity-wrap { padding: 28px; }
.section-sub-header { margin-bottom: 24px; }
.section-sub-header h3 { font-size: 1rem; margin-bottom: 4px; }
.section-sub-header strong { color: var(--accent); }

.sens-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }

/* Controls */
.sens-controls { display: flex; flex-direction: column; gap: 14px; }
.sens-weight-items { display: flex; flex-direction: column; gap: 12px; }
.sens-weight-item {}
.sw-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.sw-label { font-size: 0.8rem; font-weight: 600; color: var(--text); }
.sw-value { font-size: 0.85rem; font-weight: 800; }
.sw-track { position: relative; height: 8px; background: rgba(255,255,255,0.06); border-radius: 99px; }
.sw-fill { position: absolute; top: 0; left: 0; height: 100%; border-radius: 99px; opacity: 0.7; }
.overlay-range {
  position: absolute; top: -4px; left: 0; width: 100%; height: 16px;
  opacity: 0; cursor: pointer; z-index: 2;
}

.sens-total { font-size: 0.8rem; color: var(--text-secondary); }
.total-ok strong { color: var(--accent); }
.total-warn-class strong { color: var(--danger); }
.total-warn { color: var(--danger); font-size: 0.72rem; }

.btn-sm { padding: 7px 14px; font-size: 0.78rem; width: fit-content; }

/* Ranking */
.sens-ranking {}
.sens-empty { color: var(--text-dim); font-size: 0.85rem; text-align: center; padding: 40px; }
.rank-list { display: flex; flex-direction: column; gap: 8px; }
.rank-row {
  display: flex; align-items: center; gap: 10px;
  background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05);
  border-radius: var(--r-md); padding: 10px 14px;
  transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
}
.rank-top { background: rgba(245,158,11,0.06); border-color: rgba(245,158,11,0.2); }
.rank-num { font-size: 1rem; width: 24px; flex-shrink: 0; text-align: center; font-weight: 900; }
.rank-num.gold { filter: drop-shadow(0 0 4px rgba(245,158,11,0.6)); }
.rank-info { flex: 1; min-width: 0; }
.rank-model { font-size: 0.82rem; font-weight: 700; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rank-brand { font-size: 0.7rem; color: var(--text-dim); }
.rank-delta { width: 28px; flex-shrink: 0; text-align: center; }
.delta-up { color: var(--accent); font-size: 0.7rem; font-weight: 800; }
.delta-down { color: var(--danger); font-size: 0.7rem; font-weight: 800; }
.rank-score-wrap { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; min-width: 80px; }
.rank-score { font-size: 0.8rem; font-weight: 800; color: var(--accent); }
.rank-bar { width: 80px; height: 4px; background: rgba(255,255,255,0.06); border-radius: 99px; overflow: hidden; }
.rank-bar-fill { height: 100%; background: linear-gradient(90deg, #6366f1, #10b981); border-radius: 99px; transition: width 0.3s ease; }

/* Rank transition */
.rank-item-move { transition: transform 0.5s cubic-bezier(0.4,0,0.2,1); }
.rank-item-enter-active { transition: all 0.3s ease; }
.rank-item-leave-active { transition: all 0.2s ease; }
.rank-item-enter-from { opacity: 0; transform: translateX(-10px); }
.rank-item-leave-to { opacity: 0; transform: translateX(10px); }

@media (max-width: 768px) {
  .sens-layout { grid-template-columns: 1fr; }
}
</style>
