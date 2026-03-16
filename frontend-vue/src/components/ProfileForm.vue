<template>
  <div class="profile-form-wrap">
    <div class="form-header">
      <h2>Nhập Thông Tin Cá Nhân</h2>
      <p>AI sẽ phân tích hồ sơ và dự đoán trọng số AHP phù hợp nhất với bạn</p>
    </div>

    <form class="profile-form" @submit.prevent="handleSubmit">
      <div class="form-grid">

        <!-- Card 1: Cơ bản -->
        <div class="form-card glass-card">
          <div class="card-header">
            <span>👤</span><h3>Thông Tin Cơ Bản</h3>
          </div>

          <div class="form-group">
            <label>💰 Ngân sách</label>
            <div class="range-row">
              <input type="range" v-model.number="form.budget" min="10" max="300" step="5" />
              <div class="range-value">{{ form.budget }}M<span class="range-unit">VNĐ</span></div>
            </div>
            <div class="range-hints"><span>10M</span><span>300M</span></div>
          </div>

          <div class="form-group">
            <label>📍 Quãng đường hàng ngày</label>
            <div class="range-row">
              <input type="range" v-model.number="form.daily_distance_km" min="1" max="200" step="1" />
              <div class="range-value">{{ form.daily_distance_km }}<span class="range-unit">km</span></div>
            </div>
            <div class="range-hints"><span>1km</span><span>200km</span></div>
          </div>
        </div>

        <!-- Card 2: Mục đích -->
        <div class="form-card glass-card">
          <div class="card-header">
            <span>🎯</span><h3>Mục Đích Sử Dụng</h3>
          </div>

          <div class="form-group">
            <label>Bạn là ai?</label>
            <div class="radio-grid">
              <label
                v-for="opt in purposeOptions"
                :key="opt.value"
                class="radio-card"
                :class="{ active: form.purpose === opt.value }"
              >
                <input type="radio" :value="opt.value" v-model="form.purpose" />
                <span class="rc-icon">{{ opt.icon }}</span>
                <span class="rc-label">{{ opt.label }}</span>
                <span class="rc-desc">{{ opt.desc }}</span>
              </label>
            </div>
          </div>

          <div class="form-group">
            <label>Loại xe ưa thích</label>
            <div class="radio-grid vehicle-grid">
              <label
                v-for="opt in vehicleOptions"
                :key="opt.value"
                class="radio-card"
                :class="{ active: form.vehicle_type_preference === opt.value }"
              >
                <input type="radio" :value="opt.value" v-model="form.vehicle_type_preference" />
                <span class="rc-icon">{{ opt.icon }}</span>
                <span class="rc-label">{{ opt.label }}</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Card 3: Độ ưu tiên (full width) -->
        <div class="form-card glass-card full-width">
          <div class="card-header">
            <span>⚖️</span>
            <h3>Mức Độ Ưu Tiên Các Tiêu Chí</h3>
            <span class="badge badge-primary ml-auto">AI tự điều chỉnh trọng số AHP</span>
          </div>

          <div class="priority-grid">
            <div v-for="p in priorityItems" :key="p.key" class="priority-item">
              <div class="priority-header">
                <span class="priority-label">{{ p.icon }} {{ p.label }}</span>
                <span class="priority-value" :style="{ color: p.color }">
                  {{ form[p.key] }}%
                </span>
              </div>
              <div class="priority-track">
                <div
                  class="priority-fill"
                  :style="{ width: form[p.key] + '%', background: p.color }"
                ></div>
                <input
                  type="range"
                  :style="{ '--thumb-color': p.color }"
                  :min="0" :max="100" :step="5"
                  v-model.number="form[p.key]"
                  class="priority-range overlay-range"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Card 4: Bộ lọc nâng cao (collapse) -->
        <div class="form-card glass-card full-width">
          <button type="button" class="collapse-toggle" @click="showAdvanced = !showAdvanced">
            <span>⚙️ Bộ Lọc Nâng Cao (Tùy chọn)</span>
            <span class="toggle-arrow" :class="{ open: showAdvanced }">▾</span>
          </button>
          <transition name="collapse">
            <div v-if="showAdvanced" class="advanced-grid">
              <div class="form-group">
                <label>Dung tích tối thiểu (cc)</label>
                <input type="number" v-model.number="form.min_engine_cc" placeholder="Ví dụ: 110" class="input-text" min="50" max="1000" />
              </div>
              <div class="form-group">
                <label>Dung tích tối đa (cc)</label>
                <input type="number" v-model.number="form.max_engine_cc" placeholder="Ví dụ: 160" class="input-text" min="50" max="1000" />
              </div>
              <div class="form-group">
                <label>Số xe đề xuất</label>
                <select v-model.number="form.top_n" class="input-text">
                  <option v-for="n in [3,5,6,8,10]" :key="n" :value="n">Top {{ n }}</option>
                </select>
              </div>
            </div>
          </transition>
        </div>

      </div><!-- /form-grid -->

      <!-- Actions -->
      <div class="form-actions">
        <button type="button" class="btn btn-secondary" @click="loadDemo(0)">🎓 Demo: Sinh viên</button>
        <button type="button" class="btn btn-secondary" @click="loadDemo(1)">💼 Demo: Văn phòng</button>
        <button type="submit" class="btn btn-primary submit-btn" :disabled="loading">
          <span v-if="loading" class="spinner" style="width:18px;height:18px;border-width:2px;"></span>
          <span>{{ loading ? 'Đang phân tích AI...' : '🔍 Tìm xe phù hợp' }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const props = defineProps({ loading: Boolean })
const emit = defineEmits(['submit', 'demo'])

const showAdvanced = ref(false)

const form = reactive({
  budget: 40,
  purpose: 0,
  vehicle_type_preference: 0,
  daily_distance_km: 20,
  priority_price: 50,
  priority_fuel: 40,
  priority_performance: 30,
  priority_design: 30,
  priority_brand: 25,
  top_n: 6,
  min_engine_cc: null,
  max_engine_cc: null
})

const purposeOptions = [
  { value: 0, icon: '🎓', label: 'Sinh viên', desc: 'Ưu tiên giá & xăng' },
  { value: 1, icon: '💼', label: 'Văn phòng', desc: 'Ưu tiên thiết kế & thương hiệu' },
  { value: 2, icon: '🏕️', label: 'Đi tour', desc: 'Ưu tiên hiệu năng' },
  { value: 3, icon: '📦', label: 'Dịch vụ', desc: 'Ưu tiên tiết kiệm & bền' },
]

const vehicleOptions = [
  { value: 0, icon: '⚙️', label: 'Xe số' },
  { value: 1, icon: '🛵', label: 'Tay ga' },
  { value: 2, icon: '🏍️', label: 'Côn tay' },
  { value: 3, icon: '🔍', label: 'Tất cả' },
]

const priorityItems = [
  { key: 'priority_price', icon: '💰', label: 'Giá thành', color: '#f59e0b' },
  { key: 'priority_fuel', icon: '⛽', label: 'Tiết kiệm xăng', color: '#10b981' },
  { key: 'priority_performance', icon: '⚡', label: 'Hiệu năng', color: '#6366f1' },
  { key: 'priority_design', icon: '🎨', label: 'Thiết kế', color: '#ec4899' },
  { key: 'priority_brand', icon: '🏅', label: 'Thương hiệu', color: '#8b5cf6' },
]

const DEMOS = [
  { budget: 25, purpose: 0, vehicle_type_preference: 0, daily_distance_km: 15,
    priority_price: 70, priority_fuel: 60, priority_performance: 30, priority_design: 20, priority_brand: 20 },
  { budget: 70, purpose: 1, vehicle_type_preference: 1, daily_distance_km: 20,
    priority_price: 20, priority_fuel: 20, priority_performance: 40, priority_design: 70, priority_brand: 60 }
]

function loadDemo(idx) {
  Object.assign(form, DEMOS[idx])
}

function handleSubmit() {
  // Validate
  const totalPriority = form.priority_price + form.priority_fuel + form.priority_performance + form.priority_design + form.priority_brand
  if (totalPriority === 0) {
    alert('Vui lòng đặt ít nhất một tiêu chí ưu tiên > 0%')
    return
  }

  // Build payload (convert % → 0-1)
  const payload = {
    budget: form.budget,
    purpose: form.purpose,
    vehicle_type_preference: form.vehicle_type_preference,
    daily_distance_km: form.daily_distance_km,
    priority_price: form.priority_price / 100,
    priority_fuel: form.priority_fuel / 100,
    priority_performance: form.priority_performance / 100,
    priority_design: form.priority_design / 100,
    priority_brand: form.priority_brand / 100,
    top_n: form.top_n,
    min_engine_cc: form.min_engine_cc || null,
    max_engine_cc: form.max_engine_cc || null,
  }
  emit('submit', payload)
}
</script>

<style scoped>
.profile-form-wrap { padding: 40px 0; }
.form-header { text-align: center; margin-bottom: 36px; }
.form-header h2 { font-size: 1.8rem; margin-bottom: 8px; }

/* Form Grid */
.form-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 28px;
}
.full-width { grid-column: 1 / -1; }

