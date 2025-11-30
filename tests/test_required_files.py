import json
from pathlib import Path
import sys

# Make sure repo root is on sys.path so we can import check_required_files
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import check_required_files as checker  # noqa: E402


def write_file(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("test")


def test_all_required_files_present(tmp_path, monkeypatch):
    # Work in an isolated temp directory
    monkeypatch.chdir(tmp_path)

    # Create files expected by DEFAULT_REQUIRED_FILES
    write_file(tmp_path / "README.md")
    write_file(tmp_path / ".gitignore")

    exit_code = checker.check_required_files()
    assert exit_code == 0

    report = json.loads((tmp_path / "required-files-report.json").read_text())
    assert report["missing_files"] == []


def test_missing_required_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # Only create README.md, not .gitignore
    write_file(tmp_path / "README.md")

    exit_code = checker.check_required_files()
    assert exit_code == 1

    report = json.loads((tmp_path / "required-files-report.json").read_text())
    assert ".gitignore" in report["missing_files"]


def test_custom_config_valid(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # Custom config that only requires .gitignore
    (tmp_path / ".required-files.yml").write_text(
        "required_files:\n  - .gitignore\n"
    )
    write_file(tmp_path / ".gitignore")

    exit_code = checker.check_required_files()
    assert exit_code == 0

    report = json.loads((tmp_path / "required-files-report.json").read_text())
    assert report["missing_files"] == []


def test_config_malformed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # Intentionally bad config
    (tmp_path / ".required-files.yml").write_text("not: valid: yaml")

    exit_code = checker.check_required_files()
    assert exit_code == 1

    report = json.loads((tmp_path / "required-files-report.json").read_text())
    assert "error" in report
