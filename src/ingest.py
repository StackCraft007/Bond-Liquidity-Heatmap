"""Load generated CSV into SQLite raw_trade_events table."""
import pandas as pd, sqlite3, pathlib, datetime, os

ROOT = pathlib.Path(__file__).resolve().parent.parent
db_path = ROOT / "heatmap.db"
data_dir = ROOT / "data"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS raw_trade_events (
  trade_id      INTEGER PRIMARY KEY AUTOINCREMENT,
  isin          TEXT,
  rating        TEXT,
  maturity_date TEXT,
  trade_ts      TEXT,
  qty_cr        REAL,
  price         REAL,
  buyer_cp      TEXT,
  seller_cp     TEXT
);
""")

latest_csvs = sorted(data_dir.glob("ftrac_*.csv"))
if not latest_csvs:
    raise SystemExit("No data files found in 'data' directory.")
csv_file = latest_csvs[-1]
df = pd.read_csv(csv_file)
df.to_sql("raw_trade_events", conn, if_exists="append", index=False)
conn.commit()
print(f"Ingested {len(df)} rows from {csv_file} into {db_path}")
conn.close()