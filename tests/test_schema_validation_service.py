import pytest
import os
import json
from utils.schema_validation_service import SchemaValidationService
import jsonschema
if getattr(jsonschema, 'IS_STUB', False):
    pytest.skip('jsonschema not available', allow_module_level=True)

TEST_VALID_FILE = "tests/mock_alert_thresholds_valid.json"
TEST_INVALID_SCHEMA_FILE = "tests/mock_alert_thresholds_invalid_schema.json"
TEST_MISSING_FILE = "tests/mock_missing_file.json"
TEST_BROKEN_JSON_FILE = "tests/mock_broken_json.json"

@pytest.fixture(scope="module", autouse=True)
def setup_mock_files():
    # Valid mock alert_ranges
    valid_data = {
        "alert_ranges": {
            "liquidation_distance_ranges": {},
            "travel_percent_liquid_ranges": {},
            "heat_index_ranges": {},
            "profit_ranges": {},
            "price_alerts": {}
        },
        "cooldowns": {
            "alert_cooldown_seconds": 300,
            "call_refractory_period": 900,
            "snooze_countdown": 300
        },
        "notifications": {
            "heat_index": {
                "low": {}, "medium": {}, "high": {}
            }
        }
    }

    invalid_schema_data = {
        "alert_ranges": {
            "liquidation_distance_ranges": {},
            "travel_percent_liquid_ranges": {},
            "heat_index_ranges": {}
            # Missing profit_ranges, price_alerts
        },
        "cooldowns": {
            "alert_cooldown_seconds": "not_a_number",  # Wrong type
            "call_refractory_period": 900,
            "snooze_countdown": 300
        },
        "notifications": {
            "heat_index": {
                "low": {}, "medium": {}, "high": {}
            }
        }
    }

    broken_json_content = """{ \"alert_ranges\": { \"liquidation_distance_ranges\": {} }"""  # Missing closing }

    os.makedirs("tests", exist_ok=True)
    with open(TEST_VALID_FILE, "w") as f:
        json.dump(valid_data, f, indent=2)

    with open(TEST_INVALID_SCHEMA_FILE, "w") as f:
        json.dump(invalid_schema_data, f, indent=2)

    with open(TEST_BROKEN_JSON_FILE, "w") as f:
        f.write(broken_json_content)

    yield

    # Cleanup after tests
    os.remove(TEST_VALID_FILE)
    os.remove(TEST_INVALID_SCHEMA_FILE)
    os.remove(TEST_BROKEN_JSON_FILE)

def test_valid_alert_ranges():
    assert SchemaValidationService.validate_schema(TEST_VALID_FILE, SchemaValidationService.ALERT_THRESHOLDS_SCHEMA, name="Mock Valid Limits")

def test_invalid_schema_alert_ranges():
    assert not SchemaValidationService.validate_schema(TEST_INVALID_SCHEMA_FILE, SchemaValidationService.ALERT_THRESHOLDS_SCHEMA, name="Mock Invalid Schema")

def test_missing_alert_ranges_file():
    assert not SchemaValidationService.validate_schema(TEST_MISSING_FILE, SchemaValidationService.ALERT_THRESHOLDS_SCHEMA, name="Mock Missing File")

def test_broken_json_file():
    assert not SchemaValidationService.validate_schema(TEST_BROKEN_JSON_FILE, SchemaValidationService.ALERT_THRESHOLDS_SCHEMA, name="Mock Broken JSON")
