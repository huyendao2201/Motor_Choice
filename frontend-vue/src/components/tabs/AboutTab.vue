<template>
  <div class="about-tab page-container">
    <div class="section-title">
      <h2>📊 Về Hệ Thống</h2>
      <p>Dự án môn Hệ Hỗ Trợ Ra Quyết Định – Phương án A: AI dự đoán trọng số AHP</p>
    </div>

    <!-- Architecture Flow -->
    <div class="arch-card glass-card">
      <h3>🏗️ Kiến Trúc Hệ Thống</h3>
      <div class="arch-flow">
        <div v-for="(step, i) in archSteps" :key="i" class="arch-step-wrap">
          <div class="arch-step" :class="step.class">
            <span class="arch-icon">{{ step.icon }}</span>
            <span class="arch-label">{{ step.label }}</span>
            <span class="arch-sub">{{ step.sub }}</span>
          </div>
          <div class="arch-arrow" v-if="i < archSteps.length - 1">→</div>
        </div>
      </div>
    </div>

    <!-- About Cards -->
    <div class="about-grid">
      <div v-for="card in aboutCards" :key="card.title" class="about-card glass-card">
        <div class="about-card-icon">{{ card.icon }}</div>
        <h3>{{ card.title }}</h3>
        <p>{{ card.desc }}</p>
        <div class="about-tags">
          <span v-for="tag in card.tags" :key="tag" class="badge badge-primary">{{ tag }}</span>
        </div>
      </div>
    </div>

    <!-- DSS Algorithm -->
    <div class="algo-card glass-card">
      <h3>📐 Thuật Toán DSS</h3>
      <div class="algo-grid">
        <div class="algo-section">
          <div class="algo-title">Cost Criteria (Giá, Xăng)</div>
          <div class="algo-formula">norm = (max − x) / (max − min)</div>
          <div class="algo-note">Giá trị càng thấp → điểm chuẩn hóa càng cao</div>
        </div>
        <div class="algo-section">
          <div class="algo-title">Benefit Criteria (Hiệu năng, Thiết kế, Thương hiệu)</div>
          <div class="algo-formula">norm = (x − min) / (max − min)</div>
          <div class="algo-note">Giá trị càng cao → điểm chuẩn hóa càng cao</div>
        </div>
        <div class="algo-section full">
          <div class="algo-title">Tổng điểm AHP</div>
          <div class="algo-formula">Score(i) = Σ wⱼ × norm(xᵢⱼ)</div>
          <div class="algo-note">wⱼ được AI Random Forest dự đoán từ user profile · Tổng wⱼ = 1.000</div>
        </div>
      </div>
    </div>

    <!-- Model Metrics -->
    <div class="metrics-card glass-card">
      <h3>📈 Chỉ Số Mô Hình AI</h3>
      <div v-if="metricsLoading" class="metrics-loading">
        <div class="spinner"></div>
        <span>Đang tải chỉ số...</span>
      </div>
      <div v-else-if="health" class="metrics-grid">
        <div class="metric-item">
          <span class="mi-icon">🟢</span>
          <span class="mi-label">Trạng thái</span>
          <span class="mi-val success">{{ health.model_trained ? 'Đã huấn luyện' : 'Chưa huấn luyện' }}</span>
        </div>
        <div class="metric-item">
          <span class="mi-icon">📊</span>
          <span class="mi-label">MAE</span>
          <span class="mi-val">{{ health.eval_metrics?.mae ?? '--' }}</span>
        </div>
        <div class="metric-item">
          <span class="mi-icon">📉</span>
          <span class="mi-label">RMSE</span>
          <span class="mi-val">{{ health.eval_metrics?.rmse ?? '--' }}</span>
        </div>
        <div class="metric-item">
          <span class="mi-icon">🏍️</span>
          <span class="mi-label">Mẫu xe</span>
          <span class="mi-val">{{ health.motorcycles_loaded }}</span>
        </div>
        <div class="metric-item">
          <span class="mi-icon">🎓</span>
          <span class="mi-label">Mẫu train</span>
          <span class="mi-val">{{ health.eval_metrics?.train_samples ?? 240 }}</span>
        </div>
        <div class="metric-item">
          <span class="mi-icon">🧪</span>
          <span class="mi-label">Mẫu test</span>
          <span class="mi-val">{{ health.eval_metrics?.test_samples ?? 60 }}</span>
        </div>
      </div>
    </div>

    <!-- Tech Stack -->
    <div class="stack-card glass-card">
      <h3>🛠️ Tech Stack</h3>
      <div class="stack-grid">
        <div v-for="t in techStack" :key="t.name" class="stack-item">
          <span class="stack-icon">{{ t.icon }}</span>
          <div>
            <div class="stack-name">{{ t.name }}</div>
            <div class="stack-desc text-xs text-dim">{{ t.desc }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { healthCheck } from '../../api.js'

const health = ref(null)
const metricsLoading = ref(true)

onMounted(async () => {
  try { health.value = await healthCheck() } catch {}
  finally { metricsLoading.value = false }
})

const archSteps = [
  { icon: '👤', label: 'User Input', sub: 'Profile & Preferences', class: 'step-user' },
  { icon: '🤖', label: 'Random Forest', sub: 'Predict AHP Weights', class: 'step-ai' },
  { icon: '🔽', label: 'Filter', sub: 'Budget & Type', class: 'step-filter' },
  { icon: '📐', label: 'Normalize', sub: 'Min-Max', class: 'step-norm' },
  { icon: '📊', label: 'Score', sub: 'Σ w × norm', class: 'step-score' },
  { icon: '🏆', label: 'Top N', sub: 'Ranked Results', class: 'step-result' },
]

const aboutCards = [
  {
    icon: '🤖', title: 'Random Forest AI',
    desc: 'Multi-output Random Forest Regressor học ánh xạ từ user profile → vector trọng số AHP. Huấn luyện với 300 mẫu giả lập theo 4 nhóm người dùng điển hình.',
    tags: ['scikit-learn', '200 trees', 'Multi-output']
  },
  {
    icon: '⚖️', title: 'Phương pháp AHP',
    desc: 'Analytic Hierarchy Process với 5 tiêu chí. Trọng số được AI dự đoán và chuẩn hóa đảm bảo tổng = 1. Có AHP Calculator thủ công với kiểm tra CR ≤ 0.1.',
    tags: ['5 criteria', 'Saaty scale', 'CR check']
  },
  {
    icon: '📊', title: 'DSS Engine',
    desc: 'Chuẩn hóa Min-Max theo loại tiêu chí (Cost/Benefit). Tính điểm tổng Score = Σ wj × norm(xij). Xếp hạng và đề xuất Top N xe kèm giải thích.',
    tags: ['Min-Max norm', 'Weighted sum', 'Explain']
  },
  {
    icon: '🗃️', title: 'Dataset',
    desc: '98 mẫu xe máy từ Honda, Yamaha, Suzuki, SYM, Piaggio, Vespa, Kymco, Benelli, GPX. Đầy đủ 3 loại: Xe số, Tay ga, Côn tay với giá từ 17M đến 110M+.',
    tags: ['98 bikes', '9 brands', '3 types']
  },
]

const techStack = [
  { icon: '🐍', name: 'FastAPI + Python', desc: 'Backend REST API với full validation và logging' },
  { icon: '🌲', name: 'scikit-learn', desc: 'RandomForestRegressor, train/test split, metrics' },
  { icon: '💚', name: 'Vue.js 3 + Vite', desc: 'Frontend SPA với Composition API' },
  { icon: '📈', name: 'Chart.js', desc: 'Radar Chart visualize top xe' },
  { icon: '🐼', name: 'pandas + numpy', desc: 'Data processing và tính toán DSS' },
  { icon: '📋', name: 'Pydantic v2', desc: 'Input validation và serialization' },
]
</script>

<style scoped>
.about-tab {}
.page-container { max-width: 1400px; margin: 0 auto; padding: 40px 24px; display: flex; flex-direction: column; gap: 24px; }

/* Architecture */
.arch-card { padding: 28px; }
.arch-card h3 { margin-bottom: 24px; font-size: 1rem; }
.arch-flow { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; }
.arch-step-wrap { display: flex; align-items: center; gap: 8px; }
.arch-step {
  display: flex; flex-direction: column; align-items: center; gap: 4px; text-align: center;
  padding: 14px 16px; border-radius: var(--r-lg); border: 1px solid rgba(255,255,255,0.08);
  min-width: 90px;
}
.step-ai { background: rgba(99,102,241,0.1); border-color: rgba(99,102,241,0.25); }
.step-result { background: rgba(16,185,129,0.08); border-color: rgba(16,185,129,0.2); }
.arch-icon { font-size: 1.4rem; }
.arch-label { font-size: 0.72rem; font-weight: 800; color: var(--text); }
.arch-sub { font-size: 0.62rem; color: var(--text-dim); }
.arch-arrow { font-size: 1.2rem; color: var(--text-dim); }

/* About Grid */
.about-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.about-card { padding: 24px; display: flex; flex-direction: column; gap: 10px; }
.about-card-icon { font-size: 2rem; }
.about-card h3 { font-size: 0.95rem; }
.about-card p { font-size: 0.82rem; line-height: 1.6; color: var(--text-secondary); }
.about-tags { display: flex; gap: 6px; flex-wrap: wrap; }

/* Algorithm */
.algo-card { padding: 28px; }
.algo-card h3 { margin-bottom: 20px; font-size: 1rem; }
.algo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.algo-section.full { grid-column: 1 / -1; }
.algo-section {
  background: rgba(255,255,255,0.03); border: var(--border); border-radius: var(--r-md); padding: 16px 20px;
}
.algo-title { font-size: 0.78rem; font-weight: 700; color: var(--text-secondary); margin-bottom: 10px; }
.algo-formula {
  font-size: 1rem; font-weight: 800; color: var(--primary-light);
  font-family: 'Courier New', monospace;
  background: var(--primary-dim); border-radius: var(--r-sm); padding: 10px 14px; margin-bottom: 8px;
}
.algo-note { font-size: 0.75rem; color: var(--text-dim); }

/* Metrics */
.metrics-card { padding: 28px; }
.metrics-card h3 { margin-bottom: 20px; font-size: 1rem; }
.metrics-loading { display: flex; align-items: center; gap: 12px; padding: 20px; color: var(--text-dim); }
.metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.metric-item {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  background: rgba(255,255,255,0.03); border: var(--border); border-radius: var(--r-md);
  padding: 16px 12px; text-align: center;
}
.mi-icon { font-size: 1.2rem; }
.mi-label { font-size: 0.68rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; }
.mi-val { font-size: 0.95rem; font-weight: 800; color: var(--text); }
.mi-val.success { color: var(--accent); }

/* Tech Stack */
.stack-card { padding: 28px; }
.stack-card h3 { margin-bottom: 20px; font-size: 1rem; }
.stack-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.stack-item {
  display: flex; align-items: center; gap: 12px;
  background: rgba(255,255,255,0.03); border: var(--border); border-radius: var(--r-md);
  padding: 14px 16px;
}
.stack-icon { font-size: 1.5rem; flex-shrink: 0; }
.stack-name { font-size: 0.85rem; font-weight: 700; margin-bottom: 2px; }

@media (max-width: 768px) {
  .about-grid, .algo-grid, .metrics-grid, .stack-grid { grid-template-columns: 1fr; }
  .arch-flow { flex-direction: column; }
  .arch-arrow { transform: rotate(90deg); }
}
</style>
