#!/bin/sh
# Runs before every `git sync` and again on GitHub (CI). It only reports, it changes nothing.
# Looks at every file git would share: tracked files plus new files that aren't ignored.
cd "$(git rev-parse --show-toplevel)" || exit 1

check_file() {
  f=$1
  [ -f "$f" ] || return 0
  [ "$f" = scripts/check.sh ] && return 0

  # Secret files
  case "$f" in
    .env.example|*/.env.example) ;;
    .env|.env.*|*/.env|*/.env.*) echo "  x secret file would be shared: $f" ;;
  esac

  # Too big for git (datasets, model weights). Notebooks get more room,
  # because main.ipynb keeps its outputs (plots, images).
  size=$(wc -c < "$f" | tr -d ' ')
  case "$f" in
    *.ipynb) limit=25000000; fix="Clear or shrink its biggest outputs (images, long printouts)" ;;
    *)       limit=5000000;  fix="Download it in the notebook from its source instead" ;;
  esac
  if [ "$size" -gt "$limit" ]; then
    echo "  x too big for git ($((size / 1000000)) MB): $f. $fix"
  fi

  # Leftover merge conflict markers
  if grep -qE '^(<<<<<<<|>>>>>>>) ' "$f" 2>/dev/null; then
    echo "  x unresolved merge conflict in: $f"
  fi

  # Things that look like API keys or tokens
  if grep -qE '(sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|hf_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----)' "$f" 2>/dev/null; then
    echo "  x looks like an API key or token in: $f. Put it in .env (ignored by git)"
  fi

  # Notebooks must be valid JSON (skipped where jq isn't installed; GitHub always checks)
  case "$f" in
    *.ipynb)
      if command -v jq >/dev/null 2>&1 && ! jq empty "$f" >/dev/null 2>&1; then
        echo "  x broken notebook (not valid JSON): $f"
      fi ;;
  esac
  return 0
}

scan() {
  git ls-files -c -o --exclude-standard | while IFS= read -r f; do check_file "$f"; done
}

problems=$(scan)

# Real directors' names in main.ipynb (#112). Only where the raw data and the project's
# Python are on this computer: GitHub has neither, so there it is skipped.
if [ -d data/raw ] && [ -x .venv/bin/python ]; then
  names=$(.venv/bin/python scripts/name_guard.py) || problems="$problems
$names"
fi

if [ -n "$problems" ]; then
  echo "$problems"
  echo "check failed: nothing was shared. Fix the lines above and run git sync again."
  exit 1
fi
echo "check ok"
