// === Theme Builder Logic ===
window.addEventListener('DOMContentLoaded', () => {
  const bgInput = document.getElementById('backgroundColor');
  const textInput = document.getElementById('textColor');
  const cardInput = document.getElementById('cardBackground');
  const navInput = document.getElementById('navbarBackground');
  const presetNameInput = document.getElementById('presetName');
  const presetList = document.getElementById('presetList');
  const saveBtn = document.getElementById('savePresetBtn');
  const setActiveBtn = document.getElementById('setActiveBtn');
  const deleteBtn = document.getElementById('deletePresetBtn');

  async function loadPresets() {
    const resp = await fetch('/system/theme_config');
    const data = await resp.json();
    presetList.innerHTML = '';
    Object.entries(data).forEach(([name, cfg]) => {
      const opt = document.createElement('option');
      opt.value = name;
      opt.textContent = name;
      presetList.appendChild(opt);
    });
    if (presetList.options.length) {
      presetList.value = presetList.options[0].value;
      applyPreset(data[presetList.value]);
    }
  }

  function applyPreset(cfg) {
    if (!cfg) return;
    bgInput.value = cfg.backgroundColor || '#ffffff';
    textInput.value = cfg.textColor || '#000000';
    cardInput.value = cfg.cardBackground || '#ffffff';
    navInput.value = cfg.navbarBackground || '#ffffff';
    updatePreview();
  }

  function updatePreview() {
    document.documentElement.style.setProperty('--card-background-color', cardInput.value);
    document.body.style.backgroundColor = bgInput.value;
    document.body.style.color = textInput.value;
    const navbar = document.querySelector('.title-bar');
    if (navbar) navbar.style.backgroundColor = navInput.value;
  }

  bgInput.addEventListener('input', updatePreview);
  textInput.addEventListener('input', updatePreview);
  cardInput.addEventListener('input', updatePreview);
  navInput.addEventListener('input', updatePreview);

  if (saveBtn) saveBtn.addEventListener('click', async () => {
    const name = presetNameInput.value.trim();
    if (!name) return;
    const payload = { [name]: {
      backgroundColor: bgInput.value,
      textColor: textInput.value,
      cardBackground: cardInput.value,
      navbarBackground: navInput.value
    }};
    await fetch('/system/theme_config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    await loadPresets();
    presetList.value = name;
  });

  if (setActiveBtn) setActiveBtn.addEventListener('click', async () => {
    const active = presetList.value;
    if (!active) return;
    await fetch(`/system/themes/activate/${encodeURIComponent(active)}`, { method: 'POST' });
  });

  if (deleteBtn) deleteBtn.addEventListener('click', async () => {
    const name = presetList.value;
    if (!name) return;
    await fetch(`/system/themes/${encodeURIComponent(name)}`, { method: 'DELETE' });
    await loadPresets();
  });

  presetList.addEventListener('change', async () => {
    const resp = await fetch('/system/theme_config');
    const data = await resp.json();
    applyPreset(data[presetList.value]);
  });

  loadPresets();
});
