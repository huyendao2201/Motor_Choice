<template>
  <div id="wizard-top" class="manual-ahp-wizard">
    <div class="wizard-header">
      <div class="step-indicator" :class="{ active: step === 1, completed: step > 1 }">1. Phân Tích AI</div>
      <div class="step-divider"></div>
      <div class="step-indicator" :class="{ active: step === 2, completed: step > 2 }">2. Tiêu Chí</div>
      <div class="step-divider"></div>
      <div class="step-indicator" :class="{ active: step === 3, completed: step > 3 }">3. Phương Án</div>
      <div class="step-divider"></div>
      <div class="step-indicator" :class="{ active: step === 4, completed: step > 4 }">4. Kết Quả</div>
    </div>

    <!-- BƯỚC 1: Phân Tích AI & Chọn Xe -->
    <div v-if="step === 1" class="wizard-step">
      <!-- Form nhập -->
      <ProfileForm 
        v-if="!aiResult" 
        :loading="loadingAI" 
        @submit="handleAISubmit" 
        @demo="$refs.profileForm.loadDemo($event)"
        ref="profileForm"
      />

      <!-- Kết quả AI & Chọn xe -->
      <div v-else id="ai-results" class="glass-card step-content">
        <div class="step-title text-center">
          <h3>🤖 AI Random Forest Đã Đề Xuất</h3>
          <p>Dưới đây là các phương án xe do AI đề xuất. Hãy chọn các mẫu xe bạn muốn phân tích kỹ hơn.</p>
        </div>

        <div class="bike-selection">
          <div class="selected-count text-center">Đã chọn: <strong class="text-primary">{{ selectedBikes.length }}</strong> xe</div>
          
          <!-- Nút mở Modal thêm xe -->
          <div class="add-extra-trigger text-center">
            <button class="btn btn-add-favorite" @click="showBikePicker = true">
              <span class="plus-icon">⊕</span> Thêm xe yêu thích từ danh sách khác
            </button>
          </div>

          <div class="bike-grid">
            <!-- Luôn hiện các xe đã chọn (kể cả xe search thêm) -->
            <div v-for="b in displayingBikes" :key="b.model" 
                 class="bike-card" 
                 :class="{ selected: isSelected(b), extra: !isFromAISuggestions(b) }"
                 @click="toggleBike(b)">
              <div v-if="!isFromAISuggestions(b)" class="extra-badge">Yêu thích</div>
              <div class="bc-brand">{{ b.brand }}</div>
              <div class="bc-model">{{ b.model }}</div>
              <div class="bc-price">{{ b.price_million_vnd }} Triệu</div>
              <div class="bc-score" v-if="b.total_score">AI Score: {{(b.total_score * 100).toFixed(1)}}%</div>
              <div class="bc-score" v-else>Thêm thủ công</div>
              <div class="select-indicator"></div>
            </div>
          </div>
        </div>

        <div class="step-actions center mode-actions">
          <div class="mode-card quick-ai" @click="showQuickResults = true">
            <div class="mode-icon"><h6>⚡ Kết quả AI nhanh</h6></div>
            <div class="mode-info">
              
              <p>Xem đề xuất dựa trên mô hình Random Forest</p>
            </div>
            <button class="btn btn-primary">Xem ngay ➔</button>
          </div>
          <div class="mode-card expert-ahp" :class="{ disabled: selectedBikes.length < 2 }" @click="selectedBikes.length >= 2 && goToStep2()">
            <div class="mode-icon"><h6>⚖️ Lập ma trận AHP</h6></div>
            <div class="mode-info">
              <p>Kiểm chứng đa tiêu chí chuyên sâu (Khuyên dùng 2-5 xe)</p>
            </div>
            <button class="btn btn-secondary" :disabled="selectedBikes.length < 2">Bắt đầu ➔</button>
          </div>
        </div>
        <div class="actions-footer text-center">
          <button class="btn btn-back-colorful" @click="aiResult = null; selectedBikes = []; nextTick(() => document.getElementById('wizard-top')?.scrollIntoView({ behavior: 'auto', block: 'start' }))">⬅ Quay lại nhập thông tin</button>
        </div>
      </div>
    </div>

    <!-- BƯỚC 2: Trọng số Tiêu chí -->
    <div v-if="step === 2" class="wizard-step glass-card" id="step-2-start" style="scroll-margin-top: 100px;">
      <div class="step-title">
        <h3>⚖️ Bước 2: Đánh giá tầm quan trọng của các Tiêu chí</h3>
        <p>So sánh mức độ quan trọng giữa các tiêu chí bằng thang đo Saaty (1–9):</p>
      </div>

      <!-- Thang đo Saaty Legend -->
      <div class="saaty-guide">
        <div class="saaty-item" v-for="s in SAATY_SCALE" :key="s.val">
          <div class="saaty-val">{{ s.val }}</div>
          <div class="saaty-label">{{ s.label }}</div>
        </div>
      </div>

      <!-- NEW: Preset Ma trận Trọng số -->
      <div class="preset-weights-section">
        <p class="preset-label">💡 Mẫu ma trận trọng số AHP (Gợi ý điền nhanh):</p>
        <div class="preset-buttons">
          <button class="btn btn-demo student-demo" @click="fillCriteriaPreset('student')">🎓 Sinh Viên (Ưu tiên Giá & Xăng)</button>
          <button class="btn btn-demo office-demo" @click="fillCriteriaPreset('office')">💼 Văn Phòng (Ưu tiên Thiết kế & Thương Hiệu)</button>
          <button class="btn btn-demo tour-demo" @click="fillCriteriaPreset('tour')">🏕️ Đi Tour (Ưu tiên Hiệu Năng)</button>
          <button class="btn btn-ghost" @click="fillCriteriaPreset('balanced')">⚖️ Cân Bằng (Tất cả bằng nhau)</button>
        </div>
      </div>

      <div class="matrix-scroll">
        <div class="matrix-grid" :style="{ gridTemplateColumns: `100px repeat(5, 1fr)` }">
          <div class="mh-empty">Tiêu chí</div>
          <div v-for="c in CRITERIA" :key="c.id" class="mh-cell">{{ c.label }}</div>
          
          <template v-for="(row, i) in 5" :key="'cr_row_'+i">
            <div class="mh-cell">{{ CRITERIA[i].label }}</div>
            <div v-for="(col, j) in 5" :key="'cr_col_'+j">
              <input v-if="i === j" class="m-input diag" value="1" readonly />
              <input v-else-if="i < j" class="m-input editable" type="text"
                     v-model="criteriaMatrix[i][j]" @change="updateCriteriaMatrix(i, j)" />
              <input v-else class="m-input reciprocal" :value="getReciprocal(criteriaMatrix[j][i])" readonly />
            </div>
          </template>
        </div>
        <div class="matrix-actions">
          <button class="btn btn-calc-colorful" @click="calcCriteriaWeights" :disabled="calculating">✨ Tính trọng số Tiêu chí</button>
        </div>
      </div>

      <div id="criteria-result" class="calc-section">
        <div v-if="criteriaResult" class="result-box" :class="criteriaResult.is_consistent ? 'result-ok' : 'result-warn'">
          
          <div class="table-responsive mb-3" v-if="criteriaResult.details">
            <table class="detail-table">
              <thead>
                <tr>
                  <th class="th-label">Tiêu chí</th>
                  <th v-for="c in CRITERIA" :key="'th_'+c.id">{{ c.label }}</th>
                  <th>Weighted Sum Value</th>
                  <th>Criteria Weights</th>
                  <th>Consistency Vector</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(c, i) in CRITERIA" :key="'tr_'+i">
                  <td><strong>{{ c.label }}</strong></td>
                  <td v-for="(col, j) in 5" :key="'tc_'+j">
                    {{ criteriaResult.details.norm_matrix[i][j].toFixed(4) }}
                  </td>
                  <td class="bg-blueish">{{ criteriaResult.details.weighted_sum_value[i].toFixed(4) }}</td>
                  <td class="bg-yellowish">{{ criteriaResult.weights[i].toFixed(4) }}</td>
                  <td class="bg-greenish">{{ criteriaResult.details.consistency_vector[i].toFixed(4) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="result-content">
            <div class="result-msg-line">
              <strong>{{ criteriaResult.message }}</strong>
            </div>
            <div class="cr-stats-line">
              CR: <span>{{ criteriaResult.CR }}</span> | λ_max: <span>{{ criteriaResult.lambda_max }}</span>
            </div>
          </div>
          <div class="weights-list">
             <span v-for="(w, idx) in criteriaResult.weights" :key="idx" class="badge">
               {{ CRITERIA[idx].label }}: {{(w*100).toFixed(1)}}%
             </span>
          </div>
        </div>
      </div>

      <div class="step-actions">
        <button class="btn btn-back-colorful" @click="step = 1; nextTick(() => document.getElementById('wizard-top')?.scrollIntoView({ behavior: 'auto', block: 'start' }))">⬅ Quay lại</button>
        <button class="btn btn-primary" :disabled="!criteriaResult || !criteriaResult.is_consistent" @click="goToStep3">Tiếp tục ➔</button>
      </div>
    </div>

    <!-- BƯỚC 3: Trọng số Phương án -->
    <div v-if="step === 3" class="wizard-step glass-card" id="step-3-start" style="scroll-margin-top: 100px;">
      <div class="step-title">
        <h3>🏍️ Bước 3: So sánh các Phương án (Xe) theo từng Tiêu chí</h3>
        <p>Tiêu chí hiện tại: <strong class="text-primary">{{ CRITERIA[currentCriterionIndex].label }}</strong> ({{ currentCriterionIndex + 1 }}/5)</p>
      </div>

      <div class="matrix-scroll">
        <div class="matrix-grid" :style="{ gridTemplateColumns: `120px repeat(${selectedBikes.length}, 1fr)` }">
          <div class="mh-empty criterion-tag">{{ CRITERIA[currentCriterionIndex].label }}</div>
          <div v-for="b in selectedBikes" :key="'h'+b.model" class="mh-cell">{{ b.model }}</div>
          
          <template v-for="(row, i) in selectedBikes.length" :key="'alt_row_'+i">
            <div class="mh-cell">{{ selectedBikes[i].model }}</div>
            <div v-for="(col, j) in selectedBikes.length" :key="'alt_col_'+j">
              <input v-if="i === j" class="m-input diag" value="1" readonly />
              <input v-else-if="i < j" class="m-input editable" type="text"
                     v-model="currentAltMatrix[i][j]" @change="updateAltMatrix(i, j)" />
              <input v-else class="m-input reciprocal" :value="getReciprocal(currentAltMatrix[j][i])" readonly />
            </div>
          </template>
        </div>
        <div class="matrix-actions">
          <button class="btn btn-calc-colorful" @click="calcCurrentAltWeights" :disabled="calculating">✨ Tính trọng số Phương án</button>
        </div>
      </div>

      <div id="alt-result" class="calc-section">
        <div v-if="altResults[CRITERIA[currentCriterionIndex].id]" class="result-box" 
             :class="altResults[CRITERIA[currentCriterionIndex].id].is_consistent ? 'result-ok' : 'result-warn'">
          
          <div class="table-responsive mb-3" v-if="altResults[CRITERIA[currentCriterionIndex].id].details">
            <table class="detail-table">
              <thead>
                <tr>
                  <th class="th-label highlight">{{ CRITERIA[currentCriterionIndex].label }}</th>
                  <th v-for="b in selectedBikes" :key="'col_th_'+b.model">{{ b.model }}</th>
                  <th>Weighted Sum Value</th>
                  <th>Alternative Weights</th>
                  <th>Consistency Vector</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(b, i) in selectedBikes" :key="'row_tr_'+i">
                  <td><strong>{{ b.model }}</strong></td>
                  <td v-for="(col, j) in selectedBikes.length" :key="'row_tc_'+j">
                    {{ altResults[CRITERIA[currentCriterionIndex].id].details.norm_matrix[i][j].toFixed(4) }}
                  </td>
                  <td class="bg-blueish">{{ altResults[CRITERIA[currentCriterionIndex].id].details.weighted_sum_value[i].toFixed(4) }}</td>
                  <td class="bg-yellowish">{{ altResults[CRITERIA[currentCriterionIndex].id].weights[i].toFixed(4) }}</td>
                  <td class="bg-greenish">{{ altResults[CRITERIA[currentCriterionIndex].id].details.consistency_vector[i].toFixed(4) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="result-content">
            <div class="result-msg-line">
              <strong>{{ altResults[CRITERIA[currentCriterionIndex].id].message }}</strong>
            </div>
            <div class="cr-stats-line">
              CR: <span>{{ altResults[CRITERIA[currentCriterionIndex].id].CR }}</span> | λ_max: <span>{{ altResults[CRITERIA[currentCriterionIndex].id].lambda_max }}</span>
            </div>
          </div>
          <div class="weights-list">
             <span v-for="(w, idx) in altResults[CRITERIA[currentCriterionIndex].id].weights" :key="idx" class="badge">
               {{ selectedBikes[idx].model }}: {{(w*100).toFixed(1)}}%
             </span>
          </div>
        </div>
      </div>

      <div class="step-actions">
        <button class="btn btn-back-colorful" @click="prevCriterion">⬅ Quay lại</button>
        <button class="btn btn-primary" :disabled="!altResults[CRITERIA[currentCriterionIndex].id] || !altResults[CRITERIA[currentCriterionIndex].id].is_consistent" @click="nextCriterion">
          {{ currentCriterionIndex === 4 ? 'Hoàn tất & Xem Kết quả ➔' : 'Tiêu chí tiếp theo ➔' }}
        </button>
      </div>
    </div>

    <!-- BƯỚC 4: Kết quả -->
    <div v-if="step === 4" class="wizard-step glass-card" id="step-4-start" style="scroll-margin-top: 100px;">
      <div class="step-title text-center">
        <h2>🏆 Kết Quả Đánh Giá AHP Thủ Công</h2>
        <p>Tổng hợp điểm ưu tiên dựa trên các ma trận bạn vừa nhập.</p>
      </div>

      <!-- Add Charts to Manual Results -->
      <div class="manual-charts-row animate__animated animate__fadeIn">
        <div class="manual-doughnut-box glass-card-nested">
          <div class="card-header-compact text-center">
            <h4>⚖️ Tỷ Trọng Tiêu Chí Của Bạn</h4>
            <p>Trọng số bạn đã gán sau khi so sánh ma trận</p>
          </div>
          <div class="chart-box-manual">
            <Doughnut :data="manualDoughnutData" :options="manualDoughnutOptions" />
          </div>
        </div>
        <div class="manual-bar-box glass-card-nested">
          <div class="card-header-compact text-center">
            <h4>📊 Điểm Các Xe Qua Từng Tiêu Chí</h4>
            <p>So sánh điểm trung bình chuẩn hóa của các xe</p>
          </div>
          <div class="chart-box-manual">
            <Bar :data="manualBarData" :options="manualBarOptions" />
          </div>
        </div>
      </div>

      <div class="final-results">
        <div v-for="(res, idx) in finalRanking" :key="idx" class="result-card" :class="{ top1: idx === 0 }">
          <div class="rc-rank">#{{ idx + 1 }}</div>
          
          <div v-if="res.bike.image_url" class="rc-img-container">
            <img :src="res.bike.image_url" :alt="res.bike.model" class="rc-img" />
          </div>

          <div class="rc-info">
            <h3>{{ res.bike.brand }} {{ res.bike.model }}</h3>
            <div class="rc-score">Điểm tổng thủ công: <strong>{{ (res.score * 100).toFixed(2) }}%</strong></div>
            <div class="rc-ai-score" style="font-size: 0.8rem; opacity: 0.8">Điểm AI gốc: {{(res.bike.total_score * 100).toFixed(2)}}%</div>
          </div>
          <div class="rc-breakdown">
            <div v-for="(w, cId) in res.breakdown" :key="cId" class="breakdown-item">
              <span>{{ getCriteriaLabel(cId) }}:</span>
              <strong>{{ (w * 100).toFixed(1) }}%</strong>
            </div>
          </div>
        </div>
      </div>

      <div class="step-actions center mt-4" style="display: flex; gap: 12px; justify-content: center;">
        <button class="btn btn-primary" @click="exportExcel" :disabled="isExporting">
          {{ isExporting ? 'Đang xuất...' : '📥 Xuất báo cáo Excel' }}
        </button>
        <button class="btn btn-secondary" @click="fullReset">Tư vấn lại từ đầu</button>
      </div>
    </div>

    <!-- BƯỚC 5: Kết quả Nhanh (AI Only Overlay) -->
    <div v-if="showQuickResults" class="quick-results-layer animate__animated animate__fadeIn">
      <div class="glass-card full-results">
        <div class="results-top">
          <div class="step-title text-center">
            <h2>✨ Đề xuất từ AI (Random Forest)</h2>
            <p>Bảng xếp hạng dựa trên trọng số AI đã dự đoán từ Profile của bạn:</p>
          </div>
          <button class="close-results" @click="showQuickResults = false">✕</button>
        </div>

        <div class="quick-bike-list">
          <div v-for="(b, idx) in aiResult.top_motorcycles" :key="b.model" class="quick-bike-card" :class="{ top1: idx === 0 }">
             <div class="qb-rank">#{{ idx + 1 }}</div>
             <div class="qb-main">
               <div class="qb-meta">{{ b.brand }} · {{ b.vehicle_type }}</div>
               <div class="qb-name">{{ b.model }}</div>
               <div class="qb-price">{{ b.price_million_vnd }} Triệu VND</div>
             </div>
             <div class="qb-score-box">
                <div class="qb-score">{{ (b.total_score * 100).toFixed(1) }}%</div>
                <div class="qb-label">AI Match Score</div>
             </div>
          </div>
        </div>
        
        <div class="quick-footer">
          <p>Bạn có thể đóng bảng này để tiếp tục <strong>Phân tích AHP thủ công</strong>.</p>
          <button class="btn btn-primary" @click="showQuickResults = false">Đã hiểu & Phân tích AHP ➔</button>
        </div>
      </div>
    </div>
    <!-- MODAL: Chọn xe yêu thích -->
    <transition name="modal-fade">
      <div v-if="showBikePicker" class="bike-picker-modal">
        <div class="modal-backdrop" @click="showBikePicker = false"></div>
        <div class="modal-sheet glass-card animate__animated animate__slideInUp">
          <div class="modal-header">
            <div class="mh-title">
              <h3>⭐ Tìm & Thêm Xe Yêu Thích</h3>
              <p>Chọn thêm các mẫu xe khác để đưa vào ma trận so sánh (Tối đa 5-8 xe tổng cộng)</p>
            </div>
            <button class="modal-close" @click="showBikePicker = false">✕</button>
          </div>

          <div class="picker-controls">
            <div class="picker-search">
              <span class="search-icon">🔍</span>
              <input 
                v-model="bikeSearchQuery" 
                placeholder="Nhập tên xe muốn tìm (SH, Vision, Exciter...)" 
                class="picker-input"
                autofocus
              />
            </div>
            <div class="brand-filters">
              <button 
                v-for="brand in ['Tất cả', 'Honda', 'Yamaha', 'Suzuki', 'Kawasaki', 'VinFast']" 
                :key="brand"
                class="brand-btn"
                :class="{ active: selectedBrand === brand }"
                @click="selectedBrand = brand"
              >
                {{ brand }}
              </button>
            </div>
          </div>

          <div class="picker-results-grid">
            <div 
              v-for="b in filteredPickerBikes" 
              :key="b.model" 
              class="picker-item"
              :class="{ 'is-selected': isSelected(b) }"
              @click="toggleBike(b)"
            >
              <div class="pi-check">✓</div>
              <div class="pi-meta">{{ b.brand }} · {{ b.vehicle_type }}</div>
              <div class="pi-model">{{ b.model }}</div>
              <div class="pi-price">{{ b.price_million_vnd }}M VND</div>
            </div>
            
            <div v-if="filteredPickerBikes.length === 0" class="no-results" style="grid-column: 1/-1; padding: 40px; text-align: center; color: var(--text-dim); font-weight: 700;">
              📭 Không tìm thấy mẫu xe nào phù hợp
            </div>
          </div>

          <div class="modal-footer">
            <div class="selection-summary">Đã chọn: <strong>{{ selectedBikes.length }}</strong> xe</div>
            <button class="btn btn-primary" @click="showBikePicker = false">Hoàn tất lựa chọn ➔</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, inject } from 'vue'
import { Doughnut, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS, Title, Tooltip, Legend, ArcElement, BarElement, CategoryScale, LinearScale
} from 'chart.js'
import { getMotorcycles, calculateAHP, recommend } from '../api.js'
import ProfileForm from './ProfileForm.vue'

const scrollToForm = inject('scrollToForm')

function fullReset() {
  step.value = 1
  aiResult.value = null
  selectedBikes.value = []
  if (scrollToForm) scrollToForm()
}

ChartJS.register(Title, Tooltip, Legend, ArcElement, BarElement, CategoryScale, LinearScale)

const step = ref(1)
const calculating = ref(false)

// Step 1: AI Result
const aiResult = ref(null)
const selectedBikes = ref([])
const loadingAI = ref(false)
const showQuickResults = ref(false)

// Search Extra Bikes
const allMotorcycles = ref([])
const bikeSearchQuery = ref('')
const showSearchDropdown = ref(false)
const showBikePicker = ref(false)
const selectedBrand = ref('Tất cả')

onMounted(async () => {
  try {
    allMotorcycles.value = await getMotorcycles()
  } catch (err) {
    console.error("Failed to load all bikes for search", err)
  }
})

const filteredPickerBikes = computed(() => {
  // Fix: Lấy mảng 'motorcycles' từ object API trả về
  let bikes = Array.isArray(allMotorcycles.value?.motorcycles) ? allMotorcycles.value.motorcycles : []
  
  // Filter by brand
  if (selectedBrand.value !== 'Tất cả') {
    bikes = bikes.filter(b => b.brand === selectedBrand.value)
  }
  
  // Filter by search
  if (bikeSearchQuery.value) {
    const q = bikeSearchQuery.value.toLowerCase()
    bikes = bikes.filter(b => 
      b.model.toLowerCase().includes(q) || 
      b.brand.toLowerCase().includes(q)
    )
  }
  
  return bikes.slice(0, 50) // Limit displayed for performance
})

const filteredExtraBikes = computed(() => {
  const bikes = allMotorcycles.value?.motorcycles || []
  if (!bikeSearchQuery.value || bikeSearchQuery.value.length < 1) return []
  const q = bikeSearchQuery.value.toLowerCase()
  return bikes.filter(b => 
    b.model.toLowerCase().includes(q) || 
    b.brand.toLowerCase().includes(q)
  ).slice(0, 8)
})

const displayingBikes = computed(() => {
  if (!aiResult.value) return []
  // Combine AI suggestions with bikes manually selected but NOT in suggestions
  const topModels = aiResult.value.top_motorcycles.map(b => b.model)
  const extras = selectedBikes.value.filter(b => !topModels.includes(b.model))
  return [...aiResult.value.top_motorcycles, ...extras]
})

function isFromAISuggestions(bike) {
  if (!aiResult.value) return false
  return aiResult.value.top_motorcycles.some(b => b.model === bike.model)
}

function addExtraBike(bike) {
  const bikes = allMotorcycles.value?.motorcycles || []
  if (!isSelected(bike)) {
    selectedBikes.value.push(bike)
  }
  bikeSearchQuery.value = ''
  showSearchDropdown.value = false
}

async function handleAISubmit(payload) {
  loadingAI.value = true
  try {
    const data = await recommend(payload)
    aiResult.value = data
    // Tự động chọn top 3
    selectedBikes.value = data.top_motorcycles.slice(0, 3)

    nextTick(() => {
      const el = document.getElementById('ai-results')
      if (el) el.scrollIntoView({ behavior: 'auto', block: 'start' })
    })
  } catch (err) {
    alert('❌ Lỗi: ' + err.message)
  } finally {
    loadingAI.value = false
  }
}

function isSelected(b) {
  return selectedBikes.value.some(x => x.model === b.model)
}

function toggleBike(b) {
  const idx = selectedBikes.value.findIndex(x => x.model === b.model)
  if (idx >= 0) {
    selectedBikes.value.splice(idx, 1)
  } else {
    if (selectedBikes.value.length >= 5) {
      const proceed = confirm('Việc chọn hơn 5 xe sẽ khiến ma trận so sánh AHP trở nên rất phức tạp và dễ gây rối. Bạn có chắc chắn muốn tiếp tục không?')
      if (!proceed) return
    }
    selectedBikes.value.push(b)
  }
}

const SAATY_SCALE = [
  { val: 1, label: 'Bằng nhau' },
  { val: 3, label: 'Hơn chút' },
  { val: 5, label: 'Hơn nhiều' },
  { val: 7, label: 'Rất nhiều' },
  { val: 9, label: 'Cực kỳ' }
]

const CRITERIA = [
  { label: 'Price', id: 'price' }, 
  { label: 'Performance', id: 'performance' }, 
  { label: 'Design', id: 'design' }, 
  { label: 'Save Fuel', id: 'fuel' }, 
  { label: 'Brand', id: 'brand' }
]

const criteriaMatrix = ref(Array(5).fill(null).map(() => Array(5).fill(1)))
const criteriaResult = ref(null)

function initCriteriaMatrix() {
  for(let i=0; i<5; i++) {
    for(let j=0; j<5; j++) {
      if(i === j) criteriaMatrix.value[i][j] = 1;
      else if(i < j) criteriaMatrix.value[i][j] = 3; // Default
    }
  }
}

function fillCriteriaPreset(type) {
  // reset to 1
  for(let i=0; i<5; i++) {
    for(let j=0; j<5; j++) {
      if(i === j) criteriaMatrix.value[i][j] = 1;
      else if(i < j) criteriaMatrix.value[i][j] = 1;
    }
  }

  // 0: Price, 1: Performance, 2: Design, 3: Fuel, 4: Brand
  if (type === 'student') {
    criteriaMatrix.value[0][1] = 5; 
    criteriaMatrix.value[0][2] = 5; 
    criteriaMatrix.value[0][3] = 1; // Price vs Fuel = 1
    criteriaMatrix.value[0][4] = 7; 
    criteriaMatrix.value[1][2] = 1; 
    criteriaMatrix.value[1][3] = '1/5'; 
    criteriaMatrix.value[1][4] = 3; 
    criteriaMatrix.value[2][3] = '1/5'; 
    criteriaMatrix.value[2][4] = 3; 
    criteriaMatrix.value[3][4] = 7; // Fuel over Brand
  } else if (type === 'office') {
    criteriaMatrix.value[0][1] = '1/3'; 
    criteriaMatrix.value[0][2] = '1/5'; 
    criteriaMatrix.value[0][3] = '1/3'; 
    criteriaMatrix.value[0][4] = '1/5'; 
    criteriaMatrix.value[1][2] = '1/3'; 
    criteriaMatrix.value[1][3] = 1; 
    criteriaMatrix.value[1][4] = '1/3'; 
    criteriaMatrix.value[2][3] = 3; // Design over Fuel
    criteriaMatrix.value[2][4] = 1; // Design vs Brand
    criteriaMatrix.value[3][4] = '1/3';
  } else if (type === 'tour') {
    criteriaMatrix.value[0][1] = '1/7'; 
    criteriaMatrix.value[0][2] = '1/3';
    criteriaMatrix.value[0][3] = '1/3';
    criteriaMatrix.value[0][4] = '1/3';
    criteriaMatrix.value[1][2] = 5; // Perf over Design
    criteriaMatrix.value[1][3] = 5; 
    criteriaMatrix.value[1][4] = 5; 
    criteriaMatrix.value[2][3] = 1;
    criteriaMatrix.value[2][4] = 1;
    criteriaMatrix.value[3][4] = 1;
  }
}

function parseAHPValue(val) {
  if (typeof val === 'number') return val;
  if (!val || typeof val !== 'string') return 1;
  if (val.includes('/')) {
    const parts = val.split('/');
    const n = parseFloat(parts[0]);
    const d = parseFloat(parts[1]);
    return (d !== 0 && !isNaN(n) && !isNaN(d)) ? n / d : 1;
  }
  const v = parseFloat(val);
  return isNaN(v) ? 1 : v;
}

function updateCriteriaMatrix(i, j) {
  const val = parseAHPValue(criteriaMatrix.value[i][j]);
  if (val <= 0 || val > 9) {
    alert("Giá trị phải nằm trong khoảng từ 0 đến 9!");
    criteriaMatrix.value[i][j] = 1;
  }
}

function getReciprocal(v) {
  const val = parseAHPValue(v);
  if(!val) return '';
  const rec = 1 / val;
  return rec % 1 === 0 ? rec.toString() : rec.toFixed(3);
}

function goToStep2() {
  if(!criteriaResult.value) initCriteriaMatrix();
  step.value = 2;
  nextTick(() => document.getElementById('step-2-start')?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
}

async function calcCriteriaWeights() {
  calculating.value = true;
  try {
    const fullMat = Array(5).fill(null).map(() => Array(5).fill(1));
    for(let i=0; i<5; i++){
      for(let j=0; j<5; j++){
        if(i === j) fullMat[i][j] = 1;
        else if(i < j) fullMat[i][j] = parseAHPValue(criteriaMatrix.value[i][j]);
        else fullMat[i][j] = 1 / parseAHPValue(criteriaMatrix.value[j][i]);
      }
    }
    const res = await calculateAHP(fullMat);
    criteriaResult.value = res;

    nextTick(() => {
      const el = document.getElementById('criteria-result')
      if (el) el.scrollIntoView({ behavior: 'auto', block: 'start' })
    })
  } catch(e) {
    alert("Lỗi tính toán: " + e.message);
  } finally {
    calculating.value = false;
  }
}

// Step 3: Alternative Matrices
const currentCriterionIndex = ref(0)
const altMatrices = ref({}) // mapping: criteria_id -> 2D array
const altResults = ref({})

function initAltMatrix(n) {
  const mat = Array(n).fill(null).map(() => Array(n).fill(1));
  for(let i=0; i<n; i++) {
    for(let j=0; j<n; j++) {
      if(i < j) mat[i][j] = 2; // Default
    }
  }
  return mat;
}

const currentAltMatrix = computed(() => {
  const cid = CRITERIA[currentCriterionIndex.value].id;
  if(!altMatrices.value[cid]) {
    altMatrices.value[cid] = initAltMatrix(selectedBikes.value.length);
  }
  return altMatrices.value[cid];
})

function updateAltMatrix(i, j) {
  const cid = CRITERIA[currentCriterionIndex.value].id;
  const val = parseAHPValue(altMatrices.value[cid][i][j]);
  if (val <= 0 || val > 9) {
    alert("Giá trị phải nằm trong khoảng từ 0 đến 9!");
    altMatrices.value[cid][i][j] = 1;
  }
}

function goToStep3() {
  currentCriterionIndex.value = 0;
  // Initialize matrices for all criteria if not done
  const n = selectedBikes.value.length;
  CRITERIA.forEach(c => {
    if(!altMatrices.value[c.id] || altMatrices.value[c.id].length !== n) {
      altMatrices.value[c.id] = initAltMatrix(n);
      delete altResults.value[c.id]; // reset result
    }
  });
  step.value = 3;
  nextTick(() => document.getElementById('step-3-start')?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
}

async function calcCurrentAltWeights() {
  calculating.value = true;
  try {
    const n = selectedBikes.value.length;
    const cid = CRITERIA[currentCriterionIndex.value].id;
    const mat = altMatrices.value[cid];
    
    const fullMat = Array(n).fill(null).map(() => Array(n).fill(1));
    for(let i=0; i<n; i++){
      for(let j=0; j<n; j++){
        if(i === j) fullMat[i][j] = 1;
        else if(i < j) fullMat[i][j] = parseAHPValue(mat[i][j]);
        else fullMat[i][j] = 1 / parseAHPValue(mat[j][i]);
      }
    }
    const names = selectedBikes.value.map(b => b.model);
    
    // Sử dụng API tính AHP đã được thiết lập trong api.js
    const res = await calculateAHP(fullMat, names);
    
    altResults.value[cid] = res;

    nextTick(() => {
      const el = document.getElementById('alt-result')
      if (el) el.scrollIntoView({ behavior: 'auto', block: 'start' })
    })
  } catch(e) {
    alert("Lỗi tính toán: " + e.message);
  } finally {
    calculating.value = false;
  }
}

function prevCriterion() {
  if(currentCriterionIndex.value > 0) {
    currentCriterionIndex.value--;
  } else {
    step.value = 2;
    nextTick(() => document.getElementById('step-2-start')?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
    return;
  }
  nextTick(() => document.getElementById('step-3-start')?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
}

function nextCriterion() {
  if(currentCriterionIndex.value < 4) {
    currentCriterionIndex.value++;
    nextTick(() => document.getElementById('step-3-start')?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  } else {
    calculateFinalRanking();
    step.value = 4;
    nextTick(() => document.getElementById('step-4-start')?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  }
}

// Step 4: Final calculation
const finalRanking = ref([]);

function getCriteriaLabel(id) {
  return CRITERIA.find(c => c.id === id)?.label || id;
}

function calculateFinalRanking() {
  const cw = criteriaResult.value.weights; // array of 5
  const n = selectedBikes.value.length;
  
  const results = [];
  
  for(let i=0; i<n; i++) {
    let score = 0;
    const breakdown = {};
    
    for(let c=0; c<5; c++) {
      const cid = CRITERIA[c].id;
      const critWeight = cw[c];
      const altWeightForCrit = altResults.value[cid].weights[i];
      const contribution = critWeight * altWeightForCrit;
      score += contribution;
      breakdown[cid] = contribution;
    }
    
    results.push({
      bike: selectedBikes.value[i],
      score: score,
      breakdown: breakdown
    });
  }
    
  results.sort((a,b) => b.score - a.score);
  finalRanking.value = results;
}

const isExporting = ref(false)

const exportExcel = async () => {
  if (isExporting.value) return
  isExporting.value = true
  try {
    const formattedWeights = {}
    CRITERIA.forEach((c, idx) => {
      formattedWeights[c.label] = criteriaResult.value.weights[idx]
    })
    
    // 1. Prepare full Criteria Matrix
    const fullCriteriaMat = Array(5).fill(null).map(() => Array(5).fill(1));
    for(let i=0; i<5; i++){
      for(let j=0; j<5; j++){
        if(i === j) fullCriteriaMat[i][j] = 1;
        else if(i < j) fullCriteriaMat[i][j] = parseAHPValue(criteriaMatrix.value[i][j]);
        else fullCriteriaMat[i][j] = 1 / parseAHPValue(criteriaMatrix.value[j][i]);
      }
    }

    // 2. Prepare full Alternative Matrices for each criterion
    const fullAltMatrices = {};
    const n = selectedBikes.value.length;
    CRITERIA.forEach(c => {
      const mat = altMatrices.value[c.id];
      if (mat) {
        const fullMat = Array(n).fill(null).map(() => Array(n).fill(1));
        for(let i=0; i<n; i++){
          for(let j=0; j<n; j++){
            if(i === j) fullMat[i][j] = 1;
            else if(i < j) fullMat[i][j] = parseAHPValue(mat[i][j]);
            else fullMat[i][j] = 1 / parseAHPValue(mat[j][i]);
          }
        }
        fullAltMatrices[c.id] = fullMat;
      }
    });

    const payload = {
      type: 'MANUAL_AHP',
      criteria_weights: [formattedWeights],
      final_ranking: finalRanking.value,
      // DETAILED DATA FOR EXCEL
      criteria_matrix: fullCriteriaMat,
      criteria_labels: CRITERIA.map(c => c.label),
      alternative_names: selectedBikes.value.map(b => b.model),
      alt_matrices: fullAltMatrices,
      // FULL CALCULATION RESULTS
      criteria_full_result: criteriaResult.value,
      alt_full_results: altResults.value
    }
    
    const response = await fetch(`/api/export-report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!response.ok) throw new Error('Export failed')
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `AHP_Report_Manual_${Date.now()}.xlsx`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  } catch(e) {
    alert("Lỗi tải file Excel: " + e.message)
  } finally {
    isExporting.value = false
  }
}

const manualDoughnutData = computed(() => {
  if (!criteriaResult.value || !criteriaResult.value.weights) return { labels: [], datasets: [] };
  return {
    labels: CRITERIA.map(c => c.label),
    datasets: [{
      data: criteriaResult.value.weights.map(w => +(w * 100).toFixed(1)),
      backgroundColor: ['#f59e0b', '#10b981', '#6366f1', '#ec4899', '#8b5cf6'],
      borderWidth: 0,
      hoverOffset: 15
    }]
  };
});

const manualDoughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'right', labels: { boxWidth: 12, font: { weight: '800' } } },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      padding: 12,
      displayColors: false,
      callbacks: { label: (ctx) => ` ${ctx.label}: ${ctx.raw}%` }
    }
  },
  cutout: '70%'
};

const manualBarData = computed(() => {
  const bikes = selectedBikes.value;
  return {
    labels: CRITERIA.map(c => c.label),
    datasets: bikes.map((b, idx) => ({
      label: b.model,
      data: CRITERIA.map(c => {
         if(!altResults.value[c.id]) return 0;
         return (altResults.value[c.id].weights[idx] * 10).toFixed(1)
      }),
      backgroundColor: idx === 0 ? 'rgba(99, 102, 241, 0.8)' : idx === 1 ? 'rgba(16, 185, 129, 0.8)' : 'rgba(245, 158, 11, 0.8)',
      borderRadius: 6
    }))
  };
});

const manualBarOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top', labels: { usePointStyle: true, padding: 15, font: { weight: 'bold' } } }
  },
  scales: {
    y: { beginAtZero: true, max: 10, grid: { display: false } },
    x: { grid: { display: false } }
  }
};

</script>

<style scoped>
.manual-ahp-wizard { width: 100%; max-width: 1050px; margin: 0 auto; padding: 15px 0 140px; }

.wizard-header { 
  display: flex; align-items: center; justify-content: center; 
  margin-bottom: 30px; 
  padding: 0 20px;
}
.step-indicator { 
  padding: 15px 30px; border-radius: 99px; 
  background: white; border: var(--border);
  font-weight: 800; font-size: 1.05rem; color: var(--text-dim); 
  transition: var(--transition);
  box-shadow: var(--shadow-sm);
  white-space: nowrap;
}
.step-indicator.active { 
  background: var(--primary); color: #fff; 
  box-shadow: 0 12px 24px -5px rgba(67, 56, 202, 0.4); 
  border-color: var(--primary);
  transform: translateY(-2px);
}
.step-indicator.completed { 
  background: var(--accent-dim); color: var(--accent); 
  border-color: var(--accent);
}
.step-divider { flex: 1; max-width: 85px; height: 3px; background: var(--border-color); margin: 0 16px; border-radius: 4px; opacity: 0.5; }

.wizard-step { padding: 25px 40px; animation: slideIn 0.5s cubic-bezier(0.22, 1, 0.36, 1); }
@keyframes slideIn { from{opacity:0; transform:translateY(15px)} to{opacity:1; transform:translateY(0)} }

.step-title { margin-top: 25px; margin-bottom: 24px; text-align: center; }
.step-title h3 { font-size: 1.75rem; color: var(--text-header); margin-bottom: 12px; font-weight: 900; letter-spacing: -0.5px; }
.step-title p { color: var(--text-secondary); font-size: 1.05rem; max-width: 700px; margin: 0 auto; line-height: 1.6; }

/* Bike Selection */
.bike-selection { margin: 20px 0; }
.selected-count { margin-bottom: 8px; font-weight: 800; font-size: 1rem; color: var(--text-secondary); }
.bike-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); 
  gap: 16px; 
  margin-bottom: 20px; 
  padding: 4px 5px;
}
.bike-card { 
  padding: 16px 20px; border-radius: 18px; 
  background: var(--bg-item); border: var(--border); 
  cursor: pointer; transition: var(--transition);
  position: relative; overflow: visible;
}
.bike-card::before {
  content: ''; position: absolute; inset: 0; 
  border-radius: inherit; border: 2.5px solid transparent; 
  transition: all 0.3s ease; pointer-events: none; z-index: 2;
}
.bike-card.selected::before { border-color: var(--primary); }
.bike-card.selected { background: var(--primary-dim); transform: translateY(-3px); box-shadow: 0 10px 25px rgba(67, 56, 202, 0.15); }

.select-indicator {
  position: absolute; top: 12px; right: 12px; width: 22px; height: 22px;
  border-radius: 50%; border: 2px solid var(--border-color);
  background: white; transition: all 0.3s ease; z-index: 3;
}
.selected .select-indicator {
  background: var(--primary); border-color: var(--primary);
}
.selected .select-indicator::after {
  content: '✓'; color: white; position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 900;
}

.extra-badge {
  position: absolute; top: -10px; left: 15px; 
  background: #f59e0b; color: white; padding: 2px 10px;
  border-radius: 6px; font-size: 0.65rem; font-weight: 800;
  text-transform: uppercase; z-index: 5;
  box-shadow: 0 4px 10px rgba(245, 158, 11, 0.3);
}

/* Search Box */
.search-extra-bikes { max-width: 600px; margin: 0 auto 30px; position: relative; z-index: 100; }
.search-input-wrapper { position: relative; display: flex; align-items: center; }
.search-icon { position: absolute; left: 16px; color: var(--text-dim); }
.extra-bike-input {
  width: 100%; padding: 14px 45px; border-radius: 16px;
  border: 2px solid var(--border-color); background: var(--bg-card);
  font-family: inherit; font-weight: 600; font-size: 0.95rem;
  transition: all 0.3s ease; outline: none;
}
.extra-bike-input:focus { border-color: var(--primary); box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1); }
.clear-search { position: absolute; right: 16px; border: none; background: transparent; cursor: pointer; color: var(--text-dim); padding: 5px; }

.search-dropdown-results { 
  position: absolute; top: calc(100% + 10px); left: 0; right: 0;
  max-height: 400px; overflow-y: auto; z-index: 101;
  padding: 8px; box-shadow: var(--shadow-xl);
}
.search-result-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; border-radius: 12px; cursor: pointer;
  transition: all 0.2s ease;
}
.search-result-item:hover { background: var(--primary-dim); }
.sri-info { display: flex; flex-direction: column; }
.sri-model { font-weight: 800; color: var(--text-header); }
.sri-price { font-size: 0.8rem; color: var(--text-dim); }
.sri-type { font-size: 0.75rem; background: var(--bg-2); padding: 2px 8px; border-radius: 6px; font-weight: 700; color: var(--text-secondary); }
.sri-check { color: var(--primary); font-weight: 900; }

.fade-in-enter-active, .fade-in-leave-active { transition: opacity 0.3s ease, transform 0.3s ease; }
.fade-in-enter-from, .fade-in-leave-to { opacity: 0; transform: translateY(-10px); }

/* Picker Modal Styles */
.bike-picker-modal {
  position: fixed; inset: 0; z-index: 2000;
  display: flex; align-items: flex-end; justify-content: center;
  padding: 0;
}
.modal-backdrop {
  position: absolute; inset: 0;
  background: rgba(0,0,0,0.4); backdrop-filter: blur(8px);
}
.modal-sheet {
  position: relative; width: 100%; max-width: 1000px;
  height: 80vh; background: var(--bg-item);
  border-radius: 30px; padding: 25px 30px;
  display: flex; flex-direction: column; gap: 20px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  margin-bottom: 60px; /* Nhấc Modal lên cao hơn nữa cho cân đối */
  border: 1px solid var(--border-color);
}

.modal-header { display: flex; justify-content: space-between; align-items: flex-start; }
.mh-title h3 { font-size: 1.6rem; font-weight: 900; color: var(--text-header); margin-bottom: 4px; }
.mh-title p { color: var(--text-secondary); font-weight: 600; font-size: 0.9rem; }
.modal-close { 
  background: var(--bg-2); border: var(--border); 
  width: 44px; height: 44px; border-radius: 50%;
  font-size: 1.2rem; cursor: pointer; transition: 0.3s;
}
.modal-close:hover { background: var(--danger-dim); color: var(--danger); transform: rotate(90deg); }

.picker-controls { display: flex; flex-direction: column; gap: 15px; }
.picker-input {
  width: 100%; padding: 14px 45px; border-radius: 16px;
  border: 2px solid var(--border-color); background: var(--bg-card);
  font-family: inherit; font-size: 0.95rem; font-weight: 700; outline: none;
}
.picker-search { position: relative; }
.picker-search .search-icon { position: absolute; left: 18px; top: 50%; transform: translateY(-50%); font-size: 1.2rem; opacity: 0.5; }

.brand-filters { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 5px; }
.brand-btn {
  padding: 8px 18px; border-radius: 99px; border: var(--border);
  background: var(--bg-card); color: var(--text-secondary);
  font-weight: 700; cursor: pointer; transition: 0.3s; white-space: nowrap;
}
.brand-btn.active { background: var(--primary); color: white; border-color: var(--primary); }

.picker-results-grid {
  flex: 1; overflow-y: auto;
  display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px; padding: 10px 5px;
}
.picker-item {
  padding: 20px; border-radius: 20px; border: var(--border);
  background: var(--bg-card); cursor: pointer; transition: 0.3s;
  position: relative;
}
.picker-item:hover { transform: translateY(-3px); border-color: var(--primary-light); background: var(--bg-2); }
.picker-item.is-selected { background: var(--primary-dim); border-color: var(--primary); }

.pi-check {
  position: absolute; top: 12px; right: 12px;
  width: 20px; height: 20px; border-radius: 50%;
  background: white; border: 1.5px solid var(--border-color);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.7rem; font-weight: 900; color: transparent;
  transition: 0.2s;
}
.is-selected .pi-check { background: var(--primary); border-color: var(--primary); color: white; }

.pi-meta { font-size: 0.7rem; font-weight: 800; color: var(--text-dim); text-transform: uppercase; margin-bottom: 4px; }
.pi-model { font-weight: 900; font-size: 1.1rem; color: var(--text-header); }
.pi-price { font-size: 0.9rem; font-weight: 800; color: var(--accent); margin-top: 8px; }

.modal-footer {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 15px; border-top: 1px solid var(--border-color);
}
.selection-summary { font-weight: 800; color: var(--text-header); }

.btn-add-favorite {
  padding: 10px 20px; border-radius: 12px;
  background: var(--bg-card); border: 2px dashed var(--primary-light);
  color: var(--primary); font-weight: 800; font-size: 0.95rem;
  cursor: pointer; transition: 0.3s;
}
.btn-add-favorite:hover {
  background: var(--primary-dim); border-style: solid;
  transform: translateY(-2px);
}
.plus-icon { font-size: 1.15rem; margin-right: 4px; vertical-align: middle; }
.add-extra-trigger { margin-bottom: 30px; }
.add-hint { font-size: 0.8rem; color: var(--text-dim); margin-top: 4px; font-weight: 600; }

.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-active .modal-sheet { animation: slideUp 0.4s cubic-bezier(0.18, 0.89, 0.32, 1.28); }
@keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
.bike-card:hover { transform: translateY(-5px); box-shadow: var(--shadow-md); border-color: var(--primary-light); }
.bike-card.selected { 
  border-color: var(--primary); 
  background: var(--primary-dim); 
  box-shadow: 0 10px 25px -5px rgba(67, 56, 202, 0.1); 
}
.bike-card.selected::after {
  content: '✓'; position: absolute; top: 10px; right: 10px;
  background: var(--primary); color: white;
  width: 18px; height: 18px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 0.65rem;
}

.bc-brand { font-size: 0.65rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px; font-weight: 800; margin-bottom: 2px; }
.bc-model { font-weight: 900; font-size: 1rem; color: var(--text-header); margin-bottom: 4px; font-family: 'Outfit'; }
.bc-price { color: var(--accent); font-weight: 800; font-size: 0.9rem; }
.bc-score { font-size: 0.75rem; color: var(--primary); font-weight: 700; margin-top: 8px; }

/* Saaty Guide */
.saaty-guide {
  display: grid; grid-template-columns: repeat(5, 1fr);
  gap: 16px; margin-bottom: 40px;
  background: var(--bg-item); padding: 24px;
  border-radius: var(--r-lg); border: var(--border);
  box-shadow: var(--shadow-sm);
}
.saaty-item { display: flex; flex-direction: column; align-items: center; gap: 8px; text-align: center; }
.saaty-val {
  width: 36px; height: 36px;
  background: var(--primary-dim); color: var(--primary);
  border-radius: 12px; border: 1px solid rgba(67, 56, 202, 0.1);
  display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 1rem;
}
.saaty-label { font-size: 0.8rem; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; }

/* Matrix Styles */
.matrix-scroll { 
  overflow-x: auto; margin-bottom: 32px; padding: 10px 5px;
}
.matrix-grid { 
  display: grid; gap: 8px; min-width: 600px;
  background: var(--bg-2); padding: 16px; border-radius: var(--r-lg);
  border: var(--border);
}
.mh-cell { 
  display: flex; align-items: center; justify-content: center; 
  font-weight: 800; font-size: 0.85rem; color: var(--text-header); 
  background: var(--bg-item); border-radius: 8px; padding: 12px;
  border: var(--border);
}
.mh-empty {
  display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 0.75rem; color: var(--primary);
  text-transform: uppercase; background: var(--bg-2);
  border-radius: 8px; border: var(--border);
}
.mh-empty.criterion-tag {
  background: var(--primary-dim); color: var(--primary);
  border-color: var(--primary-light);
}

.th-label {
  font-size: 0.75rem !important; font-weight: 900 !important;
  color: var(--primary) !important; text-transform: uppercase;
  background: rgba(67, 56, 202, 0.05) !important;
}
.th-label.highlight {
  color: #2563eb !important;
  background: rgba(37, 99, 235, 0.1) !important;
}
.m-input { 
  width: 100%; border: var(--border); border-radius: 8px; 
  padding: 12px; font-family: var(--font); font-weight: 700;
  text-align: center; transition: var(--transition);
  background: var(--bg-item); color: var(--text); outline: none;
}
.m-input.diag { background: var(--bg-2); color: var(--text-dim); }
.m-input.reciprocal { background: var(--bg-2); color: var(--text-secondary); opacity: 0.7; }
.m-input.editable { 
  background: var(--bg-item); border-color: var(--primary); color: var(--primary);
  box-shadow: var(--shadow-sm);
}
.m-input.editable:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-dim); }

.calc-section, #ai-results { margin-top: 40px; scroll-margin-top: 100px; }
#wizard-top { scroll-margin-top: 90px; }
.result-box { 
  margin-top: 24px; padding: 32px; border-radius: var(--r-xl); 
  animation: fadeIn 0.4s ease; overflow: hidden;
}
.result-ok { 
  background: var(--bg-item); border: 2px solid var(--accent); 
  color: var(--accent); box-shadow: 0 10px 30px rgba(16, 185, 129, 0.12); 
  border-radius: var(--r-xl);
}
.result-warn { 
  background: var(--bg-item); border: 2px solid var(--accent2); 
  color: var(--accent2); box-shadow: 0 10px 30px rgba(245, 158, 11, 0.12); 
  border-radius: var(--r-xl);
}

.matrix-actions { display: flex; justify-content: flex-end; margin-top: 16px; }

.result-ok .cr-stats-line span { color: var(--accent); }
.result-warn .cr-stats-line span { color: var(--accent2); }
.result-ok .status-icon { filter: drop-shadow(0 0 8px rgba(16, 185, 129, 0.4)); }
.result-warn .status-icon { filter: drop-shadow(0 0 8px rgba(245, 158, 11, 0.4)); }

.result-content { margin-bottom: 24px; display: flex; flex-direction: column; gap: 8px; }
.result-msg-line { display: flex; align-items: center; gap: 12px; font-size: 1.25rem; }
.cr-stats-line { font-size: 1.1rem; font-weight: 800; font-family: 'Outfit', sans-serif; opacity: 0.9; }
.status-icon { font-size: 1.5rem; }

.detail-table { 
  width: 100%; border-collapse: separate; border-spacing: 0;
  margin-bottom: 24px; border-radius: 12px; overflow: hidden;
}
.result-box .detail-table { border: none; box-shadow: none; }
.detail-table th, .detail-table td { padding: 14px 16px; border-bottom: 1px solid rgba(0,0,0,0.05); text-align: center; font-size: 0.85rem; }
.dark-theme .detail-table th, .dark-theme .detail-table td { border-bottom: 1px solid rgba(255,255,255,0.05); }
.detail-table th { background: rgba(0,0,0,0.02); font-weight: 800; color: var(--text-secondary); border-right: 1px solid rgba(0,0,0,0.03); text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.5px; }
.dark-theme .detail-table th { background: rgba(255,255,255,0.03); border-right: 1px solid rgba(255,255,255,0.05); }
.detail-table td { border-right: var(--border); }
.detail-table td:last-child, .detail-table th:last-child { border-right: none; }
.detail-table tr:last-child td { border-bottom: none; }

.bg-blueish { background: rgba(37, 99, 235, 0.06) !important; color: #2563eb; font-weight: 700; }
.bg-yellowish { background: rgba(245, 158, 11, 0.08) !important; color: #d97706; font-weight: 900; }
.bg-greenish { background: rgba(16, 185, 129, 0.06) !important; color: #059669; font-weight: 700; }

.dark-theme .bg-blueish { background: rgba(59, 130, 246, 0.15) !important; color: #60a5fa; }
.dark-theme .bg-yellowish { background: rgba(245, 158, 11, 0.15) !important; color: #fbbf24; }
.dark-theme .bg-greenish { background: rgba(16, 185, 129, 0.15) !important; color: #34d399; }

.badge { 
  background: var(--bg-2); color: var(--text-header); 
  padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; font-weight: 800;
  border: var(--border);
}

.step-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
}

.step-actions.center {
  justify-content: center;
}

/* Final Result */
.final-results { display: flex; flex-direction: column; gap: 24px; padding: 20px 0; }
.result-card { 
  display: flex; align-items: center; gap: 30px; padding: 32px; 
  background: var(--bg-item); border-radius: var(--r-xl); border: var(--border); 
  box-shadow: var(--shadow-md); position: relative;
}
.result-card.top1 { 
  background: var(--bg-card); border-color: var(--primary); 
  box-shadow: var(--shadow-lg), var(--shadow-glow); transform: scale(1.05); z-index: 2;
}
.rc-rank { font-size: 2.5rem; font-weight: 900; color: var(--text-dim); width: 80px; text-align: center; font-family: 'Outfit'; flex-shrink: 0; }
.result-card.top1 .rc-rank { color: var(--primary); font-size: 3.5rem; }

.rc-img-container { width: 160px; height: 120px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; position: relative; }
.rc-img { max-width: 100%; max-height: 100%; object-fit: contain; transition: transform 0.3s ease; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.1)); }
.result-card:hover .rc-img { transform: scale(1.1) translateY(-4px); }
.rc-info { flex: 1; }

.rc-info h3 { font-size: 1.6rem; margin-bottom: 8px; font-family: 'Outfit'; font-weight: 900; }
.rc-score { font-size: 1.25rem; color: var(--accent); font-weight: 900; }
.rc-ai-score { color: var(--text-dim); font-weight: 600; }

.rc-breakdown { 
  display: grid; grid-template-columns: 1fr; gap: 8px; 
  border-left: 2px solid var(--border-color); padding-left: 30px; 
}
.breakdown-item { display: flex; justify-content: space-between; width: 180px; font-size: 0.85rem; font-weight: 700; }
.breakdown-item span { color: var(--text-secondary); }
.breakdown-item strong { color: var(--primary); }

@media (max-width: 768px) {
  .wizard-header { flex-direction: column; gap: 10px; }
  .step-divider { display: none; }
  .saaty-guide { grid-template-columns: repeat(3, 1fr); }
  .result-card { flex-direction: column; text-align: center; gap: 20px; }
  .rc-breakdown { border-left: none; border-top: 2px solid var(--border-color); padding: 20px 0 0; }
}

/* Mode Actions */
.mode-actions { 
  display: grid; grid-template-columns: 1fr 1fr; gap: 20px; 
  margin: 24px auto 0; text-align: left;
  max-width: 900px; /* Tăng rộng lên một chút theo yêu cầu */
}
.mode-card {
  padding: 24px; border-radius: 20px; border: 2px solid var(--border-color);
  display: flex; flex-direction: column; gap: 15px; cursor: pointer;
  transition: var(--transition); background: var(--bg-card);
}
.mode-card:hover:not(.disabled) { border-color: var(--primary); transform: translateY(-3px); box-shadow: var(--shadow-md); }
.mode-card.disabled { opacity: 0.6; cursor: not-allowed; }
.mode-icon { font-size: 2rem; }
.mode-info h5 { font-size: 1.15rem; margin-bottom: 5px; font-weight: 800; }
.mode-info p { font-size: 0.85rem; color: var(--text-dim); margin: 0; }
.quick-ai { border-color: var(--primary-light); background: var(--primary-dim); }
.expert-ahp { border-color: var(--border-color); }
.actions-footer { 
  margin-top: 10px; border-top: 1px dashed var(--border-color); 
  padding: 10px 0 25px; 
}

/* Quick Results Layer */
.quick-results-layer {
  position: fixed; inset: 0; background: rgba(0,0,32,0.4); 
  backdrop-filter: blur(8px); z-index: 1000;
  display: flex; align-items: center; justify-content: center; padding: 20px;
}
.full-results { width: 100%; max-width: 800px; max-height: 90vh; overflow-y: auto; padding: 40px; position: relative; }
.results-top { display: flex; justify-content: center; position: relative; margin-bottom: 30px; }
.close-results { position: absolute; top: 20px; right: 20px; border: none; background: none; font-size: 1.5rem; cursor: pointer; color: var(--text-dim); }
.quick-bike-list { display: flex; flex-direction: column; gap: 12px; }
.quick-bike-card { 
  display: flex; align-items: center; gap: 20px; padding: 20px; 
  background: var(--bg-item); border-radius: 18px; border: 1px solid var(--border-color);
}
.quick-bike-card.top1 { border-color: var(--accent2); background: var(--accent2-dim); }
.qb-rank { font-size: 1.5rem; font-weight: 900; color: var(--text-dim); width: 40px; }
.quick-bike-card.top1 .qb-rank { color: var(--accent2); }
.qb-main { flex: 1; }
.qb-meta { font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px; }
.qb-name { font-size: 1.25rem; font-weight: 850; color: var(--text-header); }
.qb-price { font-size: 0.9rem; color: var(--accent); font-weight: 700; }
.qb-score-box { text-align: right; }
.qb-score { font-size: 1.5rem; font-weight: 950; color: var(--primary); }
.qb-label { font-size: 0.7rem; color: var(--text-dim); font-weight: 700; }
.quick-footer { margin-top: 30px; text-align: center; border-top: 1px solid var(--border-color); padding-top: 20px; }

@media (max-width: 900px) {
  .manual-charts-row { grid-template-columns: 1fr; }
}

/* Manual Results Chart */
.manual-charts-row { display: grid; grid-template-columns: 1fr 1.2fr; gap: 24px; margin-bottom: 30px; width: 100%; }
.glass-card-nested { background: var(--bg-2); border: 1px solid var(--border-color); border-radius: var(--r-lg); padding: 24px; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; }
.manual-doughnut-box, .manual-bar-box { min-height: 400px; display: flex; flex-direction: column; overflow: hidden; }
.card-header-compact { margin-bottom: 20px; }
.card-header-compact h4 { font-size: 1.1rem; font-weight: 850; margin-bottom: 4px; color: var(--text-header); }
.card-header-compact p { font-size: 0.8rem; color: var(--text-dim); }
.chart-box-manual { flex: 1; height: 300px; position: relative; width: 100%; display: flex; align-items: center; justify-content: center; }

/* Colorful Buttons Additions */
.btn-calc-colorful {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  font-weight: 800;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}
.btn-calc-colorful:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.6);
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
}
.btn-calc-colorful:disabled { opacity: 0.6; cursor: not-allowed; box-shadow: none; transform: none; }
.btn-calc-colorful::after {
  content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 60%);
  opacity: 0; transition: opacity 0.3s ease; pointer-events: none;
}
.btn-calc-colorful:hover::after { opacity: 1; }

.btn-back-colorful {
  background: var(--bg-card);
  color: #f59e0b;
  border: 2px solid #f59e0b;
  font-weight: 800;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.15);
  transition: all 0.3s ease;
}
.btn-back-colorful:hover {
  background: #f59e0b;
  color: white;
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
  transform: translateY(-2px);
}

/* Preset Buttons Additions */
.preset-weights-section {
  margin-bottom: 24px;
  background: var(--bg-card);
  padding: 20px;
  border-radius: var(--r-lg);
  border: 1px dashed var(--border-color);
  box-shadow: var(--shadow-sm);
}
.preset-label { font-weight: 800; color: var(--text-header); margin-bottom: 12px; margin-top: 0; font-size: 0.95rem; }
.preset-buttons { display: flex; gap: 12px; flex-wrap: wrap; }
.preset-buttons .btn { font-size: 0.87rem; padding: 8px 16px; border-radius: var(--r-md); }

.btn-demo {
  background: var(--bg-card);
  border: 2px solid transparent;
  font-weight: 800;
  transition: all 0.3s ease;
  cursor: pointer;
}
.student-demo { color: #3b82f6; border-color: #3b82f6; }
.student-demo:hover { background: #3b82f6; color: white; transform: translateY(-2px); }
.office-demo { color: #8b5cf6; border-color: #8b5cf6; }
.office-demo:hover { background: #8b5cf6; color: white; transform: translateY(-2px); }
.tour-demo { color: #ef4444; border-color: #ef4444; }
.tour-demo:hover { background: #ef4444; color: white; transform: translateY(-2px); }

</style>
