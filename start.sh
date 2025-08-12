#!/usr/bin/env bash
set -euo pipefail

# Create and activate venv
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

# Install deps
pip install --upgrade pip
pip install -r requirements.txt

# Run API
exec uvicorn bbs_tool.main:app --host 0.0.0.0 --port 8000