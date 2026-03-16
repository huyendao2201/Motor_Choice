<template>
  <div
    class="bike-card glass-card"
    :class="[rankClass, { selected }]"
    @click="$emit('click')"
  >
    <!-- Rank Badge -->
    <div class="rank-badge" :class="badgeClass">{{ rankIcon }}</div>

    <!-- Compare Check -->
    <div class="compare-check" :class="{ visible: selected }">✓</div>

    <!-- Brand Tag -->
    <span class="brand-tag">{{ bike.brand }}</span>

    <!-- Model Name -->
    <div class="bike-model">{{ bike.model }}</div>

    <!-- Type & CC -->
    <div class="bike-type">
      <span class="tag" :class="typeClass">{{ bike.vehicle_type }}</span>
      <span class="bike-cc">{{ bike.engine_cc }}cc</span>
    </div>

    <!-- Specs Grid -->
    <div class="specs-grid">
      <div class="spec-item">
        <span class="spec-label">💰 Giá</span>
        <span class="spec-val price">{{ bike.price_million_vnd.toFixed(1) }}M</span>
      </div>
      <div class="spec-item">
        <span class="spec-label">⛽ Xăng</span>
        <span class="spec-val">{{ bike.fuel_consumption_l_per_100km }}L/100</span>
      </div>
      <div class="spec-item">
        <span class="spec-label">⚡ Hiệu năng</span>
        <span class="spec-val">{{ bike.performance_score }}/10</span>
      </div>
      <div class="spec-item">
        <span class="spec-label">🏅 Thương hiệu</span>
        <span class="spec-val">{{ bike.brand_score }}/10</span>
      </div>
    </div>

    <!-- Score Bar -->
    <div class="score-section">
      <div class="score-header">
        <span class="score-label">Điểm DSS tổng</span>
        <span class="score-value">{{ bike.total_score }}</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill score-fill" :style="scoreStyle"></div>
      </div>
    </div>

    <!-- Criteria Mini Bars (hover detail) -->
    <div class="criteria-mini">
      <div v-for="c in criteriaItems" :key="c.key" class="crit-row">
        <span class="crit-label">{{ c.icon }}</span>
        <div class="crit-track">
          <div class="crit-fill" :style="{ width: (bike.scores[c.normKey] * 100).toFixed(0) + '%', background: c.color }"></div>
        </div>
        <span class="crit-pct">{{ (bike.scores[c.normKey] * 100).toFixed(0) }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  bike: Object,
  weights: Object,
  selected: Boolean
})
defineEmits(['click'])

const rankClass = computed(() => {
  if (props.bike.rank === 1) return 'rank-gold'
  if (props.bike.rank === 2) return 'rank-silver'
  if (props.bike.rank === 3) return 'rank-bronze'
  return ''
})
const badgeClass = computed(() => {
  if (props.bike.rank === 1) return 'badge-gold'
  if (props.bike.rank === 2) return 'badge-silver'
  if (props.bike.rank === 3) return 'badge-bronze'
  return 'badge-default'
})
const rankIcon = computed(() => {
  if (props.bike.rank === 1) return '🥇'
  if (props.bike.rank === 2) return '🥈'
  if (props.bike.rank === 3) return '🥉'
  return `#${props.bike.rank}`
})
const typeClass = computed(() => ({
  'Xe số': 'tag-xe-so',
  'Xe tay ga': 'tag-tay-ga',
  'Xe côn tay': 'tag-con-tay',
}[props.bike.vehicle_type] || ''))

const scoreStyle = computed(() => ({
  width: (props.bike.total_score * 100).toFixed(1) + '%',
  background: props.bike.rank === 1
    ? 'linear-gradient(90deg, #f59e0b, #fbbf24)'
    : props.bike.rank === 2
    ? 'linear-gradient(90deg, #94a3b8, #cbd5e1)'
    : props.bike.rank === 3
    ? 'linear-gradient(90deg, #ca8a04, #d97706)'
    : 'linear-gradient(90deg, #6366f1, #818cf8)'
}))

