<template>
  <div class="admin-tab page-container">
    <div class="section-title">
      <h2>🛠️ Quản trị hệ thống</h2>
      <p>Quản lý danh sách xe, hiệu chỉnh thông số và đào tạo lại mô hình AI</p>
    </div>

    <!-- Login View -->
    <div v-if="!isLoggedIn" class="login-view glass-card">
      <div class="login-header">
        <span class="lock-icon">🔒</span>
        <h3>Đăng nhập quản trị</h3>
        <p>Vui lòng nhập tài khoản để truy cập hệ thống</p>
      </div>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="field">
          <label>Tên đăng nhập</label>
          <input v-model="loginForm.username" required class="admin-input" placeholder="admin" />
        </div>
        <div class="field">
          <label>Mật khẩu</label>
          <input v-model="loginForm.password" type="password" required class="admin-input" placeholder="••••••••" />
        </div>
        <button type="submit" class="btn btn-primary login-btn" :disabled="loggingIn">
          {{ loggingIn ? 'Đang xác thực...' : 'Đăng nhập' }}
        </button>
        <p v-if="loginError" class="login-error">{{ loginError }}</p>
      </form>
    </div>

    <!-- Admin Content -->
    <div v-else class="admin-grid">
      <!-- Sidebar / Navigation -->
      <aside class="admin-sidebar glass-card">
        <nav>
          <button 
            class="nav-item" 
            :class="{ active: currentSubTab === 'motorcycles' }"
            @click="currentSubTab = 'motorcycles'"
          >🏍️ Quản lý Xe</button>
          <button 
            class="nav-item" 
            :class="{ active: currentSubTab === 'ai' }"
            @click="currentSubTab = 'ai'"
          >🤖 Đào tạo AI</button>
          
          <div class="nav-divider"></div>
          
          <button class="nav-item logout-btn" @click="handleLogout">🚪 Đăng xuất</button>
        </nav>
      </aside>

      <!-- Main Content -->
      <main class="admin-main">
        <!-- Motorcycles CRUD -->
        <div v-if="currentSubTab === 'motorcycles'" class="crud-view">
          <div class="view-header">
            <div class="search-bar glass-card">
              <span>🔍</span>
              <input v-model="searchQuery" placeholder="Tìm xe cần sửa..." />
            </div>
            <button class="btn btn-primary" @click="openModal()">+ Thêm xe mới</button>
          </div>

          <div class="table-wrap glass-card">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>Image</th>
                  <th>Brand</th>
                  <th>Model</th>
                  <th>Type</th>
                  <th>Price (M)</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="bike in filteredBikes" :key="bike.id">
                  <td>
                    <img v-if="bike.image_url" :src="bike.image_url" height="40" style="border-radius: 4px; object-fit: contain;" />
                    <span v-else class="text-dim">N/A</span>
                  </td>
                  <td><strong>{{ bike.brand }}</strong></td>
                  <td>{{ bike.model }}</td>
                  <td>{{ bike.vehicle_type }}</td>
                  <td class="text-warning">{{ bike.price_million_vnd }}M</td>
                  <td class="actions">
                    <button class="btn-icon" @click="openModal(bike)">✏️</button>
                    <button class="btn-icon delete" @click="handleDelete(bike.id)">🗑️</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- AI Retrain -->
        <div v-if="currentSubTab === 'ai'" class="ai-view glass-card">
          <h3>Huấn luyện lại mô hình AI</h3>
          <p>Mô hình Random Forest sẽ học lại cách dự đoán trọng số AHP từ dữ liệu người dùng ảo.</p>
          <div class="retrain-form">
             <label>Số mẫu giả lập (Simulation Samples)</label>
             <input type="number" v-model.number="retrainSamples" min="100" max="2000" class="admin-input" />
             <button class="btn btn-secondary" @click="handleRetrain" :disabled="retraining">
                {{ retraining ? 'Đang huấn luyện...' : '🚀 Bắt đầu Train' }}
             </button>
          </div>
          <div v-if="retrainResult" class="retrain-result result-ok">
             ✅ Hoàn tất! MAE: {{ retrainResult.metrics.mae.toFixed(4) }} | RMSE: {{ retrainResult.metrics.rmse.toFixed(4) }}
          </div>
        </div>
      </main>
    </div>

    <!-- Edit/Create Modal -->
    <div v-if="modalOpen" class="modal-overlay" @click.self="modalOpen = false">
      <div class="modal-content glass-card">
        <h3>{{ editingId !== null ? 'Chỉnh sửa xe' : 'Thêm xe mới' }}</h3>
        <form @submit.prevent="saveBike" class="bike-form">
          <div class="form-grid">
            <div class="field">
              <label>Hãng (Brand)</label>
              <input v-model="form.brand" required class="admin-input" />
            </div>
            <div class="field">
              <label>Model</label>
              <input v-model="form.model" required class="admin-input" />
            </div>
            <div class="field">
              <label>Loại xe</label>
              <select v-model="form.vehicle_type" class="admin-input select-input">
                <option>Xe số</option>
                <option>Xe tay ga</option>
                <option>Xe côn tay</option>
              </select>
            </div>
            <div class="field">
              <label>Đường dẫn Hình ảnh (URL)</label>
              <input v-model="form.image_url" class="admin-input" placeholder="/bikes/example.png" />
            </div>
            <div class="field">
               <label>Dung tích (cc)</label>
               <input type="number" v-model.number="form.engine_cc" required class="admin-input" />
            </div>
            <div class="field">
               <label>Giá (M VNĐ)</label>
               <input type="number" step="0.1" v-model.number="form.price_million_vnd" required class="admin-input" />
            </div>
            <div class="field">
               <label>Tiêu thụ xăng (L/100km)</label>
               <input type="number" step="0.01" v-model.number="form.fuel_consumption_l_per_100km" required class="admin-input" />
            </div>
            <div class="field divider">--- Điểm số AHP (1-10) ---</div>
            <div class="field">
               <label>Hiệu năng</label>
               <input type="number" step="0.1" v-model.number="form.performance_score" max="10" class="admin-input" />
            </div>
            <div class="field">
               <label>Thiết kế</label>
               <input type="number" step="0.1" v-model.number="form.design_score" max="10" class="admin-input" />
            </div>
            <div class="field">
               <label>Thương hiệu</label>
               <input type="number" step="0.1" v-model.number="form.brand_score" max="10" class="admin-input" />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" @click="modalOpen = false">Hủy</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
               {{ saving ? 'Đang lưu...' : 'Lưu thay đổi' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminGetMotorcycles, adminCreateMotorcycle, adminUpdateMotorcycle, adminDeleteMotorcycle, retrainModel, adminLogin } from '../../api.js'

const isLoggedIn = ref(!!localStorage.getItem('admin_token'))
const loginForm = ref({ username: '', password: '' })
const loggingIn = ref(false)
const loginError = ref('')

const bikes = ref([])
const currentSubTab = ref('motorcycles')
const searchQuery = ref('')
const loading = ref(false)
const saving = ref(false)

const modalOpen = ref(false)
const editingId = ref(null)
const form = ref({
  brand: '', model: '', vehicle_type: 'Xe số', engine_cc: 110,
  price_million_vnd: 0, fuel_consumption_l_per_100km: 0,
  performance_score: 7, design_score: 7, brand_score: 7
})

const retraining = ref(false)
const retrainSamples = ref(300)
const retrainResult = ref(null)

const handleLogin = async () => {
  loggingIn.value = true
  loginError.value = ''
  try {
    const res = await adminLogin(loginForm.value.username, loginForm.value.password)
    localStorage.setItem('admin_token', res.token)
    isLoggedIn.value = true
    await loadBikes()
  } catch (e) {
    loginError.value = e.message
  } finally {
    loggingIn.value = false
  }
}

const handleLogout = () => {
  localStorage.removeItem('admin_token')
  isLoggedIn.value = false
  bikes.value = []
}

const loadBikes = async () => {
  if (!isLoggedIn.value) return
  loading.value = true
  try {
    bikes.value = await adminGetMotorcycles()
  } catch (e) {
    if (e.message.includes('403') || e.message.includes('401')) {
      handleLogout()
    }
  } finally {
    loading.value = false
  }
}

const filteredBikes = computed(() => {
  const q = searchQuery.value.toLowerCase()
  return bikes.value.filter(b => 
    b.brand.toLowerCase().includes(q) || 
    b.model.toLowerCase().includes(q)
  )
})

const openModal = (bike = null) => {
  if (bike) {
    editingId.value = bike.id
    form.value = { ...bike }
  } else {
    editingId.value = null
    form.value = {
      brand: '', model: '', vehicle_type: 'Xe số', engine_cc: 110,
      price_million_vnd: 20, fuel_consumption_l_per_100km: 1.8,
      performance_score: 5, design_score: 5, brand_score: 5,
      image_url: ''
    }
  }
  modalOpen.value = true
}

const saveBike = async () => {
  saving.value = true
  try {
    if (editingId.value !== null) {
      await adminUpdateMotorcycle(editingId.value, form.value)
    } else {
      await adminCreateMotorcycle(form.value)
    }
    modalOpen.value = false
    await loadBikes()
  } catch (e) {
    alert(e.message)
  } finally {
    saving.value = false
  }
}

const handleDelete = async (id) => {
  if (!confirm('Bạn có chắc muốn xóa xe này?')) return
  try {
    await adminDeleteMotorcycle(id)
    await loadBikes()
  } catch (e) {
    alert(e.message)
  }
}

const handleRetrain = async () => {
  retraining.value = true
  try {
    const res = await retrainModel(retrainSamples.value)
    retrainResult.value = res
  } catch (e) {
    alert(e.message)
  } finally {
    retraining.value = false
  }
}

onMounted(loadBikes)
</script>

<style scoped>
.admin-tab { padding: 40px 0; }
.admin-grid { display: grid; grid-template-columns: 240px 1fr; gap: 30px; }

.admin-sidebar { padding: 20px; height: fit-content; }
.nav-item {
  width: 100%; text-align: left; padding: 14px 20px; border-radius: var(--r-md);
  background: transparent; border: none; color: var(--text-secondary);
  cursor: pointer; font-family: var(--font); font-weight: 700; transition: var(--transition);
  margin-bottom: 8px; font-size: 1rem;
}
.nav-item:hover { background: var(--bg-card-hover); color: var(--text); }
.nav-item.active { background: var(--primary-dim); color: var(--primary); }

.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; gap: 24px; }
.search-bar { flex: 1; display: flex; align-items: center; padding: 12px 20px; gap: 12px; }
.search-bar input { background: transparent; border: none; outline: none; color: var(--text-header); width: 100%; font-family: var(--font); font-size: 1rem; font-weight: 600; }

