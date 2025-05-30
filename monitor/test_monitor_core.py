import sys
import os

# Make sure this is at the TOP for path resolution!
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.logging import log
from monitor.monitor_core import MonitorCore

if __name__ == "__main__":
    log.banner("🧪 MonitorCore SELF-TEST START")

    core = MonitorCore()

    monitor_names = ["price_monitor", "position_monitor", "operations_monitor"]
    results = {}

    # Run each monitor by name
    for name in monitor_names:
        log.info(f"[SELF-TEST] Running {name} by name...", source="SelfTest")
        try:
            core.run_by_name(name)
            results[name] = "Success"
        except Exception as e:
            log.error(f"Exception running {name}: {e}", source="SelfTest")
            results[name] = f"Error: {e}"

    # Run all monitors
    log.info("[SELF-TEST] Running run_all()...", source="SelfTest")
    try:
        core.run_all()
        results["run_all"] = "Success"
    except Exception as e:
        log.error(f"Exception running run_all: {e}", source="SelfTest")
        results["run_all"] = f"Error: {e}"

    log.banner("🧪 MonitorCore SELF-TEST COMPLETE")
    print("\n==== SUMMARY ====")
    for k, v in results.items():
        print(f"{k:20}: {v}")
    print("=================")
