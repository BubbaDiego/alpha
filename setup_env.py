import subprocess
import sys
import os

def run(cmd):
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        sys.exit(1)

def check_playwright():
    try:
        import playwright.sync_api
        print("✅ playwright.sync_api is available.")
    except ImportError:
        print("⏳ playwright.sync_api not found, reinstalling...")
        run("pip uninstall playwright -y")
        run("pip cache purge")
        run("pip install playwright --force-reinstall")
        run("python -m playwright install")

def main():
    print("📦 Verifying environment...")
    check_playwright()
    print("✅ Setup complete.")

if __name__ == "__main__":
    main()