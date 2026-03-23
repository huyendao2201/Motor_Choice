<template>
  <div class="profile-form-wrap">
    <div class="form-header">
      <h2>Nhập Thông Tin Cá Nhân</h2>
      <p style = "font-size:18px">AI sẽ phân tích hồ sơ và dự đoán trọng số AHP phù hợp nhất với bạn</p>
    </div>

    <form class="profile-form" @submit.prevent="handleSubmit">
      <div class="form-grid">
        <template v-if="currentStep === 1">
        <!-- Card 1: Cơ bản -->
        <div class="form-card glass-card">
          <div class="card-header">
            <span>👤</span><h3>Thông Tin Cơ Bản</h3>
          </div>

          <div class="form-group">
            <label>💰 Ngân sách</label>
            <div class="range-row">
              <input 
                type="range" 
                v-model.number="form.budget" 
                min="10" max="300" step="5" 
                class="priority-range large-slider"
                :style="{ 
                  '--thumb-color': '#215af5',
                  'background': `linear-gradient(to right, #215af5 0%, #215af5 ${(form.budget-10)/(300-10)*100}%, var(--range-track) ${(form.budget-10)/(300-10)*100}%, var(--range-track) 100%)` 
                }"
              />
              <div class="range-value">{{ form.budget }}M<span class="range-unit">VNĐ</span></div>
            </div>
            <div class="range-hints"><span>10M</span><span>300M</span></div>
          </div>

          <div class="form-group">
            <label>📍 Quãng đường hàng ngày</label>
            <div class="range-row">
              <input 
                type="range" 
                v-model.number="form.daily_distance_km" 
                min="1" max="200" step="1" 
                class="priority-range large-slider"
                :style="{ 
                  '--thumb-color': 'var(--primary)',
                  'background': `linear-gradient(to right, var(--primary) 0%, var(--primary) ${(form.daily_distance_km-1)/(200-1)*100}%, var(--range-track) ${(form.daily_distance_km-1)/(200-1)*100}%, var(--range-track) 100%)` 
                }"
              />
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
                <div class="rc-info">
                  <span class="rc-label">{{ opt.label }}</span>
                  <p class="rc-desc">{{ opt.desc }}</p>
                </div>
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
                <div class="rc-label text-center">{{ opt.label }}</div>
                <div class="rc-icon">{{ opt.icon }}</div>
              </label>
            </div>
          </div>
        </div>

        <!-- Step 1 Actions (Spans full width) -->
        <div class="form-actions full-width" style="justify-content: space-between;">
          <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <button type="button" class="btn btn-demo-colorful student-demo" @click="loadDemo(0)">🎓 Demo: Sinh viên</button>
            <button type="button" class="btn btn-demo-colorful office-demo" @click="loadDemo(1)">💼 Demo: Văn phòng</button>
          </div>
          <button type="button" class="btn btn-primary submit-btn" @click="nextStep">Tiếp theo ➔</button>
        </div>
        </template>

        <!-- STEP 2: Ưu tiên & Bộ lọc -->
        <template v-if="currentStep === 2">
        <!-- Card 3: Độ ưu tiên (full width) -->
        <div class="form-card glass-card full-width">
          <div class="card-header">
            <span style="font-size: 1.5rem;">⚖️</span>
            <h3 class="priority-title">Mức Độ Ưu Tiên Các Tiêu Chí</h3>
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
                <input
                  type="range"
                  :min="0" :max="100" :step="5"
                  v-model.number="form[p.key]"
                  class="priority-range large-slider"
                  :style="{ 
                    '--thumb-color': p.color,
                    'background': `linear-gradient(to right, ${p.color} 0%, ${p.color} ${form[p.key]}%, var(--range-track) ${form[p.key]}%, var(--range-track) 100%)`
                  }"
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

        <!-- Step 2 Actions -->
        <div class="form-actions full-width" style="justify-content: space-between;">
          <button type="button" class="btn btn-back-colorful" @click="prevStep">⬅ Quay lại</button>
          <button type="submit" class="btn btn-primary submit-btn" :disabled="loading">
            <span v-if="loading" class="spinner" style="width:18px;height:18px;border-width:2px;"></span>
            <span>{{ loading ? 'Đang phân tích AI...' : '🔍 Tư Vấn Ngay ➔' }}</span>
          </button>
        </div>
        </template>

      </div><!-- /form-grid -->
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, inject } from 'vue'

const scrollToForm = inject('scrollToForm')

const props = defineProps({ loading: Boolean })
const emit = defineEmits(['submit', 'demo'])

const currentStep = ref(1)
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
  { key: 'priority_price', icon: '💰', label: 'Giá thành', color: '#7c6338ff' },
  { key: 'priority_fuel', icon: '⛽', label: 'Tiết kiệm xăng', color: '#305e5cff' },
  { key: 'priority_performance', icon: '⚡', label: 'Hiệu năng', color: '#2d2e6aff' },
  { key: 'priority_design', icon: '🎨', label: 'Thiết kế', color: '#24603aff' },
  { key: 'priority_brand', icon: '🏅', label: 'Thương hiệu', color: '#902f81ff' },
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

function nextStep() {
  currentStep.value = 2;
  if (scrollToForm) scrollToForm();
}

function prevStep() {
  currentStep.value = 1;
  if (scrollToForm) scrollToForm();
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
.profile-form-wrap { padding: 5px 0; }
.form-header { text-align: center; margin-bottom: 20px; }
.form-header h2 { font-size: 1.6rem; margin-bottom: 6px; }

/* Form Grid */
.form-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;
}
.full-width { grid-column: 1 / -1; }

