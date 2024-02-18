# %%
import sqlite3

import pandas as pd

"""
CREATE TABLE weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requested_time DATETIME,
    temperature REAL,
    rh INTEGER,
    dewpoint REAL,
    avgWindSpeed10min TEXT,
    Patm TEXT
);
"""
# Read a sqlite database
with sqlite3.connect("./tools/import_data/data/api_data.db") as conn:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT requested_time, temperature, rh, dewpoint,avgWindSpeed10min, Patm FROM weather"
    )
    results = cursor.fetchall()
    conn.commit()

df = pd.DataFrame(
    results,
    columns=[
        "requested_time",
        "temperature",
        "rh",
        "dewpoint",
        "avgWindSpeed10min",
        "Patm",
    ],
)
