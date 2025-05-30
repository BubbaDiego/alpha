// Functions for configuring the hedge calculator
function loadLongPosition() {
  const id = document.getElementById('longSelect').value;
  const p = (window.longPositionsData || []).find(x => x.id === id);
  if (!p) return;
  document.getElementById('longEntry').value = p.entry_price;
  document.getElementById('longSize').value = p.size;
  document.getElementById('longCollateral').value = p.collateral || 0;
  document.getElementById('longLiqPrice').value = p.liquidation_price || 0;
  longLiquidation = p.liquidation_price;
  updateReferencePrice();
}

function loadShortPosition() {
  const id = document.getElementById('shortSelect').value;
  const p = (window.shortPositionsData || []).find(x => x.id === id);
  if (!p) return;
  document.getElementById('shortEntry').value = p.entry_price;
  document.getElementById('shortSize').value = p.size;
  document.getElementById('shortCollateral').value = p.collateral || 0;
  document.getElementById('shortLiqPrice').value = p.liquidation_price || 0;
  shortLiquidation = p.liquidation_price;
  updateReferencePrice();
}

function updateReferencePrice() {
  const longEntry = parseFloat(document.getElementById('longEntry').value) || 0;
  const shortEntry = parseFloat(document.getElementById('shortEntry').value) || 0;
  let current = longEntry && shortEntry ? (longEntry + shortEntry) / 2 : longEntry || shortEntry || 0;
  const slider = document.getElementById('priceSlider');
  slider.min = (longLiquidation || current * 0.8) * 0.95;
  slider.max = (shortLiquidation || current * 1.2) * 1.05;
  slider.value = current;
  lastComputedCurrentPrice = current;
  sliderChanged();
  updateEntryMarkers();
}

function updatePriceTicks() {
  if (longLiquidation) document.getElementById('tickLeft').textContent = '$' + longLiquidation.toFixed(2);
  if (shortLiquidation) document.getElementById('tickRight').textContent = '$' + shortLiquidation.toFixed(2);
}

function updateEntryMarkers() {
  const slider = document.getElementById('priceSlider');
  const width = slider.getBoundingClientRect().width;
  const longEntry = parseFloat(document.getElementById('longEntry').value) || 0;
  const shortEntry = parseFloat(document.getElementById('shortEntry').value) || 0;
  if (longEntry) {
    const left = ((longEntry - slider.min) / (slider.max - slider.min)) * width;
    const m = document.getElementById('entryMarkerLong');
    m.style.left = left + 'px';
    m.textContent = 'Long Entry: $' + longEntry.toFixed(2);
  }
  if (shortEntry) {
    const left = ((shortEntry - slider.min) / (slider.max - slider.min)) * width;
    const m = document.getElementById('entryMarkerShort');
    m.style.left = left + 'px';
    m.textContent = 'Short Entry: $' + shortEntry.toFixed(2);
  }
}

document.getElementById('saveModifiers').addEventListener('click', async () => {
  const payload = {
    hedge_modifiers: {
      feePercentage: parseFloat(document.getElementById('feePercentage').value) || 0,
      targetMargin: parseFloat(document.getElementById('targetMarginInput').value) || 0,
      adjustmentFactor: parseFloat(document.getElementById('adjustmentFactorInput').value) || 0
    },
    heat_modifiers: {
      distanceWeight: parseFloat(document.getElementById('distanceWeightInput').value) || 0,
      leverageWeight: parseFloat(document.getElementById('leverageWeightInput').value) || 0,
      collateralWeight: parseFloat(document.getElementById('collateralWeightInput').value) || 0
    }
  };
  try {
    await fetch('/sonic_labs/sonic_sauce', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    alert('Modifiers saved');
  } catch (err) {
    alert('Failed to save modifiers');
  }
});

const toggleBtn = document.getElementById('toggleConfig');
const configSection = document.getElementById('configSection');
if (toggleBtn && configSection) {
  toggleBtn.addEventListener('click', () => {
    const hidden = configSection.style.display === 'none';
    configSection.style.display = hidden ? '' : 'none';
    toggleBtn.title = hidden ? 'Hide Config' : 'Show Config';
    toggleBtn.innerHTML = hidden ? '<i class="fa-solid fa-eye-slash"></i>' : '<i class="fa-solid fa-eye"></i>';
  });
}
