#!/usr/bin/env bash
# Run the feed/page generation locally (equivalent to GitHub Actions workflow).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

source .venv/bin/activate
FEED_BASE_URL="https://tmyymmt.github.io/sca-tools-feed/feeds" python -m scripts.main
