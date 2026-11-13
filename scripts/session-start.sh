#!/bin/sh
# Runs at the start of every Claude Code session in this repo (see .claude/settings.json).
# Whatever it prints is shown to Claude, so every session starts up to date and knows the board.
cd "$(git rev-parse --show-toplevel)" || exit 0

# Switch on the team shortcuts (git sync, git board) if this clone doesn't have them yet
git config --local include.path ../.gitalias

# Get everyone else's changes. If that isn't possible right now, say so and carry on.
if git pull -q --rebase --autostash >/dev/null 2>&1; then
  echo "Pulled the latest from the team."
else
  git rebase --abort >/dev/null 2>&1
  echo "Could not pull automatically (offline, or a conflict). Run 'git pull --rebase' and look before working."
fi

echo "Task board right now:"
sh scripts/board.sh
echo "Before writing code: confirm the task with the user and read vault/Protocols/AI Agent Protocol.md. To share work, use the push skill."
exit 0
