# Threat Model

## Project Overview

"Ancient Wisdom Face Analysis" is a Flask (Python 3.11) server-rendered web app deployed on
Replit autoscale via gunicorn (`main:app`). Users upload a face photo, pay €29.99 through
Stripe hosted checkout (or use a promo code), and receive an AI-generated PDF report produced
by the Replit-managed OpenAI vision integration. There is no database; all state is held in
signed Flask session cookies and temporary files under the OS temp dir. Users are anonymous
(no accounts, despite a misleading git commit message about "registration/login").

Key files: `app.py` (routes), `openai_service.py` (OpenAI calls), `pdf_service.py` (ReportLab),
`translations.py` (i18n), `templates/*.html`.

## Assets

- **OpenAI/Stripe budget** — the Replit-managed OpenAI integration and Stripe are billable.
  Unauthenticated access to expensive model calls is a direct financial-loss asset.
- **Application secrets** — `SESSION_SECRET`, `STRIPE_SECRET_KEY`, `AI_INTEGRATIONS_OPENAI_*`
  provided via environment variables.
- **Uploaded photos & generated reports** — PII (a person's face) held transiently in temp files
  and referenced by UUID in the session.
- **Payment integrity** — the €29.99 gate before an analysis is produced.

## Trust Boundaries

- **Browser → Flask** — every request is untrusted. State-changing endpoints: `/upload`,
  `/check-promo-code`, `/free-analysis`, `/create-checkout-session`, `/translate`,
  `/success`, `/download-pdf`.
- **Flask → Stripe** — payment verified server-side in `/success` by retrieving the checkout
  session and checking `payment_status == 'paid'` against the session-stored id.
- **Flask → OpenAI** — server sends image/text to the managed OpenAI endpoint.
- **Session cookie boundary** — all authorization/state (uploaded_file, report_id,
  analysis_complete, free_analysis, stripe_session_id) lives in the client-held signed cookie;
  its integrity depends entirely on `SESSION_SECRET`.

## Scan Anchors

- Production entry points: all routes in `app.py`. Deployment run cmd: `gunicorn main:app`.
- Highest-risk areas: session-based payment/authorization state (`app.py`), unauthenticated
  `/translate` and `/free-analysis` endpoints (billable AI calls).
- Public surface: entire app is unauthenticated (anonymous users).
- File-path handling in `app.py` (`uploaded_path`, `report_path`, `analysis_path`) validates
  `filename == os.path.basename(filename)` and confirms the resolved dirname — this mitigates
  the SAST path-traversal findings at lines 59/85/395 and openai_service.py:20, which are
  effectively false positives. Uploads use `secure_filename` + UUID and are re-encoded via PIL.
- No dev-only/mockup directories of concern.

## Threat Categories

### Spoofing / Tampering (session integrity)

All payment and authorization state is stored in the Flask signed session cookie. `app.py`
falls back to a hardcoded `SESSION_SECRET` default (`"dev-secret-key-change-in-production"`)
when the env var is unset. If deployed without `SESSION_SECRET`, an attacker can forge session
cookies (e.g. `free_analysis`, `analysis_complete`) and bypass the payment gate. Guarantee:
`SESSION_SECRET` MUST be a strong secret and the app MUST refuse to run with the default in
production.

### Denial of Service / Resource abuse (financial)

`/translate` performs an unauthenticated OpenAI chat completion on attacker-supplied text with
no auth, no rate limiting, and no payment gate — a free LLM proxy that drains the OpenAI budget.
The hardcoded promo code `letsgo` plus `/free-analysis` allows unlimited free vision analyses to
anyone who knows the code, again with no rate limiting. Guarantee: billable AI calls MUST be
rate-limited and gated; secrets/backdoor codes MUST NOT be hardcoded in source.

### Information Disclosure

`/success` renders raw `str(e)` exception text to the user on analysis failure — minor internal
detail leakage. Uploaded photos and reports are transient and deleted after download.
