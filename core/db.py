from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import duckdb
from core.s3_sync import get_effective_raw_dir


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"


REQUIRED_CSV_FILES = [
    "customers.csv",
    "customer_emails.csv",
    "addresses.csv",
    "cards.csv",
    "categories.csv",
    "brands.csv",
    "products.csv",
    "stock.csv",
    "promotions.csv",
    "orders.csv",
    "order_items.csv",
    "shipments.csv",
    "tracking.csv",
]


def get_data_raw_dir() -> Path:
    return get_effective_raw_dir()


def validate_required_files() -> None:
    data_raw_dir = get_data_raw_dir()
    missing_files = [
        file_name
        for file_name in REQUIRED_CSV_FILES
        if not (data_raw_dir / file_name).exists()
    ]

    if missing_files:
        missing_str = ", ".join(sorted(missing_files))
        raise FileNotFoundError(
            f"Faltan archivos CSV en data/raw: {missing_str}"
        )


@lru_cache(maxsize=1)
def get_connection() -> duckdb.DuckDBPyConnection:
    """
    Crea una conexión DuckDB en memoria y registra vistas sobre los CSV reales.
    """
    validate_required_files()

    conn = duckdb.connect(database=":memory:")
    _register_csv_views(conn)
    return conn


def _register_csv_views(conn: duckdb.DuckDBPyConnection) -> None:
    data_raw_dir = get_data_raw_dir()
    for file_name in REQUIRED_CSV_FILES:
        table_name = file_name.replace(".csv", "")
        file_path = data_raw_dir / file_name

        conn.execute(
            f"""
            CREATE OR REPLACE VIEW {table_name} AS
            SELECT *
            FROM read_csv_auto('{file_path.as_posix()}', HEADER=TRUE);
            """
        )
