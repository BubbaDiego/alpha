// === dashboard_bottom.js ===
document.addEventListener('DOMContentLoaded', () => {
  console.log('✅ dashboard_bottom.js loaded');
  if (window.graphData) {
    renderLineChart(window.graphData);
  }
});

function renderLineChart(data) {
  const options = {
    chart: {
      type: 'line',
      height: 300,
      zoom: { enabled: true },
      toolbar: {
        autoSelected: 'zoom',
        tools: { zoom: true, zoomin: true, zoomout: true, pan: true, reset: true }
      }
    },
    series: [
      { name: 'Total Value', data: data.values },
      { name: 'Total Collateral', data: data.collateral }
    ],
    xaxis: {
      type: 'datetime',
      categories: data.timestamps
    },
    yaxis: {
      labels: {
        formatter: val => Math.round(val)
      }
    },
    colors: ['#2980b9', '#27ae60'],
    stroke: { curve: 'smooth' },
    tooltip: { x: { format: 'yyyy-MM-dd HH:mm' } }
  };

  const chartEl = document.querySelector('#lineChart');
  if (!chartEl) return;
  chartEl.textContent = '';
  chartEl.style.width = '100%';
  const chart = new ApexCharts(chartEl, options);
  chart.render();
}

