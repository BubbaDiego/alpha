# 🛒 Order Core Specification

> Version: `v1.0`
> Author: `CoreOps 🥷`
> Scope: Wallet automation and order sequencing for Jupiter trades.

---

## 📂 Module Structure
```txt
order_core/
├── order_core.py       # 🚀 High level orchestrator
├── order_engine.py     # ⚙️  Browser automation steps
├── order_sequencer.py  # ⛓️  Groups engine actions
├── order_broker.py     # 🏦 Broker payload helpers
├── order_model.py      # 📄 Dataclass representation
├── agent_phantom.py    # 👻 Phantom wallet helper
├── agent_solflare.py   # 🔥 Solflare wallet helper
```

### 🚀 `OrderCore`
Central controller that configures the wallet agent, broker, engine, and sequencer.

```python
class OrderCore:
```
- `__init__(data_locker, config_loader, wallet_type="phantom")` – store the loader and selected wallet type.
- `launch(extension_path, headless=False, phantom_password=None, solflare_password=None)` – boot browser wallet and build broker/engine/sequencer.【F:order_core/order_core.py†L35-L60】
- `sync_wallet(dapp_url)` – navigate to the dApp and trigger wallet connection.【F:order_core/order_core.py†L62-L66】
- `run_order_flow(**kwargs)` – run the full open position sequence and return an `OrderModel`.【F:order_core/order_core.py†L68-L74】
- `run_tp_sl_flow(input_mint, output_mint, in_amount, out_amount, private_key)` – convenience wrapper for TP/SL orders.【F:order_core/order_core.py†L75-L85】
- `get_order_summary()` – return the most recent `OrderModel` from the engine.【F:order_core/order_core.py†L87-L91】

### ⚙️ `OrderEngine`
Low level actions that manipulate the DEX UI via Playwright.

- `connect_wallet(dapp_url)` – delegates to the wallet agent.【F:order_core/order_engine.py†L12-L13】
- `select_position_type(kind)` – click Long/Short button.【F:order_core/order_engine.py†L15-L17】
- `select_order_type(kind)` – choose market or limit.【F:order_core/order_engine.py†L19-L21】
- `select_asset(symbol)` – select asset button on the page.【F:order_core/order_engine.py†L23-L25】
- `select_collateral_asset(symbol="SOL")` – record collateral asset choice.【F:order_core/order_engine.py†L27-L28】
- `set_position_size(size)` – fill size input and cache value.【F:order_core/order_engine.py†L30-L32】
- `set_leverage(leverage)` – click "+" the required number of times, enforcing minimum 1.1x.【F:order_core/order_engine.py†L34-L48】
- `confirm_order()` – click the submit button found via JS.【F:order_core/order_engine.py†L50-L64】
- `confirm_wallet_transaction()` – confirm the wallet popup.【F:order_core/order_engine.py†L66-L70】
- `place_tp_sl_limit_order(input_mint, output_mint, in_amount, out_amount, private_key)` – call helper to send a TP/SL trigger.【F:order_core/order_engine.py†L72-L82】
- `get_order()` – build an `OrderModel` from the stored definition.【F:order_core/order_engine.py†L84-L101】

### ⛓️ `OrderSequencer`
Composite flows built from engine steps.

- `run_full_open_position_flow(asset="SOL", kind="long", size="0.1", leverage="5x", order_type="market", collateral_asset="SOL")` – sequence to create and confirm a position.【F:order_core/order_sequencer.py†L15-L31】
- `run_tp_sl_flow(input_mint, output_mint, in_amount, out_amount, private_key=None)` – validate key and place a trigger order.【F:order_core/order_sequencer.py†L33-L50】
- `run_modify_position_flow(kind, new_leverage)` – placeholder for future modification logic.【F:order_core/order_sequencer.py†L52-L58】

### 🏦 `OrderBroker`
Abstract interface for broker logic. `JupiterBroker` implements simple payload preparation.

- `prepare_order(order_definition)` – add defaults like fees and entry price.【F:order_core/order_broker.py†L20-L27】
- `enrich_order(payload)` – placeholder for quote/slippage enrichment.【F:order_core/order_broker.py†L28-L33】
- `validate_payload(payload)` – ensure required fields are present.【F:order_core/order_broker.py†L34-L37】

### 👻 `PhantomAgent` & 🔥 `SolflareAgent`
Automated wallet controllers built with Playwright.

- Both agents launch a persistent Chromium context with the extension loaded and expose methods to unlock, connect to a dApp, and confirm transactions.
- Example unlock and connect routine for PhantomAgent shows waiting for selectors and clicking the popup buttons.【F:order_core/agent_phantom.py†L51-L79】
- SolflareAgent includes extra helpers like `confirm_connect_modal` to toggle auto‑connect and auto‑approve options before clicking connect.【F:order_core/agent_solflare.py†L74-L104】

### 📄 `OrderModel`
Dataclass capturing the normalized order details.

```python
@dataclass
class OrderModel:
```
Fields include `id`, `asset`, `position_type`, `collateral_asset`, `leverage`, `position_size`, `order_type`, `status`, plus optional `entry_price` and `fees`.【F:order_core/order_model.py†L7-L23】

### 🖼️ Order Factory Template
`templates/order_factory.html` provides a simplified two-panel layout for controlling OrderCore. It presents action controls alongside a live data sidebar and honors the global layout mode toggle.【F:templates/order_factory.html†L29-L41】

### 🧩 Integrations
- Intended for use alongside `Cyclone` or standalone console apps.
- Relies on Playwright; actual network interactions with Jupiter are planned but not yet implemented.

### ✅ Design Notes
- Mirrors the architecture of other cores with clear separation between engine, sequencer, broker, and agents.
- Browser automation keeps UI logic out of business code.
- Future expansions can extend `OrderBroker` for other DEXs or add new wallet agents.

