<template>
  <div class="recommend-tab">
    <!-- ===== HERO ===== -->
    <section class="hero">
      <div class="hero-content">
        <div class="hero-badge badge badge-primary">🤖 AI-Powered Decision Support System</div>
        <h1>Chọn Xe Máy<br /><span class="gradient-text">Thông Minh Hơn</span></h1>
        <p class="hero-desc">
          Hệ thống sử dụng <strong>Random Forest AI</strong> kết hợp phương pháp <strong>AHP</strong>
          để phân tích hồ sơ và đề xuất xe máy phù hợp nhất với bạn.
        </p>
        <div class="hero-stats">
          <div class="stat-item">
            <span class="stat-num">{{ stats.total || 98 }}</span>
            <span class="stat-label">Mẫu xe</span>
          </div>
          <div class="stat-div"></div>
          <div class="stat-item">
            <span class="stat-num">5</span>
            <span class="stat-label">Tiêu chí AHP</span>
          </div>
          <div class="stat-div"></div>
          <div class="stat-item">
            <span class="stat-num">300</span>
            <span class="stat-label">Mẫu train</span>
          </div>
          <div class="stat-div"></div>
          <div class="stat-item">
            <span class="stat-num gradient-text">RF</span>
            <span class="stat-label">Random Forest</span>
          </div>
        </div>
        <a href="#form-section" class="btn btn-primary hero-cta">
          🔍 Bắt đầu tư vấn
          <span class="cta-arrow">↓</span>
        </a>
      </div>
      <div class="hero-visual">
        <div class="orbit-ring ring-1"></div>
        <div class="orbit-ring ring-2"></div>
        <div class="orbit-ring ring-3"></div>
        <div class="center-icon">🏍️</div>
        <div class="float-badge fb-1">AI</div>
        <div class="float-badge fb-2">AHP</div>
        <div class="float-badge fb-3">DSS</div>
      </div>
    </section>

    <!-- ===== WIZARD: Manual AHP ===== -->
    <div class="tab-body" id="form-section">
      <ManualAHPWizard />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ManualAHPWizard from '../ManualAHPWizard.vue'
import { getStats } from '../../api.js'

const stats = ref({})

onMounted(async () => {
  try {
    stats.value = await getStats()
  } catch {}
})
</script>

<style scoped>
.recommend-tab { min-height: 100vh; }

/* ===== HERO ===== */
.hero {
  max-width: 1400px; margin: 0 auto;
  padding: 80px 24px 60px;
  display: grid; grid-template-columns: 1fr 1fr; gap: 60px; align-items: center;
  position: relative;
}

.hero-content { display: flex; flex-direction: column; gap: 20px; }
.hero-badge { align-self: flex-start; }
.hero-desc { font-size: 1rem; line-height: 1.7; max-width: 520px; }
.hero-desc strong { color: var(--text); }

.hero-stats {
  display: flex; align-items: center; gap: 0;
  background: var(--glass); border: var(--border); border-radius: var(--r-xl);
  padding: 16px 20px; gap: 0; width: fit-content;
}
.stat-item { display: flex; flex-direction: column; align-items: center; gap: 2px; padding: 0 20px; }
.stat-num { font-size: 1.6rem; font-weight: 900; color: var(--text); line-height: 1; }
.stat-label { font-size: 0.7rem; color: var(--text-dim); font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
.stat-div { width: 1px; height: 36px; background: rgba(255,255,255,0.08); }

.hero-cta { padding: 14px 28px; font-size: 0.95rem; width: fit-content; }
.cta-arrow { display: inline-block; animation: bounce 2s ease infinite; }
@keyframes bounce { 0%,100% { transform: translateY(0); } 50% { transform: translateY(4px); } }

/* Hero Visual - Orbital Rings */
.hero-visual {
  position: relative; width: 380px; height: 380px; margin: 0 auto;
}
.orbit-ring {
  position: absolute; border-radius: 50%;
  border: 1px solid rgba(99,102,241,0.2);
  top: 50%; left: 50%;
}
.ring-1 { width: 200px; height: 200px; transform: translate(-50%, -50%); animation: orbit 12s linear infinite; }
.ring-2 { width: 290px; height: 290px; transform: translate(-50%, -50%); animation: orbit 18s linear infinite reverse; border-color: rgba(16,185,129,0.15); }
.ring-3 { width: 370px; height: 370px; transform: translate(-50%, -50%); animation: orbit 24s linear infinite; border-color: rgba(139,92,246,0.12); }
@keyframes orbit { from { transform: translate(-50%, -50%) rotate(0deg); } to { transform: translate(-50%, -50%) rotate(360deg); } }

.center-icon {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  font-size: 5rem; filter: drop-shadow(0 0 30px rgba(99,102,241,0.6));
  animation: float 4s ease-in-out infinite;
}
@keyframes float { 0%,100% { transform: translate(-50%,-50%) translateY(0); } 50% { transform: translate(-50%,-50%) translateY(-12px); } }

.float-badge {
  position: absolute;
  background: var(--glass); border: var(--glass-border) solid rgba(255,255,255,0.1);
  border-radius: var(--r-md); padding: 8px 14px;
  font-weight: 800; font-size: 0.85rem; color: var(--primary-light);
  backdrop-filter: blur(10px);
}
.fb-1 { top: 20%; right: 5%; animation: floatBadge 3s ease-in-out infinite; }
.fb-2 { bottom: 25%; right: 0%; animation: floatBadge 3.5s ease-in-out infinite 1s; }
.fb-3 { bottom: 15%; left: 5%; animation: floatBadge 4s ease-in-out infinite 0.5s; }
@keyframes floatBadge { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }

/* Tab Body */
.tab-body {
  max-width: 1400px; margin: 0 auto;
  padding: 0 24px 80px;
}

@media (max-width: 900px) {
  .hero { grid-template-columns: 1fr; padding: 40px 20px; text-align: center; }
  .hero-visual { display: none; }
  .hero-badge, .hero-cta { align-self: center; }
  .hero-stats { width: 100%; justify-content: center; }
}
</style>
