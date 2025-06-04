# 🎨 UI Base Specification

> Version: v1.0
> Scope: Shared templates and front-end assets
> Author: CoreOps 🥷

---

## 📂 Directory Layout

```
templates/
    base.html             # master layout
    title_bar.html        # common header with nav/buttons
    ... (page templates)
static/css/               # stylesheets
static/js/                # JavaScript modules
static/images/            # icons & backgrounds
static/sounds/            # alert audio
```

The Flask app registers multiple blueprints that all extend the same base
layout. Shared files live at the repo root under `templates/` and
`static/` so any blueprint can include them using `url_for('static', ... )`.

---

## 🏗️ Base Templates

### `base.html`
Defines the skeleton for every page. It loads Bootstrap and FontAwesome,
provides `block` hooks for page content, and references common styles.
Key lines:

```html
{% raw %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{% block title %}New Sonic Dashboard{% endblock %}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://fonts.googleapis.com/css2?family=Orbitron&display=swap" rel="stylesheet">
  {% block head %}{% endblock %}
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/icons.css') }}">
  {% block extra_styles %}{% endblock %}
</head>
<body>
  {% block content %}{% endblock %}
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" defer></script>
  {% block extra_scripts %}{% endblock %}
</body>
</html>
{% endraw %}
```
【F:templates/base.html†L1-L20】

### `title_bar.html`
Reusable navigation/header bar. It shows icon buttons for major pages,
layout and theme toggles, a refresh dial and a settings menu.
Excerpt:

```html
{% raw %}
<nav class="title-bar d-flex justify-content-between align-items-center px-3 py-2">
  <div class="nav-bar d-flex align-items-center gap-2">
    <a class="btn nav-btn" href="/" title="Home"><span>🏠</span></a>
    <a class="btn nav-btn" href="{{ url_for('positions.list_positions') }}" title="Positions"><span>📊</span></a>
    ...
  </div>
  <div class="title-bar-center text-center" style="font-size:1.3rem;font-weight:bold;letter-spacing:0.04em;">
    {% if title_image %}
    <div class="sonic-title-pill {{ title_theme|default('default') }} mx-2">
      <img src="{{ title_image }}" alt="{{ title_text or 'title' }}" class="sonic-title-image">
    </div>
    {% elif title_text %}
    <div class="sonic-title-pill {{ title_theme|default('default') }} mx-2">{{ title_text }}</div>
    {% endif %}
    {% if profit_badge_value %}
    <span class="profit-badge badge text-bg-success ms-2">{{ profit_badge_value }}</span>
    {% endif %}
  </div>
  <div class="title-bar-actions d-flex align-items-center gap-3 ms-auto">
    <div class="config-bar d-flex align-items-center gap-2">
      <a id="layoutModeToggle" class="btn config-btn layout-toggle-btn" href="#" role="button" title="Switch View Mode">
        <span id="currentLayoutIcon">🖥️</span>
      </a>
      <a id="themeModeToggle" class="btn config-btn theme-btn" href="#" role="button" title="Switch Theme">
        <span id="currentThemeIcon">☀️</span>
      </a>
    </div>
    <div class="cyclone-bar d-flex align-items-center gap-2 ms-3">
        <a class="btn nav-icon-btn cyclone-btn" href="#" role="button" data-action="sync"   title="Jupiter Sync"><span>🪐</span></a>
        <a class="btn nav-icon-btn cyclone-btn" href="#" role="button" data-action="market" title="Market Update"><span>💲</span></a>
        <a class="btn nav-icon-btn cyclone-btn" href="#" role="button" data-action="full"  title="Full Cycle"><span>🌪️</span></a>
        <a class="btn nav-icon-btn cyclone-btn" href="#" role="button" data-action="wipe"  title="Wipe All"><span>🗑️</span></a>
      </div>
    ...
  </div>
</nav>
{% endraw %}
```
【F:templates/title_bar.html†L1-L64】

This template loads `refresh_timer.js` and `title_bar.js` which provide
the toast utility, cyclone API calls and the auto‑refresh dial.

---

## 📜 Core Styles

### `sonic_themes.css`
Defines CSS variables for `light`, `dark` and `funky` modes.
The variables drive background colors, card styling and accent colors.
Sample:

```css
:root[data-theme="light"] {
  --bg: #e7ecfa;
  --text: #222;
  --card-bg: #9ebcdc;
  --panel-border: #b7c5e0;
  --title-bar-bg: #8fbbef;
}
:root[data-theme="dark"] {
  --bg: #3a3a3c;
  --text: #eee;
  --card-bg: #23272f;
  --title-bar-bg: #191c22;
}
```
【F:static/css/sonic_themes.css†L26-L58】

### `title_bar.css`
Styles the navigation bar, layout/theme buttons and refresh dial.
Animation keyframes create pulsing profit badges and button hover effects.

