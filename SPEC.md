# App Studio decisions

The durable agreement between learner and AI. Update only agreed decisions and
actual evidence; pending is a valid state. Keep explanations/help in
[LEARNING.md](LEARNING.md), not a second copy here.

## Current stage

- **Current feature:** APP-002.
- **Status:** APP-001 kept and merged. APP-002 implemented and checked locally; learner contributions recorded and reviewed; PR pending.
- **Next step:** Open the APP-002 PR and wait for `check` and `windows` CI.
- **Implementation marker:** `studio.json` is `implemented_through: 2` (set after the APP-002 contracts passed).

This repository owns application code. Server/proxy changes and production
deployment are outside these three local-development lessons. Prepared helpers
are reusable foundations, not evidence that unfinished routes are implemented.

## APP-001 · Branded homepage

**Scope:** make the neutral FastAPI homepage express one chosen identity with
a simple original SVG mark, coherent copy, navigation and shared style tokens.
Keep account actions honest about their unfinished state.

| Decision | Agreement |
|---|---|
| Visitor and concrete use situation | A person interested in network engineering who wants to discover new network advances |
| Reused IS117 brand, or name / promise / primary archetype | New brand: **Network Notes** · promise "Concise, Clear, and Consistent Networking News" · primary archetype **Explorer** (chosen by learner; reason in LEARNING.md) |
| One visible choice and visitor benefit | Colors: dark server-room navy, blue-green server hues and gold circuit-trace accents (learner's prediction in LEARNING.md) |
| Own issue / branch / PR | [Issue #1](https://github.com/DylanJHrusko/my-app-studio/issues/1) · branch `app-001-homepage` · PR pending |

**Keep when:** the agreed identity is visible and usable at desktop/narrow widths;
full foundation + APP-001 checks pass; AI review and the learner's actual check
interpretation/browser observation/keep reason are recorded; reviewed evidence
and verified GitHub state are linked below.

## APP-002 · Signup, login and logout

**Scope:** add browser forms and REST behavior for member signup, login, a private
dashboard and logout backed by SQLite. Reuse the prepared password/JWT/CSRF/session
helpers; keep data local. New accounts cannot choose their role.

| Decision | Agreement |
|---|---|
| Expected public/private behavior and account flow | Anonymous `/dashboard` redirects to the Log in page and `GET /api/me` returns 401; after login the member space shows username and role. Sessions expire after 15 minutes; Log out revokes the session on the server. Signup → Log in → "Your member space" → Log out. New accounts are members only. |
| Valid and rejected cases to demonstrate | Valid signup (201, member, Argon2 hash) and login (200, HttpOnly SameSite=Lax cookie, no token in JSON). Rejected: duplicate username 409; short/long fields and `role` injection 422; wrong password/unknown user same generic 401; 5 failures → 429; missing/wrong/cross-origin CSRF 403; GET logout 405; copied cookie after logout 401. |
| Own issue / branch / PR | [Issue #3](https://github.com/DylanJHrusko/my-app-studio/issues/3) · branch `app-002-accounts` · PR pending |

**Keep when:** the agreed forms/API work; duplicate/invalid signup and wrong
credentials are rejected; passwords are hashed; authentication uses validated,
expiring JWTs with protected cookies and CSRF; private requests require a live
session and logout revokes it. Full cumulative checks, AI review, actual learner
contributions and GitHub state are recorded. This is not a production-security certification.

## APP-003 · Server-enforced roles

**Scope:** enforce a small member/admin boundary in the API and browser. Assign
roles only through the trusted local terminal command; use current server-side
permissions, including for an existing session after a role change.

| Visitor | Homepage | Member area | Admin area/API |
|---|---|---|---|
| Anonymous | Allowed | Login required | Login required |
| Member | Allowed | Allowed | Forbidden |
| Admin | Allowed | Allowed | Allowed |

| Decision | Agreement |
|---|---|
| Intended admin-only result | Pending |
| Actual allowed/denied request evidence | Pending |
| Own issue / branch / PR | Pending |

**Keep when:** a direct request cannot bypass the role boundary, role changes
take effect as specified, new signup remains member-only, and full cumulative
checks plus AI review pass. Link the learner's actual interpretation/observation,
reviewed record and verified GitHub result. Hidden navigation alone is insufficient.

## Evidence

Link actual files/checks and the student's own issues/PRs. No fabricated URLs,
customer research or claims that a timestamp proves learning.

| Feature | Files / own issue / PR | Actual checks and learner observations | Kept / GitHub state |
|---|---|---|---|
| APP-001 | `app/brand.json`, `app/static/logo.svg`, `app/static/site.css`, `app/templates/home.html`, `app/templates/base.html`, `studio.json` · [issue #1](https://github.com/DylanJHrusko/my-app-studio/issues/1) | `check --lesson APP-001` and full `check` passed locally on Nov 3, 2026 (Black, Pylint, 98 foundation tests, 2 APP-001 contracts, 2 Chromium journeys). AI review: desktop and 390px layouts without horizontal scroll, Skip-link first in tab order, contrast ≥ 6.7:1 for all text pairs. Learner contributions in [LEARNING.md](LEARNING.md#app-001) | Kept by learner · [PR #2](https://github.com/DylanJHrusko/my-app-studio/pull/2) · CI `check` + `windows` passed ([run 41697660206](https://github.com/DylanJHrusko/my-app-studio/actions/runs/41697660206)) · merge closes issue #1 |
| APP-002 | `app/features/accounts.py`, `app/templates/signup.html`, `login.html`, `dashboard.html`, `tests/test_signup_form.py`, `studio.json` · [issue #3](https://github.com/DylanJHrusko/my-app-studio/issues/3) | `check --lesson APP-002` and full `check` passed locally on Nov 3, 2026 (Black, Pylint, 100 foundation/added tests, 14 contracts through APP-002, 2 Chromium journeys). AI review on a throwaway database: anonymous dashboard → Log in; short password keeps only a valid username; wrong password generic error; logout → `/api/me` 401; 390px layout without horizontal scroll; no password in the server log. Learner contributions in [LEARNING.md](LEARNING.md#app-002) | Kept by learner; PR pending |
| APP-003 | Pending | Unfinished; explicit contracts not yet passed | Pending |

The instructor's reference branches show possible implementations. They do not
establish this repository's completion or the learner's own reasoning.
