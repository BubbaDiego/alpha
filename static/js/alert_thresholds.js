window.addEventListener('DOMContentLoaded', () => {
  const saveBtn = document.getElementById('saveAllThresholds');
  const importBtn = document.getElementById('importThresholds');
  const exportBtn = document.getElementById('exportThresholds');

  function gatherPayload() {
    const rows = document.querySelectorAll('tr[data-id]');
    return Array.from(rows).map(row => ({
      id: row.dataset.id,
      low: parseFloat(row.querySelector('[name="low"]').value) || 0,
      medium: parseFloat(row.querySelector('[name="medium"]').value) || 0,
      high: parseFloat(row.querySelector('[name="high"]').value) || 0,
      enabled: row.querySelector('[name="enabled"]').checked,
      low_notify: Array.from(row.querySelectorAll('[name="low_notify"]:checked')).map(el => el.value),
      medium_notify: Array.from(row.querySelectorAll('[name="medium_notify"]:checked')).map(el => el.value),
      high_notify: Array.from(row.querySelectorAll('[name="high_notify"]:checked')).map(el => el.value)
    }));
  }

  if (saveBtn) saveBtn.addEventListener('click', async evt => {
    evt.preventDefault();
    const payload = gatherPayload();

    try {
      const resp = await fetch('/system/alert_thresholds/update_all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      if (resp.ok && data.success) {
        if (typeof showToast === 'function') {
          showToast('✅ Alert thresholds updated');
        }
      } else {
        const msg = data.error || resp.statusText;
        if (typeof showToast === 'function') {
          showToast(`❌ Failed to save thresholds: ${msg}`, true);
        }
      }
    } catch (err) {
      if (typeof showToast === 'function') {
        showToast('❌ Error saving thresholds', true);
      }
    }
  });

  if (exportBtn) exportBtn.addEventListener('click', async evt => {
    evt.preventDefault();
    try {
      const resp = await fetch('/system/alert_thresholds/export');
      const data = await resp.json();
      if (resp.ok && Array.isArray(data)) {
        if (typeof showToast === 'function') {
          showToast('✅ Exported alert_thresholds.json');
        }
      } else {
        const msg = data.error || resp.statusText;
        if (typeof showToast === 'function') {
          showToast(`❌ Failed to export thresholds: ${msg}`, true);
        }
      }
    } catch (err) {
      if (typeof showToast === 'function') {
        showToast('❌ Failed to export thresholds', true);
      }
    }
  });

  if (importBtn) importBtn.addEventListener('click', evt => {
    evt.preventDefault();
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.addEventListener('change', async () => {
      const file = input.files[0];
      if (!file) return;
      try {
        const text = await file.text();
        const payload = JSON.parse(text);
        const resp = await fetch('/system/alert_thresholds/import', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await resp.json();
        if (resp.ok && data.success) {
          showToast('✅ Thresholds imported');
          location.reload();
        } else {
          const msg = data.error || resp.statusText;
          showToast(`❌ Import failed: ${msg}`, true);
        }
      } catch (err) {
        showToast('❌ Error importing thresholds', true);
      }
    });
    input.click();
  });
});
