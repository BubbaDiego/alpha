// Layout mode toggle script
console.log('layout_mode.js loaded');

const LAYOUT_MODES = ['wide-mode', 'fitted-mode', 'mobile-mode'];
const LAYOUT_ICONS = ['🖥️', '💻', '📱'];
let layoutIndex = 0;

function setLayoutMode(mode) {
  document.body.classList.remove(...LAYOUT_MODES);
  document.body.classList.add(mode);

  const buttons = document.querySelectorAll('.layout-btn[data-mode]');
  buttons.forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-mode') === mode);
  });

  const icon = document.getElementById('currentLayoutIcon');
  if (icon) {
    const idx = LAYOUT_MODES.indexOf(mode);
    if (idx !== -1) icon.innerText = LAYOUT_ICONS[idx];
  }

  localStorage.setItem('sonicLayoutMode', mode);
}

document.addEventListener('DOMContentLoaded', () => {
  const buttons = document.querySelectorAll('.layout-btn[data-mode]');
  let mode = localStorage.getItem('sonicLayoutMode') || LAYOUT_MODES[0];
  if (!LAYOUT_MODES.includes(mode)) mode = LAYOUT_MODES[0];
  layoutIndex = LAYOUT_MODES.indexOf(mode);
  if (layoutIndex === -1) layoutIndex = 0;
  setLayoutMode(mode);

  // Cycle layout via single toggle button if present
  const toggle = document.getElementById('layoutModeToggle');
  if (toggle) {
    toggle.addEventListener('click', e => {
      e.preventDefault();
      layoutIndex = (layoutIndex + 1) % LAYOUT_MODES.length;
      setLayoutMode(LAYOUT_MODES[layoutIndex]);
    });
  }

  // Direct selection buttons (if any)
  buttons.forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      const mode = btn.getAttribute('data-mode');
      layoutIndex = LAYOUT_MODES.indexOf(mode);
      if (layoutIndex === -1) layoutIndex = 0;
      setLayoutMode(mode);
    });
  });
});
