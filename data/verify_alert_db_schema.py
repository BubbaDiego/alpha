import sqlite3

REQUIRED_TABLES = {
    "positions": """
    CREATE TABLE IF NOT EXISTS positions (
        id TEXT PRIMARY KEY,
        asset_type TEXT,
        entry_price REAL,
        liquidation_price REAL,
        position_type TEXT,
        wallet_name TEXT,
        current_heat_index REAL,
        pnl_after_fees_usd REAL,
        travel_percent REAL,
        liquidation_distance REAL
        ,status TEXT DEFAULT 'ACTIVE'
    )
    """,
    "alerts": """
    CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY,
        created_at TEXT,
        alert_type TEXT,
        alert_class TEXT,
        asset TEXT,
        asset_type TEXT,
        trigger_value REAL,
        condition TEXT,
        notification_type TEXT,
        level TEXT,
        last_triggered TEXT,
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
    """,
    "wallets": """
    CREATE TABLE IF NOT EXISTS wallets (
        id TEXT PRIMARY KEY,
        name TEXT,
        address TEXT,
        public_address TEXT,
        network TEXT,
        label TEXT,
        type TEXT
    )
    """,
    "prices": """
    CREATE TABLE IF NOT EXISTS prices (
        id TEXT PRIMARY KEY,
        asset_type TEXT,
        current_price REAL,
        previous_price REAL,
        last_update_time TEXT,
        previous_update_time TEXT,
        source TEXT
    )
    """
}

def verify_and_patch_schema(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in cursor.fetchall()}

    for table, ddl in REQUIRED_TABLES.items():
        if table not in existing_tables:
            print(f"⚠️  Table missing: {table} — creating...")
            cursor.execute(ddl)
        else:
            print(f"✅ Table exists: {table}")
    conn.commit()
