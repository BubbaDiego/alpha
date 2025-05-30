# System Specifications Index

This repository contains multiple subsystems that make up the overall trading and monitoring platform.  Each module has its own specification document with details on structure and responsibilities. This index provides a high level summary and links to the individual specs.

## Modules

### Cyclone
The Cyclone module drives workflow orchestration and alert management. It processes market updates, evaluates portfolio risk and positions, generates alerts, and coordinates hedging logic.
For a focused look at the main engine see the [Cyclone Core specification](cyclone/cyclone_core_spec.md).

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
The [HedgeCalcServices specification](hedge_core/hedge_calc_services_spec.md) details calculations for dynamic hedging and rebalance suggestions.

### Monitor Core
The [Monitor module](monitor/monitor_module_spec.md) drives periodic tasks and health checks. It registers individual monitors and exposes CLI and API entrypoints for running them.

### Wallets
The [Wallet Core specification](wallets/wallet_core_spec.md) outlines wallet operations and blockchain helpers. The [Jupiter API spec](wallets/jupiter_api_spec.md) describes how wallets interact with Jupiter Perps for managing collateral.

### GPT Input Format
The [GPT Input specification](gpt_input_spec.md) details the JSON bundle used to send portfolio and alert context to GPT for analysis.

### GPT Core
The [GPT Core specification](gpt/gpt_core_spec.md) describes the Python modules and chat UI for interacting with OpenAI's API.

### Oracle Core
The [Oracle Core specification](oracle_core/oracle_core_spec.md) explains the strategy and persona system used to build GPT prompts.

---

Each linked specification contains more detailed design notes, functional requirements, and example workflows.
