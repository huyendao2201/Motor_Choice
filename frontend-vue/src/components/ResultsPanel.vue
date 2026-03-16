<template>
  <div class="results-panel">

    <!-- ===== RESULT HEADER ===== -->
    <div class="results-header">
      <div class="results-meta">
        <div class="meta-badge">
          <span class="meta-icon">{{ purposeIcon }}</span>
          <div>
            <div class="meta-title">{{ result.user_profile_summary.purpose_label }}</div>
            <div class="meta-sub">{{ result.user_profile_summary.vehicle_type_label }} · Ngân sách {{ result.user_profile_summary.budget }}M · {{ result.user_profile_summary.daily_km }}km/ngày</div>
          </div>
        </div>
        <div class="meta-stats">
          <div class="meta-stat">
            <span class="meta-stat-num">{{ result.total_filtered }}</span>
            <span class="meta-stat-label">xe phù hợp</span>
          </div>
          <div class="meta-stat">
            <span class="meta-stat-num">{{ result.top_motorcycles.length }}</span>
            <span class="meta-stat-label">đề xuất</span>
          </div>
        </div>
      </div>
      <button class="btn btn-ghost" @click="$emit('reset')">↩ Tư vấn lại</button>
    </div>

    <!-- Warning -->
    <div v-if="result.warning" class="alert alert-warning">
      ⚠️ {{ result.warning }}
    </div>

    <!-- ===== AI WEIGHTS PANEL ===== -->
    <div class="weights-panel glass-card">
      <div class="weights-header">
        <div>
          <div class="weights-title">🤖 Trọng số AHP dự đoán bởi Random Forest AI</div>
          <div class="weights-sub">Tổng = {{ weightSum }}% · Mô hình đã học từ 300 user profiles</div>
        </div>
        <span class="badge badge-primary">AI Generated</span>
      </div>
      <div class="weights-bars">
        <div v-for="w in weightItems" :key="w.key" class="weight-bar-row">
          <span class="wb-label">{{ w.icon }} {{ w.label }}</span>
          <div class="wb-track">
            <div class="wb-fill" :style="{ width: (result.ahp_weights[w.key] * 100).toFixed(1) + '%', background: w.color }"></div>
          </div>
          <span class="wb-pct" :style="{ color: w.color }">{{ (result.ahp_weights[w.key] * 100).toFixed(1) }}%</span>
        </div>
      </div>
    </div>

    <!-- ===== EXPLANATION ===== -->
    <div class="explanation-card glass-card" v-if="result.explanation">
      💡 <span v-html="renderMarkdown(result.explanation)"></span>
    </div>

    <!-- ===== RADAR CHART ===== -->
    <div class="radar-section glass-card">
      <div class="section-sub-header">
        <h3>🕸️ Radar Chart – So Sánh Top 3 Xe</h3>
        <p>Biểu đồ nhện thể hiện điểm chuẩn hóa của từng tiêu chí AHP</p>
      </div>
      <div class="radar-wrap">
        <Radar :data="radarData" :options="radarOptions" />
      </div>
    </div>

    <!-- ===== BIKE CARDS ===== -->
    <div class="bikes-section">
      <div class="bikes-header">
        <h3>🏆 Danh Sách Xe Đề Xuất</h3>
        <span class="compare-hint" v-if="selectedForCompare.length < 2">Bấm vào thẻ xe để chọn so sánh (2–3 xe)</span>
        <span class="compare-hint active" v-else>{{ selectedForCompare.length }} xe đã chọn</span>
      </div>

      <div class="bikes-grid">
        <BikeCard
          v-for="(bike, idx) in result.top_motorcycles"
          :key="bike.rank"
          :bike="bike"
          :weights="result.ahp_weights"
          :selected="selectedForCompare.includes(idx)"
          @click="toggleCompare(idx)"
        />
      </div>

      <!-- Compare Bar -->
      <transition name="slide-up">
        <div class="compare-bar glass-card" v-if="selectedForCompare.length > 0">
          <span class="compare-count">{{ selectedForCompare.length }} xe được chọn</span>
          <div class="compare-actions">
            <button class="btn btn-ghost" @click="clearCompare">✕ Bỏ chọn</button>
            <button
              class="btn btn-primary"
              :disabled="selectedForCompare.length < 2"
              @click="openCompare"
            >⚖️ So Sánh Xe</button>
          </div>
        </div>
      </transition>
    </div>

    <!-- ===== SENSITIVITY ANALYSIS ===== -->
    <SensitivityPanel
      :bikes="result.top_motorcycles"
      :initial-weights="result.ahp_weights"
    />

    <!-- Reset -->
    <div class="reset-section">
      <button class="btn btn-secondary" @click="$emit('reset')">↩ Quay lại và tư vấn mới</button>
    </div>

    <!-- Compare Modal -->
    <CompareModal
      v-if="compareOpen"
      :bikes="selectedBikesData"
      :weights="result.ahp_weights"
      @close="compareOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Radar } from 'vue-chartjs'
