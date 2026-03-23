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

    <!-- Feature Highlights -->
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
  try {
    const data = await healthCheck()
    health.value = data
  } catch {}
  finally {
    metricsLoading.value = false
  }
})

const importanceData = {
  labels: ['Thu nhập & Ngân sách', 'Mục đích sử dụng', 'Tần suất đi lại', 'Độ tuổi', 'Giới tính', 'Khu vực sống'],
  datasets: [{
    label: 'Mức độ ảnh hưởng (%)',
    data: [38, 25, 18, 12, 4, 3],
    backgroundColor: [
      'rgba(99, 102, 241, 0.8)',
      'rgba(37, 99, 235, 0.7)',
      'rgba(16, 185, 129, 0.6)',
      'rgba(245, 158, 11, 0.5)',
      'rgba(236, 72, 153, 0.4)',
      'rgba(107, 114, 128, 0.3)'
    ],
    borderRadius: 8,
    borderWidth: 0,
    barThickness: 30
  }]
}

const importanceOptions = {
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      titleFont: { size: 14, weight: 'bold' },
      bodyFont: { size: 13 },
      padding: 12,
      displayColors: false
    }
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { color: 'rgba(156, 163, 175, 0.8)', font: { weight: '600' } }
    },
    y: {
      grid: { display: false },
      ticks: { color: 'rgba(156, 163, 175, 1)', font: { weight: '700', size: 12 } }
    }
  }
}

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
.page-container { max-width: 1400px; margin: 0 auto; padding: 30px 32px 60px; display: flex; flex-direction: column; gap: 32px; }

.section-title h2 { font-size: 2.8rem; margin-bottom: 15px; }
.section-title p { font-size: 1.3rem; }

/* Architecture */
.arch-card { padding: 36px; }
.arch-card h3 { margin-bottom: 30px; font-size: 1.25rem; font-weight: 800; }
.arch-flow { display: flex; align-items: center; flex-wrap: wrap; gap: 12px; }
.arch-step-wrap { display: flex; align-items: center; gap: 12px; }
.arch-step {
  display: flex; flex-direction: column; align-items: center; gap: 8px; text-align: center;
  padding: 18px 20px; border-radius: var(--r-lg); 
  background: var(--bg-item); border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm); transition: var(--transition);
  min-width: 130px;
}
.arch-step:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); border-color: var(--primary-light); }
.step-ai { background: rgba(99, 102, 241, 0.1) !important; border-color: rgba(99, 102, 241, 0.3) !important; }
.step-filter { background: rgba(245, 158, 11, 0.05) !important; border-color: rgba(245, 158, 11, 0.2) !important; }
.step-result { background: rgba(16, 185, 129, 0.1) !important; border-color: rgba(16, 185, 129, 0.3) !important; }
.arch-icon { font-size: 2.2rem; margin-bottom: 2px; }
.arch-label { font-size: 0.95rem; font-weight: 850; color: var(--text-header); }
.arch-sub { font-size: 0.75rem; color: var(--text-secondary); }
.arch-arrow { font-size: 1.4rem; color: var(--primary); opacity: 0.5; font-weight: 900; }

/* About Grid */
.about-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }
.about-card { padding: 32px; display: flex; flex-direction: column; gap: 14px; }
.about-card-icon { font-size: 2.6rem; }
.about-card h3 { font-size: 1.35rem; font-weight: 800; }
.about-card p { font-size: 1.05rem; line-height: 1.7; color: var(--text-secondary); }
.about-tags .badge { font-size: 0.85rem; padding: 6px 14px; }

/* Algorithm */
.algo-card { padding: 36px; }
.algo-card h3 { margin-bottom: 28px; font-size: 1.25rem; font-weight: 800; }
.algo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.algo-section.full { grid-column: 1 / -1; }
.algo-section {
  background: var(--bg-2); border: var(--border); border-radius: var(--r-md); padding: 22px 28px;
}
.algo-title { font-size: 1rem; font-weight: 800; color: var(--text-header); margin-bottom: 12px; }
.algo-formula {
  font-size: 1.3rem; font-weight: 900; color: var(--primary);
  font-family: 'Courier New', monospace;
  background: var(--primary-dim); border-radius: var(--r-sm); padding: 14px 20px; margin-bottom: 10px;
  letter-spacing: 0.5px;
}
.algo-note { font-size: 0.95rem; color: var(--text-dim); }

/* Metrics */
.metrics-card { padding: 36px; }
.metrics-card h3 { margin-bottom: 28px; font-size: 1.25rem; font-weight: 800; }
.metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.metric-item {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  background: var(--bg-2); border: var(--border); border-radius: var(--r-md);
  padding: 24px 16px; text-align: center;
}
.mi-icon { font-size: 1.6rem; }
.mi-label { font-size: 0.85rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.8px; font-weight: 700; }
.mi-val { font-size: 1.2rem; font-weight: 900; color: var(--text-header); }

/* Tech Stack */
.stack-card { padding: 36px; }
.stack-card h3 { margin-bottom: 28px; font-size: 1.25rem; font-weight: 800; }
.stack-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.stack-item {
  display: flex; align-items: center; gap: 18px;
  background: var(--bg-2); border: var(--border); border-radius: var(--r-md);
  padding: 20px 24px;
}
.stack-icon { font-size: 2.2rem; }
.stack-name { font-size: 1.1rem; font-weight: 800; margin-bottom: 4px; }
.stack-desc { font-size: 0.85rem !important; }

@media (max-width: 992px) {
  .about-grid, .algo-grid, .metrics-grid, .stack-grid { grid-template-columns: 1fr; }
  .arch-flow { justify-content: center; }
}

/* Feature Importance Chart Styles */
.importance-card { padding: 36px; }
.card-header-with-info { margin-bottom: 30px; }
.card-header-with-info h3 { font-size: 1.25rem; font-weight: 800; margin-bottom: 6px; }
.chart-container { height: 400px; width: 100%; position: relative; }
</style>
