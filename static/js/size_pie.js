// size_pie.js - render LONG vs SHORT size composition pie chart
window.addEventListener('DOMContentLoaded', () => {
  const data = window.sizeData?.series || [];
  const isZero = data.every(v => v === 0);

  let mode = 'donut';

  const options = {
    chart: { type: mode, height: 260 },
    labels: ['Long', 'Short'],
    series: isZero ? [1] : data,
    colors: isZero ? ['#ccc'] : ['#3498db', '#e74c3c'],
    legend: { position: 'bottom' },
    tooltip: {
      y: {
        formatter: val => `${val}%`
      }
    }
  };

  const chartEl = document.querySelector('#pieChartSize');
  if (!chartEl) return;
  chartEl.textContent = '';
  chartEl.style.width = '100%';
  chartEl.style.cursor = 'pointer';

  const chart = new ApexCharts(chartEl, options);
  chart.render();

  chartEl.addEventListener('click', () => {
    mode = mode === 'donut' ? 'pie' : 'donut';
    chart.updateOptions({ chart: { type: mode } });
  });
});
