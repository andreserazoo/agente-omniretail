import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def get_runtime_env() -> str:
    return os.getenv("APP_ENV", "local")


def is_aws_env() -> bool:
    return get_runtime_env() == "aws"


def is_lambda_runtime() -> bool:
    return bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))


def get_aws_region() -> str:
    return os.getenv("AWS_REGION", "us-east-1")


def get_data_bucket() -> str:
    return os.getenv("DATA_BUCKET", "")


def get_sessions_table() -> str:
    return os.getenv("SESSIONS_TABLE", "")


def get_bedrock_model_id() -> str:
    return os.getenv("BEDROCK_MODEL_ID", "")