import {
  Chart as ChartJS, RadialLinearScale, PointElement,
  LineElement, Filler, Tooltip, Legend
} from 'chart.js'
import BikeCard from './BikeCard.vue'
import SensitivityPanel from './SensitivityPanel.vue'
import CompareModal from './CompareModal.vue'

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

const props = defineProps({ result: Object })
const emit = defineEmits(['reset'])

const selectedForCompare = ref([])
const compareOpen = ref(false)

const purposeIcons = ['🎓', '💼', '🏕️', '📦']
const purposeIdx = computed(() => {
  const labels = ['Sinh viên', 'Nhân viên văn phòng', 'Người đi tour', 'Người chạy dịch vụ']
  return labels.indexOf(props.result.user_profile_summary.purpose_label)
})
const purposeIcon = computed(() => purposeIcons[purposeIdx.value] || '👤')

const weightItems = [
  { key: 'w_price', icon: '💰', label: 'Giá thành', color: '#f59e0b' },
  { key: 'w_fuel', icon: '⛽', label: 'Tiêu thụ xăng', color: '#10b981' },
  { key: 'w_performance', icon: '⚡', label: 'Hiệu năng', color: '#6366f1' },
  { key: 'w_design', icon: '🎨', label: 'Thiết kế', color: '#ec4899' },
  { key: 'w_brand', icon: '🏅', label: 'Thương hiệu', color: '#8b5cf6' },
]

const weightSum = computed(() =>
  Math.round(Object.values(props.result.ahp_weights).reduce((a, b) => a + b, 0) * 100)
)

// Simple markdown bold
function renderMarkdown(text) {
  return text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
}

// Radar Chart
const CHART_COLORS = [
  { bg: 'rgba(245,158,11,0.15)', border: 'rgba(245,158,11,0.9)' },
  { bg: 'rgba(148,163,184,0.12)', border: 'rgba(148,163,184,0.8)' },
  { bg: 'rgba(99,102,241,0.12)', border: 'rgba(99,102,241,0.8)' },
]

const radarData = computed(() => {
  const top3 = props.result.top_motorcycles.slice(0, 3)
  return {
    labels: ['💰 Giá', '⛽ Xăng', '⚡ Hiệu năng', '🎨 Thiết kế', '🏅 Thương hiệu'],
    datasets: top3.map((bike, i) => ({
      label: `${bike.brand} ${bike.model}`,
      data: [
        +(bike.scores.price_norm * 100).toFixed(1),
        +(bike.scores.fuel_norm * 100).toFixed(1),
        +(bike.scores.performance_norm * 100).toFixed(1),
        +(bike.scores.design_norm * 100).toFixed(1),
        +(bike.scores.brand_norm * 100).toFixed(1),
      ],
      backgroundColor: CHART_COLORS[i].bg,
      borderColor: CHART_COLORS[i].border,
      borderWidth: 2.5,
      pointBackgroundColor: CHART_COLORS[i].border,
      pointRadius: 5,
      pointHoverRadius: 7,
    }))
  }
})

