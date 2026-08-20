#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "$0")/.." && pwd)"
archive_dir="$project_dir/dist"
archive_path="$archive_dir/footwear-support-agent.zip"

mkdir -p "$archive_dir"
cd "$project_dir"

zip -FSr "$archive_path" \
  app \
  data/orders.json \
  data/policies \
  tests \
  .env.example \
  .gitignore \
  AI_DISCLOSURE.md \
  DECISIONS.md \
  README.md \
  TESTING.md \
  pyproject.toml \
  requirements.txt \
  scripts/package_submission.sh \
  -x '*/__pycache__/*' '*.pyc' '.DS_Store'

echo "Created $archive_path"
