import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import jsonschema
from jsonschema import validate
from core.core_imports import log
from core.constants import ALERT_THRESHOLDS_PATH

class SchemaValidationService:
    """
    Service to validate critical configuration files.
    Can be invoked in post-deployment or other test suites.
    """

    ALERT_THRESHOLDS_FILE = str(ALERT_THRESHOLDS_PATH)

    ALERT_THRESHOLDS_SCHEMA = {
        "type": "object",
        "properties": {
            "source": {"type": "string"},
            "alert_ranges": {
                "type": "object",
                "properties": {
                    "liquidation_distance_ranges": {"type": "object"},
                    "travel_percent_liquid_ranges": {"type": "object"},
                    "heat_index_ranges": {"type": "object"},
                    "profit_ranges": {"type": "object"},
                    "price_alerts": {"type": "object"}
                },
                "required": [
                    "liquidation_distance_ranges",
                    "travel_percent_liquid_ranges",
                    "heat_index_ranges",
                    "profit_ranges",
                    "price_alerts"
                ]
            },
            "cooldowns": {
                "type": "object",
                "properties": {
                    "alert_cooldown_seconds": {"type": "number"},
                    "call_refractory_period": {"type": "number"},
                    "snooze_countdown": {"type": "number"}
                },
                "required": ["alert_cooldown_seconds", "call_refractory_period", "snooze_countdown"]
            },
            "notifications": {
                "type": "object",
                "patternProperties": {
                    "^(heat_index|travel_percent_liquid|profit|price_alerts)$": {
                        "type": "object",
                        "properties": {
                            "low": {"type": "object"},
                            "medium": {"type": "object"},
                            "high": {"type": "object"}
                        }
                    }
                }
            }
        },
        "required": ["alert_ranges", "cooldowns", "notifications"]
    }

    @staticmethod
    def validate_schema(file_path: str, schema: dict, name: str = "Unknown") -> bool:
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            log.banner(f"{name.upper()} HEALTH CHECK")

            validate(instance=data, schema=schema)
            log.success(f"✅ {name} JSON schema validation passed.", source="SchemaValidationService")
            return True

        except jsonschema.exceptions.ValidationError as ve:
            log.error(f"❌ {name} schema validation failed: {ve.message}", source="SchemaValidationService")
            return False
        except FileNotFoundError:
            log.error(f"❌ File not found: {file_path}", source="SchemaValidationService")
            return False
        except Exception as e:
            log.error(f"❌ Unexpected error during {name} validation: {e}", source="SchemaValidationService")
            return False

    @classmethod
    def validate_alert_ranges(cls):
        return cls.validate_schema(cls.ALERT_THRESHOLDS_FILE, cls.ALERT_THRESHOLDS_SCHEMA, name="Alert Ranges")

    @classmethod
    def batch_validate(cls):
        """Run all schema validations in a batch."""
        log.banner("BATCH SCHEMA VALIDATION")
        results = []

        validations = [
            ("Alert Ranges", cls.ALERT_THRESHOLDS_FILE, cls.ALERT_THRESHOLDS_SCHEMA)
            # Future: add more configs here
        ]

        for name, file_path, schema in validations:
            result = cls.validate_schema(file_path, schema, name)
            results.append(result)

        if all(results):
            log.success("✅ All schema validations passed!", source="SchemaValidationService")
            return True
        else:
            log.error("❌ One or more schema validations failed!", source="SchemaValidationService")
            return False

if __name__ == "__main__":
    SchemaValidationService.batch_validate()