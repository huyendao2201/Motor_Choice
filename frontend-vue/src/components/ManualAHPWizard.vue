<template>
  <div class="manual-ahp-wizard">
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
      <div v-else class="glass-card step-content">
        <div class="step-title text-center">
          <h3>🤖 AI Random Forest Đã Đề Xuất</h3>
          <p>Dưới đây là các phương án xe tốt nhất do AI đề xuất. Vui lòng chọn (tick) từ 2-5 xe để tiến hành lập ma trận phân tích AHP kiểm chứng thủ công.</p>
        </div>

        <div class="bike-selection">
          <div class="selected-count text-center">Đã chọn: <strong class="text-primary">{{ selectedBikes.length }}</strong>/5 xe</div>
          <div class="bike-grid">
            <div v-for="b in aiResult.top_motorcycles" :key="b.model" 
                 class="bike-card" 
                 :class="{ selected: isSelected(b) }"
                 @click="toggleBike(b)">
              <div class="bc-brand">{{ b.brand }}</div>
              <div class="bc-model">{{ b.model }}</div>
              <div class="bc-price">{{ b.price_million_vnd }} Triệu</div>
              <div class="bc-score">AI Score: {{(b.total_score * 100).toFixed(1)}}%</div>
            </div>
          </div>
        </div>

        <div class="step-actions center">
          <button class="btn btn-ghost" @click="aiResult = null; selectedBikes = []">⬅ Chạy lại AI</button>
          <button class="btn btn-primary" :disabled="selectedBikes.length < 2 || selectedBikes.length > 5" @click="goToStep2">Bắt đầu lập ma trận AHP ➔</button>
        </div>
      </div>
    </div>

    <!-- BƯỚC 2: Trọng số Tiêu chí -->
    <div v-if="step === 2" class="wizard-step glass-card">
      <div class="step-title">
        <h3>⚖️ Bước 2: Đánh giá tầm quan trọng của các Tiêu chí</h3>
        <p>So sánh mức độ quan trọng giữa các tiêu chí (1: Ngang nhau, 3: Hơn chút, 5: Hơn nhiều, 7: Rất nhiều, 9: Cực kỳ)</p>
      </div>

      <div class="matrix-scroll">
        <div class="matrix-grid" :style="{ gridTemplateColumns: `100px repeat(5, 1fr)` }">
          <div class="mh-empty"></div>
          <div v-for="c in CRITERIA" :key="c.id" class="mh-cell">{{ c.label }}</div>
          
          <template v-for="(row, i) in 5" :key="'cr_row_'+i">
            <div class="mh-cell">{{ CRITERIA[i].label }}</div>
            <div v-for="(col, j) in 5" :key="'cr_col_'+j">
              <input v-if="i === j" class="m-input diag" value="1" readonly />
              <input v-else-if="i < j" class="m-input editable" type="number" :min="1/9" :max="9" step="0.5" 
                     v-model.number="criteriaMatrix[i][j]" @change="updateCriteriaMatrix(i, j)" />
              <input v-else class="m-input reciprocal" :value="getReciprocal(criteriaMatrix[j][i])" readonly />
            </div>
          </template>
        </div>
      </div>

      <div class="calc-section">
        <button class="btn btn-secondary" @click="calcCriteriaWeights" :disabled="calculating">Tính trọng số Tiêu chí</button>
        <div v-if="criteriaResult" class="result-box" :class="criteriaResult.is_consistent ? 'result-ok' : 'result-warn'">
          
          <div class="table-responsive mb-3" v-if="criteriaResult.details">
            <table class="detail-table">
              <thead>
                <tr>
                  <th></th>
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

          <div><strong>{{ criteriaResult.message }}</strong></div>
          <div class="cr-stats">CR: {{ criteriaResult.CR }} | λ_max: {{ criteriaResult.lambda_max }}</div>
          <div class="weights-list">
             <span v-for="(w, idx) in criteriaResult.weights" :key="idx" class="badge">
               {{ CRITERIA[idx].label }}: {{(w*100).toFixed(1)}}%
             </span>
          </div>
        </div>
      </div>

      <div class="step-actions">
        <button class="btn btn-ghost" @click="step = 1">⬅ Quay lại</button>
        <button class="btn btn-primary" :disabled="!criteriaResult || !criteriaResult.is_consistent" @click="goToStep3">Tiếp tục ➔</button>
      </div>
    </div>

    <!-- BƯỚC 3: Trọng số Phương án -->
    <div v-if="step === 3" class="wizard-step glass-card">
      <div class="step-title">
        <h3>🏍️ Bước 3: So sánh các Phương án (Xe) theo từng Tiêu chí</h3>
        <p>Tiêu chí hiện tại: <strong class="text-primary">{{ CRITERIA[currentCriterionIndex].label }}</strong> ({{ currentCriterionIndex + 1 }}/5)</p>
      </div>

      <div class="matrix-scroll">
        <div class="matrix-grid" :style="{ gridTemplateColumns: `120px repeat(${selectedBikes.length}, 1fr)` }">
          <div class="mh-empty"></div>
          <div v-for="b in selectedBikes" :key="'h'+b.model" class="mh-cell">{{ b.model }}</div>
          
          <template v-for="(row, i) in selectedBikes.length" :key="'alt_row_'+i">
            <div class="mh-cell">{{ selectedBikes[i].model }}</div>
            <div v-for="(col, j) in selectedBikes.length" :key="'alt_col_'+j">
              <input v-if="i === j" class="m-input diag" value="1" readonly />
              <input v-else-if="i < j" class="m-input editable" type="number" :min="1/9" :max="9" step="0.5" 
                     v-model.number="currentAltMatrix[i][j]" @change="updateAltMatrix(i, j)" />
              <input v-else class="m-input reciprocal" :value="getReciprocal(currentAltMatrix[j][i])" readonly />
            </div>
          </template>
        </div>
      </div>

      <div class="calc-section">
        <button class="btn btn-secondary" @click="calcCurrentAltWeights" :disabled="calculating">Tính trọng số PA</button>
        <div v-if="altResults[CRITERIA[currentCriterionIndex].id]" class="result-box" 
             :class="altResults[CRITERIA[currentCriterionIndex].id].is_consistent ? 'result-ok' : 'result-warn'">
          
          <div class="table-responsive mb-3" v-if="altResults[CRITERIA[currentCriterionIndex].id].details">
            <table class="detail-table">
              <thead>
                <tr>
                  <th></th>
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

          <div><strong>{{ altResults[CRITERIA[currentCriterionIndex].id].message }}</strong></div>
          <div class="cr-stats">CR: {{ altResults[CRITERIA[currentCriterionIndex].id].CR }} | λ_max: {{ altResults[CRITERIA[currentCriterionIndex].id].lambda_max }}</div>
          <div class="weights-list">
             <span v-for="(w, idx) in altResults[CRITERIA[currentCriterionIndex].id].weights" :key="idx" class="badge">
               {{ selectedBikes[idx].model }}: {{(w*100).toFixed(1)}}%
             </span>
          </div>
        </div>
      </div>

      <div class="step-actions">
        <button class="btn btn-ghost" @click="prevCriterion">⬅ Quay lại</button>
        <button class="btn btn-primary" :disabled="!altResults[CRITERIA[currentCriterionIndex].id] || !altResults[CRITERIA[currentCriterionIndex].id].is_consistent" @click="nextCriterion">
          {{ currentCriterionIndex === 4 ? 'Hoàn tất & Xem Kết quả ➔' : 'Tiêu chí tiếp theo ➔' }}
        </button>
      </div>
    </div>

    <!-- BƯỚC 4: Kết quả -->
    <div v-if="step === 4" class="wizard-step glass-card">
      <div class="step-title text-center">
        <h2>🏆 Kết Quả Đánh Giá AHP Thủ Công</h2>
        <p>Tổng hợp điểm ưu tiên dựa trên các ma trận bạn vừa nhập.</p>
      </div>

      <div class="final-results">
        <div v-for="(res, idx) in finalRanking" :key="idx" class="result-card" :class="{ top1: idx === 0 }">
          <div class="rc-rank">#{{ idx + 1 }}</div>
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

      <div class="step-actions center mt-4">
        <button class="btn btn-secondary" @click="step = 1; aiResult = null; selectedBikes = []">Tư vấn lại từ đầu</button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { getMotorcycles, calculateAHP, recommend } from '../api.js'
