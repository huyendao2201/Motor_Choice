<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-box">
        <div class="modal-header">
          <h2>⚖️ So Sánh Chi Tiết Xe Máy</h2>
          <button class="modal-close" @click="$emit('close')">✕</button>
        </div>
        <div class="modal-body">
          <!-- Bikes Header -->
          <div class="compare-header">
            <div class="ch-label">Tiêu chí</div>
            <div
              v-for="(bike, i) in bikes"
              :key="i"
              class="ch-bike"
              :style="{ background: COLORS[i].bg }"
            >
              <span class="ch-rank">{{ RANK_ICONS[i] }}</span>
              <span class="ch-brand">{{ bike.brand }}</span>
              <span class="ch-model">{{ bike.model }}</span>
              <span class="ch-score-badge">{{ bike.total_score }}</span>
            </div>
          </div>

          <!-- Info rows -->
          <div class="compare-section-label">📋 Thông tin chung</div>
          <CompareRow label="🏍️ Loại xe" :bikes="bikes" field="vehicle_type" />
          <CompareRow label="🔧 Dung tích" :bikes="bikes" field="engine_cc" suffix="cc" />
          <CompareRow label="🏆 Hạng DSS" :bikes="bikes" field="rank" prefix="#" :highlight="true" :best-fn="(a, b) => a < b" />
          <CompareRow label="📊 Điểm tổng" :bikes="bikes" field="total_score" :highlight="true" :best-fn="(a, b) => a > b" />

          <!-- Criteria rows -->
          <div class="compare-section-label">⚖️ Điểm theo tiêu chí AHP</div>
          <CriteriaRow
            v-for="c in criteriaItems"
            :key="c.rawField"
            :label="c.label"
            :bikes="bikes"
            :raw-field="c.rawField"
            :norm-field="c.normKey"
            :weight="weights[c.wKey]"
            :type="c.type"
            :color="c.color"
            :suffix="c.suffix"
          />

          <!-- Winner -->
          <div class="compare-winner">
            💡 <strong>Kết luận:</strong> Qua so sánh trực tiếp,
            <strong style="color: var(--accent)">{{ winner.brand }} {{ winner.model }}</strong>
            đạt điểm DSS cao nhất (<strong>{{ winner.total_score }}</strong>) và là lựa chọn
            tốt nhất dựa trên trọng số AHP được AI dự đoán.
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, defineComponent, h } from 'vue'

const props = defineProps({ bikes: Array, weights: Object })
defineEmits(['close'])

const COLORS = [
  { bg: 'rgba(245,158,11,0.08)', border: '#f59e0b' },
  { bg: 'rgba(148,163,184,0.06)', border: '#94a3b8' },
  { bg: 'rgba(99,102,241,0.06)', border: '#818cf8' },
]
const RANK_ICONS = ['🥇', '🥈', '🥉']

const criteriaItems = [
  { label: '💰 Giá thành (triệu VNĐ)', rawField: 'price_million_vnd', normKey: 'price_norm', wKey: 'w_price', type: 'cost', color: '#f59e0b', suffix: 'M' },
  { label: '⛽ Xăng (L/100km)', rawField: 'fuel_consumption_l_per_100km', normKey: 'fuel_norm', wKey: 'w_fuel', type: 'cost', color: '#10b981', suffix: 'L' },
  { label: '⚡ Hiệu năng (/10)', rawField: 'performance_score', normKey: 'performance_norm', wKey: 'w_performance', type: 'benefit', color: '#6366f1', suffix: '/10' },
  { label: '🎨 Thiết kế (/10)', rawField: 'design_score', normKey: 'design_norm', wKey: 'w_design', type: 'benefit', color: '#ec4899', suffix: '/10' },
  { label: '🏅 Thương hiệu (/10)', rawField: 'brand_score', normKey: 'brand_norm', wKey: 'w_brand', type: 'benefit', color: '#8b5cf6', suffix: '/10' },
]

const winner = computed(() =>
  props.bikes.reduce((best, b) => b.total_score > best.total_score ? b : best, props.bikes[0])
)

