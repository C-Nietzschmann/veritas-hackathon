#!/bin/sh
# Prints the task board from the notes in vault/Tasks. Used by `git board` and at the start of every Claude session.
cd "$(git rev-parse --show-toplevel)" || exit 1
sed -n 's/^\*\*Phase:\*\* */Phase: /p' vault/Home.md
rows=$(for f in vault/Tasks/*.md; do
  [ -f "$f" ] || continue
  st=$(sed -n 's/^status: *//p' "$f" | head -1)
  ow=$(sed -n 's/^owner: *//p' "$f" | head -1)
  pr=$(sed -n 's/^priority: *//p' "$f" | head -1)
  echo "${st:-todo}|${pr:--}|${ow:-free}|$(basename "$f" .md)"
done)
for s in doing blocked todo; do
  group=$(echo "$rows" | grep "^$s|" | sort -t '|' -k2,2)
  [ -n "$group" ] || continue
  echo "$s ($(echo "$group" | wc -l | tr -d ' '))"
  echo "$group" | awk -F '|' '{ printf "  %-3s %-8s %s\n", $2, $3, $4 }'
done
echo "done ($(echo "$rows" | grep -c '^done|'))"
