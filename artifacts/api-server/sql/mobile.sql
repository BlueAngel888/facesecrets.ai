-- Development schema for the mobile API's PostgreSQL-backed sessions and redemptions.
-- Apply this manually to the development database before enabling the mobile API.

CREATE TABLE mobile_devices (
    device_token_hash TEXT PRIMARY KEY,
    rc_app_user_id TEXT NOT NULL UNIQUE,
    created_at BIGINT NOT NULL
);

CREATE TABLE mobile_sessions (
    token_hash TEXT PRIMARY KEY,
    expires_at BIGINT NOT NULL,
    device_token_hash TEXT REFERENCES mobile_devices(device_token_hash),
    rc_app_user_id TEXT NOT NULL,
    promo_issued INTEGER NOT NULL DEFAULT 0,
    uploaded_file TEXT,
    language TEXT,
    grant_expires_at BIGINT,
    grant_issued INTEGER NOT NULL DEFAULT 0,
    grant_used INTEGER NOT NULL DEFAULT 0,
    report_id TEXT,
    analysis_json TEXT
);

CREATE INDEX idx_mobile_sessions_expires_at
    ON mobile_sessions (expires_at);

CREATE TABLE mobile_purchase_redemptions (
    transaction_id TEXT PRIMARY KEY,
    token_hash TEXT NOT NULL,
    redeemed_at BIGINT NOT NULL
);