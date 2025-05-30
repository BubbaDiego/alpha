# utils/startup_checker.py

from core.constants import (
    DB_PATH,
    CONFIG_PATH,
    ALERT_THRESHOLDS_PATH,
    SONIC_SAUCE_PATH,
    COM_CONFIG_PATH,
    THEME_CONFIG_PATH,
)
import os
import sys

paths_to_check = {
    "Database Path": DB_PATH,
    "Config Path": CONFIG_PATH,
    "Alert Thresholds Path": ALERT_THRESHOLDS_PATH,
    "Sonic Sauce Path": SONIC_SAUCE_PATH,
    "Com Config Path": COM_CONFIG_PATH,
    "Theme Config Path": THEME_CONFIG_PATH,
}

def verify_paths():
    print("\n🛡️ Verifying Critical Paths:")
    fatal_errors = []
    
    for name, path in paths_to_check.items():
        if not os.path.exists(path):
            print(f"❌ Missing: {name} at {path}")
            fatal_errors.append(f"{name}: {path}")
        else:
            print(f"✅ Found: {name}")

    if fatal_errors:
        print("\n⛔ CRITICAL ERROR: The following required files are missing:")
        for error in fatal_errors:
            print(f"   - {error}")
        print("\n💥 ABORTING launch due to missing critical files.\n")
        sys.exit(1)  # 🚨 TERMINATE app immediately with non-zero exit code
