"""APP-003: a server-enforced member/admin boundary for Network Notes.

Authentication (``security.authenticate``) answers "who is asking?";
authorization here answers "may they do this?". The role is read from the
database on every request, so a promotion or downgrade applies to existing
sessions, and a role claim inside a JWT is never trusted. Roles change only
through the trusted local command ``studio.py user role``.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app import security
from app.database import connect

router = APIRouter()


def _accounts(request: Request) -> list[dict[str, str]]:
    """Public account fields only: never hashes, IDs or session data."""
    with connect(request.app.state.settings) as connection:
        rows = connection.execute(
            "SELECT username, role FROM users ORDER BY role, username"
        ).fetchall()
    return [{"username": row["username"], "role": row["role"]} for row in rows]


@router.get("/api/admin")
def api_admin(request: Request, _admin: dict = Depends(security.require_admin)):
    """Anonymous → 401, member → 403, admin → 200 with the account list."""
    accounts = _accounts(request)
    return {"accounts": accounts, "count": len(accounts)}


@router.get("/admin", include_in_schema=False)
def admin_page(request: Request):
    """The same boundary for the HTML page, checked on every request."""
    user = security.authenticate(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    templates = request.app.state.templates
    if user["role"] != "admin":
        return templates.TemplateResponse(
            request=request,
            name="admin.html",
            context={"allowed": False, "user": user},
            status_code=403,
        )
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={"allowed": True, "user": user, "accounts": _accounts(request)},
    )
