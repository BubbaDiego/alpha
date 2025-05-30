// Attach tooltips showing the raw value on hover
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.status-card').forEach(card => {
    const raw = card.dataset.rawValue;
    if (raw !== undefined) {
      card.addEventListener('mouseenter', () => {
        card.setAttribute('title', raw);
      });
    }
  });
});