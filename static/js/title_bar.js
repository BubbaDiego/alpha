// static/js/title_bar.js

console.log("✅ title_bar.js loaded");

// ======================
// Toast Utility
// ======================
function showToast(message, isError = false) {
  const toast = document.createElement('div');
  toast.className = `toast align-items-center text-bg-${isError ? 'danger' : 'success'} border-0`;
  toast.setAttribute('role', 'alert');
  toast.setAttribute('aria-live', 'assertive');
  toast.setAttribute('aria-atomic', 'true');
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
  `;
  const container = document.getElementById('toastContainer');
  if (container) container.appendChild(toast);
  const bootstrapToast = new bootstrap.Toast(toast, { delay: 4000 });
  bootstrapToast.show();
  toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

// ======================
// Action Endpoints
// ======================
function callEndpoint(url, icon = "✅", label = "Action", postAction = null) {
  showToast(`${icon} ${label} started...`);
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

// ======================
// Title Bar Button Logic
// ======================
document.addEventListener('DOMContentLoaded', () => {
  // Right action buttons
  const actions = {
    sync:   () => callEndpoint('/cyclone/run_position_updates', "🪐", "Jupiter Sync"),
    market: () => callEndpoint('/cyclone/run_market_updates',   "💲", "Market Update"),
    full:   () => callEndpoint('/cyclone/run_full_cycle',       "🌪️", "Full Cycle"),
    wipe:   () => callEndpoint('/cyclone/clear_all_data',       "🗑️", "Cyclone Delete")
  };

  document.querySelectorAll('[data-action]').forEach(btn => {
    const clone = btn.cloneNode(true);
    btn.parentNode.replaceChild(clone, btn);
    const key = clone.getAttribute('data-action');
    clone.addEventListener('click', function() {
      if (actions[key]) {
        actions[key]();
      } else {
        showToast(`⚠️ Unknown [data-action="${key}"]`, true);
      }
    });
  });

  // Theme toggle handled globally by sonic_theme_toggle.js

  // Apply shimmer animation to the title pill on load
  const titlePill = document.querySelector('.sonic-title-pill');
  if (titlePill) {
    titlePill.classList.add('shimmer');
  }

  // Allow dismissing the profit badge with a click
  const profitBadge = document.querySelector('.profit-badge');
  if (profitBadge) {
    profitBadge.addEventListener('click', () => {
      profitBadge.classList.add('fade-out');
      setTimeout(() => profitBadge.remove(), 400);
    });
  }
});
