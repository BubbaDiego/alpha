// alert_status_actions.js
console.log('✅ alert_status_actions loaded');

function callEndpoint(url, icon, label) {
  if (typeof showToast === 'function') {
    showToast(`${icon} ${label} started...`);
  }
  return fetch(url, { method: 'POST' })
    .then(res => res.json())
    .then(data => {
      if (data.message) {
        showToast(`${icon} ${label} complete: ${data.message}`);
      } else if (data.error) {
        showToast(`❌ ${label} failed: ${data.error}`, true);
      } else {
        showToast(`⚠️ ${label} returned unknown response`, true);
      }
    })
    .catch(err => {
      console.error(`${label} error:`, err);
      showToast(`❌ ${label} failed to connect`, true);
    });
}

document.addEventListener('DOMContentLoaded', () => {
  const actions = {
    add: () => callEndpoint('/cyclone/run_create_alerts', '➕', 'Add Alerts'),
    delete: () => callEndpoint('/cyclone/clear_alerts', '🗑️', 'Delete Alerts'),
    update: () => callEndpoint('/cyclone/run_alert_evaluations', '🔄', 'Update Alert State')
  };

  const addBtn = document.querySelector('.alert-add');
  const delBtn = document.querySelector('.alert-delete');
  const updBtn = document.querySelector('.alert-update');

  if (addBtn) addBtn.addEventListener('click', (e) => { e.preventDefault(); actions.add(); });
  if (delBtn) delBtn.addEventListener('click', (e) => { e.preventDefault(); actions.delete(); });
  if (updBtn) updBtn.addEventListener('click', (e) => { e.preventDefault(); actions.update(); });
});
