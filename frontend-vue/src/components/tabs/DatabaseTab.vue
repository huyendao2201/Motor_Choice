<template>
  <div class="db-tab page-container">
    <div class="section-title">
      <h2 style = "font-size: 35px;"> Danh sách xe</h2>
      <p style = "font-size: 15px;">Tổng cộng <strong class="text-success">{{ filtered.length }}</strong> / {{ all.length }} mẫu xe · Đây là tập alternatives cho hệ DSS</p>
    </div>

    <!-- Controls -->
    <div class="db-controls glass-card">
      <div class="search-wrap">
        <span class="search-icon">🔍</span>
        <input v-model="search" type="text" placeholder="Tìm kiếm theo tên, hãng xe..." class="search-input" />
        <button v-if="search" class="search-clear" @click="search = ''">✕</button>
      </div>
      <div class="filter-row">
        <button
          v-for="t in vehicleTypeFilters"
          :key="t.value"
          class="filter-btn"
          :class="{ active: typeFilter === t.value }"
          @click="typeFilter = t.value"
        >{{ t.label }} <span class="filter-count">{{ typeCounts[t.value] || 0 }}</span></button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-row" v-if="stats">
      <div class="stat-card glass-card">
        <span class="stat-card-icon">🏷️</span>
        <div class="stat-card-num">{{ stats.total }}</div>
        <div class="stat-card-label">Tổng mẫu xe</div>
      </div>
      <div class="stat-card glass-card">
        <span class="stat-card-icon">💰</span>
        <div class="stat-card-num">{{ stats.price_stats?.min }}M</div>
        <div class="stat-card-label">Giá thấp nhất</div>
      </div>
      <div class="stat-card glass-card">
        <span class="stat-card-icon">💎</span>
        <div class="stat-card-num">{{ stats.price_stats?.max }}M</div>
        <div class="stat-card-label">Giá cao nhất</div>
      </div>
      <div class="stat-card glass-card">
        <span class="stat-card-icon">📊</span>
        <div class="stat-card-num">{{ stats.price_stats?.mean }}M</div>
        <div class="stat-card-label">Giá trung bình</div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-wrap">
      <div class="spinner"></div>
      <span>Đang tải dữ liệu...</span>
    </div>

    <!-- Table -->
    <div v-else class="table-wrap glass-card scroll-x">
      <table class="data-table">
        <thead>
          <tr>
            <th @click="sortBy('index')" class="sortable">#</th>
            <th>Hình Ảnh</th>
            <th @click="sortBy('brand')" class="sortable">Hãng <SortIcon :field="'brand'" :sort="sort" /></th>
            <th @click="sortBy('model')" class="sortable">Model <SortIcon :field="'model'" :sort="sort" /></th>
            <th>Loại</th>
            <th @click="sortBy('engine_cc')" class="sortable">Dung tích <SortIcon :field="'engine_cc'" :sort="sort" /></th>
            <th @click="sortBy('price_million_vnd')" class="sortable">Giá (M) <SortIcon :field="'price_million_vnd'" :sort="sort" /></th>
            <th @click="sortBy('fuel_consumption_l_per_100km')" class="sortable">XL (L/100) <SortIcon :field="'fuel_consumption_l_per_100km'" :sort="sort" /></th>
            <th @click="sortBy('performance_score')" class="sortable">Hiệu năng <SortIcon :field="'performance_score'" :sort="sort" /></th>
            <th @click="sortBy('design_score')" class="sortable">Thiết kế <SortIcon :field="'design_score'" :sort="sort" /></th>
            <th @click="sortBy('brand_score')" class="sortable">Thương hiệu <SortIcon :field="'brand_score'" :sort="sort" /></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(b, i) in paginated" :key="i">
            <td class="text-dim text-xs">{{ (currentPage - 1) * pageSize + i + 1 }}</td>
            <td>
              <div class="bike-img-placeholder">
                <img v-if="b.image_url" :src="b.image_url" :alt="b.model" class="bike-img-thumbnail" />
                <img v-else src="/logo-bike.png" alt="Placeholder" style="width: 1.5rem; height: 1.5rem; object-fit: contain; opacity: 0.4;" />
              </div>
            </td>
            <td><strong>{{ b.brand }}</strong></td>
            <td>{{ b.model }}</td>
            <td><span class="tag" :class="typeClass(b.vehicle_type)">{{ b.vehicle_type }}</span></td>
            <td>{{ b.engine_cc }}cc</td>
            <td><strong class="text-warning">{{ b.price_million_vnd }}M</strong></td>
            <td>{{ b.fuel_consumption_l_per_100km }}L</td>
            <td>
              <ScoreBar :value="b.performance_score" :max="10" color="#6366f1" />
            </td>
            <td>
              <ScoreBar :value="b.design_score" :max="10" color="#ec4899" />
            </td>
            <td>
              <ScoreBar :value="b.brand_score" :max="10" color="#8b5cf6" />
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty -->
      <div v-if="filtered.length === 0" class="table-empty">
        <span>🔍</span>
        <span>Không tìm thấy xe phù hợp với bộ lọc</span>
      </div>

      <!-- Pagination -->
      <div class="pagination" v-if="totalPages > 1">
        <button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">‹ Trước</button>
        <span class="page-info">Trang {{ currentPage }} / {{ totalPages }}</span>
        <button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">Tiếp ›</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, defineComponent, h } from 'vue'