const criteriaItems = [
  { key: 'price', icon: '💰', normKey: 'price_norm', color: '#f59e0b' },
  { key: 'fuel', icon: '⛽', normKey: 'fuel_norm', color: '#10b981' },
  { key: 'performance', icon: '⚡', normKey: 'performance_norm', color: '#6366f1' },
  { key: 'design', icon: '🎨', normKey: 'design_norm', color: '#ec4899' },
  { key: 'brand', icon: '🏅', normKey: 'brand_norm', color: '#8b5cf6' },
]
</script>

<style scoped>
.bike-card {
  padding: 20px; cursor: pointer; position: relative;
  border-radius: var(--r-xl);
  transition: var(--transition);
  overflow: hidden; display: flex; flex-direction: column; gap: 12px;
}

/* Rank Styling */
.rank-gold { border-color: rgba(245,158,11,0.35) !important; }
.rank-gold::before { content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(245,158,11,0.06), transparent); pointer-events: none; }
.rank-silver { border-color: rgba(148,163,184,0.3) !important; }
.rank-bronze { border-color: rgba(202,138,4,0.3) !important; }

.bike-card.selected {
  border-color: rgba(99,102,241,0.6) !important;
  box-shadow: 0 0 0 2px rgba(99,102,241,0.3), var(--shadow-md) !important;
}
.bike-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); }

/* Compare Check */
.compare-check {
  position: absolute; top: 12px; right: 12px;
  width: 22px; height: 22px; border-radius: 50%;
  background: var(--primary); color: white;
  font-size: 0.7rem; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: var(--transition); transform: scale(0.5);
}
.compare-check.visible { opacity: 1; transform: scale(1); }

/* Rank Badge */
.rank-badge {
  position: absolute; top: 14px; left: 14px;
  font-size: 1.2rem; filter: drop-shadow(0 2px 6px rgba(0,0,0,0.3));
}
.badge-gold { color: #f59e0b; }
.badge-silver { color: #94a3b8; }
.badge-bronze { color: #ca8a04; }
.badge-default { font-size: 0.75rem; font-weight: 800; color: var(--text-dim); }

/* Brand */
.brand-tag {
  display: inline-block; margin-top: 16px; /* space for rank-badge */
  font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
  color: var(--primary-light);
  background: var(--primary-dim); border-radius: 4px; padding: 2px 8px;
}

/* Model */
.bike-model { font-size: 1.05rem; font-weight: 800; color: var(--text); line-height: 1.3; }

/* Type & CC */
.bike-type { display: flex; align-items: center; gap: 8px; }
.bike-cc { font-size: 0.72rem; color: var(--text-dim); font-weight: 500; }

/* Specs */
.specs-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.spec-item { display: flex; flex-direction: column; gap: 2px; }
.spec-label { font-size: 0.65rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.3px; }
.spec-val { font-size: 0.82rem; font-weight: 700; color: var(--text); }
.spec-val.price { color: var(--accent2); font-size: 0.9rem; }

/* Score */
.score-section { margin-top: 4px; }
.score-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.score-label { font-size: 0.68rem; color: var(--text-dim); text-transform: uppercase; }
.score-value { font-size: 0.9rem; font-weight: 900; color: var(--accent); }
.score-fill { transition: width 1s cubic-bezier(0.4,0,0.2,1) !important; }

/* Criteria Mini (visible on hover) */
.criteria-mini {
  display: flex; flex-direction: column; gap: 5px;
  max-height: 0; overflow: hidden;
  transition: max-height 0.4s ease, opacity 0.3s ease;
  opacity: 0;
  border-top: 1px solid rgba(255,255,255,0.04);
  padding-top: 0;
}
.bike-card:hover .criteria-mini {
  max-height: 200px; opacity: 1; padding-top: 10px;
}
.crit-row { display: flex; align-items: center; gap: 6px; }
.crit-label { font-size: 0.7rem; width: 20px; }
.crit-track { flex: 1; height: 4px; background: rgba(255,255,255,0.06); border-radius: 99px; overflow: hidden; }
.crit-fill { height: 100%; border-radius: 99px; transition: width 0.5s ease; }
.crit-pct { font-size: 0.66rem; color: var(--text-dim); width: 28px; text-align: right; }
</style>
