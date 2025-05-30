import os
import json
import datetime
import requests
import sqlite3
from core.constants import LOG_DATE_FORMAT, LOG_DIR  # Import LOG_DIR
from core.core_imports import DB_PATH

def query_update_ledger():
    """
    Query the alert_ledger table and return all entries as a list of dictionaries.
    Assumes the database (via DataLocker) is set up and the ledger table exists.
    """
    ledger_entries = []
    try:
        # Use the DB_PATH from config to ensure we query the correct database
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alert_ledger")
        rows = cursor.fetchall()
        for row in rows:
            ledger_entries.append(dict(row))
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error querying update ledger: {e}")
    return ledger_entries

def determine_cycle_status(ledger_entries):
    """
    Determine overall cycle status based on ledger entries.
    For example, if any entry has status 'error', then the cycle is considered failed.
    Otherwise, it's considered successful.
    """
    for entry in ledger_entries:
        # Assume the ledger has a column named 'status'
        if entry.get("status", "").lower() == "error":
            return "error"
    # If no error entries, we assume success.
    return "success"

def query_update_ledger():
    ledger_entries = []
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alert_ledger")
        rows = cursor.fetchall()
        for row in rows:
            entry = dict(row)
            ledger_entries.append(entry)
        cursor.close()
        conn.close()
        print("DEBUG: Ledger entries fetched:", ledger_entries)  # Debug print
    except Exception as e:
        print(f"Error querying update ledger: {e}")
    return ledger_entries

def generate_cycle_report():
    """
    Reads the cyclone log file (cyclone_log.txt) from the logs folder (using LOG_DIR),
    builds a summary and detailed table from the JSON log records,
    queries the alert ledger table for alert state modifications,
    and writes a pretty dark mode HTML report to cyclone_report.html.
    The header now shows a huge green check mark (✅) if no errors occurred
    or a skull (💀) if there were any errors. The ledger details are shown
    at the top right of the summary.
    """
    # Use LOG_DIR from config_constants for the logs folder
    logs_dir = str(LOG_DIR)
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    cyclone_log_path = os.path.join(logs_dir, "cyclone_log.txt")
    cyclone_report_path = os.path.join(logs_dir, "cyclone_report.html")

    if not os.path.exists(cyclone_log_path):
        print(f"No cyclone log file found at {cyclone_log_path}. Cannot generate report.")
        return

    # Read and parse cyclone log entries
    log_entries = []
    with open(cyclone_log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                log_entries.append(record)
            except json.JSONDecodeError:
                continue

    # Build summary counts
    summary = {}
    for record in log_entries:
        op_type = record.get("operation_type", "Unknown")
        summary[op_type] = summary.get(op_type, 0) + 1

    # Query the alert ledger using the updated function
    ledger_entries = query_update_ledger()
    cycle_status = determine_cycle_status(ledger_entries)
    # Choose icon based on cycle_status
    if cycle_status == "success":
        status_icon = "<span style='font-size:72px; color:lime;' title='Cycle Successful'>✅</span>"
    else:
        status_icon = "<span style='font-size:72px; color:red;' title='Cycle Failed'>💀</span>"

    # Build ledger details HTML (placed at top right)
    ledger_html = "<div style='text-align:right; font-size:14px;'>"
    ledger_html += "<h3>Update Ledger</h3>"
    if ledger_entries:
        ledger_html += "<ul style='list-style:none; padding:0;'>"
        for entry in ledger_entries:
            who = entry.get("modified_by", "Unknown")
            reason = entry.get("reason", "No reason")
            before = entry.get("before_value", "N/A")
            after = entry.get("after_value", "N/A")
            ledger_html += f"<li>👤 {who} - 📝 {reason} | Before: {before} | After: {after}</li>"
        ledger_html += "</ul>"
    else:
        ledger_html += "<p>No ledger entries recorded.</p>"
    ledger_html += "</div>"

    # Get current date and time
    current_datetime = datetime.datetime.now().strftime(LOG_DATE_FORMAT)

    # Fetch a random joke (optional)
    try:
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        if response.status_code == 200:
            joke_data = response.json()
            joke = f"{joke_data.get('setup', '')} {joke_data.get('punchline', '')}"
        else:
            joke = "Couldn't fetch a joke today, sorry!"
    except Exception as e:
        joke = "Couldn't fetch a joke today, sorry!"

    # Build HTML report with dark mode styling and header sections for status and ledger
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Cyclone Report - Dark Mode</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #2b2b2b;
            color: #e0e0e0;
            margin: 20px;
        }}
        h1, h2 {{
            color: #fff;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header .status-icon {{
            font-size: 72px;
        }}
        .header .ledger-summary {{
            text-align: right;
            font-size: 14px;
        }}
        .summary {{
            background-color: #3a3a3a;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        .summary ul {{
            list-style: none;
            padding: 0;
        }}
        .summary li {{
            margin-bottom: 10px;
            font-size: 16px;
        }}
        .joke {{
            margin-bottom: 20px;
            padding: 15px;
            background-color: #444;
            border-radius: 4px;
            font-style: italic;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background-color: #3a3a3a;
        }}
        th, td {{
            border: 1px solid #555;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background-color: #007ACC;
            color: #fff;
        }}
        tr:nth-child(even) {{ background-color: #444; }}
        tr:nth-child(odd) {{ background-color: #3a3a3a; }}
        .footer {{
            margin-top: 20px;
            font-size: 14px;
            text-align: center;
            color: #ccc;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="status-icon">{status_icon}</div>
        <div class="ledger-summary">{ledger_html}</div>
    </div>
    <h1>Cyclone Report - Dark Mode</h1>
    <div>
        <p>Report Generated on: {current_datetime}</p>
    </div>
    <div class="summary">
        <h2>Summary</h2>
        <ul>
"""
    for op, count in summary.items():
        html_content += f"            <li><strong>{op}:</strong> {count}</li>\n"
    html_content += f"""        </ul>
    </div>
    <div class="joke">
        <strong>Joke of the Day:</strong> {joke}
    </div>
    <h2>Detailed Log Entries</h2>
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Operation Type</th>
            <th>Source</th>
            <th>File</th>
            <th>Message</th>
        </tr>
"""
    for record in log_entries:
        ts = record.get("timestamp", "")
        op_type = record.get("operation_type", "")
        source = record.get("source", "")
        file_name = record.get("file", "")
        message = record.get("message", "")
        html_content += f"""        <tr>
            <td>{ts}</td>
            <td>{op_type}</td>
            <td>{source}</td>
            <td>{file_name}</td>
            <td>{message}</td>
        </tr>
"""
    html_content += """    </table>
    <div class="footer">
        Generated by Cyclone V1
    </div>
</body>
</html>
"""

    with open(cyclone_report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Cyclone report generated: {cyclone_report_path}")

if __name__ == "__main__":
    generate_cycle_report()
