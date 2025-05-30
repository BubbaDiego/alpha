// === dashboard_middle.js ===
document.addEventListener('DOMContentLoaded', () => {
  console.log('✅ dashboard_middle.js loaded');

  const rows = document.querySelectorAll('.row-pair');

  rows.forEach(row => {
    // Hover effect
    row.addEventListener('mouseenter', () => {
      row.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
      row.style.transform = 'scale(1.01)';
    });

    row.addEventListener('mouseleave', () => {
      row.style.boxShadow = '';
      row.style.transform = '';
    });

    // Click-to-toggle details (could expand row later)
    row.addEventListener('click', () => {
      row.classList.toggle('selected-row');
      console.log('🧪 Row toggled:', row);
    });
  });
});
