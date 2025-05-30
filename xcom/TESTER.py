# find_notification_service.py

import os

TARGET = "NotificationService"
ROOT = "."  # 🔧 Set to your project root if needed

matches = []

for root, dirs, files in os.walk(ROOT):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f, 1):
                    if TARGET in line:
                        matches.append((path, i, line.strip()))

# 📦 Report
if matches:
    print(f"🔍 Found {len(matches)} matches for '{TARGET}':\n")
    for path, line_no, content in matches:
        print(f"📄 {path} :: Line {line_no}")
        print(f"    {content}")
else:
    print(f"✅ No references to '{TARGET}' found.")
