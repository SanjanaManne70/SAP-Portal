/* BHEL SAP Portal — main.js */

// ── Sidebar toggle (mobile) ───────────────────────
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('sidebarOverlay').classList.toggle('show');
}

// ── T-Code popup ──────────────────────────────────
function openTcode() {
  document.getElementById('tcodeModal').classList.remove('d-none');
  document.getElementById('tcodeInput').focus();
}
function closeTcode() {
  document.getElementById('tcodeModal').classList.add('d-none');
  document.getElementById('tcodeResults').innerHTML = '';
}
function searchTcode() {
  const q = document.getElementById('tcodeInput').value.trim();
  if (!q) return;
  fetch(`/knowledge/tcodes/search/?q=${encodeURIComponent(q)}`)
    .then(r => r.json())
    .then(data => {
      const box = document.getElementById('tcodeResults');
      if (!data.results.length) {
        box.innerHTML = '<p class="text-muted small mb-0">No T-Codes found.</p>';
        return;
      }
      box.innerHTML = data.results.map(t => `
        <div class="d-flex align-items-center gap-2 mb-2">
          <span class="tcode-tag">${t.t_code}</span>
          <span class="small">${t.description}</span>
          <span class="mod-tag ms-auto">${t.module}</span>
          ${t.process_slug ? `<a href="/knowledge/processes/${t.process_slug}/" class="btn-outline-primary-sm py-0 px-2" style="font-size:0.75rem;">View</a>` : ''}
        </div>`).join('');
    });
}
document.getElementById('tcodeInput')?.addEventListener('keydown', e => {
  if (e.key === 'Enter') searchTcode();
});

// Close popup on outside click
document.addEventListener('click', e => {
  const modal = document.getElementById('tcodeModal');
  const fab = document.querySelector('.tcode-fab');
  if (modal && !modal.classList.contains('d-none')
      && !modal.contains(e.target) && fab && !fab.contains(e.target)) {
    closeTcode();
  }
});

// ── Auto-dismiss alerts ───────────────────────────
document.querySelectorAll('.alert').forEach(a => {
  setTimeout(() => { try { bootstrap.Alert.getOrCreateInstance(a).close(); } catch(e){} }, 4000);
});