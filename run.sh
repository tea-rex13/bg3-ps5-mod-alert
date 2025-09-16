#!/usr/bin/env bash
cd "$(dirname "$0")"
source .venv/bin/activate
python -m src.mod_alert "$@"
