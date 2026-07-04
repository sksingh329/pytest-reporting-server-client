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

    def test_create_user(self, api_client, new_user_payload):
        response = api_client.post(USERS_PATH, json=new_user_payload)
        assert_that(response) \
            .status_is(201) \
            .has_key("id") \
            .key_equals("name", new_user_payload["name"]) \
            .key_equals("email", new_user_payload["email"]) \
            .json_path("$.status").equals(new_user_payload["status"]) \
            .key_equals("gender", new_user_payload["gender"])


    def test_create_user_duplicate_email(self, api_client, new_user_payload, created_user):
        duplicate_payload = {**new_user_payload, "email": created_user["email"]}

        response = api_client.post(USERS_PATH, json=duplicate_payload)
        assert_that(response) \
            .status_is(422) \
            .json_path("$[0].field").equals("email") \
            .json_path("$[0].message").equals("has already been taken")

    def test_get_user(self, api_client, created_user):
        user_id = created_user["id"]

        get_response = api_client.get(f"{USERS_PATH}/{user_id}")
        assert_that(get_response) \
            .status_is(200) \
            .key_equals("id", user_id) \
            .key_equals("name", created_user["name"]) \
            .key_equals("email", created_user["email"]) \
            .key_equals("gender", created_user["gender"]) \
            .key_equals("status", created_user["status"])

    def test_delete_user(self, api_client, created_user):
        user_id = created_user["id"]

        delete_response = api_client.delete(f"{USERS_PATH}/{user_id}")
        assert_that(delete_response).status_is(204)

        get_response = api_client.get(f"{USERS_PATH}/{user_id}")
        assert_that(get_response).status_is(404)

    def test_update_user(self, api_client, created_user):
        user_id = created_user["id"]
        updated_name = f"{created_user['name']} Updated"
        updated_payload = {**created_user, "name": updated_name}

        put_response = api_client.put(f"{USERS_PATH}/{user_id}", json=updated_payload)
        assert_that(put_response) \
            .status_is(200) \
            .key_equals("name", updated_name)

        get_response = api_client.get(f"{USERS_PATH}/{user_id}")
        assert_that(get_response) \
            .status_is(200) \
            .key_equals("name", updated_name)

    def test_patch_user(self, api_client, created_user):
        user_id = created_user["id"]
        updated_status = "inactive" if created_user["status"] == "active" else "active"

        patch_response = api_client.patch(f"{USERS_PATH}/{user_id}", json={"status": updated_status})
        assert_that(patch_response) \
            .status_is(200) \
            .key_equals("status", updated_status) \
            .key_equals("name", created_user["name"]) \
            .key_equals("email", created_user["email"]) \
            .key_equals("gender", created_user["gender"])

        get_response = api_client.get(f"{USERS_PATH}/{user_id}")
        assert_that(get_response) \
            .status_is(200) \
            .key_equals("status", updated_status) \
            .key_equals("name", created_user["name"]) \
            .key_equals("email", created_user["email"]) \
            .key_equals("gender", created_user["gender"])