#!/bin/sh
# Moves a task on the GitHub board from the terminal. Claude uses this; people can simply use the board.
#   sh scripts/task.sh new "Train baseline" P0 technical   create a task (it lands in Todo)
#   sh scripts/task.sh start 12                            assign it to you, move the card to In Progress
#   sh scripts/task.sh block 12 "waiting for the dataset"  label it blocked and say why
#   sh scripts/task.sh unblock 12
#   sh scripts/task.sh note 12 "How it works: ..."         add a comment
#   sh scripts/task.sh pr 12 "Add test split"              share work in progress: branch, push, open a pull request linked to task 12
#   sh scripts/task.sh ship 12 "Add baseline model"        finish it: the same, then wait for the checks, merge, and return to main
#   sh scripts/task.sh done 12 "How it works: ..."         close a task that has nothing to push; the board moves it to Done
# Every pull request is linked to its task ("Closes #12"). Merging it closes the task and moves the card to Done.
REPO=C-Nietzschmann/veritas-hackathon
BOARD=https://github.com/users/C-Nietzschmann/projects/3
PROJECT=PVT_kwHOEwA5us4BrclP
STATUS_FIELD=PVTSSF_lAHOEwA5us4BrclPzhpvSSI
IN_PROGRESS=47fc9ee4

cmd=$1; n=$2; text=$3

# Put the current changes on a branch for this task, push it, and make sure a linked pull request is open.
# Sets $pr to the pull request's number.
share_on_branch() {
  # Without gh the steps below would switch branch, commit and push, and only then fail.
  command -v gh >/dev/null 2>&1 || { echo "The GitHub CLI (gh) is missing, so nothing was changed. Install it, then: gh auth login"; return 1; }
  cd "$(git rev-parse --show-toplevel)" || return 1
  if [ "$(git branch --show-current)" = main ]; then
    git fetch -q origin main
    # uncommitted changes come along to the new branch
    git switch -q -c "task-$n" 2>/dev/null || git switch -q "task-$n" || return 1
    # commits made on main but never pushed now live on the task branch: put local main back in step with GitHub
    git branch -q -f main origin/main
  fi
  sh scripts/check.sh || return 1
  git add -A
  git commit -q -m "$text" 2>/dev/null
  if [ -z "$(git log origin/main..HEAD --oneline)" ]; then
    echo "Nothing to share: this branch has no changes compared with main."
    return 1
  fi
  git push -q -u origin HEAD 2>/dev/null || { echo "Could not push the branch. Someone else may have pushed to it: git pull --rebase, then try again."; return 1; }
  pr=$(gh pr view --json number,state -q 'select(.state == "OPEN") | .number' 2>/dev/null)
  if [ -z "$pr" ]; then
    title=$(gh issue view "$n" -R "$REPO" --json title -q .title) || return 1
    gh pr create -R "$REPO" --title "$title" --body "$(printf 'Closes #%s\n\n%s\n' "$n" "$text")" >/dev/null || return 1
    pr=$(gh pr view --json number -q .number)
  fi
}

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
  pr)
    [ -n "$n" ] && [ -n "$text" ] || { echo "usage: task.sh pr <task number> \"what changed\""; exit 1; }
    share_on_branch || exit 1
    echo "Pull request #$pr is open and linked to task #$n. You are on branch $(git branch --show-current)."
    echo "When the task is finished: sh scripts/task.sh ship $n \"<what changed>\""
    ;;
  ship)
    [ -n "$n" ] && [ -n "$text" ] || { echo "usage: task.sh ship <task number> \"what changed\""; exit 1; }
    share_on_branch || exit 1
    echo "Pull request #$pr is linked to task #$n. Waiting for the checks ..."
    # the checks need a few seconds to appear
    i=0
    while [ "$(gh pr checks "$pr" -R "$REPO" --json name -q length 2>/dev/null || echo 0)" = 0 ] && [ "$i" -lt 20 ]; do sleep 3; i=$((i + 1)); done
    if gh pr checks "$pr" -R "$REPO" --watch --interval 5 >/dev/null 2>&1; then
      branch=$(git branch --show-current)
      if gh pr merge "$pr" -R "$REPO" --squash --delete-branch >/dev/null 2>&1; then
        git switch -q main 2>/dev/null
        git pull -q --rebase
        # the work is on main now (squashed), so the task branch on this computer can go
        [ "$branch" != main ] && git branch -q -D "$branch" 2>/dev/null
        echo "Shipped: pull request #$pr merged into main, task #$n closed, card moved to Done."
      else
        echo "The checks passed but the merge did not go through, most likely because main changed in the same files."
        echo "Bring main in with: git pull origin main   Fix what it reports, then run the same command again."
        exit 1
      fi
    else
      echo "The checks failed on pull request #$pr. Nothing was merged:"
      gh pr checks "$pr" -R "$REPO" --json name,state -q '.[] | "  \(.name): \(.state)"'
      echo "Fix it here on this branch, then run the same command again."
      exit 1
    fi
    ;;
  done)
    if [ -n "$text" ]; then gh issue close "$n" -R "$REPO" --comment "$text"; else gh issue close "$n" -R "$REPO"; fi
    ;;
  *)
    sed -n '2,11p' "$0"; exit 1
    ;;
esac
