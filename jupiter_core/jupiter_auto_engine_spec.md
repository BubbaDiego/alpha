# 🚀 Jupiter Core Step Engine Specification

> Version: `v1.1`
> Author: `BuildOps 🛠️`
> Scope: Modular step engine for Phantom wallet automation and Jupiter interactions.

---

## 📦 Objective
The Jupiter Core step engine executes discrete async steps that automate Phantom wallet flows and Jupiter dApp interactions. Each step lives in its own module and receives a `JupiterEngineCore` instance for browser automation.

It supports:

- Modular execution from the CLI or future API
- Wallet connection and approval via Phantom
- Interaction with Jupiter dApps (e.g., perps)
- Easy addition of new step modules

## 📂 Directory Layout
```txt
jupiter_core/
├── engine/
│   └── jupiter_engine_core.py    # Async engine wrapper
├── steps/
│   ├── auto_connect_wallet.py    # Example step module
│   ├── auto_unlock_wallet.py
│   └── auto_set_position_type.py
├── jupiter_modular_console.py    # Rich CLI for running steps
├── phantom_manager.py            # Playwright integration
├── jupiter_perps_flow.py         # Jupiter UI helpers
```

### 🧠 `JupiterEngineCore`
```python
async with JupiterEngineCore(extension_path, dapp_url, phantom_password=None, headless=False) as engine:
    ...
```
- Launches Playwright with `PhantomManager`.
- Exposes `engine.pm` and `engine.jp` for step modules.
- Can be used as an async context manager via `launch()` and `close()`.

### 🔗 Step Modules
- Located under `jupiter_core/steps`.
- Named `auto_<name>.py` and define `async def run(engine)`.
- Use `engine.pm` and `engine.jp` to drive wallet or dApp actions.

### 🖥️ CLI Console: `jupiter_modular_console.py`
- Scans the `steps` directory and presents a menu.
- Selected steps run inside the same browser session.
- Demonstrates how the step engine can be driven interactively.

### 🔗 Front-End Integration
- Step modules can be triggered from a console, API, or front-end.
- Future versions may expose a REST or WebSocket interface.
- Each step should return structured logs and optional payloads.

### ✅ Design Principles
- **Composable**: Each step should be isolated and testable.
- **Traceable**: Use `ConsoleLogger` for consistent logging.
- **Extendable**: New steps are added by dropping modules in the `steps` folder.
- **Robust**: Errors log a terminal event but don’t crash unless critical.

### 📌 Initial Focus
- End-to-end execution of wallet connection and Phantom transaction flow.
- Build out step templates as new needs arise (e.g., funding, liquidation monitoring).

### 📅 Future Additions
- Position close flow
- Multi-wallet sync loop
- Strategy injectors (e.g., DCA, hedge pairs)
- Async job queue for scheduled runs

The Jupiter Core step engine is the execution layer for your automated trading brain. It replaces brittle scripts with modular flows and centralized logging.