const radarOptions = {
  responsive: true, maintainAspectRatio: true,
  animation: { duration: 1000, easing: 'easeInOutQuart' },
  scales: {
    r: {
      min: 0, max: 100,
      ticks: { stepSize: 25, color: 'rgba(148,163,184,0.5)', font: { size: 9 }, backdropColor: 'transparent', callback: v => v + '%' },
      grid: { color: 'rgba(255,255,255,0.06)' },
      angleLines: { color: 'rgba(255,255,255,0.08)' },
      pointLabels: { color: '#e2e8f0', font: { size: 12, weight: '700' } }
    }
  },
  plugins: {
    legend: {
      position: 'bottom',
      labels: { color: '#e2e8f0', font: { size: 11, weight: '600' }, padding: 18, usePointStyle: true, pointStyleWidth: 10 }
    },
    tooltip: { callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.raw}%` } }
  }
}

// Compare
function toggleCompare(idx) {
  if (selectedForCompare.value.includes(idx)) {
    selectedForCompare.value = selectedForCompare.value.filter(i => i !== idx)
  } else {
    if (selectedForCompare.value.length >= 3) selectedForCompare.value.shift()
    selectedForCompare.value.push(idx)
  }
}
function clearCompare() { selectedForCompare.value = [] }
function openCompare() { compareOpen.value = true }

const selectedBikesData = computed(() =>
  selectedForCompare.value.map(i => props.result.top_motorcycles[i])
)
</script>

<style scoped>
.results-panel { padding: 40px 0; display: flex; flex-direction: column; gap: 24px; }

/* Header */
.results-header {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 16px;
  flex-wrap: wrap;
}
.results-meta { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; }
.meta-badge {
  display: flex; align-items: center; gap: 14px;
  background: var(--glass); border: var(--border); border-radius: var(--r-xl);
  padding: 14px 20px;
}
.meta-icon { font-size: 2.5rem; }
.meta-title { font-size: 1rem; font-weight: 800; }
.meta-sub { font-size: 0.78rem; color: var(--text-secondary); margin-top: 2px; }
.meta-stats { display: flex; gap: 20px; }
.meta-stat { display: flex; flex-direction: column; align-items: center; }
.meta-stat-num { font-size: 1.8rem; font-weight: 900; color: var(--accent); line-height: 1; }
.meta-stat-label { font-size: 0.68rem; color: var(--text-dim); text-transform: uppercase; }

/* Weights Panel */
.weights-panel { padding: 24px; }
.weights-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; gap: 16px; }
.weights-title { font-size: 0.9rem; font-weight: 700; margin-bottom: 4px; }
.weights-sub { font-size: 0.75rem; color: var(--text-dim); }
.weights-bars { display: flex; flex-direction: column; gap: 12px; }
.weight-bar-row { display: flex; align-items: center; gap: 12px; }
.wb-label { font-size: 0.8rem; font-weight: 600; width: 140px; flex-shrink: 0; }
.wb-track { flex: 1; height: 8px; background: rgba(255,255,255,0.06); border-radius: 99px; overflow: hidden; }
.wb-fill { height: 100%; border-radius: 99px; transition: width 1s cubic-bezier(0.4,0,0.2,1); opacity: 0.85; }
.wb-pct { font-size: 0.82rem; font-weight: 800; width: 46px; text-align: right; }

/* Explanation */
.explanation-card {
  padding: 16px 20px; font-size: 0.875rem; line-height: 1.7;
  color: var(--text-secondary); display: flex; gap: 8px;
}

/* Radar */
.radar-section { padding: 28px; }
.section-sub-header { margin-bottom: 20px; }
.section-sub-header h3 { font-size: 1rem; margin-bottom: 4px; }
.section-sub-header p { font-size: 0.8rem; }
.radar-wrap { max-width: 500px; margin: 0 auto; }

/* Bikes */
.bikes-section { display: flex; flex-direction: column; gap: 16px; }
.bikes-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.bikes-header h3 { font-size: 1rem; font-weight: 800; }
.compare-hint { font-size: 0.78rem; color: var(--text-dim); }
.compare-hint.active { color: var(--accent); font-weight: 600; }
.bikes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }

/* Compare Bar */
.compare-bar {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  padding: 14px 20px;
}
.compare-count { font-size: 0.85rem; font-weight: 600; color: var(--accent); }
.compare-actions { display: flex; gap: 10px; }

/* Reset */
.reset-section { display: flex; justify-content: center; padding-top: 16px; }

@media (max-width: 768px) {
  .results-header { flex-direction: column; }
  .meta-stats { display: none; }
}
</style>
