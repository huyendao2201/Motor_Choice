/* =========================================
   MOTOR CHOICE DSS – Frontend JavaScript
   v2.0: Radar Chart + Compare + Sensitivity
========================================= */

const API = 'http://localhost:8000';

// ============================================================
// GLOBAL STATE
// ============================================================
let allMotorcycles = [];
let currentTab = 'recommend';
let lastResult = null;        // Store last API result for sensitivity
let lastFilteredBikes = [];   // All filtered bikes for sensitivity re-rank
let selectedForCompare = [];  // Bike indices selected for comparison
let radarChartInstance = null;
let currentAhpWeights = {};   // Current AI-predicted weights
let sensWeights = {};         // Sensitivity weights (copy of AI weights, editable)

// ============================================================
// INIT
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    setupNav();
    setupForm();
    setupRanges();
    setupRadioCards();
    buildAHPMatrix();
    loadHealth();
    loadMotorcycles();
    // Close modal on overlay click
    document.getElementById('compareModal').addEventListener('click', e => {
        if (e.target === e.currentTarget) closeCompareModal();
    });
});

// ============================================================
// NAVIGATION
// ============================================================
function setupNav() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            const tab = link.dataset.tab;
            if (!tab) return;
            switchTab(tab);
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
}

function switchTab(tab) {
    currentTab = tab;
    document.querySelectorAll('.tab-section').forEach(s => s.classList.remove('active'));
    const el = document.getElementById(`tab-${tab}`);
    if (el) el.classList.add('active');
    if (tab === 'database') renderDatabase(allMotorcycles);
}

// ============================================================
// FORM SETUP
// ============================================================
function setupForm() {
    document.getElementById('profileForm').addEventListener('submit', async e => {
        e.preventDefault();
        await submitForm();
    });
    document.getElementById('dbSearch').addEventListener('input', filterDatabase);
    document.getElementById('dbTypeFilter').addEventListener('change', filterDatabase);
}

function setupRanges() {
    const budget = document.getElementById('budget');
    const budgetVal = document.getElementById('budgetVal');
    budget.addEventListener('input', () => { budgetVal.textContent = `${budget.value}M`; });

    const km = document.getElementById('daily_distance_km');
    const kmVal = document.getElementById('kmVal');
    km.addEventListener('input', () => { kmVal.textContent = `${km.value}km`; });

    const priorities = [
        ['priority_price', 'p_price_val'],
        ['priority_fuel', 'p_fuel_val'],
        ['priority_performance', 'p_perf_val'],
        ['priority_design', 'p_design_val'],
        ['priority_brand', 'p_brand_val'],
    ];
    priorities.forEach(([id, valId]) => {
        const el = document.getElementById(id);
        const valEl = document.getElementById(valId);
        el.addEventListener('input', () => { valEl.textContent = `${el.value}%`; });
    });
}

function setupRadioCards() {
    document.querySelectorAll('.radio-group').forEach(group => {
        group.querySelectorAll('.radio-card').forEach(card => {
            card.addEventListener('click', () => {
                group.querySelectorAll('.radio-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');
            });
        });
    });
}

