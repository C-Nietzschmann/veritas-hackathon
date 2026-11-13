#!/bin/sh
# Prints the task board from GitHub. Used by `git board` and at the start of every Claude session.
# Needs the GitHub CLI: install it and run `gh auth login` once.
cd "$(git rev-parse --show-toplevel)" || exit 1
BOARD=https://github.com/users/C-Nietzschmann/projects/3
REPO=C-Nietzschmann/veritas-hackathon
sed -n 's/^\*\*Phase:\*\* */Phase: /p' vault/Home.md

if ! command -v gh >/dev/null 2>&1 || ! gh auth status >/dev/null 2>&1; then
  echo "Board: $BOARD"
  echo "(to see it here, install the GitHub CLI and run: gh auth login)"
  exit 0
fi

FMT='def prio: ((.labels // []) | map(select(test("^P[0-2]$"))) | first) // "--";
def who: ((.assignees // []) | join(",")) as $a | if $a == "" then "free" else $a end;
def flag: if ((.labels // []) | index("blocked")) then "  BLOCKED" else "" end;
(["In Progress", "Todo"][] as $s
  | ($i | map(select(.status == $s))) as $g
  | select(($g | length) > 0)
  | "\($s) (\($g | length))", ($g | sort_by(prio)[] | "  \(prio)  #\(.number) \(.title)  [\(who)]\(flag)")),
"Done (\($i | map(select(.status == "Done")) | length))"'

# The exact columns come from the project board. That needs the "project" permission on your GitHub login.
if out=$(gh project item-list 3 --owner C-Nietzschmann --limit 200 --format json --jq \
  "(.items | map(select(.content.type == \"Issue\")) | map({number: .content.number, title, labels, assignees, status: (.status // \"Todo\")})) as \$i | $FMT" 2>/dev/null); then
  echo "$out"
else
  # Without it: read the issues. An open issue with an owner counts as In Progress.
  gh issue list -R "$REPO" --state all --limit 200 --json number,title,assignees,labels,state --jq \
    "(map({number, title, labels: [.labels[].name], assignees: [.assignees[].login], status: (if .state == \"CLOSED\" then \"Done\" elif (.assignees | length) > 0 then \"In Progress\" else \"Todo\" end)})) as \$i | $FMT"
  echo "(columns guessed from who is assigned. For the exact board: gh auth refresh -s project)"
fi
echo "Board: $BOARD"