import { getMotorcycles, getStats } from '../../api.js'

const all = ref([])
const stats = ref(null)
const loading = ref(true)
const search = ref('')
const typeFilter = ref('all')
const sort = ref({ field: 'price_million_vnd', dir: 'asc' })
const currentPage = ref(1)
const pageSize = 20

const vehicleTypeFilters = [
  { value: 'all', label: '🔍 Tất cả' },
  { value: 'Xe số', label: '⚙️ Xe số' },
  { value: 'Xe tay ga', label: '🛵 Tay ga' },
  { value: 'Xe côn tay', label: '🏍️ Côn tay' },
]

const typeCounts = computed(() => {
  const counts = { all: all.value.length, 'Xe số': 0, 'Xe tay ga': 0, 'Xe côn tay': 0 }
  all.value.forEach(b => { if (counts[b.vehicle_type] !== undefined) counts[b.vehicle_type]++ })
  return counts
})

const filtered = computed(() => {
  let data = all.value
  if (typeFilter.value !== 'all') data = data.filter(b => b.vehicle_type === typeFilter.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    data = data.filter(b => b.brand.toLowerCase().includes(q) || b.model.toLowerCase().includes(q))
  }
  // Sort
  const { field, dir } = sort.value
  return [...data].sort((a, b) => {
    const va = a[field] ?? 0, vb = b[field] ?? 0
    return dir === 'asc' ? (va > vb ? 1 : -1) : (va < vb ? 1 : -1)
  })
})

const totalPages = computed(() => Math.ceil(filtered.value.length / pageSize))
const paginated = computed(() => filtered.value.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize))

watch([search, typeFilter], () => { currentPage.value = 1 })

function sortBy(field) {
  if (sort.value.field === field) {
    sort.value.dir = sort.value.dir === 'asc' ? 'desc' : 'asc'
  } else {
    sort.value = { field, dir: 'asc' }
  }
}

function typeClass(t) {
  return { 'Xe số': 'tag-xe-so', 'Xe tay ga': 'tag-tay-ga', 'Xe côn tay': 'tag-con-tay' }[t] || ''
}

