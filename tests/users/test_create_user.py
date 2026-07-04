import pytest
from pytest_api_core.assertions import assert_that


"""
GET /public/v2/users  — list & single-user read tests.

All GETs on gorest.in are public (no auth required), but the session-scoped
api_client from conftest already carries a Bearer token, so these work fine
with or without auth.

Endpoints:
  GET /public/v2/users          — paginated list, filterable
  GET /public/v2/users/:id      — single user by ID
"""

USERS_PATH = "/public/v2/users"

@pytest.mark.user
class TestUsers:

    def test_create_user_flow(self, api_client, new_user_payload):
        response = api_client.post(USERS_PATH, json=new_user_payload)
        assert_that(response) \
            .status_is(201) \
            .has_key("id") \
            .key_equals("name", new_user_payload["name"]) \
            .key_equals("email", new_user_payload["email"]) \
            .json_path("$.status").equals(new_user_payload["status"]) \
            .key_equals("gender", new_user_payload["gender"])

