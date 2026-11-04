"""Network Notes admin list: an admin sees usernames and roles, never secrets."""

import pytest

from app import database
from app.features import roles

pytestmark = pytest.mark.skipif(
    not any(
        getattr(route, "path", "") == "/api/admin" for route in roles.router.routes
    ),
    reason="Roles (APP-003) are not implemented",
)


def test_admin_account_list_exposes_only_username_and_role(client, settings):
    """The admin view must not leak password hashes, IDs or session data."""
    credentials = {"username": "explorer", "password": "a disposable test password"}
    headers = {"X-CSRF-Token": client.get("/api/csrf").json()["csrf_token"]}
    client.post("/api/signup", json=credentials, headers=headers)
    client.post("/api/login", json=credentials, headers=headers)
    assert database.set_role(settings, "explorer", "admin")
    body = client.get("/api/admin").json()
    assert body["count"] == 1
    assert body["accounts"] == [{"username": "explorer", "role": "admin"}]
    page = client.get("/admin").text
    assert "argon2" not in client.get("/api/admin").text and "argon2" not in page
