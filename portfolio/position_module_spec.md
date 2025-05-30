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

Database connections are managed with SQLite’s WAL mode and thread-check disablement, though caution is advised in multi-threaded environments.