#!/bin/bash
set -e

echo "Running database migrations..."
aerich upgrade

echo "Starting API server..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