// ============================================================
// SUBMIT FORM → API
// ============================================================
async function submitForm() {
    const btn = document.getElementById('submitBtn');
    btn.disabled = true;
    btn.querySelector('.btn-text').textContent = '⏳ Đang phân tích...';

    try {
        const payload = buildPayload();
        const resp = await fetch(`${API}/api/recommend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || 'API error');
        }
        const data = await resp.json();
        lastResult = data;

        // Reset compare state
        selectedForCompare = [];
        renderResults(data);

        document.getElementById('form-section').classList.add('hidden');
        document.getElementById('resultsSection').classList.remove('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });

    } catch (err) {
        alert('❌ Lỗi: ' + err.message + '\n\nHãy đảm bảo backend đang chạy tại http://localhost:8000');
    } finally {
        btn.disabled = false;
        btn.querySelector('.btn-text').textContent = '🔍 Tìm xe phù hợp';
    }
}

function buildPayload() {
    const form = document.getElementById('profileForm');
    const purpose = +form.querySelector('input[name="purpose"]:checked').value;
    const vtype = +form.querySelector('input[name="vehicle_type_preference"]:checked').value;

    return {
        budget: +document.getElementById('budget').value,
        purpose: purpose,
        vehicle_type_preference: vtype,
        daily_distance_km: +document.getElementById('daily_distance_km').value,
        priority_price: +document.getElementById('priority_price').value / 100,
        priority_fuel: +document.getElementById('priority_fuel').value / 100,
        priority_performance: +document.getElementById('priority_performance').value / 100,
        priority_design: +document.getElementById('priority_design').value / 100,
        priority_brand: +document.getElementById('priority_brand').value / 100,
        top_n: 6
    };
}

// ============================================================
// RENDER RESULTS (Main)
// ============================================================
function renderResults(data) {
    // Meta
    const meta = data.user_profile_summary;
    document.getElementById('resultMeta').innerHTML =
        `<strong>${meta.purpose_label}</strong> · Ngân sách: <strong>${meta.budget}M VNĐ</strong> · ` +
        `Xe: <strong>${meta.vehicle_type_label}</strong> · ` +
        `Tìm thấy <strong>${data.total_filtered}</strong> xe phù hợp`;

    // AHP weights
    currentAhpWeights = { ...data.ahp_weights };
    sensWeights = { ...data.ahp_weights };
    renderWeightBars(data.ahp_weights);

    // Warning
    const warnEl = document.getElementById('resultWarning');
    if (data.warning) {
        warnEl.textContent = '⚠️ ' + data.warning;
        warnEl.classList.remove('hidden');
    } else {
        warnEl.classList.add('hidden');
    }

    // Explanation
    document.getElementById('explanationCard').innerHTML =
        `💡 <strong>Phân tích:</strong> ${data.explanation}`;

    // === 1. RADAR CHART ===
    renderRadarChart(data.top_motorcycles, data.ahp_weights);

    // === 2. BIKE CARDS (with compare checkbox) ===
    renderBikeCards(data.top_motorcycles, data.ahp_weights);

    // === 3. SENSITIVITY ANALYSIS ===
    // Store filtered bikes (need all of them for re-ranking)
    lastFilteredBikes = buildSensitivityBikeData(data.top_motorcycles);
    initSensitivity(data.ahp_weights, data.top_motorcycles);

    // Animate bars
    requestAnimationFrame(() => {
        document.querySelectorAll('.bike-score-fill, .weight-bar-fill').forEach(el => {
            el.style.width = (el.dataset.width || '0') + '%';
        });
    });
}

function renderWeightBars(weights) {
    const labels = {
        w_price: '💰 Giá thành', w_fuel: '⛽ Xăng', w_performance: '⚡ Hiệu năng',
        w_design: '🎨 Thiết kế', w_brand: '🏅 Thương hiệu'
    };
    const container = document.getElementById('weightBars');
    container.innerHTML = Object.entries(weights).map(([k, v]) => {
        const pct = (v * 100).toFixed(1);
        return `<div class="weight-bar-item">
          <span class="weight-bar-label">${labels[k] || k}</span>
          <div class="weight-bar-track"><div class="weight-bar-fill" style="width:0%" data-width="${pct}"></div></div>
          <span class="weight-bar-pct">${pct}%</span>
        </div>`;
    }).join('');
    setTimeout(() => {
        document.querySelectorAll('.weight-bar-fill').forEach(el => { el.style.width = el.dataset.width + '%'; });
    }, 50);
}

// ============================================================
// 1. RADAR CHART (Chart.js)
// ============================================================
function renderRadarChart(bikes, weights) {
    const top3 = bikes.slice(0, 3);
    if (!top3.length) return;

    const labels = ['💰 Giá', '⛽ Xăng', '⚡ Hiệu năng', '🎨 Thiết kế', '🏅 Thương hiệu'];
    const colors = [
        { bg: 'rgba(245,158,11,0.15)', border: 'rgba(245,158,11,0.9)' },
        { bg: 'rgba(148,163,184,0.1)', border: 'rgba(148,163,184,0.8)' },
        { bg: 'rgba(99,102,241,0.1)', border: 'rgba(99,102,241,0.8)' },
    ];

    const datasets = top3.map((bike, i) => {
        const norms = [
            bike.scores?.price_norm ?? 0,
            bike.scores?.fuel_norm ?? 0,
            bike.scores?.performance_norm ?? 0,
            bike.scores?.design_norm ?? 0,
            bike.scores?.brand_norm ?? 0,
        ];
        return {
            label: `${bike.brand} ${bike.model}`,
            data: norms.map(n => +(n * 100).toFixed(1)),
            backgroundColor: colors[i].bg,
            borderColor: colors[i].border,
            borderWidth: 2,
            pointBackgroundColor: colors[i].border,
            pointRadius: 4,
            pointHoverRadius: 6,
        };
    });

    const ctx = document.getElementById('radarChart').getContext('2d');
    if (radarChartInstance) radarChartInstance.destroy();

    radarChartInstance = new Chart(ctx, {
        type: 'radar',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            animation: { duration: 800, easing: 'easeInOutQuart' },
            scales: {
                r: {
                    min: 0, max: 100,
                    ticks: {
                        stepSize: 20,
                        color: 'rgba(148,163,184,0.7)',
                        font: { size: 9 },
                        backdropColor: 'transparent',
                        callback: val => val + '%'
                    },
                    grid: { color: 'rgba(255,255,255,0.07)' },
                    angleLines: { color: 'rgba(255,255,255,0.1)' },
                    pointLabels: {
                        color: '#e2e8f0',
                        font: { size: 12, weight: '700' }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e2e8f0',
                        font: { size: 11, weight: '600' },
                        padding: 16,
                        usePointStyle: true,
                        pointStyleWidth: 10
                    }
                },
                tooltip: {
                    callbacks: {
                        label: ctx => ` ${ctx.dataset.label}: ${ctx.raw}%`
                    }
                }
            }
        }
    });
}

// ============================================================
// 2. BIKE CARDS (with compare checkbox)
// ============================================================
function renderBikeCards(bikes, weights) {
    const grid = document.getElementById('resultsGrid');
    grid.innerHTML = bikes.map((bike, idx) => buildBikeCard(bike, weights, idx)).join('');

    // Score bar animation
    requestAnimationFrame(() => {
        document.querySelectorAll('.bike-score-fill').forEach(el => {
            el.style.width = el.dataset.width + '%';
        });
    });

    updateCompareBar();
}

function buildBikeCard(bike, weights, idx) {
    const rankClass = bike.rank === 1 ? 'rank-1' : bike.rank === 2 ? 'rank-2' : bike.rank === 3 ? 'rank-3' : '';
    const badgeClass = bike.rank === 1 ? 'gold' : bike.rank === 2 ? 'silver' : bike.rank === 3 ? 'bronze' : '';
    const rankIcon = bike.rank === 1 ? '🥇' : bike.rank === 2 ? '🥈' : bike.rank === 3 ? '🥉' : `#${bike.rank}`;
    const scoreWidth = (bike.total_score * 100).toFixed(1);
    const typeClass = bike.vehicle_type === 'Xe số' ? 'type-xe-so' :
        bike.vehicle_type === 'Xe tay ga' ? 'type-tay-ga' : 'type-con-tay';

    return `<div class="bike-card ${rankClass}" id="bikeCard-${idx}" onclick="toggleCompare(${idx})">
      <div class="bike-compare-check" id="check-${idx}">✓</div>
      <div class="bike-rank-badge ${badgeClass}">${rankIcon}</div>
      <span class="bike-brand-tag">${bike.brand}</span>
      <div class="bike-model">${bike.model}</div>
      <div class="bike-type">
        <span class="type-badge ${typeClass}">${bike.vehicle_type}</span> · ${bike.engine_cc}cc
      </div>
      <div class="bike-specs">
        <div class="bike-spec"><span class="bike-spec-label">💰 Giá</span><span class="bike-spec-val" style="color:#f59e0b">${bike.price_million_vnd.toFixed(1)}M</span></div>
        <div class="bike-spec"><span class="bike-spec-label">⛽ Xăng</span><span class="bike-spec-val">${bike.fuel_consumption_l_per_100km}L/100</span></div>
        <div class="bike-spec"><span class="bike-spec-label">⚡ Hiệu năng</span><span class="bike-spec-val">${bike.performance_score}/10</span></div>
        <div class="bike-spec"><span class="bike-spec-label">🏅 Thương hiệu</span><span class="bike-spec-val">${bike.brand_score}/10</span></div>
      </div>
      <div class="bike-score-bar">
        <div class="bike-score-label">
          <span>Điểm DSS tổng</span>
          <span style="color:#10b981;font-weight:800">${bike.total_score}</span>
        </div>
        <div class="bike-score-track">
          <div class="bike-score-fill" style="width:0%" data-width="${scoreWidth}"></div>
        </div>
      </div>
    </div>`;
}

// ============================================================
// 2b. COMPARE FEATURE
// ============================================================
function toggleCompare(idx) {
    const card = document.getElementById(`bikeCard-${idx}`);
    if (selectedForCompare.includes(idx)) {
        selectedForCompare = selectedForCompare.filter(i => i !== idx);
        card.classList.remove('selected');
    } else {
        if (selectedForCompare.length >= 3) {
            // Remove oldest
            const old = selectedForCompare.shift();
            document.getElementById(`bikeCard-${old}`)?.classList.remove('selected');
        }
        selectedForCompare.push(idx);
        card.classList.add('selected');
    }
    updateCompareBar();
}

function updateCompareBar() {
    const bar = document.getElementById('compareBar');
    const count = selectedForCompare.length;
    document.getElementById('compareCount').textContent = count > 0
        ? `${count} xe đã chọn`
        : 'Bấm vào thẻ xe để chọn so sánh';

    const btn = document.getElementById('btnCompare');
    if (count >= 2) {
        bar.classList.add('has-selection');
        btn.classList.add('enabled');
    } else {
        bar.classList.remove('has-selection');
        btn.classList.remove('enabled');
    }
}

function clearCompare() {
    selectedForCompare.forEach(idx => {
        document.getElementById(`bikeCard-${idx}`)?.classList.remove('selected');
    });
    selectedForCompare = [];
    updateCompareBar();
}

function openCompareModal() {
    if (selectedForCompare.length < 2 || !lastResult) return;
    const bikes = selectedForCompare.map(i => lastResult.top_motorcycles[i]);
    const weights = lastResult.ahp_weights;
    renderCompareModal(bikes, weights);
    document.getElementById('compareModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeCompareModal() {
    document.getElementById('compareModal').classList.add('hidden');
    document.body.style.overflow = '';
}

function renderCompareModal(bikes, weights) {
    const CRITERIA = [
        { key: 'price_million_vnd', label: '💰 Giá (triệu VNĐ)', type: 'cost', norm_key: 'price_norm', w: weights.w_price },
        { key: 'fuel_consumption_l_per_100km', label: '⛽ Xăng (L/100km)', type: 'cost', norm_key: 'fuel_norm', w: weights.w_fuel },
        { key: 'performance_score', label: '⚡ Hiệu năng (/10)', type: 'benefit', norm_key: 'performance_norm', w: weights.w_performance },
        { key: 'design_score', label: '🎨 Thiết kế (/10)', type: 'benefit', norm_key: 'design_norm', w: weights.w_design },
        { key: 'brand_score', label: '🏅 Thương hiệu (/10)', type: 'benefit', norm_key: 'brand_norm', w: weights.w_brand },
    ];

    const RANK_COLORS = [
        { bg: 'rgba(245,158,11,0.15)', text: '#f59e0b', label: '🥇' },
        { bg: 'rgba(148,163,184,0.1)', text: '#94a3b8', label: '🥈' },
        { bg: 'rgba(217,119,6,0.1)', text: '#d97706', label: '🥉' },
    ];

    // Build table header
    let html = `<div style="overflow-x:auto"><table class="compare-table">
    <thead><tr>
      <th>Tiêu chí / AHP</th>
      ${bikes.map((b, i) => `<th style="background:${RANK_COLORS[i].bg}">
        <span style="color:${RANK_COLORS[i].text};font-size:1.2rem">${RANK_COLORS[i].label}</span><br/>
        <strong>${b.brand}</strong><br/>${b.model}
      </th>`).join('')}
    </tr></thead><tbody>`;

    // Rank row
    html += `<tr><td>🏆 Hạng DSS</td>
      ${bikes.map(b => `<td><strong style="font-size:1.1rem;color:#10b981">#${b.rank}</strong></td>`).join('')}
    </tr>`;

    // Score row
    html += `<tr><td>📊 Điểm tổng</td>
      ${bikes.map(b => {
        const isBest = b.total_score === Math.max(...bikes.map(x => x.total_score));
        return `<td class="${isBest ? 'compare-best' : ''}">${b.total_score}</td>`;
    }).join('')}
    </tr>`;

    // Extra info rows
    html += `<tr><td>🏢 Thương hiệu</td>${bikes.map(b => `<td>${b.brand}</td>`).join('')}</tr>`;
    html += `<tr><td>🏍️ Loại xe</td>${bikes.map(b => `<td>${b.vehicle_type}</td>`).join('')}</tr>`;
    html += `<tr><td>🔧 Dung tích</td>${bikes.map(b => `<td>${b.engine_cc}cc</td>`).join('')}</tr>`;

    // Separator
    html += `<tr><td colspan="${bikes.length + 1}" style="background:rgba(99,102,241,0.06);padding:6px 14px;font-size:0.75rem;font-weight:700;color:var(--primary-light);letter-spacing:1px">ĐIỂM CHUẨN HÓA THEO TIÊU CHÍ AHP</td></tr>`;

    // Criteria rows
    CRITERIA.forEach(c => {
        const rawVals = bikes.map(b => b[c.key]);
        const normVals = bikes.map(b => b.scores ? b.scores[c.norm_key] : 0);
        const bestNorm = Math.max(...normVals);
        const bestRaw = c.type === 'cost' ? Math.min(...rawVals) : Math.max(...rawVals);

        html += `<tr>
          <td>${c.label}<br/><span style="font-size:0.68rem;color:var(--text-dim)">Trọng số AI: ${(c.w * 100).toFixed(1)}%</span></td>
          ${bikes.map((b, i) => {
            const raw = b[c.key];
            const norm = normVals[i];
            const isBestRaw = raw === bestRaw;
            const barColor = c.type === 'cost' ? '#10b981' : '#818cf8';
            return `<td class="${isBestRaw ? 'compare-best' : ''}">
              <div class="compare-bar-cell">
                <div class="compare-mini-track">
                  <div class="compare-mini-fill" style="width:${(norm * 100).toFixed(0)}%;background:${barColor}"></div>
                </div>
                <span>${raw}${c.key.includes('vnd') ? 'M' : c.key.includes('km') ? 'L' : '/10'}</span>
              </div>
              <div style="font-size:0.68rem;color:var(--text-dim);text-align:center;margin-top:2px">norm: ${(norm).toFixed(3)}</div>
            </td>`;
        }).join('')}
        </tr>`;
    });

    html += `</tbody></table></div>`;

    // Recommendation
    const winner = bikes.reduce((a, b) => a.total_score > b.total_score ? a : b);
    html += `<div style="margin-top:20px;padding:16px 20px;background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.2);border-radius:12px;font-size:0.9rem;line-height:1.7">
      💡 <strong>Nhận xét:</strong> Qua so sánh trực tiếp, <strong style="color:#10b981">${winner.brand} ${winner.model}</strong>
      đạt điểm DSS cao nhất (<strong>${winner.total_score}</strong>) và là lựa chọn tốt nhất dựa trên trọng số AHP được AI dự đoán.
    </div>`;

    document.getElementById('compareModalBody').innerHTML = html;
}

// ============================================================
// 3. SENSITIVITY ANALYSIS
// ============================================================
function buildSensitivityBikeData(bikes) {
    // Return copy with all raw data for client-side DSS re-ranking
    return bikes.map(b => ({ ...b }));
}

function initSensitivity(weights, bikes) {
    sensWeights = { ...weights };
    lastFilteredBikes = bikes.map(b => ({ ...b }));

    const SENS_ITEMS = [
        { key: 'w_price', label: '💰 Giá thành', criteriaKey: 'price_million_vnd', type: 'cost' },
        { key: 'w_fuel', label: '⛽ Xăng', criteriaKey: 'fuel_consumption_l_per_100km', type: 'cost' },
        { key: 'w_performance', label: '⚡ Hiệu năng', criteriaKey: 'performance_score', type: 'benefit' },
        { key: 'w_design', label: '🎨 Thiết kế', criteriaKey: 'design_score', type: 'benefit' },
        { key: 'w_brand', label: '🏅 Thương hiệu', criteriaKey: 'brand_score', type: 'benefit' },
    ];

    const container = document.getElementById('sensWeights');
    container.innerHTML = SENS_ITEMS.map(item => {
        const pct = Math.round(weights[item.key] * 100);
        return `<div class="sens-weight-item">
          <div class="sens-weight-header">
            <span>${item.label}</span>
            <span class="sens-weight-val" id="sv-${item.key}">${pct}%</span>
          </div>
          <input type="range" class="sens-weight-range" id="sr-${item.key}"
            min="0" max="100" value="${pct}" step="1"
            oninput="onSensInput('${item.key}', this.value)" />
        </div>`;
    }).join('');

    updateSensitivityTotal();
    updateSensRanking();
}

function onSensInput(key, val) {
    sensWeights[key] = +val / 100;
    document.getElementById(`sv-${key}`).textContent = `${val}%`;
    updateSensitivityTotal();
    updateSensRanking();
}

function updateSensitivityTotal() {
    const total = Object.values(sensWeights).reduce((a, b) => a + b, 0);
    const pct = (total * 100).toFixed(1);
    const el = document.getElementById('sensTotal');
    el.textContent = `${pct}%`;
    el.parentElement.querySelector('strong')?.remove();

    if (Math.abs(total - 1) > 0.15) {
        el.style.color = 'var(--danger)';
    } else {
        el.style.color = 'var(--accent2)';
    }
}

function updateSensRanking() {
    if (!lastFilteredBikes.length) return;

    // Normalize weights to sum = 1
    const rawSum = Object.values(sensWeights).reduce((a, b) => a + b, 0);
    const normW = rawSum > 0 ? {
        w_price: sensWeights.w_price / rawSum,
        w_fuel: sensWeights.w_fuel / rawSum,
        w_performance: sensWeights.w_performance / rawSum,
        w_design: sensWeights.w_design / rawSum,
        w_brand: sensWeights.w_brand / rawSum,
    } : sensWeights;

    // Re-rank using client-side DSS
    const ranked = clientDSSRank(lastFilteredBikes, normW);
    renderSensRanking(ranked.slice(0, 6));
}

function clientDSSRank(bikes, weights) {
    // Get ranges from bikes array
    const fields = ['price_million_vnd', 'fuel_consumption_l_per_100km', 'performance_score', 'design_score', 'brand_score'];
    const types = { price_million_vnd: 'cost', fuel_consumption_l_per_100km: 'cost', performance_score: 'benefit', design_score: 'benefit', brand_score: 'benefit' };
    const wMap = { price_million_vnd: weights.w_price, fuel_consumption_l_per_100km: weights.w_fuel, performance_score: weights.w_performance, design_score: weights.w_design, brand_score: weights.w_brand };

    // Compute ranges over all bikes
    const ranges = {};
    fields.forEach(f => {
        const vals = bikes.map(b => b[f]);
        ranges[f] = { min: Math.min(...vals), max: Math.max(...vals) };
    });

    // Normalize & score
    const scored = bikes.map(b => {
        let score = 0;
        fields.forEach(f => {
            const { min, max } = ranges[f];
            const norm = max === min ? 1 : (types[f] === 'cost' ? (max - b[f]) / (max - min) : (b[f] - min) / (max - min));
            score += wMap[f] * norm;
        });
        return { ...b, sens_score: +score.toFixed(4) };
    });

    return scored.sort((a, b) => b.sens_score - a.sens_score);
}

let prevSensRanking = [];
function renderSensRanking(bikes) {
    const container = document.getElementById('sensRanking');
    const maxScore = bikes[0]?.sens_score || 1;

    container.innerHTML = bikes.map((bike, i) => {
        const prevIdx = prevSensRanking.findIndex(b => b.brand === bike.brand && b.model === bike.model);
        const changed = prevIdx !== -1 && prevIdx !== i;
        const isTop1 = i === 0;
        const barW = ((bike.sens_score / maxScore) * 100).toFixed(1);

        let changeIndicator = '';
        if (prevIdx !== -1 && prevIdx !== i) {
            const delta = prevIdx - i;
            changeIndicator = delta > 0
                ? `<span style="color:#10b981;font-size:0.7rem;font-weight:700">▲${delta}</span>`
                : `<span style="color:#ef4444;font-size:0.7rem;font-weight:700">▼${Math.abs(delta)}</span>`;
        }

        return `<div class="sens-rank-row ${isTop1 ? 'top1' : ''} ${changed ? 'changed' : ''}">
          <div class="sens-rank-num ${isTop1 ? 'gold' : ''}">${isTop1 ? '🥇' : i + 1}</div>
          <div style="flex:1;min-width:0">
            <div class="sens-rank-name">${bike.model}</div>
            <div class="sens-rank-brand">${bike.brand} · ${bike.vehicle_type}</div>
          </div>
          ${changeIndicator}
          <div class="sens-rank-score-wrap">
            <span class="sens-rank-score">${bike.sens_score}</span>
            <div class="sens-rank-bar">
              <div class="sens-rank-bar-fill" style="width:${barW}%"></div>
            </div>
          </div>
        </div>`;
    }).join('');

    prevSensRanking = [...bikes];
}

function resetSensitivity() {
    if (!currentAhpWeights) return;
    sensWeights = { ...currentAhpWeights };
    Object.entries(sensWeights).forEach(([k, v]) => {
        const slider = document.getElementById(`sr-${k}`);
        const val = document.getElementById(`sv-${k}`);
        if (slider) { slider.value = Math.round(v * 100); }
        if (val) val.textContent = `${Math.round(v * 100)}%`;
    });
    updateSensitivityTotal();
    updateSensRanking();
}

function resetForm() {
    document.getElementById('form-section').classList.remove('hidden');
    document.getElementById('resultsSection').classList.add('hidden');
    selectedForCompare = [];
    prevSensRanking = [];
    if (radarChartInstance) { radarChartInstance.destroy(); radarChartInstance = null; }
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ============================================================
// DEMO PROFILES
// ============================================================
function loadDemo(type) {
    if (type === 0) {
        setRadio('purpose', '0'); setRadio('vehicle_type_preference', '0');
        setRange('budget', 25); setRange('daily_distance_km', 15);
        setRange('priority_price', 70); setRange('priority_fuel', 60);
        setRange('priority_performance', 30); setRange('priority_design', 20); setRange('priority_brand', 20);
    } else {
        setRadio('purpose', '1'); setRadio('vehicle_type_preference', '1');
        setRange('budget', 70); setRange('daily_distance_km', 20);
        setRange('priority_price', 20); setRange('priority_fuel', 20);
        setRange('priority_performance', 40); setRange('priority_design', 70); setRange('priority_brand', 60);
    }
}

function setRange(id, val) {
    const el = document.getElementById(id);
    if (!el) return;
    el.value = val;
    el.dispatchEvent(new Event('input'));
}

function setRadio(name, value) {
    document.querySelectorAll(`input[name="${name}"]`).forEach(inp => {
        if (inp.value === value) {
            inp.checked = true;
            const card = inp.closest('.radio-card');
            const group = card.closest('.radio-group');
            group.querySelectorAll('.radio-card').forEach(c => c.classList.remove('active'));
            card.classList.add('active');
        }
    });
}

// ============================================================
// DATABASE TAB
// ============================================================
async function loadMotorcycles() {
    try {
        const resp = await fetch(`${API}/api/motorcycles`);
        const data = await resp.json();
        allMotorcycles = data.motorcycles;
        document.getElementById('stat-bikes').textContent = data.total;
        document.getElementById('dbTotal').textContent = data.total;
    } catch (e) { console.warn('Cannot load motorcycles:', e.message); }
}

function renderDatabase(bikes) {
    const tbody = document.getElementById('dbTableBody');
    tbody.innerHTML = bikes.map((b, i) => {
        const tc = b.vehicle_type === 'Xe số' ? 'type-xe-so' : b.vehicle_type === 'Xe tay ga' ? 'type-tay-ga' : 'type-con-tay';
        return `<tr>
          <td>${i + 1}</td><td><strong>${b.brand}</strong></td><td>${b.model}</td>
          <td><span class="type-badge ${tc}">${b.vehicle_type}</span></td>
          <td>${b.engine_cc}</td>
          <td><strong style="color:#f59e0b">${b.price_million_vnd}M</strong></td>
          <td>${b.fuel_consumption_l_per_100km}</td>
          <td>${b.performance_score}/10</td><td>${b.design_score}/10</td><td>${b.brand_score}/10</td>
        </tr>`;
    }).join('');
}

function filterDatabase() {
    const search = document.getElementById('dbSearch').value.toLowerCase();
    const typeFilter = document.getElementById('dbTypeFilter').value;
    const filtered = allMotorcycles.filter(b => {
        const ms = !search || b.brand.toLowerCase().includes(search) || b.model.toLowerCase().includes(search);
        const mt = !typeFilter || b.vehicle_type === typeFilter;
        return ms && mt;
    });
    renderDatabase(filtered);
}

// ============================================================
// AHP CALCULATOR
// ============================================================
const AHP_CRITERIA = ['Giá', 'Xăng', 'Hiệu năng', 'Thiết kế', 'Thương hiệu'];
const N = 5;
let ahpMatrix = [];

function buildAHPMatrix() {
    ahpMatrix = Array.from({ length: N }, (_, i) =>
        Array.from({ length: N }, (_, j) => (i === j ? 1 : i < j ? 3 : null))
    );
    for (let i = 0; i < N; i++)
        for (let j = 0; j < i; j++)
            ahpMatrix[i][j] = 1 / ahpMatrix[j][i];
    renderAHPMatrix();
}

function renderAHPMatrix() {
    const container = document.getElementById('ahpMatrix');
    let html = `<div class="matrix-grid" style="grid-template-columns: 80px repeat(${N}, 1fr); gap:4px;">`;
    html += '<div></div>';
    AHP_CRITERIA.forEach(c => { html += `<div class="matrix-cell-header" style="font-size:0.65rem">${c}</div>`; });
    for (let i = 0; i < N; i++) {
        html += `<div class="matrix-cell-header" style="font-size:0.65rem">${AHP_CRITERIA[i]}</div>`;
        for (let j = 0; j < N; j++) {
            if (i === j) {
                html += `<input class="matrix-input diagonal" value="1" readonly />`;
            } else if (i < j) {
                html += `<input class="matrix-input" type="number" min="0.111" max="9" step="0.5"
                  data-i="${i}" data-j="${j}" value="${ahpMatrix[i][j]}" onchange="updateMatrix(this)" />`;
            } else {
                html += `<input class="matrix-input" value="${(1 / ahpMatrix[j][i]).toFixed(3)}" readonly style="opacity:0.5" id="cell-${i}-${j}" />`;
            }
        }
    }
    html += '</div>';
    container.innerHTML = html;
}

function updateMatrix(input) {
    const i = +input.dataset.i, j = +input.dataset.j;
    const v = parseFloat(input.value);
    if (isNaN(v) || v <= 0) return;
    ahpMatrix[i][j] = v; ahpMatrix[j][i] = 1 / v;
    const rc = document.getElementById(`cell-${j}-${i}`);
    if (rc) rc.value = (1 / v).toFixed(3);
}

function resetAHPMatrix() {
    buildAHPMatrix();
    document.getElementById('ahpResult').classList.add('hidden');
}

async function calculateAHP() {
    try {
        const resp = await fetch(`${API}/api/ahp/calculate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ matrix: ahpMatrix.map(row => [...row]) })
        });
        const data = await resp.json();
        renderAHPResult(data);
    } catch (e) { alert('Lỗi kết nối API: ' + e.message); }
}

