# Required File Presence Checker

This project simulates an internal platform policy for CloudBank where every service repository must include baseline files before code can be merged or deployed. The system enforces required file standards using GitHub Actions and sends enriched audit logs to Amazon CloudWatch for both beta (pull request) and prod (push) environments.

---

## 1. What This Project Does

- Verifies required files exist in the repo.
- Supports custom file requirements via a `.required-files.yml` file.
- Fails pull requests or pushes if required files are missing or config is invalid.
- Runs automated unit tests (pytest) on every PR and merge.
- Sends structured audit logs to CloudWatch when all validations pass.

This ensures long-term consistency, quality enforcement, and observable CI events.

---

## 2. Repository Structure
check_required_files.py # Core validation logic
.required-files.yml # Optional override config
required-files-report.json # Generated validation summary
tests/test_required_files.py # Pytest unit tests
.github/workflows/on_pull_request.yml
.github/workflows/on_merge.yml
validation-screenshots/ # For CI checks, CloudWatch logs, and test output screenshots
README.md

---

## 3. Required File Logic

### Default Files (when no config file exists)
README.md
.gitignore


### Custom File Requirements

If `.required-files.yml` exists, it overrides the defaults.

Example:

```yaml
required_files:
  - README.md
  - .gitignore
  - .github/workflows/on_pull_request.yml
  - .github/workflows/on_merge.yml

Rules:

Must contain a top-level key required_files

Must be a list of strings

If malformed → script exits with error

4. Validation Output (required-files-report.json)

A successful check produces:
{
  "used_config_file": true,
  "config_file": ".required-files.yml",
  "required_files": ["README.md", ".gitignore"],
  "missing_files": [],
  "error": null
}

If files are missing:

Exit code = 1

missing_files contains the missing entries

If config is malformed:

Exit code = 1

error contains the message

This file is consumed by GitHub Actions to generate CloudWatch audit logs.

5. GitHub Actions Workflows
5.1 PR Workflow – Beta

.github/workflows/on_pull_request.yml

Trigger:

pull_request → main

Steps:

1. Checkout code

2. Set up Python

3. Install deps (pyyaml, pytest)

4. Run pytest

5. Run check_required_files.py

6. If all checks pass → Send audit log to:
/github-actions/required-files-checker/beta

5.2 Merge Workflow – Prod

.github/workflows/on_merge.yml

Trigger:

push → main

Same flow, but logs to:
/github-actions/required-files-checker/prod

Audit logs include:

Workflow name

Commit SHA

Actor

Branch

Event type

Repository

Full required-files-report.json

6. GitHub Secrets Required

Set these under:

Settings → Secrets and variables → Actions

| Secret Name             | Description            |
| ----------------------- | ---------------------- |
| `AWS_ACCESS_KEY_ID`     | IAM user key           |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret        |
| `AWS_REGION`            | Your region            |
| `LOG_GROUP_NAME`        | Beta or prod log group |


Log groups:
/github-actions/required-files-checker/beta
/github-actions/required-files-checker/prod

No AWS values are hardcoded anywhere.

7. CloudWatch Logging Behavior

On success, workflows:

Create a timestamp-based log stream

Read required-files-report.json

Build full JSON metadata payload

Send record using:

aws logs put-log-events

Find logs under:

Beta: /github-actions/required-files-checker/beta

Prod: /github-actions/required-files-checker/prod

8. Running Everything Locally
Install dependencies
pip install pyyaml pytest

Run the checker
python3 check_required_files.py
cat required-files-report.json
echo $?

Run unit tests
pytest

9. Unit Tests

Tests validate:

Required files present

Files missing

Valid config

Missing or malformed config

All PRs and merges must pass tests before CloudWatch logging runs.

10. CI Summary
On Pull Request → Beta

Run tests

Run file presence checker

If all succeed → log to CloudWatch beta

On Push → Prod

Run tests

Run file presence checker

If all succeed → log to CloudWatch prod

If tests fail OR required files are missing:
Workflow fails and NO log is written.

This ensures safety, consistency, and full auditability.




