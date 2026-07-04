"""
Environment settings for the GoRest API test suite.

Resolution order (highest → lowest priority):
  1. Shell / CI environment variables (API_BASE_URL, API_TOKEN, …)
  2. --api-base-url CLI flag
  3. ENVIRONMENTS[env] class defined here
  4. Built-in framework defaults
"""
import os
from pytest_api_core.config.base_settings import BaseSettings


class DevSettings(BaseSettings):
    base_url = "https://gorest.in"
    timeout = 30
    verify_ssl = True
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


class StagingSettings(DevSettings):
    """Staging mirrors dev for gorest.in; override base_url for your own staging env."""
    base_url = os.environ.get("API_BASE_URL", "https://gorest.in")
    timeout = 60


class ProdSettings(DevSettings):
    """Read-only prod checks — point at your real prod base URL."""
    base_url = os.environ.get("API_BASE_URL", "https://gorest.in")
    timeout = 60


ENVIRONMENTS = {
    "dev":     DevSettings,
    "staging": StagingSettings,
    "prod":    ProdSettings,
}
