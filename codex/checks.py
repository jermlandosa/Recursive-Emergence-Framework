"""Policy checks for Codex rules enforcement."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

RULES_PATH = Path("codex/rules.json")
MEMORY_PATH = Path("data/memory.jsonl")


def load_rules(path: Path = RULES_PATH) -> dict[str, Any]:
    """Load rule configuration from ``path``.

    Returns an empty mapping if the file does not exist or is invalid.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def friction_alarm_passed(memory_file: Path | str = MEMORY_PATH, *, last_n: int = 10) -> bool:
    """Return ``True`` if a passing friction alarm exists in the last ``last_n`` entries."""
    path = Path(memory_file)
    if not path.exists():
        return False
    try:
        lines = path.read_text(encoding="utf-8").splitlines()[-last_n:]
    except OSError:
        return False
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("event") == "friction_alarm" and entry.get("status") == "pass":
            return True
    return False


def commit_signed() -> bool:
    """Return ``True`` if the latest commit is signed with a trusted signature.

    Uses ``git log -1 --pretty=%G?`` where ``G`` indicates a good signature and
    ``R`` indicates a good, trusted signature.
    """
    try:
        status = subprocess.check_output(
            ["git", "log", "-1", "--pretty=%G?"], text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    return status in {"G", "R"}


def verify_compliance() -> bool:
    """Verify all enabled Codex rules.

    Returns ``True`` when all checks pass, otherwise ``False``.
    """
    rules = load_rules()
    if rules.get("require_friction_alarm"):
        if not friction_alarm_passed():
            return False
    if rules.get("enforce_signed_commits"):
        if not commit_signed():
            return False
    return True
