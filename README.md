# pytest-api-core — Quickstart Template

> A ready-to-use API test project built on [`pytest-api-core`](https://pypi.org/project/pytest-api-core/), targeting the [gorest.in](https://www.gorest.in/) mock REST API.

## Features

- Example test for `/public/v2/users` (more CRUD examples coming)
- Environment-aware config (`dev` / `staging` / `prod`)
- `.env` file support for secrets
- Self-contained HTML test report with charts and request/response details

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
│   ├── conftest.py          # Session-scoped api_client with BearerAuth
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

### Markers

| Marker       | Description                                |
|--------------|--------------------------------------------|
| `smoke`      | Fast sanity checks — run on every commit   |
| `regression` | Full regression suite                      |
| `user`       | Tests covering the `/public/v2/users` API  |

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
