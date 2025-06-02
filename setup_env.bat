@echo off
cd /d C:\alpha

echo 🔥 Deleting old .venv...
rmdir /s /q .venv

echo 🧱 Creating new virtual environment...
python -m venv .venv

echo ✅ Activating virtual environment...
call .venv\Scripts\activate

echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

echo 📦 Installing required packages...
pip install base58 requests solders

echo 🧪 Done. You can now run your console app:
echo python jupiter_auto_console.py
