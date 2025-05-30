# scripts/rewrite_to_core_imports.py
"""
Author: BubbaDiego
Purpose: Rewrites multi-line imports to use centralized core imports.
"""

import os
import re

ROOT_DIR = "C:/v0.8"  # update if needed
CORE_IMPORTS = {
    "ConsoleLogger as log": "log",
    "get_locker": "get_locker",
    "DB_PATH": "DB_PATH",
    "CONFIG_PATH": "CONFIG_PATH",
    "BASE_DIR": "BASE_DIR",
    "ALERT_THRESHOLDS_PATH": "ALERT_THRESHOLDS_PATH",
    "retry_on_locked": "retry_on_locked",
    "JsonManager": "JsonManager"
}

def patch_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    original = lines[:]
    kept_lines = []
    found_symbols = set()

    for line in lines:
        # match lines like: from x import y [, z...]
        from_match = re.match(r"^\s*from\s+([a-zA-Z0-9_\.]+)\s+import\s+(.+)", line)
        if from_match:
            mod = from_match.group(1)
            symbols = [s.strip() for s in from_match.group(2).split(",")]
            new_symbols = []
            for s in symbols:
                key = f"{s} (from {mod})"
                alt = f"{s} (from utils.console_logger)" if "log" in s else key
                if s in CORE_IMPORTS or alt in CORE_IMPORTS:
                    found_symbols.add(CORE_IMPORTS.get(s, s))
                else:
                    new_symbols.append(s)

            if new_symbols:
                kept_lines.append(f"from {mod} import {', '.join(new_symbols)}\n")
            continue

        kept_lines.append(line)

    if found_symbols:
        # Insert core import line after built-ins
        insert_at = 0
        for i, line in enumerate(kept_lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_at = i + 1
        kept_lines.insert(insert_at, f"from core import {', '.join(sorted(found_symbols))}\n")

    if original != kept_lines:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(kept_lines)
        print(f"✅ Patched: {filepath}")
    else:
        print(f"👌 Already clean: {filepath}")

def scan_and_patch(root):
    print(f"\n🚀 Rewriting imports in: {root}")
    for foldername, _, filenames in os.walk(root):
        for fname in filenames:
            if fname.endswith(".py") and "venv" not in foldername:
                patch_file(os.path.join(foldername, fname))

if __name__ == "__main__":
    scan_and_patch(ROOT_DIR)