### Other CSS
- `sonic_dashboard.css` – general dashboard layout
- `hedge_labs.css`, `trader_dashboard.css`, etc. – page specific styles
- `icons.css` – avatar/icon sizing

---

## ⚙️ JavaScript Modules

### `base.js`
Executes on page load to fetch mini price data and update the ticker
spans (`btcPrice`, `ethPrice`, `solPrice`). It also manages a legacy
light/dark toggle using localStorage.

```javascript
// === base.js ===
(function() {
  const body = document.body;
  const themeToggleButton = document.getElementById('themeToggleButton');
  function applyTheme(mode) {
    if (mode === 'dark') {
      body.classList.remove('light-bg');
      body.classList.add('dark-bg');
    } else {
      body.classList.remove('dark-bg');
      body.classList.add('light-bg');
    }
  }
  if (themeToggleButton) {
    themeToggleButton.addEventListener('click', function() {
      const currentTheme = body.classList.contains('dark-bg') ? 'dark' : 'light';
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      applyTheme(newTheme);
      localStorage.setItem('preferredThemeMode', newTheme);
    });
  }
})();
```
【F:static/js/base.js†L1-L44】

### `sonic_theme_toggle.js`
Centralized theme cycling across `light`, `dark` and `funky` modes. It
stores the choice in both `localStorage` and cookies so all pages share
the same appearance.

### `layout_mode.js`
Toggles body classes `wide-mode`, `fitted-mode` and `mobile-mode`. The
current mode persists via `localStorage`.

### `title_bar.js`
Attaches click handlers to cyclone buttons and displays Bootstrap
"toast" notifications. Also handles profit badge dismissal and title
image shimmer effects.

---

## 📄 Existing Page Templates

```
alert_matrix.html
alert_status.html
alert_thresholds_legacy.html
chat_gpt.html
components/alert_card.html
components/hedge_card.html
dash_top.html
dash_middle.html
dash_bottom.html
db_viewer.html
hedge_calculator_config.html
hedge_calculator_results.html
hedge_labs.html
hedge_modifiers.html
hedge_report.html
liquidation_bars.html
monitor_cards.html
oracle_gpt.html
order_factory.html
partials/global_alerts_section.html
partials/portfolio_alerts_section.html
partials/positions_alerts_section.html
partials/price_alerts_section.html
playwright_test.html
portfolio_cards.html
positions/portfolio.html
positions/positions.html
positions_table.html
sonic_dashboard.html
sonic_titles.html
system/alert_thresholds.html
system/xcom_config.html
trader_cards.html
trader_dashboard.html
trader_factory.html
wallets/wallet_form.html
wallets/wallet_manager.html
```

These extend `base.html` and most include `title_bar.html` for
consistent navigation.

---

## 🖼️ Static Assets

### CSS Files
```
alert_matrix.css
alert_status.css
dashboard_middle.css
dashboard_parallax.css
hedge_calculator.css
hedge_calculator_config.css
hedge_labs.css
hedge_report.css
icons.css
liquidation_bars.css
sonic_dashboard.css
sonic_theme_toggle.css
sonic_themes.css
sonic_titles.css
title_bar.css
trader_dashboard.css
trader_factory.css
```

### JavaScript Files
```
alert_matrix.js
alert_status_actions.js
alert_thresholds.js
api_routes.js
base.js
dashboard.js
dashboard_bottom.js
dashboard_middle.js
dashboard_oracle.js
dashboard_parallax.js
dashboard_top.js
debug_outlines.js
hedge_calculator_config.js
hedge_calculator_results.js
hedge_labs.js
layout_mode.js
order_factory.js
playwright_test.js
portfolio_status.js
refresh_timer.js
size_pie.js
sonic_theme_toggle.js
title_bar.js
trader_dashboard.js
trader_factory.js
```

### Images
Common assets such as `sonic.png`, token logos, wallpapers and themed
backgrounds reside in `static/images/`. These are referenced by the CSS
themes and page templates.

#### Icon & Image Glossary

