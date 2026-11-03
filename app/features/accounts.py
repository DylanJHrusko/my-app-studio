"""APP-002: signup, login, a private dashboard and logout for Network Notes.

Every route reuses the prepared helpers in ``app.security``: Argon2 password
hashes, signed expiring JWT sessions in an HttpOnly cookie, server-side session
revocation, CSRF synchronizer tokens and login/signup throttling. HTML forms and
the JSON API call the same functions, so both enforce the same rules.
"""

import re

from fastapi import APIRouter, Depends, Form, Header, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app import security
from app.schemas import LoginInput, PublicUser, SignupInput

router = APIRouter()

USERNAME = re.compile(r"[a-z0-9_]{3,32}")

FIELD_HELP = (
    "Use a 3–32 character username (letters, numbers or underscores) "
    "and a password of 15–128 characters."
)


def _render(request: Request, name: str, context: dict, status_code: int = 200):
    """Render a page with a valid CSRF token, carrying any new pre-login cookie."""
    carrier = Response()
    token = security.csrf_token(request, carrier)
    page = request.app.state.templates.TemplateResponse(
        request=request,
        name=name,
        context={**context, "csrf_token": token},
        status_code=status_code,
    )
    for key, value in carrier.raw_headers:
        if key == b"set-cookie":
            page.raw_headers.append((key, value))
    return page


def _valid_username(username: str) -> str:
    """Return the normalized username only if it passes the signup rules."""
    normalized = username.strip().lower()
    return normalized if USERNAME.fullmatch(normalized) else ""


def _form_error(request, name, username, error):
    """Show a recoverable form, keeping only an already validated username."""
    return _render(
        request,
        name,
        {"username": username, "error": error.detail},
        status_code=error.status_code,
    )


# --- JSON API ---------------------------------------------------------------


@router.get("/api/csrf")
def api_csrf(request: Request, response: Response):
    """Start or reuse a server session and return its CSRF token."""
    return {"csrf_token": security.csrf_token(request, response)}


@router.post("/api/signup", status_code=201, response_model=PublicUser)
def api_signup(
    request: Request,
    credentials: SignupInput,
    x_csrf_token: str | None = Header(default=None),
):
    """Create a member. The schema forbids extra fields such as ``role``."""
    security.require_csrf(request, x_csrf_token)
    security.limit_signup(request)
    return security.signup(
        request.app.state.settings, credentials.username, credentials.password
    )


@router.post("/api/login", response_model=PublicUser)
def api_login(
    request: Request,
    response: Response,
    credentials: LoginInput,
    x_csrf_token: str | None = Header(default=None),
):
    """Authenticate and set the session cookie; the token is never in the JSON."""
    security.require_csrf(request, x_csrf_token)
    return security.login(request, response, credentials.username, credentials.password)


@router.get("/api/me", response_model=PublicUser)
def api_me(user: dict = Depends(security.require_user)):
    """Return the current member, or 401 when there is no live session."""
    return user


@router.post("/api/logout")
def api_logout(
    request: Request,
    response: Response,
    x_csrf_token: str | None = Header(default=None),
):
    """Revoke the session on the server, then clear the browser cookie."""
    security.require_csrf(request, x_csrf_token)
    security.logout(request, response)
    return {"detail": "Logged out."}


# --- HTML pages ---------------------------------------------------------------


@router.get("/signup", include_in_schema=False)
def signup_page(request: Request):
    """Show the signup form."""
    return _render(request, "signup.html", {"username": ""})


@router.post("/signup", include_in_schema=False)
def signup_form(
    request: Request,
    username: str = Form(default=""),
    password: str = Form(default=""),
    csrf_token: str = Form(default=""),
):
    """Create a member from the HTML form, then send them to log in."""
    try:
        security.require_csrf(request, csrf_token)
        security.limit_signup(request)
        try:
            credentials = SignupInput(username=username, password=password)
        except ValidationError as error:
            raise HTTPException(422, FIELD_HELP) from error
    except HTTPException as error:
        return _form_error(request, "signup.html", _valid_username(username), error)
    try:
        security.signup(
            request.app.state.settings, credentials.username, credentials.password
        )
    except HTTPException as error:
        return _form_error(request, "signup.html", credentials.username, error)
    return RedirectResponse("/login?created=1", status_code=303)


@router.get("/login", include_in_schema=False)
def login_page(
    request: Request, created: str | None = None, logged_out: str | None = None
):
    """Show the login form, with a confirmation after signup or logout."""
    notice = ""
    if created == "1":
        notice = "Account created. Log in to continue."
    elif logged_out == "1":
        notice = "You are logged out. Your session has ended on the server."
    return _render(request, "login.html", {"username": "", "notice": notice})


@router.post("/login", include_in_schema=False)
def login_form(
    request: Request,
    username: str = Form(default=""),
    password: str = Form(default=""),
    csrf_token: str = Form(default=""),
):
    """Log in from the HTML form and continue to the private dashboard."""
    try:
        security.require_csrf(request, csrf_token)
        credentials = LoginInput(username=username, password=password)
    except ValidationError:
        error = HTTPException(401, "The username or password is incorrect.")
        return _form_error(request, "login.html", "", error)
    except HTTPException as error:
        return _form_error(request, "login.html", "", error)
    destination = RedirectResponse("/dashboard", status_code=303)
    try:
        security.login(request, destination, credentials.username, credentials.password)
    except HTTPException as error:
        return _form_error(request, "login.html", credentials.username, error)
    return destination


@router.get("/dashboard", include_in_schema=False)
def dashboard(request: Request):
    """Private member space; anonymous visitors are sent to the login page."""
    user = security.authenticate(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    return _render(request, "dashboard.html", {"user": user})


@router.post("/logout", include_in_schema=False)
def logout_form(request: Request, csrf_token: str = Form(default="")):
    """Revoke the current session from the dashboard's Log out button."""
    try:
        security.require_csrf(request, csrf_token)
    except HTTPException:
        return RedirectResponse("/dashboard", status_code=303)
    destination = RedirectResponse("/login?logged_out=1", status_code=303)
    security.logout(request, destination)
    return destination
