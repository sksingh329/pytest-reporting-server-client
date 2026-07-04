# pytest-api-core — Quickstart Template

> A ready-to-use API test project built on [`pytest-api-core`](https://pypi.org/project/pytest-api-core/), targeting the [gorest.in](https://www.gorest.in/) mock REST API.

## Features

- Example test for `/public/v2/users` (more CRUD examples coming)
- Environment-aware config (`dev` / `staging` / `prod`)
- `.env` file support for secrets
- Self-contained HTML test report with charts and request/response details
- Optional remote reporting: every test's pass/fail result, duration, and full
  setup/call/teardown logs can be pushed to a [Test Reporting Server](#test-reporting-server-integration)

---

## Quick Start

```bash
# 1. Clone (or use this as a GitHub template)
git clone git@github.com:sksingh329/pytest-api-core-framework.git
cd pytest-api-core-framework

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — set BEARER_TOKEN (any non-empty string works for gorest.in)

# 5. Run all tests
pytest

# 6. Run only smoke tests
pytest -m smoke

# 7. Run against staging
pytest --api-env=staging
```

The HTML report is written to `reports/dev/report_<timestamp>.html`.

---

## Project Layout

```
.
├── config/
│   └── settings.py          # Dev / Staging / Prod environment classes
├── tests/
│   ├── conftest.py          # Session-scoped api_client with BearerAuth, fixtures
│   ├── reporting_plugin.py  # Pushes each test's result to the Test Reporting Server
│   └── users/
│       └── test_create_user.py
├── reports/                 # Generated HTML reports (git-ignored)
├── .env.example             # Copy to .env and fill in secrets
├── pytest.ini               # Framework + report + logging config
└── requirements.txt
```

---

## Configuration

### pytest.ini options

| Option                | Description                          | Default  |
|-----------------------|--------------------------------------|----------|
| `api_env`             | Active environment                   | `dev`    |
| `api_settings_module` | Dotted path to settings module       | —        |
| `api_dotenv_file`     | Path to `.env` file                  | `.env`   |
| `api_html_theme`      | Report theme: `light` or `dark`      | `dark`   |

### Environment variables (`.env`)

| Variable       | Purpose                                |
|----------------|----------------------------------------|
| `BEARER_TOKEN` | Auth token for write operations        |
| `API_BASE_URL` | Override the base URL from settings    |
| `API_ENV`      | Override `api_env` from `pytest.ini`   |
| `API_TIMEOUT`  | Request timeout in seconds             |
| `REPORT_ENABLED`        | Must be explicitly `true` to enable remote reporting. Default (missing/anything else): disabled. |
| `REPORT_SERVER_URL`     | Base URL of the Test Reporting Server (e.g. `https://api.dev.report.subodhsingh.in`). If unset, remote reporting is skipped. |
| `REPORT_PROJECT_ID`     | Project ID on the reporting server to report test results into |
| `REPORT_SERVICE_TOKEN`  | Service token for authenticating with the reporting server      |

### Markers

| Marker       | Description                                |
|--------------|--------------------------------------------|
| `smoke`      | Fast sanity checks — run on every commit   |
| `regression` | Full regression suite                      |
| `user`       | Tests covering the `/public/v2/users` API  |

---

## Test Reporting Server integration

`tests/reporting_plugin.py` is a pytest plugin (registered in `tests/conftest.py`
via `pytest_plugins = ["tests.reporting_plugin"]`) that pushes every test's
result — pass/fail status, duration, error message, and full setup + call +
teardown logs — to an external **Test Reporting Server** at the end of the run.
It requires no changes as you add new tests; it hooks into pytest's generic
`pytest_runtest_logreport` / `pytest_sessionfinish` events and picks up every
test automatically.

Reporting is entirely optional and best-effort:

- `REPORT_ENABLED` must be explicitly set to `true` to opt in. If it's missing,
  or any of the other required env vars (below) is unset, reporting is
  skipped silently.
- If a request to the server fails (network error, bad token, server down),
  a warning is logged — the test run's pass/fail outcome is never affected.

### Setup

1. On the reporting server, create (or obtain) a **project** and a **service
   token** scoped to it — this repo does not create these for you.
2. Add the following to your `.env` (see `.env.example`):

   ```bash
   REPORT_ENABLED=true
   REPORT_SERVER_URL=https://api.dev.report.subodhsingh.in
   REPORT_PROJECT_ID=1
   REPORT_SERVICE_TOKEN=your-service-token
   ```

3. Run tests as usual — `pytest`. Results appear on the reporting server's
   dashboard under the configured project, tagged with the active environment
   (`API_ENV`, default `dev`).

To temporarily stop sending reports without losing your project ID/token,
just set `REPORT_ENABLED=false` (or remove/comment it out) — no need to
comment out the other values.

### What gets sent

Per test, a `POST /api/projects/{project_id}/test-cases` request is made with:

| Field         | Source                                                          |
|---------------|------------------------------------------------------------------|
| `test_name`   | The test's pytest node ID (e.g. `tests/users/test_create_user.py::TestUsers::test_get_user`) |
| `status`      | `passed` / `failed` / `skipped`                                  |
| `duration_ms` | Combined duration of setup + call + teardown                     |
| `error_message` | Traceback text, if the test failed                              |
| `log_text`    | Combined logs/captured stdout & stderr across setup, call, and teardown (deduplicated — each phase's *new* output only) |
| `environment` | Value of `API_ENV` (default `dev`)                                |

> **Note:** the reporting server's live API currently requires the field name
> `status`, even though its published OpenAPI docs (`/docs`) list it as
> `test_status` — this was verified against the running server.

---

## gorest.in API Summary

| Method | Path                  | Auth   | Description         |
|--------|-----------------------|--------|---------------------|
| GET    | /public/v2/users      | No     | List users          |
| POST   | /public/v2/users      | Yes    | Create user         |
| GET    | /public/v2/users/:id  | No     | Get user by ID      |
| PUT    | /public/v2/users/:id  | Yes    | Full replace        |
| PATCH  | /public/v2/users/:id  | Yes    | Partial update      |
| DELETE | /public/v2/users/:id  | Yes    | Delete user         |

Any non-empty string is a valid token. Use `blocked-token` to trigger 403.

---

## License

MIT
