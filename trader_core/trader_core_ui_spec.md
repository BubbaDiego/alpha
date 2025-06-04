# 🎨 Trader Core UI Specification

> Version: v1.0
> Author: CoreOps 🥷
> Scope: Overview of pages and assets used to manage Trader personas.

---

## 📂 Relevant Files
```
trader_core/
  trader_factory_service.py  # wrapper around TraderCore for UI
  trader_core_spec.md        # core logic reference
  trader_core_ui_spec.md     # (this doc)

templates/
  trader_factory.html        # main management page
  trader_shop.html           # simplified listing / new form
  title_bar.html             # shared navigation/header

static/css/
  trader_factory.css         # styles for factory dashboard
  trader_shop.css            # card styling

static/js/
  trader_factory.js          # placeholder for factory interactivity
  trader_shop.js             # load traders, avatar selector
```

These pages extend the shared `base.html` template and include `title_bar.html` for navigation, theme toggles and layout controls.

---

## 🏗️ Template Dependencies

- **`base.html`** – loads Bootstrap, FontAwesome, common styles and script hooks.
- **`title_bar.html`** – provides the header with nav icons, profit badge and layout/theme buttons.
- **`trader_factory.html`** – dashboard style page showing sample trader cards, leaderboard and activity log. Includes:
  - `trader_factory.css`
  - `trader_dashboard.js`, `layout_mode.js`, `sonic_theme_toggle.js` and `trader_factory.js`
- **`trader_shop.html`** – form based UI with cards listing created traders. References:
  - `trader_shop.css`
  - `trader_shop.js`

Both pages rely on icons defined in `static/images/` and `static/css/icons.css`.

---

## 🌟 Trader Factory Structure

`trader_factory.html` shows a grid of flip-card components. Each card front displays the trader avatar, name and mood. The back lists origin story and strategy weights with a button to ping the oracle. Below the cards are panels for a leaderboard and an activity log.

The page imports `trader_factory.js`, currently a placeholder script, along with shared theme/layout scripts. Styling is handled by `trader_factory.css` which defines card dimensions, 3D flip transitions and panel layouts.

---

## 🛍️ Trader Shop View

`trader_shop.html` lists traders fetched from `/trader/api/traders`. The new trader form lets users choose an avatar using emoji or uploaded images specified in `trader_shop.js`'s `AVATARS` map. Cards highlight the top performer via the `.top-score` CSS class.

Interactivity such as create/delete actions is encapsulated in `trader_shop.js` while `trader_shop.css` styles card fronts, backs and the flip effect.

---

## 🖼️ Icons & Images

Avatar icons live under `static/images/` (e.g., `r2vault.jpg`, `landovault.jpg`). `icons.css` sets their sizing within cards. Title bar icons rely on Unicode emoji or FontAwesome classes. New uploads go under `static/uploads/`.

---

## ✅ Summary

Use `base.html` + `title_bar.html` as the foundation. Build trader management screens with `trader_factory.html` or `trader_shop.html`, referencing the associated CSS/JS modules. Icons and avatars are stored in the `static/images` directory and sized via `icons.css`.
