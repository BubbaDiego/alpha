# clear_alerts.py
import pytest

try:
    from data.data_locker import DataLocker
    from core.core_imports import get_locker, log
except Exception:
    pytest.skip("DataLocker dependencies missing", allow_module_level=True)

def clear_all_alerts():
    try:
        dl = get_locker()
        count_before = len(dl.get_alerts())
        dl.clear_alerts()
        count_after = len(dl.get_alerts())
        log.success(f"✅ Cleared {count_before} alert(s). Now {count_after} remain.", source="ClearAlerts")
    except Exception as e:
        log.error(f"❌ Failed to clear alerts: {e}", source="ClearAlerts")

if __name__ == "__main__":
    print("⚠️  WARNING: This will delete ALL alerts.")
    confirm = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    if confirm == "yes":
        clear_all_alerts()
    else:
        print("Aborted. No alerts deleted.")
