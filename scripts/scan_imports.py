# scripts/scan_imports.py
"""
Author: BubbaDiego
Purpose: Analyze all `import` and `from ... import ...` statements in your codebase.
         Prints frequency counts of modules and symbols to prep for centralization.
"""

import os
import re
from collections import defaultdict

ROOT_DIR = "C:/v0.8"  # Update this path to match your project root

module_counts = defaultdict(int)
symbol_counts = defaultdict(int)

IMPORT_RE = re.compile(r"^\s*import\s+([a-zA-Z0-9_\.]+)")
FROM_IMPORT_RE = re.compile(r"^\s*from\s+([a-zA-Z0-9_\.]+)\s+import\s+(.+)")

def scan_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match1 = IMPORT_RE.match(line)
            match2 = FROM_IMPORT_RE.match(line)
            if match1:
                module = match1.group(1)
                module_counts[module] += 1
            elif match2:
                module = match2.group(1)
                symbols = [s.strip() for s in match2.group(2).split(",")]
                module_counts[module] += 1
                for symbol in symbols:
                    key = f"{symbol} (from {module})"
                    symbol_counts[key] += 1

def scan_project(root_dir):
    print(f"🔍 Scanning Python imports in: {root_dir}")
    for foldername, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith(".py") and "venv" not in foldername:
                path = os.path.join(foldername, fname)
                scan_file(path)

def print_results():
    print("\n📊 Top Imported Symbols:")
    for symbol, count in sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:30]:
        print(f"  - {symbol:<40}: {count} uses")

    print("\n📦 Top Imported Modules:")
    for mod, count in sorted(module_counts.items(), key=lambda x: x[1], reverse=True)[:30]:
        print(f"  - {mod:<40}: {count} uses")

if __name__ == "__main__":
    scan_project(ROOT_DIR)
    print_results()
