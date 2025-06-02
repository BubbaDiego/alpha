console.log('✅ order_factory.js loaded');

document.addEventListener('DOMContentLoaded', () => {
  function postJson(url, payload, label, icon = '✅') {
    showToast(`${icon} ${label} started...`);
    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
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

  const launchBtn = document.getElementById('launchCoreBtn');
  if (launchBtn) {
    launchBtn.addEventListener('click', () => {
      postJson('/sonic_labs/api/order_core_launch', {}, 'Launch Core', '🚀');
    });
  }

  document.querySelectorAll('[data-engine-action]').forEach(btn => {
    btn.addEventListener('click', () => {
      const action = btn.getAttribute('data-engine-action');
      const value = btn.getAttribute('data-value');
      postJson('/sonic_labs/api/order_engine_action', { action, value }, action, '🔧');
    });
  });

  const runFlowBtn = document.getElementById('runFullFlowBtn');
  if (runFlowBtn) {
    runFlowBtn.addEventListener('click', () => {
      postJson('/sonic_labs/api/order_sequence', { flow: 'run_full_open_position_flow' }, 'Full Flow', '🧩');
    });
  }
});
