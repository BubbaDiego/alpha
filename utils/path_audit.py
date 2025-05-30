# utils/path_audit.py

import os
import re

SUSPICIOUS_PATTERNS = [
    r"data\/.*\.json",
    r"config\/.*\.json",
    r"images\/.*\.(jpg|png|gif)",
    r"alert_thresholds\.json",
    r"sonic_config\.json",
]

EXCLUDED_DIRS = {"__pycache__", ".git", "venv", "env", ".venv"}

def search_hardcoded_paths(root_dir="."):
    findings = []
    for subdir, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(subdir, file)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    for idx, line in enumerate(lines, start=1):
                        for pattern in SUSPICIOUS_PATTERNS:
                            if re.search(pattern, line):
                                findings.append((file_path, idx, line.strip()))
    return findings

def run_audit():
    print("\n🔎 Starting Path Audit...")
    findings = search_hardcoded_paths()
    if not findings:
        print("\n✅ No hardcoded suspicious paths detected. You're clean!")
    else:
        print("\n🚨 Potential hardcoded paths found:")
        for path, line_no, content in findings:
            print(f"  {path} [Line {line_no}]: {content}")

if __name__ == "__main__":
    run_audit()
