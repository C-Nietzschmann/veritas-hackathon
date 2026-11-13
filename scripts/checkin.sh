#!/bin/sh
# Facts for a check-in: what happened since the last one. The checkin skill uses this; you can also run it by hand.
#   sh scripts/checkin.sh       the last 4 hours
#   sh scripts/checkin.sh 11    the last 11 hours (for the first check-in of the day)
cd "$(git rev-parse --show-toplevel)" || exit 1
H=${1:-4}
REPO=C-Nietzschmann/veritas-hackathon
git pull -q --rebase --autostash >/dev/null 2>&1 || echo "(could not pull, the push list may be incomplete)"

echo "== Check-in facts, last $H hours =="
echo
echo "Pushed to main:"
log=$(git log origin/main --since="$H hours ago" --format='%an|%s')
if [ -n "$log" ]; then
  echo "$log" | cut -d'|' -f1 | sort | uniq -c | while read -r count name; do
    echo "  $name: $count push(es), latest: $(echo "$log" | grep "^$name|" | head -1 | cut -d'|' -f2-)"
  done
else
  echo "  nothing"
fi
echo

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  echo "Tasks finished:"
  done_list=$(gh issue list -R "$REPO" --state closed --limit 100 --json number,title,assignees,closedAt \
    --jq "map(select((.closedAt | fromdateiso8601) > (now - $H * 3600))) | .[] | \"  #\(.number) \(.title)  [\([.assignees[].login] | join(\",\") | if . == \"\" then \"-\" else . end)]\"")
  echo "${done_list:-  none}"
  echo
  echo "Blocked:"
  blocked=$(gh issue list -R "$REPO" --state open --label blocked --json number,title,assignees \
    --jq ".[] | \"  #\(.number) \(.title)  [\([.assignees[].login] | join(\",\") | if . == \"\" then \"-\" else . end)]\"")
  echo "${blocked:-  nothing}"
  echo
  echo "main: $(gh run list -R "$REPO" --branch main --limit 1 --json status,conclusion,displayTitle \
    --jq '.[0] | if . == null then "no checks have run yet" elif .status != "completed" then "checks still running (\(.displayTitle))" elif .conclusion == "success" then "green (last checked push: \(.displayTitle))" else "RED: \(.conclusion) on \(.displayTitle)" end')"
  echo
fi
sh scripts/board.sh