function renderAHPResult(data) {
    const el = document.getElementById('ahpResult');
    const isOk = data.is_consistent;
    el.className = `ahp-result ${isOk ? '' : 'warning'}`;
    el.classList.remove('hidden');
    const wHtml = Object.entries(data.weights_named).map(([name, w]) => `
      <div style="display:flex;align-items:center;gap:10px;margin:6px 0">
        <span style="min-width:100px;font-size:0.8rem;font-weight:600;color:var(--text-muted)">${name}</span>
        <div style="flex:1;height:8px;background:var(--border);border-radius:4px;overflow:hidden">
          <div style="width:${(w * 100).toFixed(1)}%;height:100%;background:linear-gradient(90deg,var(--primary),var(--primary-light));border-radius:4px"></div>
        </div>
        <span style="min-width:48px;text-align:right;font-size:0.8rem;font-weight:700;color:var(--primary-light)">${(w * 100).toFixed(1)}%</span>
      </div>`).join('');
    el.innerHTML = `<h4 style="margin-bottom:12px">📊 Kết Quả AHP</h4>${wHtml}
      <div style="margin-top:16px;padding-top:12px;border-top:1px solid var(--border);display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;font-size:0.8rem">
        <div><span style="color:var(--text-muted)">λ_max: </span><strong>${data.lambda_max}</strong></div>
        <div><span style="color:var(--text-muted)">CI: </span><strong>${data.CI}</strong></div>
        <div><span style="color:var(--text-muted)">CR: </span><strong style="color:${isOk ? '#10b981' : '#ef4444'}">${data.CR}</strong></div>
      </div>
      <div style="margin-top:12px;font-size:0.85rem;font-weight:600;color:${isOk ? '#10b981' : '#f59e0b'}">${data.message}</div>`;
}

// ============================================================
// HEALTH CHECK (About tab)
// ============================================================
async function loadHealth() {
    try {
        const resp = await fetch(`${API}/api/health`);
        const data = await resp.json();
        const metrics = data.eval_metrics || {};
        document.getElementById('m-status').textContent = data.model_trained ? '✅ Đã train' : '❌ Chưa train';
        document.getElementById('m-mae').textContent = metrics.mae ? metrics.mae.toFixed(4) : '--';
        document.getElementById('m-rmse').textContent = metrics.rmse ? metrics.rmse.toFixed(4) : '--';
        document.getElementById('m-bikes').textContent = data.motorcycles_loaded || '--';
    } catch (e) {
        document.getElementById('m-status').textContent = '⚠️ Offline';
    }
}
