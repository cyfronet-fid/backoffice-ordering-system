import subprocess
import sys

from backend.config import get_settings


def run_command(command: str) -> int:
    result = subprocess.run(command, shell=True)
    return result.returncode


def lint() -> None:
    commands = [
        "black --check backend/ migrations/",
        "isort --check-only backend/ migrations/",
        "bandit -r backend/",
        "mypy backend/",
        "pylint backend/",
    ]

    for command in commands:
        print(f"Running: {command}")
        if run_command(command) != 0:
            sys.exit(1)


def format_() -> None:
    commands = ["black backend/ migrations/", "isort backend/ migrations/"]

    for command in commands:
        print(f"Running: {command}")
        if run_command(command) != 0:
            sys.exit(1)


def generate_whitelabel_client() -> None:
    # Run and then copy only what you need from ./out/whitelabel_client into $ROOT_DIR$/whitelabel_client
    run_command(
        (
            f"openapi-generator generate "
            f"-i {get_settings().whitelabel_endpoint}/api_docs/swagger/v1/ordering_swagger.json "
            f"-o ./out "
            f"-g python "
            f"--additional-properties=generateSourceCodeOnly=true,packageName=whitelabel_client "
        )
    )
