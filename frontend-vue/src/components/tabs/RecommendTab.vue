<template>
  <div class="recommend-tab">
    <!-- ===== HERO ===== -->
    <section class="hero">
      <div class="hero-content">
        <div class="hero-badge badge badge-primary">🤖 AI tư vấn chọn xe máy - Hệ hỗ trợ ra quyết định</div>
        <h1>Khám Phá Xe Lý Tưởng<br /><span class="gradient-text">Dành Riêng Cho Bạn</span></h1>
        <p class="hero-desc">
          Giải pháp <span class="highlight">AI</span> tư vấn xe máy dựa trên <span class="highlight">Random Forest</span> & <span class="highlight">AHP</span>.<br />
          Phân tích đa tiêu chí để cá nhân hóa đề xuất cho từng người dùng.
        </p>
        
        <div class="hero-actions">
          <button @click="scrollToForm" class="btn btn-primary hero-cta">
            Tìm xe phù hợp ngay 🚀
            <span class="cta-arrow">↓</span>
          </button>
          <div class="trust-signals">
            <span class="trust-item">Phân tích thông minh</span>
            <span class="trust-sep"></span>
            <span class="trust-item">Đề xuất cá nhân hóa</span>
          </div>
        </div>

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
      </div>
      <div class="hero-visual">
        <div class="orbit-ring ring-1"></div>
        <div class="orbit-ring ring-2"></div>
        <div class="orbit-ring ring-3"></div>
        <div class="center-icon">
          <img src="/hero-bike.png" alt="Motorcycle" class="hero-bike-img" />
        </div>
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
import { ref, onMounted, inject } from 'vue'
import ManualAHPWizard from '../ManualAHPWizard.vue'
import { getStats } from '../../api.js'

const stats = ref({})
const scrollToForm = inject('scrollToForm')

onMounted(async () => {
  try {
    stats.value = await getStats()
  } catch {}
})
</script>

<style scoped>
.recommend-tab { min-height: 100vh; position: relative; }

/* ===== HERO ===== */
.hero {
  max-width: 1400px; margin: 0 auto;
  min-height: calc(100vh - 72px); /* Full height minus header */
  padding: 60px 40px 10vh;
  display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 80px; align-items: center;
  position: relative;
  overflow: visible;
}

.hero-content { display: flex; flex-direction: column; gap: 28px; z-index: 10; transform: translateY(-40px); animation: slideUp 0.8s cubic-bezier(0.22, 1, 0.36, 1) forwards; }

@keyframes slideUp { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }

.badge-primary {
  align-self: flex-start;
  padding: 8px 16px; border-radius: 99px;
  background: var(--primary-dim); color: var(--primary);
  font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;
  border: 1px solid rgba(67, 56, 202, 0.1);
}

h1 { font-size: 3.8rem; line-height: 1.1; margin: 0; }
.gradient-text { background: var(--grad-hero); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

.hero-desc { font-size: 1.15rem; color: var(--text-secondary); line-height: 1.8; max-width: 580px; }
.highlight { color: var(--primary); font-weight: 800; background: var(--primary-dim); padding: 2px 6px; border-radius: 6px; }

.hero-cta { 
  padding: 18px 36px; font-size: 1.15rem; width: fit-content; 
  border-radius: 18px; position: relative; overflow: hidden;
  box-shadow: 0 15px 35px -5px rgba(37, 99, 235, 0.4);
}
.hero-actions { display: flex; flex-direction: column; gap: 20px; }
.trust-signals { display: flex; align-items: center; gap: 16px; margin-left: 4px; }
.trust-item { 
  font-size: 0.9rem; font-weight: 600; color: var(--text-dim); 
  display: flex; align-items: center; gap: 8px;
}
.trust-item::before { content: '✓'; color: var(--primary); font-weight: 900; }
.trust-sep { width: 4px; height: 4px; background: var(--border-color); border-radius: 50%; }
.hero-cta::after {
  content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255,255,255,0.2), transparent);
  transform: rotate(45deg); animation: shine 3s infinite;
}
@keyframes shine { 0% { left: -100%; } 100% { left: 100%; } }

