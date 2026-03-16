<template>
  <footer class="footer">
    <div class="footer-inner">
      <div class="footer-logo">
        <span>🏍️</span>
        <span><strong>MotorChoice DSS</strong> – Hệ Hỗ Trợ Ra Quyết Định Lựa Chọn Xe Máy</span>
      </div>
      <div class="footer-info">
        <span class="badge badge-primary">AI + AHP + Random Forest</span>
        <span class="text-dim text-xs">Môn HHTRQD – HCMUNRE · 2026</span>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  margin-top: 60px;
  border-top: 1px solid rgba(255,255,255,0.06);
  padding: 24px;
  position: relative; z-index: 1;
}
.footer-inner {
  max-width: 1400px; margin: 0 auto;
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
}
.footer-logo { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; color: var(--text-secondary); }
.footer-info { display: flex; align-items: center; gap: 12px; }
</style>
