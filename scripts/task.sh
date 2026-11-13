#!/bin/sh
# Moves a task on the GitHub board from the terminal. Claude uses this; people can simply use the board.
#   sh scripts/task.sh new "Train baseline" P0 technical   create a task (it lands in Todo)
#   sh scripts/task.sh start 12                            assign it to you, move the card to In Progress
#   sh scripts/task.sh block 12 "waiting for the dataset"  label it blocked and say why
#   sh scripts/task.sh unblock 12
#   sh scripts/task.sh note 12 "How it works: ..."         add a comment
#   sh scripts/task.sh done 12 "How it works: ..."         comment and close; the board moves it to Done
# A push whose message contains "closes #12" also closes task 12, so "done" is only for tasks with nothing to push.
REPO=C-Nietzschmann/veritas-hackathon
BOARD=https://github.com/users/C-Nietzschmann/projects/3
PROJECT=PVT_kwHOEwA5us4BrclP
STATUS_FIELD=PVTSSF_lAHOEwA5us4BrclPzhpvSSI
IN_PROGRESS=47fc9ee4

cmd=$1; n=$2; text=$3
case "$cmd" in
  new)
    [ -n "$2" ] || { echo "usage: task.sh new \"Title\" [P0|P1|P2] [rubric label]"; exit 1; }
    gh issue create -R "$REPO" --title "$2" --label "${3:-P1}${4:+,$4}" \
      --body "$(printf '## Goal\nOne sentence: what exists when this is done.\n\n## Done when\n- [ ] \n\n## Notes\n')"
    ;;
  start)
    gh issue edit "$n" -R "$REPO" --add-assignee @me >/dev/null || exit 1
    item=$(gh api graphql -F n="$n" -f query='query($n:Int!){repository(owner:"C-Nietzschmann",name:"veritas-hackathon"){issue(number:$n){projectItems(first:10){nodes{id project{id}}}}}}' \
      --jq ".data.repository.issue.projectItems.nodes[] | select(.project.id == \"$PROJECT\") | .id" 2>/dev/null)
    if [ -n "$item" ] && gh project item-edit --project-id "$PROJECT" --id "$item" --field-id "$STATUS_FIELD" --single-select-option-id "$IN_PROGRESS" >/dev/null 2>&1; then
      echo "#$n is yours and In Progress"
    else
      echo "#$n is assigned to you. Now drag its card to In Progress: $BOARD"
    fi
    ;;
  block)
    gh issue edit "$n" -R "$REPO" --add-label blocked >/dev/null || exit 1
    [ -n "$text" ] && gh issue comment "$n" -R "$REPO" --body "Blocked: $text" >/dev/null
    echo "#$n marked blocked. Say it on the call."
    ;;
  unblock)
    gh issue edit "$n" -R "$REPO" --remove-label blocked >/dev/null && echo "#$n unblocked"
    ;;
  note)
    [ -n "$text" ] || { echo "usage: task.sh note <number> \"text\""; exit 1; }
    gh issue comment "$n" -R "$REPO" --body "$text" >/dev/null && echo "comment added to #$n"
    ;;
  done)
    if [ -n "$text" ]; then gh issue close "$n" -R "$REPO" --comment "$text"; else gh issue close "$n" -R "$REPO"; fi
    ;;
  *)
    sed -n '2,10p' "$0"; exit 1
    ;;
esac
