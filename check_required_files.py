import os
import sys
import json

import yaml  # PyYAML


DEFAULT_REQUIRED_FILES = ["README.md", ".gitignore"]
CONFIG_FILE = ".required-files.yml"
REPORT_FILE = "required-files-report.json"


def load_required_files():
    """
    Load required files from .required-files.yml if present.
    Returns (required_files, used_config_file, error_message_or_None)
    """
    if not os.path.isfile(CONFIG_FILE):
        # No config -> use defaults
        return DEFAULT_REQUIRED_FILES, False, None

    try:
        with open(CONFIG_FILE, "r") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        return None, True, f"Error reading {CONFIG_FILE}: {e}"

    if not isinstance(data, dict) or "required_files" not in data:
        return None, True, f"{CONFIG_FILE} must contain a 'required_files' key"

    required_files = data["required_files"]

    if not isinstance(required_files, list) or not all(
        isinstance(f, str) for f in required_files
    ):
        return None, True, "'required_files' must be a list of strings"

    return required_files, True, None


def write_report(required_files, missing_files, used_config_file, error=None):
    report = {
        "used_config_file": used_config_file,
        "config_file": CONFIG_FILE if used_config_file else None,
        "required_files": required_files or [],
        "missing_files": missing_files,
    }
    if error:
        report["error"] = error

    with open(REPORT_FILE, "w") as f:
        json.dump(report, f)


def check_required_files():
    required_files, used_config_file, error = load_required_files()

    # Config problem -> write report + fail
    if error:
        write_report(required_files, [], used_config_file, error=error)
        print(f"Configuration error: {error}")
        return 1

    missing_files = []
    for filename in required_files:
        if not os.path.isfile(filename):
            missing_files.append(filename)

    write_report(required_files, missing_files, used_config_file)

    if missing_files:
        print("Missing required files:")
        for f in missing_files:
            print(" -", f)
        return 1

    print("All required files are present.")
    return 0


if __name__ == "__main__":
    sys.exit(check_required_files())
