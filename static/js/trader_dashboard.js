(function() {
  const colors = {
    calm: 'blue',
    excited: 'orange',
    nervous: 'yellow',
    chaotic: 'red',
    neutral: 'green'
  };
  const moodEl = document.getElementById('mood');
  if (moodEl) {
    const color = colors[moodEl.textContent.trim()] || 'gray';
    moodEl.style.backgroundColor = color;
  }
})();
