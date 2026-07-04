"""
Root conftest — project-level fixture overrides and shared helpers.

The pytest-api-core plugin auto-registers `api_config` and a default
`api_client` fixture.  Override `api_client` here to inject the Bearer
token from the .env file so every authenticated test gets it for free.
"""
import random

import pytest
from pytest_api_core.auth.auth_handlers import BearerAuth
from pytest_api_core.client.api_client import APIClient
from pytest_api_core.config.env_loader import get_env
from faker import Faker

faker = Faker()


@pytest.fixture
def faker_seed():
    """Randomize Faker's seed per test instead of the plugin's fixed default (0)."""
    return random.random()


# ── Authenticated client (session-scoped) ────────────────────────────────────

@pytest.fixture(scope="session")
def api_client(api_config):
    """
    Overrides the default api_client to attach a BearerAuth handler.

    The token is read from the BEARER_TOKEN env var (set in .env).
    For gorest.in any non-empty string works; use 'blocked-token' to
    intentionally trigger 403 responses in negative auth tests.
    """
    token = get_env("BEARER_TOKEN", required=True)
    client = APIClient(
        base_url=api_config["base_url"],
        auth=BearerAuth(token),
        timeout=api_config.get("timeout", 30),
        verify_ssl=api_config.get("verify_ssl", True),
        default_headers=api_config.get("headers"),
    )
    yield client
    client.close()


@pytest.fixture(scope="session")
def base_url(api_config):
    """Convenience fixture — exposes the resolved base URL as a plain string."""
    return api_config["base_url"]


@pytest.fixture
def new_user_payload():
    first = faker.first_name_male()
    last =  faker.last_name_male()
    uid = faker.uuid4()[:8]
    return {
        "name": f"{first} {last}",
        "email": f"{first.lower()}.{last.lower()}.{uid}@{faker.free_email_domain()}",
        "gender": "male",
        "status": "active",
    }