.admin-table { width: 100%; border-collapse: collapse; }
.admin-table th, .admin-table td { padding: 16px; text-align: left; border-bottom: var(--border); }
.admin-table td { font-size: 0.95rem; font-weight: 600; color: var(--text-header); }
.admin-table th { font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase; font-weight: 800; letter-spacing: 1px; }

.actions { display: flex; gap: 10px; }
.btn-icon { background: var(--bg-card); border: var(--border); padding: 10px; border-radius: 10px; cursor: pointer; transition: 0.2s; font-size: 1rem; }
.btn-icon:hover { background: var(--primary-dim); border-color: var(--primary); transform: scale(1.1); }
.btn-icon.delete:hover { background: var(--danger-dim); border-color: var(--danger); }

.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(12px);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
  animation: fadeIn 0.3s ease;
}
.modal-content { width: 100%; max-width: 650px; padding: 40px; animation: slideUp 0.3s ease; }
@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

.bike-form .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 24px 0; }
.field { display: flex; flex-direction: column; gap: 8px; }
.field label { font-size: 0.85rem; font-weight: 800; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; }
.admin-input {
  padding: 14px; border-radius: 12px; background: var(--bg-item); border: var(--border); color: var(--text-header);
  font-family: var(--font); font-size: 1rem; outline: none; transition: 0.2s; font-weight: 600;
}
.select-input {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2364748b'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  background-size: 16px;
  padding-right: 40px;
}
.admin-input:focus { border-color: var(--primary); box-shadow: 0 0 0 4px var(--primary-dim); }
.field.divider { grid-column: 1 / -1; text-align: center; font-weight: 900; opacity: 0.5; font-size: 0.75rem; margin: 15px 0; color: var(--primary); text-transform: uppercase; }
.modal-actions { display: flex; justify-content: flex-end; gap: 16px; margin-top: 32px; }

