"""
One-off migration: add country_code to manufacturing_units.

manufacturing_units already exists, so Base.metadata.create_all()
will NOT add this column -- a manual ALTER is required (project rule).
Safe to re-run: checks for the column first, defaults existing rows
to "IN".

Run from backend/ with venv active:
    python3 migrate_country_code.py
"""

from sqlalchemy import inspect, text

import app.main  # noqa: F401  (registers models / engine)
from app.database.session import engine


def column_exists(table: str, column: str) -> bool:
    inspector = inspect(engine)
    cols = [c["name"] for c in inspector.get_columns(table)]
    return column in cols


def main():
    if column_exists("manufacturing_units", "country_code"):
        print("SKIP: country_code already exists on manufacturing_units")
        return

    with engine.begin() as conn:
        conn.execute(text(
            "ALTER TABLE manufacturing_units "
            "ADD COLUMN country_code VARCHAR(10) NOT NULL DEFAULT 'IN'"
        ))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_manufacturing_units_country_code "
            "ON manufacturing_units (country_code)"
        ))
    print("DONE: added country_code (default IN) + index")


if __name__ == "__main__":
    main()
