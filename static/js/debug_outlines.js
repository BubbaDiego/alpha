// Toggle debug outlines for layout containers
// Press Ctrl+Alt+D to toggle and persist across sessions
(function() {
  const KEY = 'debugOutlines';
  function apply(active) {
    document.body.classList.toggle('debug-outlines', active);
  }
  function toggle() {
    const active = !document.body.classList.contains('debug-outlines');
    apply(active);
    localStorage.setItem(KEY, active ? '1' : '0');
  }
  document.addEventListener('DOMContentLoaded', () => {
    apply(localStorage.getItem(KEY) === '1');
  });
  document.addEventListener('keydown', e => {
    if (e.ctrlKey && e.altKey && e.key.toLowerCase() === 'd') {
      e.preventDefault();
      toggle();
    }
  });
})();
