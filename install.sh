#!/bin/bash
set -euo pipefail
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
exec uv run --no-project --with-requirements "$REPO_DIR/requirements.txt" python3 "$REPO_DIR/install.py" "$@"