// Inline sub-components
const CompareRow = defineComponent({
  props: ['label', 'bikes', 'field', 'prefix', 'suffix', 'highlight', 'bestFn'],
  setup(p) {
    return () => {
      const vals = p.bikes.map(b => b[p.field])
      const bestVal = p.highlight && p.bestFn
        ? vals.reduce((best, v) => p.bestFn(v, best) ? v : best, vals[0])
        : null
      return h('div', { class: 'cmp-row' }, [
        h('div', { class: 'cmp-label' }, p.label),
        ...p.bikes.map((b, i) => h('div', {
          class: ['cmp-cell', p.highlight && b[p.field] === bestVal ? 'cell-best' : '']
        }, `${p.prefix || ''}${b[p.field]}${p.suffix || ''}`))
      ])
    }
  }
})

const CriteriaRow = defineComponent({
  props: ['label', 'bikes', 'rawField', 'normField', 'weight', 'type', 'color', 'suffix'],
  setup(p) {
    return () => {
      const rawVals = p.bikes.map(b => b[p.rawField])
      const normVals = p.bikes.map(b => b.scores?.[p.normField] || 0)
      const bestRaw = p.type === 'cost' ? Math.min(...rawVals) : Math.max(...rawVals)

      return h('div', { class: 'cmp-row criteria-row' }, [
        h('div', { class: 'cmp-label' }, [
          p.label,
          h('div', { class: 'cmp-weight', style: { color: p.color } },
            `Trọng số AI: ${(p.weight * 100).toFixed(1)}%`)
        ]),
        ...p.bikes.map((b, i) => {
          const raw = b[p.rawField]
          const norm = normVals[i]
          const isBest = raw === bestRaw
          return h('div', { class: ['cmp-cell', isBest ? 'cell-best' : ''] }, [
            h('div', { class: 'mini-bar-wrap' }, [
              h('div', { class: 'mini-track' }, [
                h('div', { class: 'mini-fill', style: { width: (norm * 100).toFixed(0) + '%', background: p.color } })
              ]),
              h('span', { class: 'mini-raw' }, `${raw}${p.suffix}`)
            ]),
            h('div', { class: 'mini-norm-label' }, `norm: ${norm.toFixed(3)}`)
          ])
        })
      ])
    }
  }
})
</script>

<style scoped>
.modal-box { max-width: 860px; }

/* Header */
.compare-header {
  display: grid; gap: 8px; margin-bottom: 16px;
}
.compare-header {
  grid-template-columns: 120px repeat(v-bind('bikes.length'), 1fr);
}
.ch-label { display: flex; align-items: center; font-size: 0.75rem; color: var(--text-dim); font-weight: 600; }
.ch-bike {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  padding: 12px 8px; border-radius: var(--r-md); text-align: center;
}
.ch-rank { font-size: 1.5rem; }
.ch-brand { font-size: 0.7rem; font-weight: 600; color: var(--text-secondary); }
.ch-model { font-size: 0.82rem; font-weight: 800; color: var(--text); }
.ch-score-badge { font-size: 0.75rem; font-weight: 800; color: var(--accent); background: var(--accent-dim); border-radius: 99px; padding: 2px 8px; }

/* Section Labels */
.compare-section-label {
  font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
  color: var(--primary-light); background: var(--primary-dim);
  padding: 6px 12px; border-radius: var(--r-sm); margin: 12px 0 8px;
}

/* Compare Rows */
.cmp-row {
  display: grid;
  gap: 8px; padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  align-items: center;
}
.cmp-row {
  grid-template-columns: 120px repeat(v-bind('bikes.length'), 1fr);
}
.cmp-label { font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); }
.cmp-weight { font-size: 0.66rem; margin-top: 2px; }
.cmp-cell { font-size: 0.82rem; font-weight: 700; text-align: center; color: var(--text); padding: 6px; border-radius: var(--r-sm); }
.cell-best { background: var(--accent-dim); color: var(--accent); }

/* Mini Bar */
.mini-bar-wrap { display: flex; align-items: center; gap: 6px; justify-content: center; }
.mini-track { width: 60px; height: 6px; background: rgba(255,255,255,0.06); border-radius: 99px; overflow: hidden; }
.mini-fill { height: 100%; border-radius: 99px; }
.mini-raw { font-size: 0.78rem; font-weight: 700; }
.mini-norm-label { font-size: 0.62rem; color: var(--text-dim); text-align: center; margin-top: 2px; }

/* Winner */
.compare-winner {
  margin-top: 20px; padding: 16px 20px;
  background: var(--accent-dim); border: 1px solid rgba(16,185,129,0.2);
  border-radius: var(--r-md); font-size: 0.875rem; line-height: 1.7;
}
</style>
