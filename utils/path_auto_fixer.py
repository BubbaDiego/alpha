# utils/path_auto_fixer.py

import os
import re

# Define which replacements to make
FIX_PATTERNS = {
    r"['\"]data/alert_thresholds\.json['\"]": "str(ALERT_THRESHOLDS_PATH)",
}

TARGET_IMPORT = "from config.config_constants import ALERT_THRESHOLDS_PATH"

EXCLUDED_DIRS = {"__pycache__", ".git", "venv", "env", ".venv"}

def fix_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content
    fixed = False

    # Ensure ALERT_THRESHOLDS_PATH import
    if "ALERT_THRESHOLDS_PATH" not in content:
        content = TARGET_IMPORT + "\n" + content
        fixed = True

    # Apply all regex fixes
    for pattern, replacement in FIX_PATTERNS.items():
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            fixed = True

    if fixed:
        # Backup original first
        backup_path = file_path + ".bak"
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        # Save fixed file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Fixed: {file_path}")
    else:
        print(f"✅ OK: {file_path}")

def scan_and_fix(root_dir="."):
    print("\n🛠️ Auto-Fixing Hardcoded Paths...")
    for subdir, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(subdir, file)
                fix_file(file_path)

if __name__ == "__main__":
    scan_and_fix()
