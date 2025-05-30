from uuid import uuid4
from datetime import datetime

def log_alert_update(data_locker, alert_id: str, modified_by: str, reason: str, before_value: str, after_value: str):
    """
    Logs an update to an alert state into the alert_ledger table.
    :param data_locker: The DataLocker instance with an open DB connection.
    :param alert_id: The ID of the alert being updated.
    :param modified_by: Who made the update (e.g. "system" or a username).
    :param reason: Reason for the update.
    :param before_value: The state before the update.
    :param after_value: The new state.
    """
    cursor = data_locker.db.get_cursor()
    ledger_entry = {
        "id": str(uuid4()),
        "alert_id": alert_id,
        "modified_by": modified_by,
        "reason": reason,
        "before_value": before_value,
        "after_value": after_value,
        "timestamp": datetime.now().isoformat()
    }
    sql = """
        INSERT INTO alert_ledger (
            id, alert_id, modified_by, reason, before_value, after_value, timestamp
        ) VALUES (
            :id, :alert_id, :modified_by, :reason, :before_value, :after_value, :timestamp
        )
    """
    cursor.execute(sql, ledger_entry)
    data_locker.db.commit()
