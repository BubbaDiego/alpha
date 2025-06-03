# System Specifications Index

This repository contains multiple subsystems that make up the overall trading and monitoring platform.  Each module has its own specification document with details on structure and responsibilities. This index provides a high level summary and links to the individual specs.

## Modules

### Cyclone
The Cyclone module drives workflow orchestration and alert management. It processes market updates, evaluates portfolio risk and positions, generates alerts, and coordinates hedging logic.
For a focused look at the main engine see th[trader_factory.html](templates/trader_factory.html)e [Cyclone Core specification](cyclone/cyclone_core_spec.md).

### Positions
The [Positions module](positions/position_module_spec.md) manages trading positions. It handles enrichment of positions with risk metrics, synchronization with external services, grouping for hedge analysis, and database persistence.

### Alerts
The [Alert module](alert_core/alert_module_spec.md) defines the lifecycle for alerts. It evaluates alert conditions, stores alert data, enriches values, and routes notifications.

### Portfolio
The [Portfolio position module](portfolio/position_module_spec.md) focuses on managing and updating position data within the portfolio. It exposes API endpoints, records snapshots, and triggers alert re-evaluation when positions change.

### Data
The [Sonic Data module](data/sonic_data_module_spec.md) defines the core data models and the DataLocker database layer used across the system. It provides persistence, schema management, and overall data integrity enforcement.

### Calculation Core
The [Calculation Core module](calc_core/calculation_module_spec.md) houses risk calculations and hedge utilities. It exposes pure math services, loads modifier weights, updates position metrics, and groups hedges for analysis.

### Hedge Core
The [Hedge Core module](hedge_core/hedge_core_module_spec.md) links long and short positions into hedge groups and aggregates their metrics.

### Monitor Core
The [Monitor module](monitor/monitor_module_spec.md) drives periodic tasks and health checks. It registers individual monitors and exposes CLI and API entrypoints for running them.

### Wallets
The [Wallet Core specification](wallets/wallet_core_spec.md) outlines wallet operations and blockchain helpers. The [Jupiter API spec](wallets/jupiter_api_spec.md) describes how wallets interact with Jupiter Perps for managing collateral.

### Auto Core
The [Auto Core module](auto_core/auto_core_module_spec.md) automates collateral actions in the Jupiter UI using Playwright and Phantom.

### GPT Input Format
The [GPT Input specification](gpt_input_spec.md) details the JSON bundle used to send portfolio and alert context to GPT for analysis.

### GPT Core
The [GPT Core specification](gpt/gpt_core_spec.md) describes the modules and chat UI for OpenAI integration.

### Oracle Core
The [Oracle Core specification](oracle_core/oracle_core_spec.md) explains the strategy and persona system used to build GPT prompts.

### Trader Core
The [Trader Core specification](trader_core/trader_core_spec.md) outlines trader creation, enrichment, and persistence services.

---

Each linked specification contains more detailed design notes, functional requirements, and example workflows.
\n---\n
# File: alert_core/alert_module_spec.md
# 🧠 Alert Module Specification

> Version: `v1.0`  
> Author: `CoreOps 🥷`  
> Scope: Core + Service + DataLayer architecture for managing alert lifecycle.

---

## 📂 Module Structure

