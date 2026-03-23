<template>
  <div class="app-root">
    <!-- Background animated blobs -->
    <div class="bg-blob blob-1" :style="{ opacity: isDark ? 0.12 : 0.06 }"></div>
    <div class="bg-blob blob-2" :style="{ opacity: isDark ? 0.12 : 0.06 }"></div>
    <div class="bg-blob blob-3" :style="{ opacity: isDark ? 0.12 : 0.06 }"></div>

    <!-- Header -->
    <TheHeader 
      :active-tab="activeTab" 
      :is-dark="isDark"
      @tab-change="handleTabChange" 
      @theme-toggle="toggleTheme"
    />

    <!-- Main -->
    <main class="app-main">
      <transition name="tab-fade" mode="out-in">
        <RecommendTab 
          v-if="activeTab === 'recommend'" 
          :key="'rec-' + recommendKey" 
        />
        <DatabaseTab v-else-if="activeTab === 'database'" key="database" />
        <AboutTab v-else-if="activeTab === 'about'" key="about" />
        <AdminTab v-else-if="activeTab === 'admin'" key="admin" />
      </transition>
    </main>

    <!-- Footer -->
    <TheFooter />
  </div>
</template>

<script setup>
import { ref, nextTick, watch, provide } from 'vue'
import TheHeader from './components/TheHeader.vue'
import TheFooter from './components/TheFooter.vue'
import RecommendTab from './components/tabs/RecommendTab.vue'
import DatabaseTab from './components/tabs/DatabaseTab.vue'
import AboutTab from './components/tabs/AboutTab.vue'
import AdminTab from './components/tabs/AdminTab.vue'

const activeTab = ref('recommend')
const recommendKey = ref(0)
const isDark = ref(localStorage.getItem('theme') === 'dark')

// 🔥 Scroll helper (clean + chuẩn)
const scrollToForm = async () => {
  await nextTick()
  const el = document.getElementById('form-section')
  if (el) {
    const HEADER_OFFSET = -120 // 🔥 chỉnh tại đây nếu cần
    const y = el.offsetTop - HEADER_OFFSET
    window.scrollTo({ top: y, behavior: 'smooth' })
  } else {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

provide('scrollToForm', scrollToForm)

const handleTabChange = async (newTab, shouldScroll = true) => {
  if (newTab === 'recommend' && activeTab.value === 'recommend') {
    recommendKey.value++ // reset tab
  }

  activeTab.value = newTab

  if (newTab === 'recommend' && shouldScroll) {
    // delay đủ lâu để transition "out-in" hoàn tất (transition khoảng 200-350ms)
    setTimeout(() => {
      scrollToForm()
    }, 450)
  } else {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  }
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

watch(isDark, (val) => {
  document.documentElement.classList.toggle('dark-theme', val)
}, { immediate: true })
</script>

<style scoped>
.app-root {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

/* Background blobs */
.bg-blob {
  position: fixed;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
  animation: blobFloat 12s ease-in-out infinite;
}
.blob-1 {
  width: 600px; height: 600px;
  background: radial-gradient(circle, #6366f1, transparent);
  top: -200px; left: -200px;
}
.blob-2 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, #10b981, transparent);
  bottom: 100px; right: -150px;
}
.blob-3 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, #8b5cf6, transparent);
  top: 50%; left: 50%;
}

@keyframes blobFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -20px) scale(1.05); }
  66% { transform: translate(-20px, 30px) scale(0.95); }
}

.app-main {
  position: relative;
  z-index: 1;
  padding-top: 70px;
}

/* Transition */
.tab-fade-enter-active { animation: tabSlide 0.35s cubic-bezier(0.34, 1.56, 0.64, 1); }
.tab-fade-leave-active { animation: tabSlide 0.2s ease reverse; }

@keyframes tabSlide {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>