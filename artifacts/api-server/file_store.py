"""Durable copies of temporary files for serverless hosting.

On a single long-running server (Replit) uploads and reports live in the
temp folder between requests. On Vercel each request may run on a different
instance with its own empty /tmp, so with FILE_STORE=postgres every file the
API writes is also stored in PostgreSQL and restored into /tmp on demand.
Without FILE_STORE the functions below do nothing.
"""
import logging
import os
import time
from pathlib import Path

import psycopg2

FILE_TTL_SECONDS = 24 * 60 * 60
_SCHEMA_SQL = Path(__file__).with_name('sql') / 'vercel.sql'
_schema_ready = False


def enabled():
    return os.environ.get('FILE_STORE', '').strip().lower() == 'postgres'


def _connect():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise RuntimeError('DATABASE_URL is required when FILE_STORE=postgres')
    connection = psycopg2.connect(database_url, connect_timeout=10)
    global _schema_ready
    if not _schema_ready:
        # Serverless deployments have no separate migration step; the
        # statements are idempotent (IF NOT EXISTS).
        with connection, connection.cursor() as cursor:
            cursor.execute(_SCHEMA_SQL.read_text(encoding='utf-8'))
        _schema_ready = True
    return connection


def _key(path):
    folder, name = os.path.split(os.path.abspath(path))
    return f'{os.path.basename(folder)}/{name}'


def save(path):
    """Store the file at path; failures are logged and re-raised."""
    if not enabled() or not path:
        return
    with open(path, 'rb') as handle:
        data = handle.read()
    now = int(time.time())
    connection = _connect()
    try:
        with connection, connection.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO stored_files (key, data, expires_at) VALUES (%s, %s, %s)
                   ON CONFLICT (key) DO UPDATE SET data = EXCLUDED.data, expires_at = EXCLUDED.expires_at''',
                (_key(path), psycopg2.Binary(data), now + FILE_TTL_SECONDS),
            )
            cursor.execute('DELETE FROM stored_files WHERE expires_at <= %s', (now,))
    finally:
        connection.close()


def fetch(path):
    """Make sure path exists locally, restoring it from storage if needed."""
    if not path or os.path.exists(path) or not enabled():
        return bool(path) and os.path.exists(path)
    try:
        connection = _connect()
        try:
            with connection, connection.cursor() as cursor:
                cursor.execute(
                    'SELECT data FROM stored_files WHERE key = %s AND expires_at > %s',
                    (_key(path), int(time.time())),
                )
                row = cursor.fetchone()
        finally:
            connection.close()
    except Exception:
        logging.exception('Unable to restore a stored file')
        return False
    if not row:
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary = f'{path}.restore'
    with open(temporary, 'wb') as handle:
        handle.write(bytes(row[0]))
    os.replace(temporary, path)
    return True


def delete(path):
    if not enabled() or not path:
        return
    try:
        connection = _connect()
        try:
            with connection, connection.cursor() as cursor:
                cursor.execute('DELETE FROM stored_files WHERE key = %s', (_key(path),))
        finally:
            connection.close()
    except Exception:
        logging.warning('Unable to delete a stored file')
