from pathlib import Path
import subprocess
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
VENV_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"

if VENV_PYTHON.exists() and Path(sys.executable).resolve() != VENV_PYTHON.resolve():
    completed = subprocess.run([str(VENV_PYTHON), str(Path(__file__).resolve())], check=False)
    raise SystemExit(completed.returncode)

LOCAL_SITE_PACKAGES = ROOT / ".venv" / "Lib" / "site-packages"
if LOCAL_SITE_PACKAGES.exists() and str(LOCAL_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(LOCAL_SITE_PACKAGES))

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.lambda_handler import lambda_handler


def main() -> None:
    event = {
        "body": json.dumps(
            {
                "message": "Hola",
                "session_id": "test-aws-local",
            },
            ensure_ascii=False,
        )
    }

    result = lambda_handler(event, None)

    print("statusCode:", result.get("statusCode"))
    print("headers:", result.get("headers"))
    print("body:", result.get("body"))


if __name__ == "__main__":
    main()
