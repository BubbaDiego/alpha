const listEl = document.getElementById('alertList');

function renderAlerts(alerts) {
  listEl.innerHTML = '';
  alerts.forEach(alert => {
    const trigger = alert.trigger_value ?? 0;
    let start = alert.starting_value;
    const current = alert.evaluated_value ?? 0;
    if (start == null) {
      start = trigger || 0;
    }
    let travelPercent = 0;
    if (trigger !== start) {
      travelPercent = ((current - start) / (trigger - start)) * 100;
    } else if (start !== 0) {
      travelPercent = (current / start) * 100;
    }
    travelPercent = Math.min(Math.max(travelPercent, -100), 100);

    const flip = document.createElement('div');
    flip.className = 'alert-flip';
    flip.innerHTML = `
      <div class="flip-card-inner">
        <div class="flip-card-front">
          <div class="card-face-content">
            <img src="/static/images/${alert.asset?.toLowerCase() ?? 'unknown'}_logo.png" class="asset-icon" alt="${alert.asset || 'unknown'}" onerror="this.src='/static/images/unknown.png'">
            <div class="bar-card">
              <span style="font-size:1.01em;font-weight:500;min-width:120px;">${alert.alert_type || 'Unknown'}</span>
              <div class="liq-row">
                <div class="liq-bar-container">
                  <div class="liq-midline"></div>
                  <div class="liq-bar-fill ${travelPercent >= 0 ? 'positive' : 'negative'}"
                    style="${travelPercent >= 0
                      ? `left:50%;width:${travelPercent}%`
                      : `right:50%;width:${Math.abs(travelPercent)}%`}">
                    <span class="travel-text">${travelPercent.toFixed(1)}%</span>
                  </div>
                </div>
                <div class="liq-level-badge level-${alert.level}">${alert.level.charAt(0)}</div>
              </div>
            </div>
            <span class="flip-hint">⤵ flip</span>
          </div>
        </div>
        <div class="flip-card-back">
          <div class="card-face-content">
            <div class="threshold-row">
              <span style="font-weight: 600;">Thresholds:</span>
              <span>Low: <b>${alert.thresholds?.low ?? '-'}</b></span>
              <span>Med: <b>${alert.thresholds?.medium ?? '-'}</b></span>
              <span>High: <b>${alert.thresholds?.high ?? '-'}</b></span>
            </div>
            <div class="value-row">
              <span>Eval: <b>${alert.evaluated_value}</b></span>
              <span>Trigger: <b>${alert.trigger_value}</b></span>
              <span>Start: <b>${alert.starting_value}</b></span>
            </div>
            <span class="flip-hint">⤴ flip back</span>
          </div>
        </div>
      </div>
    `;
    flip.addEventListener('click', () => {
      flip.classList.toggle('flipped');
    });
    listEl.appendChild(flip);
  });
}

async function loadAlerts() {
  try {
    const response = await fetch('/alerts/monitor');
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    const data = await response.json();
    renderAlerts(data.alerts || []);
  } catch (err) {
    console.error('Error loading alerts:', err);
    listEl.innerHTML = '<div class="text-danger">Failed to load alerts.</div>';
  }
}

document.addEventListener('DOMContentLoaded', loadAlerts);
