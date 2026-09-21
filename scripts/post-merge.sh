#!/usr/bin/env bash
set -euo pipefail

# Reconcile the environment exactly to the committed Python lockfile.
uv sync --frozen --no-dev

# Fail immediately if a merge introduced invalid Python syntax.
uv run python -m compileall -q \
  app.py main.py openai_service.py pdf_service.py translations.py test_app.py