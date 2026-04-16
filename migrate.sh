#!/bin/bash
# DB migration bootstrap for order-service.
#
# Migration 001 adds columns and creates tables that ALREADY EXIST in
# environments bootstrapped via SQLAlchemy create_all() — running it would fail.
# Solution: if no Alembic version is tracked yet, stamp at 001 to skip it,
# then upgrade head to apply only the delta migrations (002, 003, ...).
set -e

echo "=== DB Migration: order-service ==="

# Filter alembic INFO lines — remaining output is the current revision (if any)
CURRENT_REV=$(alembic current 2>&1 | grep -vE "^INFO|^WARNING|^$" | head -1 || true)
echo "Current revision: '${CURRENT_REV:-none}'"

if [ -z "$CURRENT_REV" ]; then
    echo "No Alembic version tracked — stamping baseline (001) to skip initial migration"
    echo "(Initial schema already exists from first deploy)"
    alembic stamp 001
fi

echo "Running: alembic upgrade head"
alembic upgrade head
echo "=== Migration complete ==="