/* Form Card */
.form-card { padding: 24px; }
.card-header {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 20px; padding-bottom: 16px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.card-header span:first-child { font-size: 1.2rem; }
.card-header h3 { font-size: 0.95rem; font-weight: 700; flex: 1; }
.ml-auto { margin-left: auto; }

/* Form Groups */
.form-group { margin-bottom: 20px; }
.form-group:last-child { margin-bottom: 0; }
.form-group label {
  display: block; font-size: 0.82rem; font-weight: 600; color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;
}

/* Range */
.range-row { display: flex; align-items: center; gap: 12px; }
.range-row input[type="range"] { flex: 1; }
.range-value { font-size: 1rem; font-weight: 800; color: var(--text); min-width: 60px; text-align: right; }
.range-unit { font-size: 0.65rem; font-weight: 500; color: var(--text-dim); margin-left: 2px; }
.range-hints { display: flex; justify-content: space-between; font-size: 0.68rem; color: var(--text-dim); margin-top: 4px; }

/* Radio Cards */
.radio-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.vehicle-grid { grid-template-columns: repeat(4, 1fr); }
.radio-card {
  position: relative; display: flex; flex-direction: column; align-items: center; gap: 4px;
  padding: 14px 10px; border-radius: var(--r-md);
  background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
  cursor: pointer; transition: var(--transition); text-align: center;
}
.radio-card input { position: absolute; opacity: 0; width: 0; height: 0; }
.radio-card:hover { background: rgba(99,102,241,0.08); border-color: rgba(99,102,241,0.2); }
.radio-card.active {
  background: rgba(99,102,241,0.12); border-color: rgba(99,102,241,0.4);
  box-shadow: 0 0 16px rgba(99,102,241,0.15);
}
.rc-icon { font-size: 1.4rem; }
.rc-label { font-size: 0.78rem; font-weight: 700; color: var(--text); }
.rc-desc { font-size: 0.66rem; color: var(--text-dim); line-height: 1.3; }

/* Priority Sliders */
.priority-grid { display: flex; flex-direction: column; gap: 16px; }
.priority-item { display: flex; flex-direction: column; gap: 8px; }
.priority-header { display: flex; justify-content: space-between; align-items: center; }
.priority-label { font-size: 0.82rem; font-weight: 600; color: var(--text); }
.priority-value { font-size: 0.9rem; font-weight: 800; }
.priority-track { position: relative; height: 8px; border-radius: 99px; background: rgba(255,255,255,0.06); }
.priority-fill {
  position: absolute; top: 0; left: 0; height: 100%;
  border-radius: 99px; opacity: 0.6;
  transition: width 0.1s linear;
}
.overlay-range {
  position: absolute; top: -4px; left: 0; right: 0; width: 100%;
  height: 16px; opacity: 0; cursor: pointer; z-index: 2;
}

/* Advanced */
.collapse-toggle {
  display: flex; align-items: center; justify-content: space-between; width: 100%;
  background: transparent; border: none; color: var(--text-secondary); cursor: pointer;
  font-family: var(--font); font-size: 0.85rem; font-weight: 600; padding: 4px 0;
  transition: var(--transition);
}
.collapse-toggle:hover { color: var(--text); }
.toggle-arrow { font-size: 1.1rem; transition: transform 0.2s; }
.toggle-arrow.open { transform: rotate(180deg); }
.advanced-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 20px;
}
.input-text {
  width: 100%; padding: 10px 14px; border-radius: var(--r-md);
  background: rgba(255,255,255,0.04); border: var(--border);
  color: var(--text); font-family: var(--font); font-size: 0.85rem;
  outline: none; transition: var(--transition);
}
.input-text:focus { border-color: rgba(99,102,241,0.4); background: rgba(99,102,241,0.06); }
.input-text option { background: #1e293b; }

/* Transitions */
.collapse-enter-active, .collapse-leave-active { transition: all 0.3s ease; overflow: hidden; }
.collapse-enter-from, .collapse-leave-to { opacity: 0; max-height: 0; }
.collapse-enter-to, .collapse-leave-from { opacity: 1; max-height: 400px; }

/* Form Actions */
.form-actions {
  display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;
  padding-top: 8px;
}
.submit-btn { padding: 14px 36px; font-size: 1rem; min-width: 200px; }

@media (max-width: 768px) {
  .form-grid { grid-template-columns: 1fr; }
  .vehicle-grid { grid-template-columns: repeat(2, 1fr); }
  .advanced-grid { grid-template-columns: 1fr; }
}
</style>