.ai-view { padding: 40px; }
.retrain-form { display: flex; flex-direction: column; gap: 16px; max-width: 400px; margin: 30px 0; }
.retrain-form label { font-size: 0.9rem; font-weight: 800; color: var(--text-secondary); }
.retrain-result { margin-top: 24px; padding: 20px; border-radius: 12px; font-weight: 700; font-size: 1rem; }

.result-ok { background: var(--accent-dim); color: var(--accent); border: 1px solid var(--accent); }

@media (max-width: 768px) {
  .admin-grid { grid-template-columns: 1fr; }
  .bike-form .form-grid { grid-template-columns: 1fr; }
}

/* Login Styles */
.login-view {
  max-width: 450px; margin: 80px auto; padding: 50px; text-align: center;
  animation: fadeIn 0.4s ease;
}
.login-header { margin-bottom: 40px; }
.lock-icon { font-size: 3.5rem; display: block; margin-bottom: 20px; filter: drop-shadow(0 0 15px var(--primary-dim)); }
.login-header h3 { font-size: 2rem; margin-bottom: 10px; }
.login-header p { font-size: 1rem; color: var(--text-secondary); }
.login-form { display: flex; flex-direction: column; gap: 24px; text-align: left; }
.login-btn { width: 100%; padding: 16px; font-weight: 800; margin-top: 15px; font-size: 1.1rem; }
.login-error { color: var(--danger); font-size: 0.95rem; margin-top: 20px; text-align: center; font-weight: 700; }

.nav-divider { height: 1px; background: var(--border); margin: 15px 0; opacity: 0.5; }
.logout-btn:hover { color: var(--danger) !important; background: var(--danger-dim) !important; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