```txt
alerts/
├── alert_core.py               # 🔧 Main orchestrator
├── alert_store.py              # 💾 DB access (formerly repository)
├── alert_enrichment_service.py # 🧠 Adds evaluated_value
├── alert_evaluation_service.py # 📊 Determines alert level
├── alert_utils.py              # 🧰 Normalizers / aliases
├── threshold_service.py        # 🛡️ CRUD for alert thresholds
🔧 AlertCore
Purpose
Central orchestrator for alert creation, enrichment, evaluation, and lifecycle ops.

Constructor
python
Copy
Edit
AlertCore(data_locker, config_loader)
data_locker: reference to DataLocker

config_loader: lambda returning config dict (alert_thresholds.json)

Methods
async create_alert(alert_dict: dict) → bool
Creates an alert via AlertStore, handles error logging.

async evaluate_alert(alert: Alert) → Alert
Enriches the alert

Evaluates it

Updates its evaluated_value and level in DB

async evaluate_all_alerts() → List[Alert]
Evaluates all alerts in the system. Runs enrich → evaluate → update.

async process_alerts()
Runs a full pass of enrich + evaluate across all alerts, no notify.

async enrich_all_alerts() → List[Alert]
Enriches all active alerts with latest data (without evaluation).

async update_evaluated_values()
Only updates evaluated_value (no level or notify). Useful for charts/analytics.

async create_portfolio_alerts()
Auto-generates portfolio alerts based on alert config:

Uses "high" or fallback "medium"/"low"

alert_class = "Portfolio"

async create_position_alerts()
Same logic as above, but:

Iterates all positions

Sets position_reference_id

alert_class = "Position"

async create_all_alerts()
Calls both create_portfolio_alerts() and create_position_alerts() in sequence.

clear_stale_alerts()
Deletes alerts with position_reference_id not found in current position set.

🧠 AlertEnrichmentService
Purpose
Adds evaluated_value to an alert based on live system metrics (e.g. portfolio size, position heat index)

Constructor
python
Copy
Edit
AlertEnrichmentService(data_locker)
Methods
async enrich(alert: Alert) → Alert
Dispatches to appropriate _enrich_* method based on alert_class

async enrich_all(alerts: List[Alert]) → List[Alert]
Runs enrich() concurrently across all alerts

_enrich_portfolio(alert: Alert) → Alert
Uses get_dashboard_context()

Evaluates metrics from totals

_enrich_position(alert: Alert) → Alert
Uses get_position_by_reference_id()

Computes based on per-position fields

📊 AlertEvaluationService
Purpose
Computes alert level based on evaluated_value vs thresholds

Constructor
python
Copy
Edit
AlertEvaluationService(threshold_service: ThresholdService)
threshold_service: helper for DB-backed threshold lookups

Methods
evaluate(alert: Alert) → Alert
Routes to correct evaluator based on alert class.

_evaluate_portfolio(alert)
Matches description to config key

Applies fuzzy key logic

Returns level based on thresholds

_evaluate_position(alert)
Uses "heatindex", "travel_percent" etc.

Uses alert.asset_type and alert type to locate correct range

update_alert_evaluated_value(alert_id, value)
Updates evaluated_value in the DB

update_alert_level(alert_id, level)
Updates level field in DB

inject_repo(AlertStore)
Optional: injects repo into evaluator to support updates

💾 AlertStore
Purpose
CRUD interface to the alerts table

Constructor
python
Copy
Edit
AlertStore(data_locker)
Methods
create_alert(alert_dict) → bool
Normalizes enum values (e.g. Condition, AlertType)

Injects starting_value if needed

Calls initialize_alert_data() for safe defaults

Inserts into alerts

get_alerts() → List[dict]
SELECT * from alerts

Ordered by created_at DESC

get_all_alerts() → List[dict]
Alias for get_alerts()

get_active_alerts() → List[Alert]
Filters status == "Active"

Ensures safe level and starting_value

Parses into Alert model

delete_alert(alert_id: str)
Deletes a single alert

initialize_alert_data(alert_dict: dict) → dict
Injects:

id, created_at

Default values for counter, status, etc.

Safe fallbacks for alert fields

🧰 AlertUtils (select methods)
Method	Purpose
normalize_alert_type(val)	Converts str → AlertType enum
normalize_condition(val)	Converts str → Condition
normalize_notification_type(val)	Same
get_dashboard_context()	Used in enrichment

🔧 Alert Config (alert_thresholds.json)
Format:
json
Copy
Edit
{
  "alert_ranges": {
    "total_value": {
      "low": 10000,
      "medium": 25000,
      "high": 50000
    },
    "heat_index": {
      "low": 5,
      "medium": 25,
      "high": 50
    }
  }
}
Consumed by:
AlertEvaluationService thresholds

AlertCore.create_portfolio_alerts() + create_position_alerts()

🧩 Integrations
Module	Consumes AlertCore
cyclone_engine.py	Yes
cyclone_console_app.py	Yes
position_core	Only for alerts on positions (optional)
api routes (future)	Can expose alert APIs via alert_core

✅ Lifecycle Flow
Create → via create_alert() or create_portfolio_alerts()

Enrich → evaluated_value injected

Evaluate → level assigned

Update → values stored in DB

Notify (optional) → future enhancement

Clear → clear_stale_alerts() removes broken links

🧠 Design Highlights
Fully async where applicable

Structured logging via ConsoleLogger

Core handles orchestration

Services are logic-pure

Data layer is read/write only\n---\n
# File: calc_core/calculation_module_spec.md
# 🧮 Calculation Core Specification

> Version: `v1.0`
> Author: `CoreOps 🥷`
> Scope: Risk metric calculations, aggregation utilities, and hedge grouping.

---

## 📂 Module Structure

```txt
calc_core/
├── calculation_core.py  # 🧮 Loads modifiers, updates DB fields, aggregates totals
├── calc_services.py     # ⚙️ Pure math utilities for leverage and risk metrics
├── hedge_manager.py     # 🌿 Groups positions into hedges
```

### 🧮 CalculationCore
Purpose
Central orchestrator for risk calculations and DB updates.

Constructor
```python
CalculationCore(data_locker)
```
`data_locker`: DataLocker instance for database access.

Methods
- `get_heat_index(position: dict) -> float` – composite risk index via CalcServices.
- `get_travel_percent(position_type, entry_price, current_price, liquidation_price)` – wrapper over CalcServices.
- `aggregate_positions_and_update(positions: list, db_path: str) -> list` – updates DB with travel %, liquidation distance, value, leverage, and heat index.
- `set_modifier(key: str, value: float)` – persist heat index weighting factors.
- `export_modifiers() -> str` – export modifiers as JSON.
- `import_modifiers(json_data: str)` – import and apply modifier values.
- `calculate_totals(positions: list) -> dict` – return aggregated totals via CalcServices.

### ⚙️ CalcServices
Purpose
Collection of pure functions for risk and position metrics.

Key Methods
- `calculate_composite_risk_index(position: dict) -> Optional[float>`
- `calculate_value(position) -> float`
- `calculate_leverage(size: float, collateral: float) -> float`
- `calculate_travel_percent(position_type, entry_price, current_price, liquidation_price) -> float`
- `calculate_liquid_distance(current_price, liquidation_price) -> float`
- `calculate_heat_index(position: dict) -> Optional[float>`
- `calculate_totals(positions: List[dict]) -> dict`
- `apply_minimum_risk_floor(risk_index, floor=5.0)`
- `get_color(value: float, metric: str) -> str`

### 🌿 HedgeManager
Purpose
Detects and groups hedges from position sets.

Highlights
- `build_hedges()` forms `Hedge` objects from positions sharing `hedge_buddy_id`.
- `find_hedges(db_path)` scans the database for long/short pairs and assigns hedge IDs.
- `clear_hedge_data(db_path)` removes hedge associations in bulk.
- `get_hedges()` returns the computed hedge list.

🧩 Integrations
- `PositionCore` uses `CalculationCore` for enrichment and portfolio snapshots.
- `Cyclone` engine can trigger `HedgeManager.find_hedges()` during risk evaluation cycles.

✅ Design Notes
- Calculations are logged via `ConsoleLogger` for transparency.
- Modifier weights allow runtime tuning of risk formulas without redeploying code.
- CalcServices is stateless and easily unit tested.
\n---\n
# File: cyclone/cyclone_core_spec.md
# 🌪️ Cyclone Core Specification

> Version: `v1.0`
> Author: `CoreOps 🥷`
> Scope: Orchestration engine for market updates, position enrichment, alert creation, hedge linkage, and reporting.

---

## 📂 Module Structure
```txt
cyclone/
├── cyclone_engine.py          # 🌪️ Cyclone class and run_cycle entry point
├── cyclone_alert_service.py   # 🚨 Generates and evaluates alerts
├── cyclone_position_service.py# 📊 Position operations and enrichment
├── cyclone_portfolio_service.py # 📈 Portfolio alert helpers
├── cyclone_hedge_service.py   # 🔗 Hedge detection wrapper
├── cyclone_wallet_service.py  # 👛 Wallet management utilities
├── cyclone_report_generator.py# 📝 HTML report builder
├── cyclone_console/           # 🎛️ Rich CLI interface
├── cyclone_bp.py              # 🌐 Flask Blueprint endpoints
```

## 🌪️ `Cyclone` Class
Central orchestrator defined in `cyclone_engine.py`.

### Constructor
```python
Cyclone(monitor_core, poll_interval=60)
```
- Initializes a shared `DataLocker` instance.
- Creates `PositionCore`, `AlertCore`, `PriceSyncService`, and helper services.
- Configures the central logger via `configure_cyclone_console_log()`.

### Key Methods
- `async run_cycle(steps=None)` – runs a sequence of operations such as price updates, position enrichment, hedge linking, and alert evaluation.
- `async run_market_updates()` – fetches latest prices using `PriceSyncService`.
- `async run_enrich_positions()` – enriches all positions via `PositionCore`.
- `async run_create_position_alerts()` – generates position level alerts.
- `async run_create_portfolio_alerts()` – generates portfolio level alerts.
- `async run_alert_evaluation()` – evaluates alert levels after enrichment.
- `async run_link_hedges()` – detects hedge pairs using `CycloneHedgeService`.
- `async run_cleanse_ids()` – clears stale alerts from the datastore.
- `async run_update_hedges()` – refreshes hedge groups after linking.

The default cycle executes steps in the following order:
`update_operations`, `market_updates`, `check_jupiter_for_updates`,
`enrich_positions`, `enrich_alerts`, `update_evaluated_value`,
`create_market_alerts`, `create_portfolio_alerts`, `create_position_alerts`,
`create_global_alerts`, `evaluate_alerts`, `cleanse_ids`, `link_hedges`,
`update_hedges`.

Each method logs progress with emojis and delegates to the appropriate service or core module.

## 🧩 Integrations
- **DataLocker** – provides persistence for alerts, prices, positions, and system variables.
- **AlertCore** – all alert creation and evaluation flows.
- **PositionCore** – position synchronization and enrichment.
- **MonitorCore** – optional monitoring callbacks during `run_cycle`.
- **Flask API** – `cyclone_bp.py` exposes HTTP endpoints that call into the same run methods.
- **Console** – `cyclone_console` offers an interactive menu using the `rich` library.

## ✅ Design Notes
- Steps are asynchronous and can be executed individually or as a full cycle.
- Centralized logging tags each message with the Cyclone source for clarity.
- Error handling in `run_cycle` emits "death" events through `SystemCore` when a step fails fatally.
- The architecture keeps services thin so logic is reusable in both CLI and API contexts.

\n---\n
# File: data/sonic_data_module_spec.md
Data Module / Subsystem Specification
This document provides a comprehensive specification for the Data Module / Subsystem, which is responsible for managing the core data structures and database interactions in your application. It comprises two main components:

Data Models (models.py): Defines the core entities used in the system.

DataLocker (data_locker.py): Manages SQLite database interactions including CRUD operations and system state management.

1. Overview
The Data Module / Subsystem is designed to:

Represent Trading Data: Capture details for prices, alerts, trading positions, hedges, crypto wallets, and brokers.

Manage Persistence: Store and retrieve data using SQLite with a well-defined schema.

Ensure Data Integrity: Enforce validations and constraints on key fields.

Support System Operations: Track system variables (such as update times and strategy performance) and portfolio snapshots.

2. Data Model Definitions
The data models are defined in models.py and represent the core entities of the system. Each model encapsulates both the data structure and validation logic.

2.1 Enumerations
Several enumerations standardize the allowed values across the system:

AssetType:

BTC, ETH, SOL, OTHER

Purpose: Classify different asset types (with support for future generic asset types).

SourceType:

AUTO, MANUAL, IMPORT, COINGECKO, COINMARKETCAP, COINPAPRIKA, BINANCE

Purpose: Identify the origin of the price data.

Status:

ACTIVE, SILENCED, LIQUIDATED, INACTIVE

Purpose: Reflect the current state of alerts and positions.

AlertLevel:

NORMAL, LOW, MEDIUM, HIGH

Purpose: Prioritize or grade alerts based on urgency.

AlertType:

PRICE_THRESHOLD, DELTA_CHANGE, TRAVEL_PERCENT_LIQUID, TIME, PROFIT, HEAT_INDEX

Purpose: Specify different types of alerts for monitoring various conditions.

AlertClass:

SYSTEM, MARKET, POSITION

Purpose: Categorize alerts to determine their context.

NotificationType:

EMAIL, SMS, ACTION

Purpose: Define how alerts should be communicated.

2.2 Data Classes
Price
Purpose: Represents the pricing details for an asset.

Key Fields:

id: Unique identifier.

asset_type: Type of asset (e.g., BTC, ETH).

current_price: Must be > 0.

previous_price: Must be ≥ 0.

last_update_time: Timestamp for the current price.

previous_update_time: Optional timestamp; must be ≤ last_update_time if set.

source: Origin of the price data.

Validations:

Enforces that the current price is greater than zero.

Ensures chronological order for update times.

Alert
Purpose: Configures monitoring alerts for various thresholds.

Key Fields:

id: Unique identifier.

alert_type: The type of alert (e.g., PRICE_THRESHOLD).

alert_class: Derived based on the alert type.

trigger_value: The value that triggers the alert.

notification_type: How the alert is delivered.

last_triggered: Optional timestamp when the alert was last activated.

status: Current alert status.

frequency: How often the alert can trigger.

counter: Tracks alert occurrences.

liquidation_distance, travel_percent, liquidation_price: Numeric fields relevant to risk/position management.

notes, description: Freeform fields for additional context.

position_reference_id: Links to a related position.

level: Priority level of the alert.

evaluated_value: Computed value during evaluation.

Processing:

Normalizes the alert_type (e.g., converts "PRICETHRESHOLD" to "PRICE_THRESHOLD").

Sets default values via an initialization function.

Position
Purpose: Represents a trading position in an asset.

Key Fields:

id: Unique identifier (auto-generated if not provided).

asset_type: Type of asset (default to a generic type if not specified).

position_type: Specifies the nature of the position (e.g., LONG).

entry_price, liquidation_price: Price levels defining the position.

travel_percent: Must be between -11500 and 1000.

value, collateral, size, leverage: Numeric fields describing position metrics.

wallet: The wallet associated with the position.

last_updated: Timestamp of the last update.

alert_reference_id: Optional link to an alert.

hedge_buddy_id: Optional field for hedge grouping.

current_price: Optional field for current market price.

liquidation_distance: Risk measurement.

heat_index, current_heat_index: Fields for market sentiment metrics.

pnl_after_fees_usd: Net profit/loss after fees.

Validations:

Ensures that travel_percent falls within the specified range.

Hedge
Purpose: Aggregates multiple positions to form a hedge.

Key Fields:

id: Unique identifier.

positions: List of associated position IDs.

total_long_size, total_short_size: Aggregated sizes.

long_heat_index, short_heat_index, total_heat_index: Risk/market sentiment metrics.

created_at, updated_at: Timestamps for tracking hedge lifecycle.

notes: Optional descriptive field.

CryptoWallet
Purpose: Represents a crypto wallet.

Key Fields:

name: Wallet identifier.

public_address: Public blockchain address.

private_address: (For development use only) Private key.

image_path: Visual identifier (URL/path).

balance: Total balance (in USD or another currency).

Broker
Purpose: Represents a trading broker or platform.

Key Fields:

name: Broker name.

image_path: Visual branding.

web_address: URL to the broker’s website.

total_holding: Total asset holding managed by the broker.

3. Database Schema & DataLocker (data_locker.py)
The DataLocker class handles all interactions with a SQLite database. It encapsulates database initialization, CRUD operations, and system state management.

3.1 Database Initialization
When an instance of DataLocker is created, it checks for the existence of the necessary tables and creates them if they do not exist. The schema includes:

system_vars

Fields:

id

last_update_time_positions

last_update_positions_source

last_update_time_prices

last_update_prices_source

last_update_time_jupiter

last_update_jupiter_source

total_brokerage_balance

total_wallet_balance

total_balance

strategy_start_value

strategy_description

Purpose: Stores system-level variables such as update timestamps, balance aggregates, and strategy performance data.

prices

Fields:

id

asset_type

current_price

previous_price

last_update_time

previous_update_time

source

Purpose: Stores asset price snapshots.

positions

Fields:

id

asset_type

position_type

entry_price

liquidation_price

travel_percent

value

collateral

size

leverage

wallet_name

last_updated

alert_reference_id

hedge_buddy_id

current_price

liquidation_distance

heat_index

current_heat_index

pnl_after_fees_usd

Purpose: Stores details of each trading position.

alerts

Fields:

id

created_at

alert_type

alert_class

asset_type

trigger_value

condition

notification_type

level

last_triggered

status

frequency

counter

liquidation_distance

travel_percent

liquidation_price

notes

description

position_reference_id

evaluated_value

Purpose: Records alert configurations and tracks their status.

alert_ledger

Fields:

id

alert_id

modified_by

reason

before_value

after_value

timestamp

Purpose: Maintains a history of modifications to alerts.

brokers

Fields:

name

image_path

web_address

total_holding

Purpose: Stores broker-related information.

wallets

Fields:

name

public_address

private_address

image_path

balance

Purpose: Stores crypto wallet information.

portfolio_entries

Fields:

id

snapshot_time

total_value

Purpose: Records snapshots of the overall portfolio value over time.

positions_totals_history

Fields:

id

snapshot_time

total_size

total_value

total_collateral

avg_leverage

avg_travel_percent

avg_heat_index

Purpose: Captures historical aggregates of positions for trend analysis.

3.2 DataLocker Class Overview
Singleton Pattern:
The class implements a singleton design via the get_instance() method to ensure only one database connection is active at any time.

Connection Management:

Uses SQLite with check_same_thread=False to allow multi-threaded access.

Initializes the connection in WAL mode to enhance performance and concurrency.

Error Handling & Logging:

Comprehensive error handling for all CRUD operations.

Uses Python’s logging framework to record both debug and error messages.

3.3 Core Methods
Price Operations
insert_price(price_dict)
Inserts a new price record. If fields like id or timestamps are missing, defaults are assigned.

get_prices(asset_type=None) / read_prices()
Retrieves price records, optionally filtered by asset type.

get_latest_price(asset_type)
Fetches the most recent price record for the specified asset type.

delete_price(price_id)
Deletes a price record by its identifier.

update_price(price_id, current_price, last_update_time)
Updates the current price and update timestamp.

Alert Operations
create_alert(alert_obj)
Inserts a new alert after normalizing and initializing default fields.

get_alert(alert_id) / get_alerts()
Retrieves one or more alert records.

update_alert_conditions(alert_id, update_fields)
Updates specified fields of an alert.

update_alert_status(alert_id, new_status)
Changes the status of an alert.

delete_alert(alert_id)
Deletes an alert by its identifier.

create_alert_instance(alert_obj)
A helper method to create an alert using an object’s dictionary representation.

Position Operations
create_position(pos_dict)
Inserts a new trading position record, ensuring all required defaults are set (e.g., auto-generating an ID).

get_positions() / read_positions()
Retrieves all position records.

delete_position(position_id) / delete_all_positions()
Deletes specific or all position records.

update_position_size(position_id, new_size) / update_position(position_id, size, collateral)
Updates size and collateral values for a position.

Wallet & Broker Operations
Wallet Methods:

read_wallets(), update_wallet(wallet_name, wallet_dict), create_wallet(wallet_dict), get_wallet_by_name(wallet_name)
Purpose: Manage crypto wallet records.

Broker Methods:

create_broker(broker_dict), read_brokers()
Purpose: Manage broker-related data.

Portfolio and System Variables
Portfolio Snapshots:

add_portfolio_entry(entry), get_portfolio_entries(), record_positions_totals_snapshot(totals)
Purpose: Record and retrieve snapshots of overall portfolio value and positions.

System Variables:

set_strategy_performance_data(start_value, description), get_strategy_performance_data()

set_last_update_times(...), get_last_update_times()
Purpose: Manage update timestamps, strategy performance data, and balance aggregates.

4. Validations & Constraints
Price Validations:

current_price must be > 0.

previous_price must be ≥ 0.

previous_update_time (if provided) must not exceed last_update_time.

Position Validations:

travel_percent is strictly enforced to lie between -11500 and 1000.

Alert Normalization:

The alert type is normalized (e.g., removing spaces, converting to uppercase) to ensure consistency.

Default values are assigned if certain fields are missing.

Database Integrity:

Unique constraints are enforced on primary keys (e.g., id for prices, positions, and alerts; name for brokers and wallets).

Transactions are used to ensure atomicity of operations.

5. Additional Considerations
Logging & Debugging:
Extensive logging is built into the DataLocker to facilitate debugging and traceability of operations.

Concurrency:
By configuring SQLite in WAL mode and allowing multithreaded access (check_same_thread=False), the module supports concurrent database operations.

Configuration:
The database path is configured via a constant (DB_PATH from config_constants), allowing for flexible deployment.

Extensibility:
The system is designed to easily accommodate new data models, additional alert types, or extended functionalities (such as enhanced risk metrics or migration support).

6. Usage & Integration
Importing Models:
Use models.py to instantiate objects for prices, alerts, positions, hedges, wallets, and brokers.

Database Operations:
Use DataLocker.get_instance() to obtain a singleton instance of the DataLocker. Then, utilize the provided CRUD methods to interact with the SQLite database.

Error Handling:
Ensure to catch and log exceptions from DataLocker methods to handle any database or integrity issues gracefully.

This specification provides a detailed look at your Data Module / Subsystem, outlining the data structures, validations, and database interactions that form the backbone of your trading or monitoring system. Let me know if you need any more details or refinements, honey!










Search

Deep research


ChatGPT can make mistakes. Check important info.\n---\n
# File: hedge_core/hedge_core_module_spec.md
# 🌿 Hedge Core Specification

> Version: `v1.0`
> Author: `CoreOps 🥷`
> Scope: Grouping and managing hedges derived from position data.

---

## 📂 Module Structure

```txt
hedge_core/
├── hedge_core.py  # 🔗 Builds and links hedges
```

### 🔗 `HedgeCore`
Central orchestrator that creates, links, and fetches hedge objects.

```python
HedgeCore(data_locker)
```
- `data_locker`: instance of `DataLocker` providing DB access and helper managers.

**Key Methods**
- `update_hedges()` – orchestrates linking and building hedges from live positions.
- `build_hedges(positions=None) -> List[Hedge]` – converts position records into `Hedge` objects grouped by `hedge_buddy_id`.
- `link_hedges() -> List[list]` – scans current positions and assigns a shared UUID to long/short pairs.
- `unlink_hedges()` – clears all `hedge_buddy_id` values in the database.
- `get_modifiers(group=None) -> dict` – returns hedge/heat modifiers via `DLModifierManager`.
- `get_db_hedges() -> List[Hedge]` – retrieves persisted hedges using `DLHedgeManager`.

### 🗂️ Data Flow
1. `update_hedges()` logs the refresh, invokes `HedgeManager.find_hedges()` and builds results. 【F:hedge_core/hedge_core.py†L24-L41】
2. `build_hedges()` groups positions by `hedge_buddy_id`, aggregates sizes and heat indices, and returns a list of `Hedge` objects. 【F:hedge_core/hedge_core.py†L43-L89】
3. `link_hedges()` iterates positions grouped by `(wallet_name, asset_type)` and assigns a UUID when both long and short types are present. 【F:hedge_core/hedge_core.py†L91-L118】
4. `unlink_hedges()` performs a bulk SQL update to remove links. 【F:hedge_core/hedge_core.py†L121-L129】

### ✅ Design Notes
- All logging is handled through the shared logger injected via `core.core_imports`. 【F:hedge_core/hedge_core.py†L24-L129】
- Hedge detection relies solely on wallet/asset pairs and does not consider leverage or size weighting in this implementation.
- `get_modifiers()` provides a simple pass-through to the data layer so external callers can inspect weighting factors.
- Hedge IDs mirror the `hedge_buddy_id` used to link positions ensuring stable lookups across API calls.

\n---\n
# File: monitor/monitor_module_spec.md
# 🛰️ Monitor Core Specification

> Version: `v1.0`
> Author: `CoreOps 🥷`
> Scope: Monitor orchestrator and supporting monitors.

---

## 📂 Module Structure

```txt
monitor/
├── monitor_core.py         # 🚦 Registers and runs monitors
├── base_monitor.py         # 🔧 Shared run_cycle/ledger wrapper
├── monitor_registry.py     # 📇 Holds monitor instances
├── price_monitor.py        # 💰 Fetches prices from APIs
├── position_monitor.py     # 📈 Syncs and enriches positions
├── operations_monitor.py   # 🧪 Startup POST tests and health checks
├── latency_monitor.py      # ⏱️ External API latency checker
├── ledger_service.py       # 🧾 JSON ledger utilities
├── monitor_api.py          # 🌐 Flask API endpoints
└── sonic_monitor.py        # ❤️ Background cycle runner
```

### 🚦 MonitorCore
Central controller for executing registered monitors.

```python
MonitorCore(registry: MonitorRegistry | None = None)
```
- If `registry` is not provided, a new one is created and default monitors are registered (`PriceMonitor`, `PositionMonitor`, `OperationsMonitor`).

**Methods**
- `run_all()` – iterate and run every monitor in the registry, logging success or failure.
- `run_by_name(name)` – run a single monitor by its key if present.

### 🧩 Monitor Implementations
- **BaseMonitor** – provides `run_cycle()` wrapper that records results in the database ledger.
- **PriceMonitor** – fetches BTC/ETH/SOL prices via `MonitorService`.
- **PositionMonitor** – syncs positions from Jupiter and logs summary metrics.
- **OperationsMonitor** – runs POST tests on startup and stores results.
- **LatencyMonitor** – optional HTTP latency checker for third-party services.

### 🌐 API & Background Runner
- `monitor_api.py` exposes REST endpoints to trigger monitors individually or all at once.
- `sonic_monitor.py` runs periodic cycles using `Cyclone` and records a heartbeat in the database.

### ✅ Design Notes
- Monitors write a summary entry to the ledger table via `DataLocker.ledger`.
- Registration through `MonitorRegistry` keeps monitor setup centralized.
- Execution paths include CLI scripts, Flask API, and long‑running background loops.
\n---\n
# File: oracle_core/oracle_core_spec.md
# 🔮 Oracle Core Specification

> Version: `v1.0`
> Author: `CoreOps 🥷`
> Scope: Strategy-aware topic aggregator for GPT queries.

## 📂 Module Structure
```txt
oracle_core/
├── oracle_core.py           # Main orchestrator
├── oracle_data_service.py   # Fetch context data from DataLocker
├── strategy_manager.py      # Load strategy definitions
├── persona_manager.py       # Load persona definitions
├── alerts_topic_handler.py  # Build alerts context
├── portfolio_topic_handler.py # Build portfolio context
├── prices_topic_handler.py  # Build price context
├── system_topic_handler.py  # Build system status context
├── personas/                # Default persona JSON files
└── strategies/              # Strategy modifier JSON files
```

### 🔮 `OracleCore`
Central entry point that builds prompts and invokes the OpenAI API.

```python
class OracleCore:
    def __init__(self, data_locker):
        self.data_locker = data_locker
        if OpenAI:
            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_AI_KEY") or ""
            self.client = OpenAI(api_key=api_key) if api_key else None
        else:
            self.client = None
        self.strategy_manager = StrategyManager()
        self.persona_manager = PersonaManager()
        self.handlers: Dict[str, object] = {}
        self.register_topic_handler("portfolio", PortfolioTopicHandler(data_locker))
        self.register_topic_handler("alerts", AlertsTopicHandler(data_locker))
        self.register_topic_handler("prices", PricesTopicHandler(data_locker))
        self.register_topic_handler("system", SystemTopicHandler(data_locker))
```
【F:oracle_core/oracle_core.py†L16-L38】

`ask()` obtains context from the selected handler and optionally applies a strategy or persona before sending the prompt to GPT.

### 🎭 Personas and Strategies
`PersonaManager` loads persona JSON files that provide instructions and strategy weights. `StrategyManager` loads strategy JSON files defining modifier dictionaries. Persona weights are merged so multiple strategies can influence the final prompt.

### 🗂️ Topic Handlers
Each handler (`PortfolioTopicHandler`, `AlertsTopicHandler`, `PricesTopicHandler`, `SystemTopicHandler`) returns a small context dictionary via `OracleDataService`.

### 🛰️ Data Service
`OracleDataService` wraps `DataLocker` managers and exposes helpers:
- `fetch_portfolio()` → latest portfolio snapshot
- `fetch_alerts()` → recent alerts
- `fetch_prices()` → recent prices
- `fetch_system()` → last update timestamps

\n---\n
# File: portfolio/position_module_spec.md
Position Module/Subsystem Specification
1. Overview
The Position Module is responsible for managing trading position data throughout its lifecycle. It retrieves raw positions from persistent storage, enriches them with computed analytics (such as profit, leverage, travel percent, heat index, etc.), updates positions by integrating with external APIs (like Jupiter and dYdX), and handles deletion and archival (snapshot recording) of positions. It also supports the grouping of positions for hedge analysis and facilitates real-time updates via web endpoints.

2. Scope
Data Retrieval: Read raw position records from the database.

Data Enrichment: Compute and update metrics (profit, leverage, travel percent, heat index, liquidation distance) using defined formulas and external data (e.g., latest market prices).

Position Updates: Synchronize positions with external trading APIs (Jupiter, dYdX).

Data Persistence: Update the enriched position records back into the database and record periodic snapshots for trend analysis.

Alerts Integration: Trigger re-evaluation of alerts based on updated positions.

Web API Endpoints: Expose position-related operations (list, update, delete, trends, mobile view, etc.) via a Flask blueprint.

Hedge Analysis: Identify and group positions for potential hedging opportunities.

3. Functional Requirements
3.1 Position Retrieval and Enrichment
Get All Positions:

Retrieve raw positions via the DataLocker interface.

Enrich each position record by computing:

Profit: Based on the position size and price difference.

Leverage: Calculated as size divided by collateral.

Travel Percent: Determined using entry, current, and liquidation prices.

Liquidation Distance: The absolute difference between the current price and liquidation price.

Heat Index: A composite risk metric derived from position size, leverage, and collateral.

Update each position’s current_price field by fetching the latest market price from persistent storage.

3.2 Position Updates from External APIs
Jupiter API Integration:

Delete existing Jupiter positions (based on wallet name) prior to an update.

Fetch new position data from Jupiter’s API, map fields to the internal model, and avoid duplicates.

Update the database with new positions.

dYdX API Integration:

Retrieve positions from dYdX, format data accordingly, and insert new records if they do not already exist.

3.3 Position Modification and Deletion
Edit Position:

Allow updates to fields like size and collateral via web forms.

Delete Single Position:

Remove a position record from the database by its unique identifier.

Delete All Positions:

Provide an endpoint for bulk deletion of all position records (typically for administrative or reset purposes).

3.4 Snapshot and Trend Analysis
Record Positions Snapshot:

Aggregate key metrics (total size, value, collateral, average leverage, etc.) using CalcServices.

Persist snapshots into a history table for future trend analysis.

Trend Reporting:

Expose endpoints that allow users to view historical trends over selectable time frames (e.g., last 24 hours).

3.5 Hedge Analysis
Find Hedges:

Analyze current positions to identify potential hedges by grouping positions (long and short) by asset and wallet.

Return aggregated hedge metrics for display or further analysis.

3.6 Web API Endpoints
Positions Blueprint:

Endpoints include listing positions, detailed table views, mobile-friendly views, editing, deletion, and data APIs.

Sorting, filtering, and grouping functionalities are provided at the UI level.

SocketIO Integration:

Emit events upon position updates to notify connected clients in real time.

4. Data Model
4.1 Position Data (from models.py)
A Position record includes:

Identifiers: id (UUID), wallet_name

Asset Details: asset_type (e.g., BTC, ETH, SOL)

Trading Data: entry_price, liquidation_price, current_price

Metrics:

Travel Percent: The percentage movement from the entry toward a profit target or liquidation.

Profit/Value: Computed profit added to collateral.

Collateral & Size: Financial inputs for leverage.

Leverage: Calculated ratio (size / collateral).

Heat Index: Composite risk index.

Liquidation Distance: Absolute difference between current and liquidation prices.

Relationships:[cyclone.py](../cyclone/cyclone_engine.py)

alert_reference_id for associated alerts.

hedge_buddy_id for positions grouped in hedges.

Timestamps: last_updated

4.2 Other Models
Alert Model: For linking positions to alerts (used for re-evaluation after position updates).

Hedge Model: Represents grouped positions for hedging analysis.

Wallet Model: Stores wallet information (used for associating positions with specific wallets).

5. Interfaces and Dependencies
5.1 Internal Modules
PositionService (position_service.py):

Offers static and instance methods for retrieving, enriching, updating, and deleting positions.

CalcServices (calc_services.py):

Provides calculation logic for travel percent, heat index, leverage, and risk metrics.

DataLocker (data_locker.py):

Manages all database interactions, including reading/writing positions, prices, and snapshots.

Alerts Module:

Integrates with the AlertEvaluator to update alerts based on changes in positions.

5.2 External Dependencies
External APIs:

Jupiter API and dYdX API for fetching real-time position data.

Flask Framework:

Positions endpoints are exposed via a Flask blueprint.

SocketIO:

Real-time notifications for updates to positions.

SQLite Database:

Used as the underlying persistent storage mechanism.

6. Error Handling and Logging
Robust Exception Management:

Each method catches and logs exceptions using the built-in logger or UnifiedLogger.

API endpoints return structured JSON error messages along with appropriate HTTP status codes.

Database Transaction Safety:

Updates and deletions are wrapped in commits with rollback mechanisms on errors.

Logging:

Detailed debug logs are generated at key points (e.g., before and after enrichment, during API updates, and during database transactions) to facilitate troubleshooting.

7. Non-Functional Requirements
Performance:

The module leverages batch updates and efficient querying via SQLite. Asynchronous processing is used for API calls and heavy computations where applicable.

Extensibility:

The design allows for easy integration of additional asset types, new calculation methods, and support for more external APIs.

Maintainability:

Code is modularized into clear components (service, persistence, calculations, and web endpoints) for easier maintenance and updates.

Usability:

Exposed web interfaces (HTML views, JSON APIs) and real-time updates via SocketIO improve user experience.

Scalability:

While built on SQLite, the architecture can be scaled to other database systems with minimal modifications to the DataLocker interface.

8. Assumptions and Constraints
Singleton Pattern:

DataLocker is used as a singleton to ensure consistent database access across modules.

External Configuration:

Critical parameters (such as API keys, wallet addresses, thresholds for calculations, and logging levels) are managed via configuration files.

Data Consistency:

It is assumed that external API data is consistent and that appropriate validations (such as ensuring non-zero collateral) are enforced in calculation methods.

Thread Safety:

Database connections are managed with SQLite’s WAL mode and thread-check disablement, though caution is advised in multi-threaded environments.\n---\n
# File: positions/position_module_spec.md
# 💾 Position Module Specification

> Version: `v1.0`  
> Author: `CoreOps 🥷`  
> Scope: PositionCore + Enrichment + Sync + Hedge + Store  
> System: Cyclone Console + Engine + DL Layer

---

## 📂 Module Structure

```txt
positions/
├── position_core.py             # 🧠 Core orchestrator
├── position_store.py            # 💾 DB wrapper
├── position_enrichment_service.py # 🧬 Computes risk, value, travel, heat
├── position_sync_service.py     # 🔁 Jupiter sync (API ingestion)
├── hedge_manager.py             # 🔗 Groups hedges by size/collateral
🧠 PositionCore
Purpose
Central orchestrator for ingesting, enriching, syncing, snapshotting, and hedging position data.

Constructor
python
Copy
Edit
PositionCore(data_locker)
Accepts full DL for internal access to pricing, portfolio, system, positions, etc.

Methods
get_all_positions() → List[dict]
Loads all positions from the store
Returns raw position dictionaries

get_active_positions() → List[dict]
Returns only positions with status "ACTIVE"

create_position(pos_dict) → bool
Enriches position

Inserts into store

Logs success/failure via ConsoleLogger

delete_position(pos_id: str)
Passes through to store

Logs outcome

clear_all_positions()
Passes to store or DL

Used in reset/test cycles

record_snapshot()
Calls CalcServices.calculate_totals(...)

Delegates to DLPortfolioManager.record_snapshot(...)

Logs total size/value/collateral, averages, heat

update_positions_from_jupiter(source="console")
Wrapper to PositionSyncService.run_full_jupiter_sync()

Used in console and engine as backward-compatible API

link_hedges() → List[dict]
Uses HedgeManager.get_hedges() internally

Returns hedge objects

Logs count, groups, and validation tags

enrich_positions() → List[dict]
Similar to get_all_positions(), but logs per enrichment

Used as standalone operation in console engine cycle

🔁 PositionSyncService
Purpose
Ingests live positions from Jupiter wallets and stores them locally

Constructor
python
Copy
Edit
PositionSyncService(data_locker)
Main Method
run_full_jupiter_sync(source="console") → dict
Deletes all current positions

Calls update_jupiter_positions()

Enriches new ones

Rebuilds hedges

Records a snapshot

Updates system_vars with last sync timestamps

Logs every step

Internal Method
update_jupiter_positions() → dict
Loops through wallets

Hits Jupiter API: `${JUPITER_API_BASE}/v1/positions`

Maps and inserts valid positions

Skips failed or empty responses

Logs imported count and skips

🧬 PositionEnrichmentService
Purpose
Enriches a position with:

Leverage

Travel percent

Liquidation distance

Heat index (risk)

Constructor
python
Copy
Edit
PositionEnrichmentService(data_locker)
Method
enrich(pos_dict: dict) → dict
Uses CalcServices:

calculate_value()

calculate_leverage()

calculate_travel_percent()

calculate_liquid_distance()

calculate_composite_risk_index()

Injects market price via dl.prices.get_last_price_for(asset_type)

Logs results inline

🔗 HedgeManager
Purpose
Detects and groups hedge pairs from active positions.

Constructor
python
Copy
Edit
HedgeManager(positions: List[dict])
Methods
get_hedges() → List[dict]
Compares long/short matches across same asset

Looks at leverage, collateral size, wallet

Builds hedge candidates

Adds hedge_ratio, delta, imbalance

Logs hedge_count

clear_hedge_data()
Clears existing hedge state from file or memory

Rarely used — mostly for dev tools or CLI

💾 PositionStore
Purpose
Interacts directly with the positions table

Constructor
python
Copy
Edit
PositionStore(data_locker)
Methods
get_all() → List[dict]
Loads all positions from DB

Used by core + hedge + enrichment

get_by_id(pos_id: str) → dict
Single position lookup

insert(position: dict) → bool
Inserts fully-formed record

Expects enriched data

Injects default timestamps, logs failure reason

delete(pos_id: str)
Deletes by ID

delete_all()
Wipes table

Logs count if needed

⚙️ CalcServices (Used by Enrichment)
Method	Purpose
calculate_value()       collateral + P&L
calculate_leverage()	value ÷ collateral
calculate_travel_percent()	price deviation vs liquidation
calculate_liquid_distance()	dollar or % distance
calculate_composite_risk_index()	aggregation of leverage + travel + heat

🔐 SystemVars Touchpoints
last_update_time_positions

last_update_time_jupiter

last_update_positions_source

Set via dl.system.set_last_update_times({...}) during sync

🧠 Position Flow
Jupiter Sync
→ Fetch → parse → insert → enrich → snapshot → timestamp

Manual Create
→ Enrich → insert → log

Evaluate / Score
→ Enrich → snapshot → alertable

Hedge
→ Group positions → tag as hedge pair

View / Report
→ Enriched summary returned via get_all_positions()

🧩 Console/Engine Integration
Step	Uses
Update Positions	update_positions_from_jupiter()
Enrich Positions	enrich_positions()
Link Hedges	link_hedges()
Record Snapshot	record_snapshot()

✅ Design Philosophy
Core controls flow — no logic in UI/route

Services are single-purpose, composable

DB ops are isolated to PositionStore

ConsoleLogger used consistently for transparency

All enrichment & sync is testable end-to-end

\n---\n
# File: positions/position_core_detailed_spec.md
# Position Core Detailed Specification

## Overview

The `PositionCore` module orchestrates position management, enrichment, synchronization, and snapshotting. It relies on the `DataLocker` data layer for persistent storage and shared services.  This specification documents the behavior of `PositionCore`, its interaction with subordinate services (`PositionStore`, `PositionEnrichmentService`, `PositionSyncService`, and `HedgeManager`), and the responsibilities of the data layer components it uses.

## Module Relationships

```
PositionCore
 ├─ PositionStore             → wrappers around DataLocker.positions
 ├─ PositionEnrichmentService → uses CalculationCore and DataLocker.prices
 ├─ PositionSyncService       → fetches from Jupiter API, inserts via DataLocker
 └─ HedgeManager              → pure in‑memory hedge detection
DataLocker
 ├─ DatabaseManager           → SQLite wrapper
 ├─ DLPositionManager         → CRUD for `positions` table
 ├─ DLPortfolioManager        → records portfolio snapshots
 ├─ DLSystemDataManager       → stores system vars (update times, theme, etc.)
 └─ other managers (alerts, prices, wallets, …)
```

`PositionCore` receives a `DataLocker` instance at construction and passes it to all sub‑components. Because `DataLocker` holds an open connection to the SQLite database, all position operations ultimately go through `DLPositionManager`.

## DataLocker Schema

The relevant schema for positions is created in `DataLocker.initialize_database()`:

```python
# data/data_locker.py
130  "positions": """
131      CREATE TABLE IF NOT EXISTS positions (
132          id TEXT PRIMARY KEY,
133          asset_type TEXT,
134          position_type TEXT,
135          entry_price REAL,
136          liquidation_price REAL,
137          travel_percent REAL,
138          value REAL,
139          collateral REAL,
140          size REAL,
141          leverage REAL,
142          wallet_name TEXT,
143          last_updated TEXT,
144          alert_reference_id TEXT,
145          hedge_buddy_id TEXT,
146          current_price REAL,
147          liquidation_distance REAL,
148          heat_index REAL,
149          current_heat_index REAL,
150          pnl_after_fees_usd REAL
151      )
"""
```

This table stores every imported or manually created position. `DLPositionManager` operates on this table.

Additional tables used by `PositionCore` workflows:

- `positions_totals_history` for snapshots (`DLPortfolioManager.record_snapshot`).
- `system_vars` where last update timestamps are kept (`DLSystemDataManager`).

## `PositionCore` Class

### Construction

```python
# positions/position_core.py
13 class PositionCore:
14     def __init__(self, data_locker):
15         self.dl = data_locker
16         self.store = PositionStore(data_locker)
17         self.enricher = PositionEnrichmentService(data_locker)
```

Upon instantiation, `PositionCore` keeps a reference to the provided `DataLocker` and initializes two helpers:

- `PositionStore` – thin wrapper over `DLPositionManager` for CRUD operations.
- `PositionEnrichmentService` – calculates leverage, travel percent, heat index, and injects live prices.

### Basic CRUD

```python
19 def get_all_positions(self):
20     return self.store.get_all_positions()

22 def get_active_positions(self):
23     return self.store.get_active_positions()

25 def create_position(self, pos: dict):
26     enriched = self.enricher.enrich(pos)
27     return self.store.insert(enriched)

29 def delete_position(self, pos_id: str):
30     return self.store.delete(pos_id)

32 def clear_all_positions(self):
33     self.store.delete_all()
```

- `get_all_positions()` fetches all rows via `PositionStore.get_all()`, which calls `DataLocker.positions.get_all_positions()`.
- `create_position()` enriches the provided dictionary then inserts it via `DLPositionManager.create_position()`.
- `delete_position()` and `clear_all_positions()` map to `DLPositionManager.delete_position` and `DLPositionManager.delete_all_positions` respectively.

### Snapshot Recording

```python
35 def record_snapshot(self):
36     try:
37         raw = self.store.get_all()
38         totals = CalcServices().calculate_totals(raw)
39         self.dl.portfolio.record_snapshot(totals)
40         log.success("📸 Position snapshot recorded", source="PositionCore")
41     except Exception as e:
42         log.error(f"❌ Snapshot recording failed: {e}", source="PositionCore")
```

Snapshots summarize all positions into aggregate metrics and store them using `DLPortfolioManager.record_snapshot`. The `CalcServices.calculate_totals()` utility computes totals (size, value, collateral) plus averages such as leverage and heat index. The resulting data is persisted in `positions_totals_history`.

### Jupiter Synchronization

```python
44 def update_positions_from_jupiter(self, source="console"):
49     from positions.position_sync_service import PositionSyncService
50     sync_service = PositionSyncService(self.dl)
51     return sync_service.run_full_jupiter_sync(source=source)
```

This delegates to `PositionSyncService`. During a full sync the service:
1. Calls `update_jupiter_positions()` to fetch wallet positions from the Jupiter API and insert them into the database via `DLPositionManager.create_position`.
2. Generates hedges with `HedgeManager`.
3. Updates timestamps in `system_vars` with `DLSystemDataManager.set_last_update_times`.
4. Records a portfolio snapshot using `DLPortfolioManager`.

### Hedge Linking

```python
53 def link_hedges(self):
57     log.banner("🔗 Generating Hedges via PositionCore")
60     positions = self.store.get_all()
63     hedge_manager = HedgeManager(positions)
64     hedges = hedge_manager.get_hedges()
66     log.success("✅ Hedge generation complete", source="PositionCore", payload={"hedge_count": len(hedges)})
67     return hedges
```

`HedgeManager` analyzes in‑memory positions to pair long and short exposures. The resulting hedge records are not persisted by `PositionCore` directly but may be inserted via other DataLocker utilities if required.

### Enrichment of Existing Positions

```python
73 async def enrich_positions(self):
78     log.banner("🧠 Enriching All Positions via PositionCore")
81     raw = self.store.get_all()
82     enriched = []
83     failed = []
85     for pos in raw:
87         enriched_pos = self.enricher.enrich(pos)
89         if validate_enriched_position(enriched_pos, source="EnrichmentValidator"):
90             enriched.append(enriched_pos)
91         else:
92             failed.append(enriched_pos.get("id"))
97     log.success("✅ Position enrichment complete", source="PositionCore", payload={"enriched": len(enriched), "failed": len(failed)})
102     if failed:
103         log.warning("⚠️ Some positions failed enrichment validation", source="PositionCore", payload={"invalid_ids": failed})
107     return enriched
```

This method reloads all positions, enriches each using `PositionEnrichmentService`, validates them, and returns the enriched list (without writing back to the database). Failures are logged for review.

## `PositionStore`

`PositionStore` is a very small wrapper around `DLPositionManager`. Key methods:

```python
11 class PositionStore:
15     def get_all(self) -> list:
17         rows = self.dl.positions.get_all_positions()

27 def get_active_positions(self) -> list:
29     cursor = self.dl.db.get_cursor()
30     cursor.execute("SELECT * FROM positions WHERE status = 'ACTIVE'")
31     rows = cursor.fetchall()

41 def insert(self, position: dict) -> bool:
45     self.dl.positions.create_position(position)

52 def delete(self, pos_id: str) -> bool:
54     self.dl.positions.delete_position(pos_id)

61 def delete_all(self):
63     self.dl.positions.delete_all_positions()
```

Because `DataLocker` already exposes `DLPositionManager`, `PositionStore` mainly adds logging and default fields.

## `DLPositionManager`

The data layer implementation for positions resides here. Highlights:

- **Defaults & Sanitization** – `create_position()` inserts defaults for all missing fields before writing to the database and strips any keys not present in the schema. [`data/dl_positions.py` lines 33‑71]【F:data/dl_positions.py†L33-L71】
- **Retrieval** – `get_all_positions()` returns a list of dictionaries for all rows. [`data/dl_positions.py` lines 109‑118]【F:data/dl_positions.py†L109-L118】
- **Deletion** – `delete_position()` and `delete_all_positions()` remove rows from the table. [`data/dl_positions.py` lines 124‑142]【F:data/dl_positions.py†L124-L142】
- **Snapshots** – `record_positions_totals_snapshot()` persists aggregate metrics to `positions_totals_history`. [`data/dl_positions.py` lines 152‑176】

## Data Flow Example

Creating a position via `PositionCore.create_position()` proceeds as follows:

1. Caller supplies a basic position dictionary.
2. `PositionEnrichmentService.enrich()` computes derived fields such as leverage, heat index, and injects current market price via `DataLocker.prices.get_latest_price`.
3. The enriched dictionary is passed to `PositionStore.insert()`.
4. `PositionStore` calls `DLPositionManager.create_position()` which ensures defaults, sanitizes fields against the schema, constructs the SQL insert, and commits to SQLite.
5. Success is logged at each stage via the centralized logger.

## Snapshot Lifecycle

When `record_snapshot()` is invoked:

1. All positions are loaded from the database.
2. `CalcServices.calculate_totals()` computes totals and averages.
3. `DLPortfolioManager.record_snapshot()` writes these aggregates to `positions_totals_history` with a timestamp.
4. The operation is logged as a success or failure.

## Timestamp Management

`PositionSyncService` and other callers use `DataLocker.system.set_last_update_times()` to record when data was last refreshed. The `system_vars` table holds fields such as `last_update_time_positions`, `last_update_time_jupiter`, and their corresponding source labels. This ensures UI components can display the freshness of data.

## Error Handling & Logging

Throughout the module stack, errors are caught and logged with the same console logger (`core.logging`). Failures to write to the database are logged both to the console and, in the case of `DLPositionManager.create_position`, to a persistent log file (`logs/dl_failed_inserts.log`) so that problematic payloads can be inspected later.

## Summary

`PositionCore` is the high‑level API for anything related to trading positions. It delegates storage to `DataLocker`’s managers and uses enrichment logic to ensure positions carry calculated metrics. By combining synchronization, enrichment, hedge detection, and snapshotting, it provides a single entry point for the rest of the application (Flask routes, console tools, and monitoring engine) to manage position data in a consistent manner.
\n---\n
# File: trader_core/trader_core_spec.md
# 🧑‍💼 TraderCore Specification

> Version: `v1.0`
> Author: `CoreOps 🧠`
> Scope: Service layer for managing Trader creation, enrichment, and lifecycle operations

## 📂 Module Structure
```txt
trader_core/
├── trader_core.py            # 🌟 Central core logic for trader creation and updates
├── trader_factory_service.py # 🛠️ Optional builder for persona-to-trader conversion
├── trader_store.py           # 💾 Persistence and lookup utilities
```

## 🎯 Purpose
The TraderCore is responsible for:

- Creating new Trader entities based on persona configurations.
- Enriching trader data with live portfolio and position information.
- Managing mood, heat index, and performance scores.
- Persisting trader metadata in the database.
- Serving as the service gateway for factory UIs or API endpoints.

## 🧱 Constructor
```python
class TraderCore:
    def __init__(self, data_locker, persona_manager=None, strategy_manager=None)
```
- `data_locker`: Required. Used for accessing positions, portfolio, wallets.
- `persona_manager`: Optional override; otherwise loaded internally.
- `strategy_manager`: Optional override.

## 🛠 Key Methods
- `create_trader(trader_name: str) -> Trader`
  - Creates a Trader instance from a registered persona.
  - Loads persona profile.
  - Computes mood via `evaluate_mood(...)`.
  - Computes performance score.
  - Pulls positions, portfolio, and wallet data.
  - Returns a full Trader object (not persisted).
- `save_trader(trader: Trader) -> bool`
  - Persists a Trader's metadata.
  - Stores persona-specific overrides if applicable.
  - Saves to traders table (if it exists).
  - Future-proofed for tracking trader history or evolution.
- `get_trader(name: str) -> Trader`
  - Returns the enriched trader object using current data and persona config.
- `list_traders() -> List[Trader]`
  - Returns enriched traders for all available personas.
- `delete_trader(name: str) -> bool`
  - Optional. Deletes associated metadata (not personas or wallets).

## 🧠 Mood and Score Logic
Uses `mood_engine.evaluate_mood(heat_index, mood_map)` for:

- Assigning trader mood based on average heat index.
- Score formula (subject to tuning):

```python
score = int(100 - abs(avg_heat_index - 30))
```

## 📄 Trader Object
This module relies on the `Trader` data class:

```python
@dataclass
class Trader:
    name: str
    avatar: str
    persona: str
    origin_story: str
    risk_profile: str
    mood: str
    moods: Dict[str, str]
    strategies: Dict[str, float]
    wallet: str
    portfolio: Dict
    positions: List[Dict]
    hedges: List[Dict]
    performance_score: int
    heat_index: float
```

## 🔗 Integrations
Used by:
- `trader_bp.py` Flask routes (`/factory/<name>`, `/api/<name>`)
- Factory UI (HTML/JS) for trader creation and visualization

Depends on:
- `oracle_core.strategy_manager`
- `oracle_core.persona_manager`
- `oracle_core.oracle_data_service`
- `calc_core.calc_services`
- `mood_engine.evaluate_mood`

## 🔧 Future Expansion
- Trader lifecycle tracking (e.g. day-to-day score deltas)
- GPT analysis through `OracleCore.ask_trader(...)`
- Trader team generation (group trading simulations)
- Enhanced factory UI creation wizard
---
