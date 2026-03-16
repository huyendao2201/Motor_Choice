<template>
  <div class="db-tab page-container">
    <div class="section-title">
      <h2>🗃️ Cơ Sở Dữ Liệu Xe Máy</h2>
      <p>Tổng cộng <strong class="text-success">{{ filtered.length }}</strong> / {{ all.length }} mẫu xe · Đây là tập alternatives cho hệ DSS</p>
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
      h('div', { style: 'flex:1;height:6px;background:rgba(255,255,255,0.06);border-radius:99px;overflow:hidden' }, [
        h('div', { style: `width:${(p.value/p.max)*100}%;height:100%;background:${p.color};border-radius:99px;` })
      ]),
      h('span', { style: 'font-size:0.75rem;font-weight:700;min-width:28px' }, `${p.value}`)
    ])
  }
})
</script>

<style scoped>
.db-tab { padding: 40px 0 80px; }
.page-container { max-width: 1400px; margin: 0 auto; padding: 40px 24px; }

/* Controls */
.db-controls { padding: 16px 20px; display: flex; flex-direction: column; gap: 14px; margin-bottom: 20px; }
.search-wrap {
  position: relative; display: flex; align-items: center;
  background: rgba(255,255,255,0.04); border: var(--border); border-radius: var(--r-md);
  padding: 10px 16px; gap: 10px;
  transition: var(--transition);
}
.search-wrap:focus-within { border-color: rgba(99,102,241,0.4); background: rgba(99,102,241,0.05); }
.search-icon { font-size: 1rem; flex-shrink: 0; }
.search-input { flex: 1; background: transparent; border: none; outline: none; color: var(--text); font-family: var(--font); font-size: 0.9rem; }
.search-input::placeholder { color: var(--text-dim); }
.search-clear { background: transparent; border: none; color: var(--text-dim); cursor: pointer; font-size: 0.9rem; padding: 2px 6px; border-radius: 4px; }
.search-clear:hover { color: var(--danger); }
.filter-row { display: flex; gap: 8px; flex-wrap: wrap; }
.filter-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 14px; border-radius: 99px; border: var(--border);
  background: transparent; color: var(--text-secondary); cursor: pointer;
  font-family: var(--font); font-size: 0.78rem; font-weight: 500;
  transition: var(--transition);
}
.filter-btn:hover { background: rgba(255,255,255,0.05); color: var(--text); }
.filter-btn.active { background: var(--primary-dim); border-color: rgba(99,102,241,0.4); color: var(--primary-light); font-weight: 700; }
.filter-count { background: rgba(255,255,255,0.08); border-radius: 99px; padding: 1px 7px; font-size: 0.68rem; font-weight: 700; }

/* Stats */
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
.stat-card { padding: 16px 20px; display: flex; flex-direction: column; align-items: center; gap: 4px; text-align: center; }
.stat-card-icon { font-size: 1.4rem; }
.stat-card-num { font-size: 1.4rem; font-weight: 900; color: var(--text); }
.stat-card-label { font-size: 0.7rem; color: var(--text-dim); }

/* Loading */
.loading-wrap { display: flex; align-items: center; justify-content: center; gap: 12px; padding: 60px; color: var(--text-secondary); }

/* Table */
.table-wrap { padding: 0; overflow: hidden; }
.sortable { cursor: pointer; user-select: none; white-space: nowrap; }
.sortable:hover { color: var(--primary-light); }

.table-empty { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 50px; color: var(--text-dim); font-size: 0.85rem; }
.table-empty span:first-child { font-size: 2rem; }

/* Pagination */
.pagination { display: flex; align-items: center; justify-content: center; gap: 16px; padding: 16px; border-top: var(--border); }
.page-btn { padding: 7px 16px; border-radius: var(--r-md); background: rgba(255,255,255,0.05); border: var(--border); color: var(--text); cursor: pointer; font-family: var(--font); font-size: 0.82rem; transition: var(--transition); }
.page-btn:hover:not(:disabled) { background: var(--primary-dim); border-color: rgba(99,102,241,0.3); color: var(--primary-light); }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.page-info { font-size: 0.8rem; color: var(--text-secondary); }

@media (max-width: 900px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
}
</style>
