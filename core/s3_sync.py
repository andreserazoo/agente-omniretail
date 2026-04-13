from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import boto3

from core.runtime_config import (
    get_aws_region,
    get_data_bucket,
    is_aws_env,
    is_lambda_runtime,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCAL_RAW_DIR = PROJECT_ROOT / "data" / "raw"
LOCAL_POLICIES_DIR = PROJECT_ROOT / "data" / "policies"
AWS_CACHE_DIR = PROJECT_ROOT / ".aws_cache"
AWS_RAW_DIR = AWS_CACHE_DIR / "raw"
AWS_POLICIES_DIR = AWS_CACHE_DIR / "policies"


RAW_FILES = [
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


POLICY_FILES = [
    "Política de devoluciones.md",
    "Política de garantía.md",
    "Políticas de envío.md",
]


def get_effective_raw_dir() -> Path:
    if is_aws_env():
        ensure_s3_data_available()
        return _get_cache_root() / "raw"

    return LOCAL_RAW_DIR


def get_effective_policies_dir() -> Path:
    if is_aws_env():
        ensure_s3_data_available()
        return _get_cache_root() / "policies"

    return LOCAL_POLICIES_DIR


@lru_cache(maxsize=1)
def ensure_s3_data_available() -> None:
    if not is_aws_env():
        return

    bucket = get_data_bucket().strip()
    if not bucket:
        raise ValueError("DATA_BUCKET no está configurado para APP_ENV=aws.")

    raw_dir = _get_cache_root() / "raw"
    policies_dir = _get_cache_root() / "policies"
    raw_dir.mkdir(parents=True, exist_ok=True)
    policies_dir.mkdir(parents=True, exist_ok=True)

    s3 = boto3.client("s3", region_name=get_aws_region())

    for file_name in RAW_FILES:
        _download_if_missing(
            s3,
            bucket=bucket,
            key=f"raw/{file_name}",
            destination=raw_dir / file_name,
        )

    for file_name in POLICY_FILES:
        _download_if_missing(
            s3,
            bucket=bucket,
            key=f"policies/{file_name}",
            destination=policies_dir / file_name,
        )


def _download_if_missing(s3, bucket: str, key: str, destination: Path) -> None:
    if destination.exists():
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    s3.download_file(bucket, key, str(destination))


def _get_cache_root() -> Path:
    if is_lambda_runtime():
        return Path("/tmp") / "agent-omniretail-cache"

    return AWS_CACHE_DIR
