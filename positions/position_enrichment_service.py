import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calc_core.calculation_core import CalculationCore
from core.logging import log
from core.constants import DB_PATH
from data.data_locker import DataLocker
from utils.fuzzy_wuzzy import fuzzy_match_key
from calc_core.calculation_core import CalculationCore

class PositionEnrichmentService:
    def __init__(self, data_locker=None):
        self.dl = data_locker
        self.calc_core = CalculationCore(data_locker)

    def enrich(self, position):
        from core.logging import log
        from utils.fuzzy_wuzzy import fuzzy_match_key

        pos_id = position.get('id', 'UNKNOWN')
        asset = position.get('asset_type', '??')

        log.info(f"\n📥 Enriching position [{pos_id}] — Asset: {asset}", source="Enrichment")

        try:
            # Step 1: Field defaults
            defaults = {
                'entry_price': 0.0,
                'current_price': position.get('entry_price', 0.0),
                'liquidation_price': 0.0,
                'collateral': 0.0,
                'size': 0.0,
                'leverage': None,
                'value': 0.0,
                'pnl_after_fees_usd': 0.0,
                'travel_percent': 0.0,
                'liquidation_distance': 0.0,
                'current_heat_index': 0.0
            }
            for k, v in defaults.items():
                position.setdefault(k, v)

            if not position.get("wallet_name"):
                position["wallet_name"] = "Unknown"
                log.warning(f"⚠️ No wallet_name for [{pos_id}] — defaulted", source="Enrichment")

            # 🔍 Step 2: Position Type Normalization
            raw_type = str(position.get("position_type", "")).strip().lower()
            if raw_type in ["long", "l"]:
                position["position_type"] = "LONG"
            elif raw_type in ["short", "s"]:
                position["position_type"] = "SHORT"
            else:
                match = fuzzy_match_key(raw_type, {"LONG": None, "SHORT": None}, threshold=60.0)
                position["position_type"] = match.upper() if match else "UNKNOWN"

            if position["position_type"] == "UNKNOWN":
                log.warning(f"⚠️ Could not normalize position_type for [{pos_id}] — input: '{raw_type}'",
                            source="Enrichment")

            # Step 3: Validation before coercion
            required_fields = ['entry_price', 'current_price', 'liquidation_price', 'collateral', 'size']
            missing = [k for k in required_fields if position.get(k) is None]
            if missing:
                log.warning(f"⚠️ Missing numeric fields for [{pos_id}]: {missing}", source="Enrichment")

            # Step 4: Safe coercion
            for field in required_fields:
                try:
                    position[field] = float(position.get(field) or 0.0)
                except Exception as e:
                    log.error(f"❌ Failed to coerce field [{field}] for [{pos_id}]: {e}", source="Enrichment")
                    position[field] = 0.0

            # Step 5: Derived field enrichment (through CalculationCore)
            # NOTE: Jupiter already provides an accurate value field.
            # Historically we recomputed value from size * current_price,
            # but that overwrote the API-provided figure.  We keep the
            # original value now for correctness.
            # position['value'] = position['size'] * position['current_price']
            position['leverage'] = self.calc_core.calc_services.calculate_leverage(position['size'],
                                                                                   position['collateral']) if position[
                                                                                                                  'collateral'] > 0 else 0.0
            position['travel_percent'] = self.calc_core.get_travel_percent(
                position['position_type'],
                position['entry_price'], position['current_price'], position['liquidation_price']
            )
            position['liquidation_distance'] = self.calc_core.calc_services.calculate_liquid_distance(
                position['current_price'], position['liquidation_price']
            )
            try:
                risk = self.calc_core.get_heat_index(position)
            except Exception as e:
                log.error(f"❌ Risk index calculation failed: {e}", source="calculate_composite_risk_index",
                          payload=position)
                risk = 0.0

            position['heat_index'] = risk
            position['current_heat_index'] = risk

            # Step 6: Market price injection
            latest = self.dl.get_latest_price(asset)
            if latest and 'current_price' in latest:
                position['current_price'] = float(latest['current_price'])
                log.info(f"🌐 Market price injected for {asset}: {position['current_price']}", source="Enrichment")

            log.success(f"✅ Enriched [{pos_id}] complete", source="Enrichment")
            return position

        except Exception as e:
            log.error(f"🔥 Enrichment FAILED for [{pos_id}]: {e}", source="Enrichment")
            return position


def validate_enriched_position(position: dict, source="EnrichmentValidator") -> bool:
    pos_id = position.get("id", "UNKNOWN")
    failures = []

    required_fields = {
        "position_type": lambda v: v in {"LONG", "SHORT"},
        "leverage": lambda v: isinstance(v, (int, float)) and v >= 0,
        "travel_percent": lambda v: isinstance(v, (int, float)),
        "liquidation_distance": lambda v: isinstance(v, (int, float)),
        "heat_index": lambda v: isinstance(v, (int, float)),
        "value": lambda v: isinstance(v, (int, float)),
        "current_price": lambda v: isinstance(v, (int, float)),
        "wallet_name": lambda v: isinstance(v, str) and len(v) > 0,
    }

    for field, validator in required_fields.items():
        value = position.get(field)
        if value is None or not validator(value):
            failures.append((field, value))

    if failures:
        log.error(f"❌ Position [{pos_id}] failed validation on {len(failures)} fields", source=source, payload={
            f: v for f, v in failures
        })
        return False
    else:
        log.success(f"✅ Position [{pos_id}] passed all enrichment checks", source=source)
        return True
