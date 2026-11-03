"""Network Notes signup form: recoverable errors keep only a valid username."""

import re

import pytest

from app.features import accounts

pytestmark = pytest.mark.skipif(
    not any(
        getattr(route, "path", "") == "/api/me" for route in accounts.router.routes
    ),
    reason="Accounts (APP-002) are not implemented",
)

PASSWORD = "a disposable test password"


def _token(page_text):
    return re.search(r'name="csrf_token" value="([^"]+)"', page_text).group(1)


def test_short_password_keeps_valid_username_but_not_password(client):
    """A password mistake should not force retyping a valid username."""
    form = client.get("/signup")
    response = client.post(
        "/signup",
        data={
            "username": " Explorer_1 ",
            "password": "short",
            "csrf_token": _token(form.text),
        },
    )
    assert response.status_code == 422
    username = re.search(r'<input[^>]*name="username"[^>]*>', response.text).group(0)
    password = re.search(r'<input[^>]*name="password"[^>]*>', response.text).group(0)
    assert 'value="explorer_1"' in username
    assert "value=" not in password
    assert "short" not in password


def test_invalid_username_is_not_echoed_back(client):
    """Only a username that already meets the rules is retained in the form."""
    form = client.get("/signup")
    response = client.post(
        "/signup",
        data={
            "username": "<b>x</b>",
            "password": PASSWORD,
            "csrf_token": _token(form.text),
        },
    )
    assert response.status_code == 422
    username = re.search(r'<input[^>]*name="username"[^>]*>', response.text).group(0)
    assert "value=" not in username