import ProfileForm from './ProfileForm.vue'

const step = ref(1)
const calculating = ref(false)

// Step 1: AI Result
const aiResult = ref(null)
const selectedBikes = ref([])
const loadingAI = ref(false)

async function handleAISubmit(payload) {
  loadingAI.value = true
  try {
    const data = await recommend(payload)
    aiResult.value = data
    // Tự động chọn top 3
    selectedBikes.value = data.top_motorcycles.slice(0, 3)
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
      alert('Chỉ chọn tối đa 5 xe để ma trận không quá lớn!')
      return
    }
    selectedBikes.value.push(b)
  }
}

// Step 2: Criteria
const CRITERIA = [
  { label: 'Giá', id: 'price' }, 
  { label: 'Xăng', id: 'fuel' },
  { label: 'Hiệu năng', id: 'performance' }, 
  { label: 'Thiết kế', id: 'design' }, 
  { label: 'Thương hiệu', id: 'brand' }
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

function updateCriteriaMatrix(i, j) {
  const val = parseFloat(criteriaMatrix.value[i][j]);
  if(isNaN(val) || val <= 0) criteriaMatrix.value[i][j] = 1;
}

function getReciprocal(v) {
  const val = parseFloat(v);
  if(isNaN(val) || val === 0) return '';
  return (1 / val).toFixed(3);
}

function goToStep2() {
  if(!criteriaResult.value) initCriteriaMatrix();
  step.value = 2;
}

async function calcCriteriaWeights() {
  calculating.value = true;
  try {
    const fullMat = Array(5).fill(null).map(() => Array(5).fill(1));
    for(let i=0; i<5; i++){
      for(let j=0; j<5; j++){
        if(i === j) fullMat[i][j] = 1;
        else if(i < j) fullMat[i][j] = parseFloat(criteriaMatrix.value[i][j]);
        else fullMat[i][j] = 1 / parseFloat(criteriaMatrix.value[j][i]);
      }
    }
    const res = await calculateAHP(fullMat);
    criteriaResult.value = res;
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
  const val = parseFloat(altMatrices.value[cid][i][j]);
  if(isNaN(val) || val <= 0) altMatrices.value[cid][i][j] = 1;
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
        else if(i < j) fullMat[i][j] = parseFloat(mat[i][j]);
        else fullMat[i][j] = 1 / parseFloat(mat[j][i]);
      }
    }
    const names = selectedBikes.value.map(b => b.model);
    
    // Sử dụng API tính AHP đã được thiết lập trong api.js
    const res = await calculateAHP(fullMat, names);
    
    altResults.value[cid] = res;
  } catch(e) {
    alert("Lỗi tính toán: " + e.message);
  } finally {
    calculating.value = false;
  }
}