/* Form Card */
.form-card { padding: 20px 24px; }
.card-header {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 14px; padding-bottom: 12px;
  border-bottom: var(--border);
}
.card-header span:first-child { font-size: 1.35rem; }
.card-header h3 { font-size: 1.1rem; font-weight: 800; flex: 1; }
.ml-auto { margin-left: auto; }

/* Form Groups */
.form-group { margin-bottom: 16px; }
.form-group:last-child { margin-bottom: 0; }
.form-group label {
  display: block; font-size: 0.88rem; font-weight: 700; color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;
}

/* Range Row (Basic Info) */
.range-row { display: flex; align-items: center; gap: 16px; margin: 10px 0; }
.range-row .priority-range { flex: 1; }
.range-value { font-size: 1.25rem; font-weight: 900; color: var(--text-header); min-width: 75px; text-align: right; font-family: 'Outfit'; }
.range-unit { font-size: 0.75rem; font-weight: 600; color: var(--text-dim); margin-left: 3px; }
.range-hints { display: flex; justify-content: space-between; font-size: 0.75rem; font-weight: 500; color: var(--text-dim); margin-top: 5px; }

/* Radio Cards */
.radio-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.vehicle-grid { grid-template-columns: repeat(4, 1fr); }
.radio-card {
  position: relative; display: flex; flex-direction: column; align-items: center; gap: 4px;
  padding: 12px 10px; border-radius: var(--r-md);
  background: var(--bg-card); border: var(--border);
  cursor: pointer; transition: var(--transition); text-align: center;
}
.radio-card input { position: absolute; opacity: 0; width: 0; height: 0; }
.radio-card:hover { background: var(--primary-dim); border-color: var(--primary-light); transform: translateY(-2px); }
.radio-card.active {
  background: var(--primary-dim); border-color: var(--primary);
  box-shadow: 0 6px 20px rgba(99,102,241,0.18);
}
.rc-icon { font-size: 1.9rem; margin-bottom: 4px; }
.rc-info { display: flex; flex-direction: column; gap: 3px; }
.rc-label { font-size: 0.95rem; font-weight: 900; color: var(--text-header); }
.rc-desc { font-size: 0.76rem; color: var(--text-secondary); line-height: 1.45; margin-top: 3px; }

/* Priority Sliders */
.priority-grid { display: flex; flex-direction: column; gap: 16px; }
.priority-item { display: flex; flex-direction: column; gap: 8px; }
.priority-header { display: flex; justify-content: space-between; align-items: center; }
.priority-label { font-size: 0.82rem; font-weight: 600; color: var(--text); }
.priority-value { font-size: 0.9rem; font-weight: 800; }
.priority-track { position: relative; height: 32px; display: flex; align-items: center; }
.priority-range {
  width: 100%; height: 10px; border-radius: 99px;
  -webkit-appearance: none; appearance: none;
  background: var(--range-track); outline: none; transition: 0.2s;
  cursor: pointer;
  border: 1px solid var(--border-color);
}
.priority-range::-webkit-slider-thumb {
  -webkit-appearance: none; appearance: none;
  width: 18px; height: 18px;
  background: var(--thumb-color, var(--primary));
  border: 2px solid white; border-radius: 50%;
  box-shadow: 0 3px 10px rgba(0,0,0,0.15);
  transition: 0.2s;
  margin-top: -4.5px; /* (9px track - 18px thumb) / 2 */
}
.priority-range::-webkit-slider-thumb:hover { transform: scale(1.15); box-shadow: 0 6px 15px rgba(0,0,0,0.2); }

.priority-title { font-size: 1.25rem !important; font-weight: 900 !important; font-family: 'Outfit' !important; }
.priority-label { font-size: 1rem; font-weight: 700; color: var(--text-header); }
.priority-value { font-size: 1.1rem; font-weight: 900; }

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
  background: var(--bg-card); border: var(--border);
  color: var(--text); font-family: var(--font); font-size: 0.85rem;
  outline: none; transition: var(--transition);
}
.input-text:focus { border-color: var(--primary); background: var(--bg-card-hover); }
.input-text option { background: var(--bg-2); }

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

/* Colorful Buttons Additions */
.btn-back-colorful {
  background: var(--bg-card);
  color: #f59e0b;
  border: 2px solid #f59e0b;
  font-weight: 800;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.15);
  transition: all 0.3s ease;
  padding: 10px 24px;
  border-radius: var(--r-md);
  font-family: inherit;
  font-size: 0.95rem;
  cursor: pointer;
}
.btn-back-colorful:hover {
  background: #f59e0b;
  color: white;
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
  transform: translateY(-2px);
}

.btn-demo-colorful {
  background: var(--bg-card);
  border: 2px solid transparent;
  font-weight: 800;
  transition: all 0.3s ease;
  padding: 10px 24px;
  border-radius: var(--r-md);
  font-family: inherit;
  font-size: 0.95rem;
  cursor: pointer;
}
.student-demo {
  color: #3b82f6;
  border-color: #3b82f6;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.15);
}
.student-demo:hover {
  background: #3b82f6;
  color: white;
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
  transform: translateY(-2px);
}
.office-demo {
  color: #8b5cf6;
  border-color: #8b5cf6;
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.15);
}
.office-demo:hover {
  background: #8b5cf6;
  color: white;
  box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4);
  transform: translateY(-2px);
}
</style>
