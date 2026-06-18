/* GED Courriers – JavaScript principal */
document.addEventListener('DOMContentLoaded', function () {

  /* ── Sidebar mobile ── */
  const toggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', (e) => {
      if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== toggle)
        sidebar.classList.remove('open');
    });
  }

  /* ── Auto-dismiss alertes ── */
  document.querySelectorAll('.alert.fade.show').forEach(el => {
    setTimeout(() => { try { bootstrap.Alert.getOrCreateInstance(el).close(); } catch(e){} }, 5000);
  });

  /* ── Rows cliquables ── */
  document.querySelectorAll('.table-ged tbody tr[data-href]').forEach(row => {
    row.addEventListener('click', () => window.location.href = row.dataset.href);
  });

  /* ── Confirmation actions sensibles ── */
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', (e) => { if (!confirm(el.dataset.confirm)) e.preventDefault(); });
  });

  /* ── Toggle mot de passe ── */
  document.querySelectorAll('[data-toggle-pwd]').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = document.querySelector(btn.dataset.togglePwd);
      const icon = btn.querySelector('i');
      if (!input) return;
      const visible = input.type === 'text';
      input.type = visible ? 'password' : 'text';
      if (icon) icon.className = visible ? 'bi bi-eye' : 'bi bi-eye-slash';
    });
  });

  /* ── Calcul auto date échéance ── */
  const prio = document.querySelector('[name="priorite"]');
  const dateR = document.querySelector('[name="date_reception"]');
  const dateE = document.querySelector('[name="date_echeance"]');
  const delais = window.GED_PRIORITES_DELAIS || {};
  if (prio && dateR && dateE) {
    function calcEch() {
      if (dateE.value) return;
      const d = parseInt(delais[prio.value] || 0);
      if (d && dateR.value) {
        const dt = new Date(dateR.value);
        dt.setDate(dt.getDate() + d);
        dateE.value = dt.toISOString().split('T')[0];
      }
    }
    prio.addEventListener('change', calcEch);
    dateR.addEventListener('change', calcEch);
  }

  /* ── Stepper (désactivé - formulaire unique) ── */
  // const panes = document.querySelectorAll('.step-pane');
  // const dots  = document.querySelectorAll('.step-dot');

  /* ── Récap enregistrement (désactivé) ── */
  // function updateRecap() {}

  /* ── Tooltips Bootstrap ── */
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => new bootstrap.Tooltip(el));

  /* ── Bulk dispatch ── */
  const selectAll = document.getElementById('select-all');
  const checkboxes = document.querySelectorAll('.courrier-checkbox');
  const bulkBtn = document.getElementById('bulk-dispatch-btn');
  const selectedCount = document.getElementById('selected-count');
  if (selectAll && bulkBtn) {
    function updateBulkBtn() {
      const checked = document.querySelectorAll('.courrier-checkbox:checked:not(:disabled)');
      const count = checked.length;
      selectedCount.textContent = count;
      bulkBtn.disabled = count === 0;
    }
    selectAll.addEventListener('change', () => {
      checkboxes.forEach(cb => { if (!cb.disabled) cb.checked = selectAll.checked; });
      updateBulkBtn();
    });
    checkboxes.forEach(cb => cb.addEventListener('change', updateBulkBtn));
    bulkBtn.addEventListener('click', () => {
      const selected = Array.from(document.querySelectorAll('.courrier-checkbox:checked')).map(cb => cb.value);
      if (selected.length) {
        // Open bulk dispatch modal or redirect
        window.location.href = `/courriers/bulk-dispatch/?ids=${selected.join(',')}`;
      }
    });
  }

  /* ── Preview avatar ── */
  const av = document.getElementById('id_avatar');
  const ap = document.getElementById('avatar-preview');
  if (av && ap) {
    av.addEventListener('change', function () {
      const f = this.files[0];
      if (f) { const r = new FileReader(); r.onload = e => ap.src = e.target.result; r.readAsDataURL(f); }
    });
  }
});
