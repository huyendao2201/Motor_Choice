<template>
  <header class="header">
    <div class="header-inner">
      <!-- Logo (Home - No scroll to form) -->
      <div class="logo" @click="$emit('tab-change', 'recommend', false)" style="cursor: pointer;">
        <div class="logo-icon">
          <img src="/logo-bike.png" alt="Logo" style="max-width: 100%; max-height: 100%; object-fit: contain;" />
        </div>
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
          @click="$emit('tab-change', tab.id, true)"
        >
          <span class="nav-icon">{{ tab.icon }}</span>
          <span class="nav-label">{{ tab.label }}</span>
        </button>
      </nav>

      <!-- Theme Toggle & Status -->
      <div class="header-actions">
        <button class="theme-toggle" @click="$emit('theme-toggle')" :title="isDark ? 'Chế độ sáng' : 'Chế độ tối'">
          <span v-if="isDark">☀️</span>
          <span v-else>🌙</span>
        </button>

        <div class="status-indicator" :class="statusClass">
          <span class="status-dot"></span>
          <span class="status-label">{{ statusText }}</span>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { healthCheck } from '../api.js'

const props = defineProps({ 
  activeTab: String,
  isDark: Boolean
})
const emit = defineEmits(['tab-change', 'theme-toggle'])

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
  { id: 'database', icon: '🗃️', label: 'Danh sách xe' },
  { id: 'admin', icon: '🛠️', label: 'Admin' },
  { id: 'about', icon: '📊', label: 'Về hệ thống' },
]

onMounted(() => {
  const check = async () => {
    try {
      const data = await healthCheck()
      systemStatus.value = data.model_trained ? 'ok' : 'error'
    } catch {
      systemStatus.value = 'error'
    }
  }
  
  check() // Check immediately
  setInterval(check, 30000) // Re-check every 30 seconds
})
</script>

<style scoped>
.header {
  position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
  background: var(--glass);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-color);
  height: 72px;
  display: flex; align-items: center;
}
.header-inner {
  max-width: 1400px; margin: 0 auto;
  width: 100%;
  padding: 0 40px;
  display: flex; align-items: center; justify-content: space-between; gap: 30px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.theme-toggle {
  background: var(--bg-card);
  border: var(--border);
  width: 40px;
  height: 40px;
  border-radius: var(--r-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  transition: var(--transition);
  color: var(--text-header);
  box-shadow: var(--shadow-sm);
  outline: none;
}
.theme-toggle:focus { outline: none; }

.theme-toggle:hover {
  background: var(--bg-2);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* Logo */
.logo { display: flex; align-items: center; gap: 14px; text-decoration: none; flex-shrink: 0; }
.logo-icon { 
  font-size: 2.2rem; filter: drop-shadow(0 0 15px rgba(67, 56, 202, 0.4)); 
  background: var(--bg-card); width: 48px; height: 48px; 
  display: flex; align-items: center; justify-content: center; 
  border-radius: 14px; border: var(--border); 
}
.logo-title { font-size: 1.4rem; font-weight: 900; color: var(--text-header); letter-spacing: -0.5px; }
.logo-accent { color: var(--primary); }
.logo-sub { font-size: 0.7rem; color: var(--text-dim); letter-spacing: 2px; font-weight: 700; text-transform: uppercase; margin-top: -2px; }

/* Nav */
.nav { display: flex; gap: 6px; padding: 4px; background: rgba(0,0,0,0.03); border-radius: 16px; border: var(--border); }
.nav-btn {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 18px; border-radius: 12px;
  background: transparent; border: none;
  color: var(--text-secondary); cursor: pointer;
  font-family: var(--font); font-size: 1.05rem; font-weight: 800;
  transition: var(--transition); white-space: nowrap;
}
.nav-btn:hover { color: var(--text-header); transform: scale(1.02); }
.nav-btn.active {
  background: var(--bg-card);
  color: var(--primary);
  box-shadow: 0 4px 12px rgba(67, 56, 202, 0.08);
  border: 1px solid var(--primary-light);
}
.dark-theme .nav-btn.active { border-color: var(--primary); }
.nav-icon { font-size: 1rem; }

/* Status Indicator */
.status-indicator {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 16px; border-radius: 12px;
  font-size: 0.95rem; font-weight: 800; cursor: default;
  transition: var(--transition);
  border: var(--border);
  box-shadow: var(--shadow-sm);
}
.status-dot {
  width: 8px; height: 8px; border-radius: 50%;
  flex-shrink: 0;
}
.status-ok .status-dot { background: var(--accent); box-shadow: 0 0 10px var(--accent); animation: pulse 2s infinite; }
.status-ok { background: var(--bg-card); color: var(--accent); }

.status-loading .status-dot { background: var(--accent2); animation: pulse 1s infinite; }
.status-loading { background: var(--bg-card); color: var(--accent2); }

.status-error .status-dot { background: var(--danger); }
.status-error { background: var(--bg-card); color: var(--danger); border-color: var(--danger-dim); }

.status-label { display: none; }
@media (min-width: 1024px) { .status-label { display: inline; } }

@keyframes pulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.9); } }

@media (max-width: 900px) {
  .nav-label { display: none; }
  .nav-btn { padding: 10px; }
  .header-inner { padding: 0 20px; gap: 12px; }
  .logo-sub { display: none; }
}
</style>
