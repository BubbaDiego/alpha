// == SONIC THEME TOGGLE LOGIC ==

const THEME_KEY = "themeMode";
const THEMES = ["light", "dark", "funky"];
const THEME_ICONS = { light: "☀️", dark: "🌙", funky: "🎨" };

function setTheme(mode) {
  document.documentElement.setAttribute("data-theme", mode);
  localStorage.setItem(THEME_KEY, mode);
  document.cookie = `${THEME_KEY}=${mode};path=/;max-age=31536000`;

  const icon = document.getElementById("currentThemeIcon");
  if (icon) icon.innerText = THEME_ICONS[mode] || "";

  const buttons = document.querySelectorAll('.theme-btn[data-theme]');
  buttons.forEach(btn => btn.classList.toggle('active', btn.getAttribute('data-theme') === mode));
}

function getPersistedTheme() {
  let mode = localStorage.getItem(THEME_KEY);
  if (!mode) {
    const cookie = document.cookie.split('; ').find(r => r.startsWith(`${THEME_KEY}=`));
    if (cookie) mode = cookie.split('=')[1];
  }
  return THEMES.includes(mode) ? mode : "light";
}

function cycleTheme() {
  const current = getPersistedTheme();
  const idx = THEMES.indexOf(current);
  const next = THEMES[(idx + 1) % THEMES.length];
  setTheme(next);
}

function bindThemeButtons() {
  document.querySelectorAll('.theme-btn[data-theme]').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      const mode = btn.getAttribute('data-theme');
      setTheme(mode);
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  setTheme(getPersistedTheme());

  const toggle = document.getElementById('themeModeToggle');
  if (toggle) {
    toggle.addEventListener('click', e => {
      e.preventDefault();
      cycleTheme();
    });
  }

  bindThemeButtons();
});
