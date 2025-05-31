# 🚀 Jupiter Auto Engine Specification

> Version: `v0.1`
> Author: `BuildOps 🛠️`
> Scope: Modular automation engine for orchestrating Phantom wallet workflows, Jupiter interactions, and order lifecycle automation.

---

## 📦 Objective
The Jupiter Auto Engine is a modular automation layer designed to programmatically execute finite steps in a structured sequence. It mirrors the design of the Cyclone orchestration engine, enabling reusability, testability, and eventual front-end integration.

It supports:

- Wallet connection and approval via Phantom
- Interaction with Jupiter dApps (e.g., perps)
- Modular execution via CLI or API
- Finite step execution (cookie-cutter additions)

## 📂 Directory Layout
```txt
jupiter_core/
├── auto_engine/
│   ├── jupiter_auto_engine.py         # 🎯 Orchestration layer
│   ├── jupiter_wallet_service.py      # 👛 Phantom wallet steps
│   ├── jupiter_position_service.py    # 📈 Position setup helpers
│   ├── jupiter_order_service.py       # 💱 Order management
│   └── step_registry.py               # 📋 Maps step names to callable methods
├── phantom_manager.py                 # Phantom browser integration
├── jupiter_perps_flow.py              # Existing dApp interaction helpers
├── console_logger.py                  # Enhanced colored logging
├── jupiter_console.py                 # 🎛️ CLI test console (like cyclone_app.py)
```

### 🧠 `JupiterAutoEngine`
```python
JupiterAutoEngine(extension_path, dapp_url, phantom_password=None, headless=False)
```
- Sets up `PhantomManager` and `JupiterPerpsFlow`.
- Uses `ConsoleLogger` for all logging.
- Central entry point for step execution.

### 🧱 `run_cycle()`
```python
async def run_cycle(self, steps: Optional[List[str]] = None) -> None:
```
- Accepts a list of steps to run.
- Maps step names to method calls via an internal registry.
- Emits emoji-rich log statements before and after each step.
- Catches and logs terminal errors per step.

### 🔁 Example Execution Steps
| Step Name | Description | Method Name |
|-----------|-------------|-------------|
| `connect_wallet` | Opens Phantom popup and connects wallet | `step_connect_wallet` |
| `unlock_wallet` | Unlocks Phantom via password input | `step_unlock_wallet` |
| `set_position_type` | Selects long or short | `step_set_position_type` |
| `set_payment_asset` | Sets asset for margin/collateral | `step_set_payment_asset` |
| `set_leverage` | Adjusts slider to match input leverage | `step_set_leverage` |
| `set_position_size` | Sets size field | `step_set_position_size` |
| `approve_transaction` | Confirms tx in Phantom | `step_approve_transaction` |
| `capture_order_payload` | Waits for specific POST | `step_capture_order_payload` |

Each `step_*` method is:

- Self-contained
- Logged before and after
- Callable from the CLI console or frontend runner

### 🖥️ CLI Console: `jupiter_console.py`
- Text-based UI using `rich`.
- Step menu for selecting and executing steps.
- Supports batch or interactive flow.
- Uses `JupiterAutoEngine` under the hood.

### 🔗 Front-End Integration
- Every method in `JupiterAutoEngine` is frontend-callable.
- Plan to expose a REST or WebSocket interface.
- Return value should contain structured logs, status flags, and optional payloads.

### ✅ Design Principles
- **Composable**: Each step should be isolated and testable.
- **Traceable**: Use `ConsoleLogger` for consistent logging.
- **Extendable**: New steps are added via `step_registry` or engine methods.
- **Robust**: Errors log a terminal event but don’t crash unless critical.

### 📌 Initial Focus
- End-to-end execution of wallet connection and Phantom transaction flow.
- Build out step templates as new needs arise (e.g., funding, liquidation monitoring).

### 📅 Future Additions
- Position close flow
- Multi-wallet sync loop
- Strategy injectors (e.g., DCA, hedge pairs)
- Async job queue for scheduled runs

The Jupiter Auto Engine is the execution layer for your automated trading brain. It replaces brittle scripts with orchestrated flows and centralized logging.
