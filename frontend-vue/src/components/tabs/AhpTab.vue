<template>
  <div class="ahp-tab page-container">
    <div class="section-title">
      <h2>⚖️ AHP Pairwise Calculator</h2>
      <p>Nhập ma trận so sánh cặp (Saaty 1–9) để tính trọng số AHP thủ công và kiểm tra tính nhất quán</p>
    </div>

    <div class="ahp-layout">
      <!-- Left: Info -->
      <div class="ahp-info glass-card">
        <h3>📐 Thang đo Saaty</h3>
        <table class="saaty-table">
          <thead><tr><th>Giá trị</th><th>Ý nghĩa</th></tr></thead>
          <tbody>
            <tr v-for="s in saatyScale" :key="s.val">
              <td><strong>{{ s.val }}</strong></td>
              <td>{{ s.meaning }}</td>
            </tr>
          </tbody>
        </table>
        <div class="cr-note">
          <div class="cr-item ok">✅ CR ≤ 0.1 → Ma trận nhất quán tốt</div>
          <div class="cr-item warn">⚠️ CR > 0.1 → Cần điều chỉnh lại ma trận</div>
        </div>

        <!-- Result Panel -->
        <transition name="slide-up">
          <div v-if="ahpResult" class="ahp-result-card" :class="ahpResult.is_consistent ? 'result-ok' : 'result-warn'">
            <div class="result-status">
              {{ ahpResult.is_consistent ? '✅' : '⚠️' }}
              {{ ahpResult.message }}
            </div>
            <div class="result-grid">
              <div class="result-item">
                <span class="ri-label">λ_max</span>
                <span class="ri-val">{{ ahpResult.lambda_max }}</span>
              </div>
              <div class="result-item">
                <span class="ri-label">CI</span>
                <span class="ri-val">{{ ahpResult.CI }}</span>
              </div>
              <div class="result-item">
                <span class="ri-label">CR</span>
                <span class="ri-val" :class="ahpResult.is_consistent ? 'text-success' : 'text-danger'">
                  {{ ahpResult.CR }}
                </span>
              </div>
            </div>
            <div class="result-weights">
              <div class="rw-title">Vector trọng số:</div>
              <div v-for="(w, crit) in ahpResult.weights_named" :key="crit" class="rw-row">
                <span class="rw-label">{{ criteriaNames.find(c => c.label === crit)?.icon || '' }} {{ crit }}</span>
                <div class="progress-bar rw-bar"><div class="progress-fill" :style="{ width: (w*100).toFixed(1) + '%' }"></div></div>
                <span class="rw-pct">{{ (w*100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </transition>
      </div>

      <!-- Right: Matrix -->
      <div class="ahp-matrix-wrap glass-card">
        <h3>Ma Trận So Sánh Cặp 5×5</h3>
        <p class="matrix-desc">Tiêu chí: {{ criteriaNames.map(c => c.label).join(' · ') }}</p>

        <div class="matrix-scroll scroll-x">
          <div class="matrix-grid" :style="{ gridTemplateColumns: `100px repeat(${N}, 1fr)` }">
            <!-- Header row -->
            <div class="mh-empty"></div>
            <div v-for="c in criteriaNames" :key="c.label" class="mh-cell">{{ c.short }}</div>
            <!-- Data rows -->
            <template v-for="(row, i) in N" :key="i">
              <div class="mh-cell">{{ criteriaNames[i].short }}</div>
              <div v-for="(col, j) in N" :key="j">
                <input
                  v-if="i === j"
                  class="m-input diag"
                  value="1" readonly
                />
                <input
                  v-else-if="i < j"
                  class="m-input editable"
                  type="number"
                  :min="1/9" :max="9" step="0.5"
                  :value="matrix[i][j]"
                  @change="updateCell(i, j, $event.target.value)"
                />
                <input
                  v-else
                  class="m-input reciprocal"
                  :value="(1/matrix[j][i]).toFixed(3)" readonly
                />
              </div>
            </template>
          </div>
        </div>

        <div class="matrix-actions">
          <button class="btn btn-ghost" @click="resetMatrix">↺ Reset ma trận</button>
          <button class="btn btn-primary" :disabled="calculating" @click="calcAHP">
            <span v-if="calculating" class="spinner" style="width:16px;height:16px;border-width:2px"></span>
            ⚡ Tính AHP
          </button>
        </div>

        <div v-if="error" class="alert alert-danger" style="margin-top:12px">{{ error }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { calculateAHP } from '../../api.js'

const N = 5
const criteriaNames = [
  { label: 'Giá', short: 'G', icon: '💰' },
  { label: 'Xăng', short: 'X', icon: '⛽' },
  { label: 'Hiệu năng', short: 'HN', icon: '⚡' },
  { label: 'Thiết kế', short: 'TK', icon: '🎨' },
  { label: 'Thương hiệu', short: 'TH', icon: '🏅' },
]

const saatyScale = [
  { val: 1, meaning: 'Quan trọng ngang nhau' },
  { val: 3, meaning: 'Quan trọng hơn một chút' },
  { val: 5, meaning: 'Quan trọng hơn nhiều' },
  { val: 7, meaning: 'Quan trọng hơn rất nhiều' },
  { val: 9, meaning: 'Cực kỳ quan trọng hơn' },
  { val: '2,4,6,8', meaning: 'Giá trị trung gian' },
  { val: '1/n', meaning: 'Nghịch đảo – kém quan trọng hơn' },
]

function initMatrix() {
  return Array.from({ length: N }, (_, i) =>
    Array.from({ length: N }, (_, j) => {
      if (i === j) return 1
      if (i < j) return 3  // default: slightly more important
      return null
    })
  )
}

const matrix = reactive(initMatrix())

// Fill reciprocals
function getVal(i, j) {
  if (i === j) return 1
  if (i < j) return matrix[i][j]
  return 1 / matrix[j][i]
}

function updateCell(i, j, rawVal) {
  const v = parseFloat(rawVal)
  if (isNaN(v) || v <= 0 || v > 9) return
  matrix[i][j] = v
}

function resetMatrix() {
  const fresh = initMatrix()
  for (let i = 0; i < N; i++)
    for (let j = 0; j < N; j++)
      matrix[i][j] = fresh[i][j]
  ahpResult.value = null
  error.value = ''
}

const ahpResult = ref(null)
const calculating = ref(false)
const error = ref('')

async function calcAHP() {
  calculating.value = true
  error.value = ''
  ahpResult.value = null

  try {
    // Build full matrix
    const fullMatrix = Array.from({ length: N }, (_, i) =>
      Array.from({ length: N }, (_, j) => parseFloat(getVal(i, j).toFixed(4)))
    )
    const result = await calculateAHP(fullMatrix)
    ahpResult.value = result
  } catch (e) {
    error.value = e.message
  } finally {
    calculating.value = false
  }
}
</script>

<style scoped>
.ahp-tab {}
.page-container { max-width: 1400px; margin: 0 auto; padding: 40px 24px; }

.ahp-layout { display: grid; grid-template-columns: 320px 1fr; gap: 20px; align-items: start; }

/* Info */
.ahp-info { padding: 24px; display: flex; flex-direction: column; gap: 20px; }
.ahp-info h3 { font-size: 0.95rem; }
.saaty-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
.saaty-table th { padding: 8px 10px; background: rgba(255,255,255,0.04); text-align: left; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-secondary); }
.saaty-table td { padding: 7px 10px; border-bottom: 1px solid rgba(255,255,255,0.04); color: var(--text-secondary); }
.saaty-table tr:last-child td { border-bottom: none; }
.saaty-table strong { color: var(--primary-light); }

.cr-note { display: flex; flex-direction: column; gap: 8px; }
.cr-item { font-size: 0.8rem; padding: 8px 12px; border-radius: var(--r-md); }
.cr-item.ok { background: var(--accent-dim); color: var(--accent); }
.cr-item.warn { background: var(--accent2-dim); color: var(--accent2); }

/* AHP Result */
.ahp-result-card { padding: 16px 20px; border-radius: var(--r-xl); border: 1px solid; display: flex; flex-direction: column; gap: 14px; }
.result-ok { background: var(--accent-dim); border-color: rgba(16,185,129,0.25); }
.result-warn { background: var(--accent2-dim); border-color: rgba(245,158,11,0.25); }
.result-status { font-size: 0.85rem; font-weight: 700; }
.result-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 8px; text-align: center; }
.result-item { background: rgba(255,255,255,0.06); border-radius: var(--r-sm); padding: 10px; }
.ri-label { display: block; font-size: 0.65rem; color: var(--text-dim); text-transform: uppercase; margin-bottom: 4px; }
.ri-val { font-size: 1rem; font-weight: 800; color: var(--text); }
.result-weights {}
.rw-title { font-size: 0.75rem; font-weight: 700; color: var(--text-secondary); margin-bottom: 8px; }
.rw-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.rw-label { font-size: 0.72rem; width: 80px; flex-shrink: 0; }
.rw-bar { flex: 1; }
.rw-pct { font-size: 0.72rem; font-weight: 800; width: 40px; text-align: right; }

/* Matrix */
.ahp-matrix-wrap { padding: 24px; }
.ahp-matrix-wrap h3 { margin-bottom: 6px; }
.matrix-desc { font-size: 0.78rem; color: var(--text-dim); margin-bottom: 20px; }
.matrix-scroll { overflow-x: auto; }
.matrix-grid { display: grid; gap: 4px; min-width: 400px; }
.mh-empty {}
.mh-cell {
  display: flex; align-items: center; justify-content: center;
  font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
  color: var(--primary-light); padding: 6px 4px; text-align: center;
}
.m-input {
  width: 100%; padding: 8px 4px; text-align: center;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
  border-radius: var(--r-sm); color: var(--text); font-family: var(--font); font-size: 0.8rem;
  outline: none; transition: var(--transition);
}
.m-input.diag { background: rgba(255,255,255,0.08); color: var(--text-dim); cursor: default; font-weight: 700; }
.m-input.editable:focus { border-color: rgba(99,102,241,0.5); background: rgba(99,102,241,0.08); }
.m-input.reciprocal { opacity: 0.45; cursor: default; }
.matrix-actions { display: flex; gap: 12px; margin-top: 20px; justify-content: flex-end; }

@media (max-width: 900px) {
  .ahp-layout { grid-template-columns: 1fr; }
}
</style>
