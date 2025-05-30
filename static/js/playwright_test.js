console.log('✅ playwright_test.js loaded');

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('runTestBtn');
  if (btn) {
    btn.addEventListener('click', () => {
      showToast('🎭 Playwright test starting...');
      fetch('/sonic_labs/api/run_playwright_test', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
          if (data.message) {
            showToast('✅ ' + data.message);
          } else if (data.error) {
            showToast('❌ ' + data.error, true);
          } else {
            showToast('⚠️ Unknown response', true);
          }
        })
        .catch(err => {
          console.error('Playwright test error', err);
          showToast('❌ Test failed to connect', true);
        });
    });
  }
});
