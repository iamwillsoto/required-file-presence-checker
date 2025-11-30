import sys
import json
from pathlib import Path

# --- Fix Python import path so pytest can find check_required_files.py ---
ROOT = Path(__file__).resolve().parents[1]  # repo root
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Now this import will work
import check_required_files as checker


def write_file(path: Path):
    """Helper to create files for tests."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("test")


def test_all_required_files_present(tmp_path, monkeypatch):
    # Run inside a temporary directory that mimics the repo
    monkeypatch.chdir(tmp_path)

    # Create files expected by default config
    write_file(tmp_path / "README.md")
    write_file(tmp_path / ".gitignore")
    write_file(tmp_path / ".github/workflows/on_pull_request.yml")
    write_file(tmp_path / ".github/workflows/on_merge.yml")

    exit_code = checker.check_required_files()
    assert exit_code == 0

    report = json.loads((tmp_path / "required-files-report.json").read_text())
    assert report["missing_files"] == []


def test_missing_required_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # Only create README.md — missing others
    write_file(tmp_path / "README.md")

    exit_code = checker.check_required_files()
    assert exit_code == 1

    report = json.loads((tmp_path / "required-files-report.json").read_text())
    assert ".gitignore" in report["missing_files"]


def test_custom_config_valid(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # Custom config requiring only .gitignore
    (tmp_path / ".required-files.yml").write_text(
        "required_files:\n  - .gitignore\n"
    )
    write_file(tmp_path / ".gitignore")

    exit_code = checker.check_required_files()
    assert exit_code == 0


def test_config_malformed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # Intentionally broken YAML
    (tmp_path / ".required-files.yml").write_text("not: valid: yaml")

    exit_code = checker.check_required_files()
    assert exit_code == 1

    report = json.loads((tmp_path / "required-files-report.json").read_text())
    assert "error" in report
