"""
prepare_data.py

Loads data/raw/match_events.csv into the PostgreSQL table match_events
(schema: raw).  Idempotent: drops and recreates the table on every run.

Prerequisites:
  pip install pandas sqlalchemy psycopg2-binary python-dotenv

Environment:
  Copy .env.example → .env and fill in your DATABASE_URL, e.g.:
    DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/dbname

Run from the project root:
  python src/prepare_data.py
"""

from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent
RAW_CSV      = PROJECT_ROOT / "data" / "raw" / "match_events.csv"
SCHEMA       = "raw"
TABLE        = "match_events"


def get_engine():
    load_dotenv(PROJECT_ROOT / ".env")
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise EnvironmentError(
            "DATABASE_URL not set. Copy .env.example → .env and fill it in."
        )
    return create_engine(db_url)


def ensure_schema(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}"))


def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["match_date"])
    # Normalise bool column (CSV stores 'True'/'False' strings)
    df["is_cheater"] = df["is_cheater"].astype(bool)
    return df


def write_table(df: pd.DataFrame, engine) -> None:
    df.to_sql(
        name=TABLE,
        con=engine,
        schema=SCHEMA,
        if_exists="replace",   # drop + recreate each run → idempotent
        index=False,
        method="multi",
        chunksize=500,
    )


def main() -> None:
    print(f"Loading {RAW_CSV} …")
    df = load_csv(RAW_CSV)
    print(f"  {len(df):,} rows, {df.columns.tolist()}")

    engine = get_engine()
    ensure_schema(engine)

    print(f"Writing to {SCHEMA}.{TABLE} …")
    write_table(df, engine)

    with engine.connect() as conn:
        count = conn.execute(
            text(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE}")
        ).scalar()
    print(f"Done. {count:,} rows now in {SCHEMA}.{TABLE}.")


if __name__ == "__main__":
    main()
