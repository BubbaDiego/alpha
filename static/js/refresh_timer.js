console.log('✅ refresh_timer.js loaded');

document.addEventListener('DOMContentLoaded', () => {
  const INTERVAL = 60; // seconds
  let remaining = INTERVAL;
  const dial = document.getElementById('refreshDial');
  if (!dial) return;

  const progress = dial.querySelector('circle.progress');
  const number = dial.querySelector('.timer-number');
  if (!progress) return;

  const radius = progress.r.baseVal.value;
  const circumference = 2 * Math.PI * radius;

  progress.style.strokeDasharray = `${circumference}`;
  progress.style.strokeDashoffset = `${circumference}`;

  function updateDial() {
    const offset = circumference * (1 - remaining / INTERVAL);
    progress.style.strokeDashoffset = offset;
    if (number) number.textContent = remaining;
  }

  updateDial();

  setInterval(() => {
    remaining -= 1;
    if (remaining <= 0) {
      window.location.reload();
    } else {
      updateDial();
    }
  }, 1000);
});
