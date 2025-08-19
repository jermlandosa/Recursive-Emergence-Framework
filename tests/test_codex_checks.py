import json
import tempfile
from pathlib import Path
from unittest import mock

from codex import checks


def _write_entries(entries, path: Path):
    with path.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


def test_friction_alarm_passed():
    with tempfile.TemporaryDirectory() as tmp:
        mem = Path(tmp) / "memory.jsonl"
        entries = [{"event": "other"}] * 9 + [{"event": "friction_alarm", "status": "pass"}]
        _write_entries(entries, mem)
        assert checks.friction_alarm_passed(mem)

        entries = [{"event": "other"}] * 10
        _write_entries(entries, mem)
        assert not checks.friction_alarm_passed(mem)


@mock.patch("subprocess.check_output")
def test_commit_signed(mock_co):
    mock_co.return_value = "G"
    assert checks.commit_signed()
    mock_co.return_value = "R"
    assert checks.commit_signed()
    mock_co.return_value = "N"
    assert not checks.commit_signed()


@mock.patch("codex.checks.commit_signed", return_value=True)
def test_verify_compliance(mock_signed):
    with tempfile.TemporaryDirectory() as tmp:
        mem = Path(tmp) / "memory.jsonl"
        _write_entries([{"event": "friction_alarm", "status": "pass"}], mem)
        rules = {"require_friction_alarm": True, "enforce_signed_commits": True}
        with mock.patch("codex.checks.load_rules", return_value=rules), \
             mock.patch("codex.checks.MEMORY_PATH", mem):
            assert checks.verify_compliance()
