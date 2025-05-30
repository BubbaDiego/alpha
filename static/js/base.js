// === base.js ===
console.log('✅ base.js loaded');

(function() {
  const body = document.body;
  const themeToggleButton = document.getElementById('themeToggleButton');
  const themeIcon = document.getElementById('themeIcon');

  function applyTheme(mode) {
    if (mode === 'dark') {
      body.classList.remove('light-bg');
      body.classList.add('dark-bg');
      if (themeIcon) {
        themeIcon.classList.remove('fa-sun');
        themeIcon.classList.add('fa-moon');
      }
      const navbar = document.querySelector('.main-header.navbar');
      if (navbar) navbar.classList.remove('gradient-navbar');
    } else {
      body.classList.remove('dark-bg');
      body.classList.add('light-bg');
      if (themeIcon) {
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
      }
      const navbar = document.querySelector('.main-header.navbar');
      if (navbar && !navbar.classList.contains('gradient-navbar')) {
        navbar.classList.add('gradient-navbar');
      }
    }
  }

  if (themeToggleButton) {
    themeToggleButton.addEventListener('click', function() {
      const currentTheme = body.classList.contains('dark-bg') ? 'dark' : 'light';
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      console.log(`🎛️ Toggling theme: ${currentTheme} ➡️ ${newTheme}`);
      applyTheme(newTheme);
      localStorage.setItem('preferredThemeMode', newTheme);
    });
  } else {
    console.warn('⚠️ Theme toggle button not found.');
  }
})();

// === DOM Ready Logic ===
document.addEventListener('DOMContentLoaded', function() {
  console.log('✅ DOM fully loaded and parsed');

  async function fetchAndUpdatePrices() {
    console.log('🚀 Fetching prices from /prices/api/data...');

    const btcPriceSpan = document.getElementById('btcPrice');
    const ethPriceSpan = document.getElementById('ethPrice');
    const solPriceSpan = document.getElementById('solPrice');

    if (!btcPriceSpan || !ethPriceSpan || !solPriceSpan) {
      console.error('❌ Price span elements not found!');
      return;
    } else {
      console.log('✅ Price span elements found.');
    }

    function showLoading() {
      btcPriceSpan.textContent = 'Loading...';
      ethPriceSpan.textContent = 'Loading...';
      solPriceSpan.textContent = 'Loading...';
    }

    function updatePriceElement(span, newPrice) {
      if (!span) return;

      const oldText = span.textContent.replace('$', '').replace('Loading...', '').trim();
      const oldPrice = parseFloat(oldText);

      span.textContent = `$${newPrice.toFixed(2)}`;

      // Animate flash if price changed
      if (!isNaN(oldPrice)) {
        if (newPrice > oldPrice) {
          span.classList.add('flash-green');
        } else if (newPrice < oldPrice) {
          span.classList.add('flash-red');
        }
      }

      // Always fade in
      span.classList.add('fade-in');

      // Remove classes after animation
      setTimeout(() => {
        span.classList.remove('flash-green', 'flash-red', 'fade-in');
      }, 1000);
    }

    showLoading();

    try {
      const response = await fetch('/prices/api/data');
      console.log('📡 Fetch response:', response);

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      console.log('📦 Fetched JSON data:', data);

      if (data.mini_prices) {
        const btc = data.mini_prices.find(p => p.asset_type === 'BTC');
        const eth = data.mini_prices.find(p => p.asset_type === 'ETH');
        const sol = data.mini_prices.find(p => p.asset_type === 'SOL');

        console.log('💰 BTC data:', btc);
        console.log('💰 ETH data:', eth);
        console.log('💰 SOL data:', sol);

        if (btc) updatePriceElement(btcPriceSpan, btc.current_price);
        if (eth) updatePriceElement(ethPriceSpan, eth.current_price);
        if (sol) updatePriceElement(solPriceSpan, sol.current_price);
      } else {
        console.error('❌ No mini_prices array found in response.');
      }
    } catch (error) {
      console.error('❌ Error fetching or parsing prices:', error);
      btcPriceSpan.textContent = '--';
      ethPriceSpan.textContent = '--';
      solPriceSpan.textContent = '--';
    }
  }

  fetchAndUpdatePrices();

  // Refresh prices every 30 seconds
  setInterval(fetchAndUpdatePrices, 30000);
});
