import subprocess
import sys


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
