<template>
  <header class="header">
    <div class="header-inner">
      <!-- Logo -->
      <div class="logo">
        <span class="logo-icon">🏍️</span>
        <div>
          <div class="logo-title">Motor<span class="logo-accent">Choice</span></div>
          <div class="logo-sub">DSS · AI · AHP</div>
        </div>
      </div>

      <!-- Desktop Nav -->
      <nav class="nav">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="nav-btn"
          :class="{ active: activeTab === tab.id }"
          @click="$emit('tab-change', tab.id)"
        >
          <span class="nav-icon">{{ tab.icon }}</span>
          <span class="nav-label">{{ tab.label }}</span>
        </button>
      </nav>

      <!-- Status Dot -->
      <div class="status-indicator" :class="statusClass" :data-tooltip="statusText">
        <span class="status-dot"></span>
        <span class="status-label">{{ statusText }}</span>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { healthCheck } from '../api.js'

const props = defineProps({ activeTab: String })
const emit = defineEmits(['tab-change'])

const systemStatus = ref('loading') // 'ok' | 'loading' | 'error'

const statusClass = computed(() => ({
  'status-ok': systemStatus.value === 'ok',
  'status-loading': systemStatus.value === 'loading',
  'status-error': systemStatus.value === 'error',
}))

const statusText = computed(() => ({
  ok: 'Hệ thống sẵn sàng',
  loading: 'Đang kết nối...',
  error: 'Mất kết nối backend'
})[systemStatus.value])

const tabs = [
  { id: 'recommend', icon: '🔍', label: 'Tư vấn xe' },
  { id: 'database', icon: '🗃️', label: 'Cơ sở dữ liệu' },
  { id: 'ahp', icon: '⚖️', label: 'AHP Calculator' },
  { id: 'about', icon: '📊', label: 'Về hệ thống' },
]

onMounted(async () => {
  try {
    const data = await healthCheck()
    systemStatus.value = data.model_trained ? 'ok' : 'error'
  } catch {
    systemStatus.value = 'error'
  }
})
</script>

<style scoped>
.header {
  position: fixed; top: 0; left: 0; right: 0; z-index: 900;
  background: rgba(8, 12, 20, 0.85);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255,255,255,0.07);
  height: 70px;
}
.header-inner {
  max-width: 1400px; margin: 0 auto;
  padding: 0 24px;
  height: 100%;
  display: flex; align-items: center; justify-content: space-between; gap: 20px;
}

/* Logo */
.logo { display: flex; align-items: center; gap: 12px; text-decoration: none; flex-shrink: 0; }
.logo-icon { font-size: 1.8rem; filter: drop-shadow(0 0 10px rgba(99,102,241,0.5)); }
.logo-title { font-size: 1.1rem; font-weight: 900; color: var(--text); letter-spacing: -0.5px; }
.logo-accent { color: var(--primary-light); }
.logo-sub { font-size: 0.65rem; color: var(--text-dim); letter-spacing: 1.5px; font-weight: 500; text-transform: uppercase; }

/* Nav */
.nav { display: flex; gap: 4px; }
.nav-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 14px; border-radius: var(--r-md);
  background: transparent; border: 1px solid transparent;
  color: var(--text-secondary); cursor: pointer;
  font-family: var(--font); font-size: 0.82rem; font-weight: 500;
  transition: var(--transition); white-space: nowrap;
}
.nav-btn:hover { background: rgba(255,255,255,0.06); color: var(--text); }
.nav-btn.active {
  background: var(--primary-dim);
  border-color: rgba(99,102,241,0.3);
  color: var(--primary-light);
  font-weight: 600;
}
.nav-icon { font-size: 0.9rem; }

/* Status Indicator */
.status-indicator {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 12px; border-radius: 99px;
  font-size: 0.72rem; font-weight: 600; cursor: default;
  transition: var(--transition);
}
.status-dot {
  width: 7px; height: 7px; border-radius: 50%;
  flex-shrink: 0;
}
.status-ok .status-dot { background: var(--accent); box-shadow: 0 0 6px var(--accent); animation: pulse 2s infinite; }
.status-ok { background: var(--accent-dim); border: 1px solid rgba(16,185,129,0.2); color: var(--accent); }

.status-loading .status-dot { background: var(--accent2); animation: pulse 1s infinite; }
.status-loading { background: var(--accent2-dim); border: 1px solid rgba(245,158,11,0.2); color: var(--accent2); }

.status-error .status-dot { background: var(--danger); }
.status-error { background: var(--danger-dim); border: 1px solid rgba(239,68,68,0.2); color: var(--danger); }

.status-label { display: none; }
@media (min-width: 768px) { .status-label { display: inline; } }

@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }

@media (max-width: 640px) {
  .nav-label { display: none; }
  .nav-btn { padding: 8px 10px; }
  .header-inner { gap: 12px; }
}
</style>