| File | Description | Location |
|------|-------------|----------|
| `Wally.png` | Wallpaper featuring the Wally robot used by funky theme backgrounds. | `static/images/Wally.png` |
| `aave.jpg` | Aave protocol logo. | `static/images/aave.jpg` |
| `alert_wall.jpg` | Background image for alert pages. | `static/images/alert_wall.jpg` |
| `btc_logo.png` | Bitcoin logo icon used in positions and hedge reports. | `static/images/btc_logo.png` |
| `cityscape3.jpg` | Cityscape wallpaper used in dashboards. | `static/images/cityscape3.jpg` |
| `container_wallpaper.jpg` | Container themed background. | `static/images/container_wallpaper.jpg` |
| `corner_icon.jpg` | Small corner icon for page layouts. | `static/images/corner_icon.jpg` |
| `corner_logo_owl.jpg` | Owl variant of the corner logo. | `static/images/corner_logo_owl.jpg` |
| `corner_logos.jpg` | Composite image of corner logos. | `static/images/corner_logos.jpg` |
| `crypto_icon.jpg` | Generic cryptocurrency icon. | `static/images/crypto_icon.jpg` |
| `crypto_iconz.png` | Alternate crypto icon style. | `static/images/crypto_iconz.png` |
| `database_wall.jpg` | Wallpaper for the database viewer. | `static/images/database_wall.jpg` |
| `error.png` | Error status icon. | `static/images/error.png` |
| `eth_logo.png` | Ethereum logo icon. | `static/images/eth_logo.png` |
| `jupiter.jpg` | Jupiter aggregator logo. | `static/images/jupiter.jpg` |
| `landovault.jpg` | Landovault wallet image. | `static/images/landovault.jpg` |
| `monitor_wallpaper.jpg` | Background for monitor dashboard. | `static/images/monitor_wallpaper.jpg` |
| `obivault.jpg` | ObiVault wallet image. | `static/images/obivault.jpg` |
| `r2vault - Copy.jpg` | Alternate R2Vault wallet image. | `static/images/r2vault - Copy.jpg` |
| `r2vault.jpg` | R2Vault wallet image. | `static/images/r2vault.jpg` |
| `raydium.jpg` | Raydium DEX logo. | `static/images/raydium.jpg` |
| `sol_logo.png` | Solana logo icon. | `static/images/sol_logo.png` |
| `sonic.png` | Main Sonic mascot used across dashboards. | `static/images/sonic.png` |
| `sonic_title.png` | Sonic styled title banner. | `static/images/sonic_title.png` |
| `space_wall4.jpg` | Space themed wallpaper. | `static/images/space_wall4.jpg` |
| `sys_config_wall.jpg` | System configuration wallpaper. | `static/images/sys_config_wall.jpg` |
| `twilio.png` | Twilio API logo. | `static/images/twilio.png` |
| `unknown.png` | Placeholder icon for unknown assets. | `static/images/unknown.png` |
| `unknown_wallet.jpg` | Generic wallet placeholder. | `static/images/unknown_wallet.jpg` |
| `vadervault.jpg` | VaderVault wallet image. | `static/images/vadervault.jpg` |
| `yodavault.jpg` | YodaVault wallet image. | `static/images/yodavault.jpg` |
| `bobavault.jpg` | BobaVault wallet image. | `static/images/bobavault.jpg` |
| `leiavault.jpg` | LeiaVault wallet image. | `static/images/leiavault.jpg` |

| `wallpaper2.jpg` | Additional wallpaper option. | `static/images/wallpaper2.jpg` |
| `wallpaper2.png` | PNG variant of wallpaper2. | `static/images/wallpaper2.png` |
| `wallpaper4.jpg` | Background image option. | `static/images/wallpaper4.jpg` |
| `wallpaper5.jpg` | Background image option. | `static/images/wallpaper5.jpg` |
| `wallpaper6.jpg` | Background image option. | `static/images/wallpaper6.jpg` |
| `wallpapersden.jpg` | Wallpaper from wallpapersden site. | `static/images/wallpapersden.jpg` |
| `wally2.png` | Secondary Wally wallpaper used in funky theme. | `static/images/wally2.png` |
| `landovault.jpg` (upload) | Sample uploaded wallet logo. | `static/uploads/wallets/landovault.jpg` |
| `vadervault.jpg` (upload) | Sample uploaded wallet logo. | `static/uploads/wallets/vadervault.jpg` |
| `yodavault.jpg` (upload) | Sample uploaded wallet logo. | `static/uploads/wallets/yodavault.jpg` |
| `bobavault.jpg` (upload) | Sample uploaded wallet logo. | `static/uploads/wallets/bobavault.jpg` |

| `leiavault.jpg` (upload) | Sample uploaded wallet logo. | `static/uploads/wallets/leiavault.jpg` |

### Sounds
```
death_spiral.mp3
error.mp3
fail.mp3
level-up.mp3
message_alert.mp3
web_station_startup.mp3
```

---

## 🚀 Getting Started for New UI Contributors
1. **Extend `base.html`** – create new templates using Jinja blocks
   `head`, `content`, `extra_styles`, and `extra_scripts`.
2. **Include `title_bar.html`** to gain navigation, theme toggles and
auto-refresh features.
3. **Use CSS variables** defined in `sonic_themes.css` for consistent
theming. Switch modes via `sonic_theme_toggle.js`.
4. **Add page‑specific scripts** under `static/js/` and styles under
   `static/css/`.
5. **Reference assets** with `url_for('static', filename='...')` so all
   blueprints can find them.

This spec should give a GPT agent the context needed to build or modify
UI pages within the existing framework.
