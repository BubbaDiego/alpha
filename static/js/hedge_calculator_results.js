// Simplified Hedge Calculator JS extracted from template

function setDisplayMode(mode) {
  const toggle = (id, show) => document.getElementById(id).style.display = show ? 'flex' : 'none';
  const showInputs = mode === 'full';
  const showMods = mode !== 'test';
  toggle('positionInputRow', showInputs);
  toggle('modifierRow', showMods);
  ['approachToggleRow','recommendationRow','outputRow','projectedOutputRow'].forEach(id=>toggle(id,true));
}

let longLiquidation = null;
let shortLiquidation = null;
let lastComputedCurrentPrice = 0;

function updateMarker() {
  const slider = document.getElementById('priceSlider');
  const simPrice = parseFloat(slider.value);
  const pos = (simPrice-slider.min)/(slider.max-slider.min);
  const left = pos*slider.getBoundingClientRect().width;
  const marker = document.getElementById('currentMarker');
  marker.style.left = left+'px';
  marker.textContent = 'Price: $'+simPrice.toFixed(2);
}

function updateEntryMarkers() {
  const slider = document.getElementById('priceSlider');
  const width = slider.getBoundingClientRect().width;
  const longEntry = parseFloat(document.getElementById('longEntry').value) || 0;
  const shortEntry = parseFloat(document.getElementById('shortEntry').value) || 0;
  if (longEntry) {
    const left = ((longEntry-slider.min)/(slider.max-slider.min))*width;
    const m = document.getElementById('entryMarkerLong');
    m.style.left = left+'px';
    m.textContent = 'Long Entry: $'+longEntry.toFixed(2);
  }
  if (shortEntry) {
    const left = ((shortEntry-slider.min)/(slider.max-slider.min))*width;
    const m = document.getElementById('entryMarkerShort');
    m.style.left = left+'px';
    m.textContent = 'Short Entry: $'+shortEntry.toFixed(2);
  }
}

function updateLong(simPrice) {
  const entry = parseFloat(document.getElementById('longEntry').value) || 0;
  const size = parseFloat(document.getElementById('longSize').value) || 0;
  const collateral = parseFloat(document.getElementById('longCollateral').value) || 0;
  let pnl = (simPrice - entry) * (entry? size/entry:0);
  document.getElementById('longPnL').textContent = 'P&L: '+pnl.toFixed(2);
}

function updateShort(simPrice) {
  const entry = parseFloat(document.getElementById('shortEntry').value) || 0;
  const size = parseFloat(document.getElementById('shortSize').value) || 0;
  let pnl = (entry - simPrice) * (entry? size/entry:0);
  document.getElementById('shortPnL').textContent = 'P&L: '+pnl.toFixed(2);
}

function sliderChanged(){
  const price = parseFloat(document.getElementById('priceSlider').value);
  updatePriceTicks();
  updateMarker();
  updateLong(price);
  updateShort(price);
  updateProjectedHeatIndex();
}


function updateProjectedHeatIndex(){
  const lev = parseFloat(document.getElementById('leverageSlider').value);
  document.getElementById('leverageValue').textContent = 'Leverage: '+lev+'x';
}

function resetPriceToCurrent(){
  const slider=document.getElementById('priceSlider');
  slider.value=lastComputedCurrentPrice;
  sliderChanged();
}

document.addEventListener('DOMContentLoaded', () => {
  const longSel = document.getElementById('longSelect');
  if (longSel && longSel.value) {
    loadLongPosition();
  }
  const shortSel = document.getElementById('shortSelect');
  if (shortSel && shortSel.value) {
    loadShortPosition();
  }
  const priceSlider = document.getElementById('priceSlider');
  if (priceSlider) {
    priceSlider.addEventListener('input', sliderChanged);
  }
  const leverageSlider = document.getElementById('leverageSlider');
  if (leverageSlider) {
    leverageSlider.addEventListener('input', updateProjectedHeatIndex);
  }
  const longSizeInput = document.getElementById('longSize');
  if (longSizeInput) {
    longSizeInput.addEventListener('input', sliderChanged);
  }
  const shortSizeInput = document.getElementById('shortSize');
  if (shortSizeInput) {
    shortSizeInput.addEventListener('input', sliderChanged);
  }
});
