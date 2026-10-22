"""Vercel entry point: serves the Flask API in artifacts/api-server under /api."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'artifacts', 'api-server'))

from app import app  # noqa: E402,F401
