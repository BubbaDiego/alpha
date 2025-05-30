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


ChatGPT can make mistakes. Check important info.