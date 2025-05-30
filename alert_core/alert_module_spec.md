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

Data layer is read/write only