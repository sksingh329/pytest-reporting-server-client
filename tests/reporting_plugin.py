"""
Pytest hooks that push each test's pass/fail result to the external
Test Reporting Server (see README for the REPORT_* env vars).

Reporting is best-effort: if the server env vars are unset, or a request
fails, we log a warning and never affect the test run's outcome.
"""
import logging
import os

import requests

logger = logging.getLogger("reporting_server")

_results = []
_in_progress = {}


def pytest_runtest_logreport(report):
    entry = _in_progress.setdefault(report.nodeid, {
        "test_name": report.nodeid,
        "status": "passed",
        "duration_ms": 0.0,
        "error_message": None,
        "log_parts": [],
        # pytest's caplog/capstdout/capstderr are cumulative since test start,
        # not per-phase deltas — track how much of each we've already used.
        "_cursors": {"caplog": 0, "capstdout": 0, "capstderr": 0},
    })

    cursors = entry["_cursors"]
    for field in ("caplog", "capstdout", "capstderr"):
        full_text = getattr(report, field) or ""
        new_text = full_text[cursors[field]:]
        cursors[field] = len(full_text)
        if new_text:
            entry["log_parts"].append(f"----- {report.when} ({field}) -----\n{new_text}")

    entry["duration_ms"] += report.duration * 1000

    if report.failed:
        entry["status"] = "failed"
        entry["log_parts"].append(f"----- {report.when} traceback -----\n{report.longreprtext}")
        if entry["error_message"] is None:
            entry["error_message"] = report.longreprtext
    elif report.skipped and entry["status"] == "passed":
        entry["status"] = "skipped"

    if report.when != "teardown":
        return

    entry = _in_progress.pop(report.nodeid)
    log_parts = entry.pop("log_parts")
    entry.pop("_cursors")
    entry["log_text"] = "\n\n".join(log_parts) or None
    _results.append(entry)


def pytest_sessionfinish(session, exitstatus):
    if os.environ.get("REPORT_ENABLED", "false").strip().lower() not in ("true", "1", "yes"):
        return

    url = os.environ.get("REPORT_SERVER_URL")
    project_id = os.environ.get("REPORT_PROJECT_ID")
    token = os.environ.get("REPORT_SERVICE_TOKEN")
    if not (url and project_id and token):
        return

    endpoint = f"{url.rstrip('/')}/api/projects/{project_id}/test-cases"
    environment = os.environ.get("API_ENV", "dev")

    for result in _results:
        payload = {"environment": environment, **result}
        payload = {k: v for k, v in payload.items() if v is not None}
        try:
            response = requests.post(
                endpoint,
                headers={"Authorization": f"Bearer {token}"},
                data=payload,
                timeout=10,
            )
            if not response.ok:
                logger.warning(
                    "Reporting server rejected result for %s: %s %s",
                    result["test_name"], response.status_code, response.text,
                )
        except requests.RequestException as e:
            logger.warning(
                "Failed to report test result for %s to reporting server: %s",
                result["test_name"], e,
            )