function prevCriterion() {
  if(currentCriterionIndex.value > 0) currentCriterionIndex.value--;
  else step.value = 2;
}

function nextCriterion() {
  if(currentCriterionIndex.value < 4) {
    currentCriterionIndex.value++;
  } else {
    calculateFinalRanking();
    step.value = 4;
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

</script>

<style scoped>
.manual-ahp-wizard { width: 100%; max-width: 1000px; margin: 0 auto; padding: 20px 0; }
.wizard-header { display: flex; align-items: center; justify-content: center; margin-bottom: 30px; }
.step-indicator { padding: 10px 16px; border-radius: 30px; background: rgba(255,255,255,0.05); font-weight: 700; color: var(--text-dim); transition: 0.3s; }
.step-indicator.active { background: var(--primary); color: #fff; box-shadow: 0 0 15px var(--primary); }
.step-indicator.completed { background: var(--primary-dark); color: #fff; }
.step-divider { flex: 1; max-width: 60px; height: 2px; background: rgba(255,255,255,0.1); margin: 0 10px; }

.wizard-step { padding: 30px; animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from{opacity:0; transform:translateY(10px)} to{opacity:1; transform:translateY(0)} }

.step-title { margin-bottom: 24px; }
.step-title h3 { font-size: 1.4rem; color: var(--primary-light); margin-bottom: 8px; }
.step-title p { color: var(--text-secondary); font-size: 0.95rem; }

.filters { display: flex; gap: 12px; margin-bottom: 20px; }
.m-input { padding: 10px 14px; border-radius: var(--r-md); background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #fff; flex: 1; outline: none; }
.m-input:focus { border-color: var(--primary); }
.m-input option { background: #1e1e1e; }

.bike-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; max-height: 400px; overflow-y: auto; padding-right: 10px; }
.bike-card { padding: 15px; border-radius: var(--r-md); background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); cursor: pointer; transition: 0.2s; }
.bike-card:hover { background: rgba(255,255,255,0.08); }
.bike-card.selected { border-color: var(--primary); background: rgba(99,102,241,0.15); box-shadow: 0 0 10px rgba(99,102,241,0.2); }
.bc-brand { font-size: 0.8rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; }
.bc-model { font-weight: 800; font-size: 1.1rem; margin: 4px 0; }
.bc-price { color: var(--accent); font-weight: 700; }
.selected-count { margin-bottom: 10px; font-weight: 600; }

.step-actions { display: flex; justify-content: space-between; margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); }
.step-actions.center { justify-content: center; }

/* Matrix Styles */
.matrix-scroll { overflow-x: auto; margin-bottom: 24px; padding-bottom: 10px; }
.matrix-grid { display: grid; gap: 6px; }
.mh-cell { display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; color: var(--primary-light); background: rgba(0,0,0,0.2); border-radius: 4px; padding: 8px;}
.m-input.diag { background: rgba(255,255,255,0.1); color: var(--text-dim); text-align: center; }
.m-input.reciprocal { background: transparent; opacity: 0.5; text-align: center; }
.m-input.editable { text-align: center; background: rgba(99,102,241,0.05); border-color: rgba(99,102,241,0.3); font-weight: bold;}
.m-input.editable:focus { background: rgba(99,102,241,0.15); }

.calc-section { background: rgba(0,0,0,0.2); padding: 20px; border-radius: var(--r-md); }
.result-box { margin-top: 15px; padding: 15px; border-radius: var(--r-md); border: 1px solid; }
.result-ok { background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.3); color: #10b981; }
.result-warn { background: rgba(245,158,11,0.1); border-color: rgba(245,158,11,0.3); color: #f59e0b; }
.cr-stats { font-size: 0.85rem; margin: 8px 0; }
.weights-list { display: flex; flex-wrap: wrap; gap: 8px; }
.badge { background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; color: #fff; }

/* Final Result */
.final-results { display: flex; flex-direction: column; gap: 15px; }
.result-card { display: flex; align-items: center; gap: 20px; padding: 20px; background: rgba(255,255,255,0.03); border-radius: var(--r-lg); border: 1px solid rgba(255,255,255,0.05); }
.result-card.top1 { background: rgba(99,102,241,0.1); border-color: var(--primary); box-shadow: 0 0 20px rgba(99,102,241,0.15); transform: scale(1.02); }
.rc-rank { font-size: 2rem; font-weight: 900; color: var(--primary-light); width: 60px; text-align: center; }
.result-card.top1 .rc-rank { font-size: 2.8rem; color: var(--accent); }
.rc-info { flex: 1; }
.rc-info h3 { font-size: 1.4rem; margin-bottom: 5px; }
.rc-score { font-size: 1.1rem; color: var(--accent); }
.rc-breakdown { display: flex; flex-direction: column; gap: 4px; font-size: 0.8rem; color: var(--text-dim); border-left: 1px solid rgba(255,255,255,0.1); padding-left: 20px; }
.breakdown-item { display: flex; justify-content: space-between; width: 150px; }

/* Detail Table */
.table-responsive { overflow-x: auto; }
.mb-3 { margin-bottom: 20px; }
.detail-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; background: rgba(0,0,0,0.1); }
.detail-table th, .detail-table td { padding: 8px 12px; border: 1px solid rgba(255,255,255,0.1); text-align: center; }
.detail-table th { background: rgba(255,255,255,0.05); font-weight: 700; color: var(--primary-light); }
.bg-blueish { background: rgba(59, 130, 246, 0.15) !important; color: #93c5fd; }
.bg-yellowish { background: rgba(234, 179, 8, 0.15) !important; color: #fde047; font-weight: bold; }
.bg-greenish { background: rgba(34, 197, 94, 0.15) !important; color: #86efac; }

</style>
