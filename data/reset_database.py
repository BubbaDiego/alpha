import sqlite3
from datetime import datetime
import os

# Use shared DB_PATH from core.constants to ensure consistent location
from core.constants import DB_PATH

def reset_database(db_path):
    # 🔍 Show full absolute path for inspection
    abs_path = os.path.abspath(db_path)
    print(f"📂 DB PATH BEING USED: {abs_path}")

    # 🛑 Do NOT auto-create the directory
    db_dir = os.path.dirname(abs_path)
    if not os.path.exists(db_dir):
        print(f"❌ Directory missing: {db_dir}")
        print("🛑 Aborting reset. Please create the directory manually or adjust DB_PATH.")
        return

    if os.path.exists(abs_path):
        os.remove(abs_path)
        print(f"🧨 Removed existing database: {abs_path}")

    # 🔁 Create DB and tables
    conn = sqlite3.connect(abs_path)
    cursor = conn.cursor()

    print("⚙️ Creating tables...")

    cursor.execute("""
        CREATE TABLE alerts (
            id TEXT PRIMARY KEY,
            created_at DATETIME,
            alert_type TEXT,
            alert_class TEXT,
            asset TEXT,
            asset_type TEXT,
            trigger_value REAL,
            condition TEXT,
            notification_type TEXT,
            level TEXT,
            last_triggered DATETIME,
            status TEXT,
            frequency INTEGER,
            counter INTEGER,
            liquidation_distance REAL,
            travel_percent REAL,
            liquidation_price REAL,
            notes TEXT,
            description TEXT,
            position_reference_id TEXT,
            evaluated_value REAL,
            position_type TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE positions (
            id TEXT PRIMARY KEY,
            asset_type TEXT,
            position_type TEXT,
            entry_price REAL,
            liquidation_price REAL,
            travel_percent REAL,
            value REAL,
            collateral REAL,
            size REAL,
            leverage REAL,
            wallet_name TEXT,
            last_updated TEXT,
            alert_reference_id TEXT,
            hedge_buddy_id TEXT,
            current_price REAL,
            liquidation_distance REAL,
            heat_index REAL,
            current_heat_index REAL,
            pnl_after_fees_usd REAL,
            status TEXT DEFAULT 'ACTIVE'
        )
    """)

    cursor.execute("""
        CREATE TABLE position_alert_map (
            id TEXT PRIMARY KEY,
            position_id TEXT NOT NULL,
            alert_id TEXT NOT NULL,
            FOREIGN KEY(position_id) REFERENCES positions(id),
            FOREIGN KEY(alert_id) REFERENCES alerts(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE system_vars (
            id INTEGER PRIMARY KEY,
            last_update_time_positions DATETIME,
            last_update_positions_source TEXT,
            last_update_time_prices DATETIME,
            last_update_prices_source TEXT,
            last_update_time_jupiter DATETIME,
            last_update_jupiter_source TEXT,
            theme_mode TEXT DEFAULT 'light',
            total_brokerage_balance REAL DEFAULT 0.0,
            total_wallet_balance REAL DEFAULT 0.0,
            total_balance REAL DEFAULT 0.0,
            strategy_start_value REAL DEFAULT 0.0,
            strategy_description TEXT DEFAULT ''
        )
    """)

    cursor.execute("INSERT OR IGNORE INTO system_vars (id) VALUES (1)")

    conn.commit()
    conn.close()
    print("✅ DB reset complete.")

if __name__ == "__main__":
    reset_database(DB_PATH)
