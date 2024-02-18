# %%
import sqlite3

import pandas as pd

"""CREATE TABLE data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requested_time DATETIME,
    device_id TEXT,
    value REAL,
    variable TEXT);
"""

# Read a sqlite database
with sqlite3.connect("./tools/import_data/data/api_data.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT requested_time, device_id, value, variable FROM data")
    results = cursor.fetchall()
    conn.commit()

df = pd.DataFrame(results, columns=["requested_time", "device_id", "value", "variable"])
device_ids = [
    "619e4af8a43d67819d7d027a",
    "619e4af8a43d67819d7d0277",
    "619e4af8a43d67819d7d0278",
    "619e4af8a43d67819d7d0279",
]