onMounted(async () => {
  try {
    const [motoData, statsData] = await Promise.all([getMotorcycles(), getStats()])
    all.value = motoData.motorcycles || []
    stats.value = statsData
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

// Inline sub-components
const SortIcon = defineComponent({
  props: ['field', 'sort'],
  setup(p) {
    return () => {
      if (p.sort.field !== p.field) return h('span', { style: 'opacity:0.2;margin-left:2px' }, '⇅')
      return h('span', { style: 'margin-left:2px;color:var(--primary-light)' },
        p.sort.dir === 'asc' ? '↑' : '↓')
    }
  }
})

const ScoreBar = defineComponent({
  props: ['value', 'max', 'color'],
  setup(p) {
    return () => h('div', { style: 'display:flex;align-items:center;gap:6px' }, [
      h('div', { style: 'flex:1;height:6px;background:var(--bg-2);border-radius:99px;overflow:hidden' }, [
        h('div', { style: `width:${(p.value/p.max)*100}%;height:100%;background:${p.color};border-radius:99px;` })
      ]),
      h('span', { style: 'font-size:0.75rem;font-weight:700;min-width:28px' }, `${p.value}`)
    ])
  }
})
</script>

<style scoped>
.db-tab { padding: 40px 0 80px; }

/* Controls */
.db-controls { 
  padding: 24px; display: flex; flex-direction: column; gap: 20px; margin-bottom: 24px; 
}
.search-wrap {
  position: relative; display: flex; align-items: center;
  background: var(--bg-item); border: var(--border); border-radius: 16px;
  padding: 16px 24px; gap: 14px;
  transition: var(--transition);
  box-shadow: var(--shadow-sm);
}
.search-wrap:focus-within { border-color: var(--primary); transform: translateY(-2px); box-shadow: var(--shadow-md); }
.search-icon { font-size: 1.2rem; flex-shrink: 0; }
.search-input { flex: 1; background: transparent; border: none; outline: none; color: var(--text-header); font-family: var(--font); font-size: 1.1rem; font-weight: 600; }
.search-input::placeholder { color: var(--text-dim); font-weight: 500; }
.search-clear { background: var(--bg-2); border: none; color: var(--text-secondary); cursor: pointer; font-size: 0.8rem; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.search-clear:hover { background: var(--danger-dim); color: var(--danger); }

.filter-row { display: flex; gap: 10px; flex-wrap: wrap; }
.filter-btn {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 28px; border-radius: 16px; border: var(--border);
  background: var(--bg-item); color: var(--text-secondary); cursor: pointer;
  font-family: var(--font); font-size: 1.1rem; font-weight: 700;
  transition: var(--transition);
}
.filter-btn:hover { border-color: var(--primary-light); color: var(--text-header); transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.filter-btn.active { background: var(--primary); border-color: var(--primary); color: white; box-shadow: 0 4px 12px rgba(67, 56, 202, 0.2); }
.filter-count { background: rgba(0,0,0,0.05); border-radius: 8px; padding: 4px 10px; font-size: 0.85rem; font-weight: 800; }
.filter-btn.active .filter-count { background: rgba(255,255,255,0.2); color: white; }

/* Stats */
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }
.stat-card { padding: 24px; display: flex; flex-direction: column; align-items: center; gap: 8px; text-align: center; }
.stat-card-icon { font-size: 1.8rem; margin-bottom: 4px; }
.stat-card-num { font-size: 1.8rem; font-weight: 900; color: var(--text-header); font-family: 'Outfit'; }
.stat-card-label { font-size: 0.75rem; color: var(--text-dim); font-weight: 800; text-transform: uppercase; letter-spacing: 1px; }

/* Table */
.table-wrap { padding: 0; overflow: hidden; border-radius: var(--r-xl); }
.data-table { width: 100%; border-collapse: collapse; text-align: left; }
.data-table th { 
  background: var(--bg-2); padding: 18px 24px; 
  font-size: 0.82rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1.2px;
  color: var(--text-secondary); border-bottom: var(--border);
}

.bike-img-placeholder {
  width: 50px; height: 50px;
  background: var(--bg-card);
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
  border: 1px solid var(--border-color);
}
.bike-img-thumbnail { width: 100%; height: 100%; object-fit: cover; }

.data-table tr { transition: var(--transition); }
.data-table tr:hover:not(thead tr) { background: var(--bg-2); }
.data-table td { padding: 18px 24px; border-bottom: var(--border); font-size: 1rem; font-weight: 600; color: var(--text-header); vertical-align: middle; }

.sortable { cursor: pointer; user-select: none; }
.sortable:hover { color: var(--primary); }

.table-empty { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 80px; color: var(--text-dim); }
.table-empty span:first-child { font-size: 3rem; margin-bottom: 10px; }

/* Pagination */
.pagination { display: flex; align-items: center; justify-content: center; gap: 24px; padding: 24px; background: var(--bg-card); }
.page-btn { 
  padding: 10px 20px; border-radius: 12px; 
  background: var(--bg-item); border: var(--border); color: var(--text-header); 
  cursor: pointer; font-family: var(--font); font-weight: 700; font-size: 0.85rem;
  transition: var(--transition);
  box-shadow: var(--shadow-sm);
}
.page-btn:hover:not(:disabled) { border-color: var(--primary); color: var(--primary); transform: translateY(-2px); box-shadow: var(--shadow-md); }
.page-btn:disabled { opacity: 0.3; cursor: not-allowed; box-shadow: none; }
.page-info { font-size: 0.9rem; color: var(--text-secondary); font-weight: 600; }

@media (max-width: 1024px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .db-controls { padding: 20px; }
  .data-table th, .data-table td { padding: 12px 14px; }
  .stats-row { grid-template-columns: repeat(2, 1fr); }
}
</style>
