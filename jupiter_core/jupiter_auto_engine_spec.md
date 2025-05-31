# 🚀 Jupiter Auto Engine Specification

> Version: `v1.0`
> Author: `CoreOps 🥷`
> Scope: Phantom wallet automation and Jupiter Perps flows

---

## 📂 Module Structure

```txt
jupiter_core/
├── engine/                 # JupiterEngineCore wrapper
├── jupiter_auto_console.py # Interactive CLI
├── jupiter_perps_flow.py   # Jupiter page helpers
├── jupiter_perps_steps.py  # Console step functions
├── phantom_manager.py      # Browser + Phantom automation
├── phantom_wallet/         # Packed Phantom extension
```

### 🧩 `JupiterEngineCore`
Provides a high level wrapper around `PhantomManager` and `JupiterPerpsFlow`.
It launches the browser, exposes the current page, and cleans up when done.

```python
class JupiterEngineCore:
    """Async wrapper around :class:`PhantomManager` and :class:`JupiterPerpsFlow`."""
    def __init__(self, extension_path: str, dapp_url: str, *, phantom_password: Optional[str] = None, headless: bool = False) -> None:
        self.extension_path = extension_path
        self.dapp_url = dapp_url
        self.phantom_password = phantom_password
        self.headless = headless
        self.pm: Optional[PhantomManager] = None
        self.jp: Optional[JupiterPerpsFlow] = None
        self.page = None
```
【F:jupiter_core/engine/jupiter_engine_core.py†L9-L27】

`launch()` creates the managers and opens the browser:

```python
    async def launch(self) -> None:
        self.pm = PhantomManager(extension_path=self.extension_path, headless=self.headless)
        await self.pm.launch_browser()
        self.page = self.pm.page
        self.jp = JupiterPerpsFlow(self.pm)
```
【F:jupiter_core/engine/jupiter_engine_core.py†L30-L35】

### 🦊 `PhantomManager`
Handles launching a Chromium instance with the Phantom extension and provides helpers for connecting and approving transactions.

```python
class PhantomManager:
    def __init__(self, extension_path: str, user_data_dir: str = "playwright-data", headless: bool = False) -> None:
        self.extension_path = extension_path
        self.user_data_dir = user_data_dir
        self.headless = headless
        self.browser_context: Optional[BrowserContext] = None
        ...
```
【F:jupiter_core/phantom_manager.py†L10-L19】

The browser is started via `launch_browser()` which loads the unpacked extension:

```python
    async def launch_browser(self) -> None:
        logger.info("Launching browser with Phantom extension...")
        self.playwright = await async_playwright().start()
        self.browser_context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=self.headless,
            channel="chrome",
            args=[
                f"--disable-extensions-except={self.extension_path}",
                f"--load-extension={self.extension_path}",
                "--window-size=1280,720",
                "--start-maximized",
            ],
        )
        self.page = await self.browser_context.new_page()
```
【F:jupiter_core/phantom_manager.py†L24-L45】

`connect_wallet()` navigates to the dApp, handles the Jupiter terms modal and clicks through the Phantom popup:

```python
    async def connect_wallet(
        self,
        dapp_url: str,
        dapp_connect_selector: str = "css=span.text-v2-primary",
        popup_connect_selector: str = "text=Connect",
        wallet_selection_selector: str = "text=Use this wallet",
        dapp_connected_selector: str = "text=Connected",
        phantom_password: Optional[str] = None,
    ) -> None:
        logger.debug("Navigating to dApp: %s", dapp_url)
        await self.page.goto(dapp_url, timeout=15000)
        ...
```
【F:jupiter_core/phantom_manager.py†L185-L199】

Unlocking the wallet is handled with `unlock_phantom()`:

```python
    async def unlock_phantom(self, phantom_password: str) -> None:
        logger.debug("Unlocking Phantom: selecting password input field.")
        if self.popup is None or self.popup.is_closed():
            await self.open_phantom_popup()
        await self.popup.wait_for_selector("input[data-testid='unlock-form-password-input']", timeout=5000)
        await self.popup.fill("input[data-testid='unlock-form-password-input']", phantom_password, timeout=2000)
        await self.popup.click("button[data-testid='unlock-form-submit-button']", timeout=5000)
        await self.popup.wait_for_timeout(2000)
        await self.dismiss_post_unlock_dialog()
```
【F:jupiter_core/phantom_manager.py†L304-L324】

### 📈 `JupiterPerpsFlow`
Contains helper methods for interacting with the Jupiter Perps UI using the active page.

Selecting a long or short position updates `order_definition`:

```python
    async def select_position_type(self, position_type: str):
        logger.debug("Selecting position type: %s", position_type)
        if position_type.lower() == "long":
            await self.page.click("button:has-text('Long')", timeout=10000)
            self.order_definition["position_type"] = "long"
        elif position_type.lower() == "short":
            await self.page.click("button:has-text('Short')", timeout=10000)
            self.order_definition["position_type"] = "short"
        else:
            raise Exception("Invalid position type provided. Choose 'long' or 'short'.")
```
【F:jupiter_core/jupiter_perps_flow.py†L22-L42】

Order types are toggled similarly:

```python
    def select_order_type(self, order_type: str):
        logger.debug("Selecting order type: %s", order_type)
        if order_type.lower() == "market":
            self.page.click("button:has-text('Market')", timeout=10000)
            self.order_definition["order_type"] = "market"
        elif order_type.lower() == "limit":
            self.page.click("button:has-text('Limit')", timeout=10000)
            self.order_definition["order_type"] = "limit"
        else:
            raise Exception("Invalid order type provided. Choose 'market' or 'limit'.")
```
【F:jupiter_core/jupiter_perps_flow.py†L44-L64】

### 🖥️ Console and Step Modules
`jupiter_auto_console.py` exposes an interactive menu that runs step functions from `jupiter_perps_steps`:

```python
STEPS = [
    ("🔗 Connect Wallet", steps_module.connect_wallet),
    ("🔓 Unlock Wallet", steps_module.unlock_wallet),
    ("📊 Select Position Type", steps_module.select_position_type),
    ("📦 Select Order Asset", steps_module.select_order_asset),
    ("📈 Select Order Type", steps_module.select_order_type),
    ("🎯 Place TP/SL Limit Order", steps_module.place_tp_sl_limit_order),
    ("🧹 Dump Visible Buttons", steps_module.dump_visible_buttons),
]
```
【F:jupiter_core/jupiter_auto_console.py†L12-L20】

Each step calls into the engine to perform actions. Example step implementations:

```python
async def connect_wallet(engine):
    await engine.pm.connect_wallet(dapp_url=engine.dapp_url, phantom_password=engine.phantom_password)

async def select_position_type(engine):
    choice = Prompt.ask("📊 Choose position type", choices=["long", "short"], default="long")
    await engine.jp.select_position_type(choice)
```
【F:jupiter_core/jupiter_perps_steps.py†L3-L16】

---

### ✅ Design Notes
- The Phantom browser extension is bundled in `phantom_wallet/` for offline automation.
- `JupiterEngineCore` can be used as an async context manager to ensure proper cleanup.
- Step modules are easily extended by adding new `auto_*.py` files within the package.