.hero-stats {
  display: flex; align-items: center;
  background: var(--bg-card); 
  border: 1px solid var(--border-color); 
  border-radius: 20px;
  padding: 20px; gap: 0; width: fit-content;
  box-shadow: var(--shadow-md);
  margin-top: 10px;
}
.stat-item { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 0 24px; }
.stat-num { font-size: 1.8rem; font-weight: 900; color: var(--text-header); line-height: 1; font-family: 'Outfit'; }
.stat-label { font-size: 0.7rem; color: var(--text-dim); font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
.stat-div { width: 1px; height: 32px; background: var(--border-color); opacity: 0.5; }

/* Hero Visual - Orbital */
.hero-visual {
  position: relative; width: 600px; height: 600px; margin: 0 auto;
  animation: fadeIn 1s ease-out 0.3s forwards; opacity: 0;
}
@keyframes fadeIn { from { opacity: 0; scale: 0.9; } to { opacity: 1; scale: 1; } }

.orbit-ring {
  position: absolute; border-radius: 50%;
  border: 2px solid var(--primary);
  top: 50%; left: 50%;
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.3), inset 0 0 20px rgba(59, 130, 246, 0.15);
}
.ring-1 { width: 320px; height: 320px; transform: translate(-50%, -50%); animation: orbit 18s linear infinite, pulseGlow 4s ease-in-out infinite; border-color: rgba(59, 130, 246, 0.8); border-width: 4px; }
.ring-2 { width: 460px; height: 460px; transform: translate(-50%, -50%); animation: orbit 25s linear infinite reverse, pulseGlow 5s ease-in-out infinite 0.5s; border-color: rgba(59, 130, 246, 0.6); border-width: 3px; }
.ring-3 { width: 600px; height: 600px; transform: translate(-50%, -50%); animation: orbit 35s linear infinite, pulseGlow 6s ease-in-out infinite 1s; border-color: rgba(59, 130, 246, 0.4); border-width: 2px; }
@keyframes orbit { from { transform: translate(-50%, -50%) rotate(0deg); } to { transform: translate(-50%, -50%) rotate(360deg); } }
@keyframes pulseGlow { 
  0%, 100% { opacity: 0.6; scale: 1; filter: blur(0px); } 
  50% { opacity: 1; scale: 1.03; filter: blur(1px); box-shadow: 0 0 50px rgba(59, 130, 246, 0.6), inset 0 0 30px rgba(59, 130, 246, 0.4); } 
}


.center-icon {
  position: absolute; top: 50%; left: 50%;
  width: 340px; height: 340px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(1px);
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
  display: flex; align-items: center; justify-content: center;
  transform: translate(-50%, -50%);
  box-shadow: 0 40px 80px rgba(37, 99, 235, 0.1), var(--shadow-glow);
  animation: float 6s ease-in-out infinite;
  z-index: 5;
}

.hero-bike-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.1); /* Minor zoom for better framing */
}
@keyframes float { 0%,100% { transform: translate(-50%,-50%) translateY(0) rotate(0.5deg); } 50% { transform: translate(-50%,-50%) translateY(-30px) rotate(-0.5deg); } }

.float-badge {
  position: absolute; z-index: 6;
  background: var(--bg-card); 
  border: 1px solid var(--primary-light);
  border-radius: 12px; padding: 10px 22px;
  font-weight: 900; font-size: 0.95rem; color: var(--primary);
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 30px -5px rgba(37, 99, 235, 0.15);
  transition: var(--transition);
}
.fb-1 { top: 15%; right: 10%; animation: floatBadge 3s ease-in-out infinite; }
.fb-2 { bottom: 20%; right: 5%; animation: floatBadge 3.5s ease-in-out infinite 1s; }
.fb-3 { bottom: 30%; left: -5%; animation: floatBadge 4s ease-in-out infinite 0.5s; }
@keyframes floatBadge { 0%,100% { transform: translateY(0) scale(1); } 50% { transform: translateY(-12px) scale(1.05); } }

/* Tab Body */
.tab-body {
  padding-top: 20px;
}

@media (max-width: 1024px) {
  h1 { font-size: 3rem; }
  .hero { gap: 40px; }
  .hero-visual { width: 350px; height: 350px; }
  .ring-1 { width: 180px; height: 180px; }
  .ring-2 { width: 260px; height: 260px; }
  .ring-3 { width: 340px; height: 340px; }
}

@media (max-width: 900px) {
  .hero { grid-template-columns: 1fr; padding: 60px 40px; text-align: center; }
  .hero-visual { display: none; }
  .badge-primary, .hero-cta { align-self: center; }
  .hero-stats { width: 100%; justify-content: center; }
  .hero-desc { margin: 0 auto; }
}
</style>
