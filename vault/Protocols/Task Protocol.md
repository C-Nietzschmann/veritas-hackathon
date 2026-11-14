# Task Protocol

Tasks live on GitHub, not in the vault. Every piece of work is one **issue**, and the **[board](https://github.com/users/C-Nietzschmann/projects/3)** shows the issues as cards in three columns: Todo, In Progress, Done. A change there is visible to everyone at once.

The vault keeps what does not change by the minute: how we work, the project notes, decisions and logs.

## Create a task
On the board, click **+ Add item** at the bottom of the Todo column, type a title, press Enter, then choose **Create new issue** in `veritas-hackathon` with the **Task** template.
Or in the repo: Issues → New issue → Task. It shows up on the board by itself.

Name it with a verb: "Load and clean dataset", "Train baseline", "Record demo video".
A good task takes 1 to 3 hours and has a result you can show. Bigger than that: split it.

## What a card carries

| What | Where on GitHub | Meaning |
|---|---|---|
| Status | The column | Todo, In Progress or Done |
| Owner | Assignee | Exactly one person. Nobody assigned means free to claim |
| Priority | Label `P0` `P1` `P2` | P0: no demo without it. P1: makes it clearly better. P2: stretch |
| Rubric | Label `technical` `originality` `impact` `testing` `communication` | Which criterion it earns points for |
| Blocked | Label `blocked` | Cannot continue without help |
| Area | Label `area: …` | Which technical area it belongs to (see below) |
| Gate | Milestone | Which gate it is due at, with the due time |

## Areas, cards and sub-tasks
The board has three levels. GitHub shows the progress of each level on the one above.

1. **Area** (7 issues titled "Area · …"): Setup, Data, Model, Evaluation, Tests and end-to-end runs, Interface and privacy, Submission. Nobody claims an area. It only groups its cards and shows how far they are.
2. **Card** (for example #22 "Write the evidence schema"): one box or one result from Modules.
3. **Sub-task** (label `subtask`, titled like "22.3 · Check the rows"): one file, one function or result, one check. **This is what you claim and what a pull request closes.** A card closes when its sub-tasks are done.

Cards with no sub-tasks (setup, the end-to-end runs, the write-up, submitting) are claimed directly.

Gates are milestones: 1 · Scope lock, 2 · L0 tiny world, 3 · L1 real slice, 4 · L2 improvement, 5 · First submission, 6 · Final submission. Open a milestone to see what is still open for that gate.

On the board, filter with `label:subtask` to see only the pieces to claim, or `-label:subtask` to see only the cards.

## The flow

- **Claim:** assign yourself and drag the card to **In Progress**. Do this before you start, not after.
- **One card In Progress per person.** Finish or hand back before starting the next.
- **Blocked:** add the `blocked` label, write one comment saying on what, and say it on the call.
- **Done:** the task's pull request is merged. That closes the issue and moves the card to Done by itself, with the pull request shown next to it. With Claude Code, say "push". By hand: `sh scripts/task.sh ship 12 "Add baseline"`, or `git sync "Add baseline, closes #12"` for a direct push. Then add your "How it works" comment (below) on the issue. A task with nothing to push: close the issue by hand.
- **Pull request?** Its description starts with `Closes #12`. This is a rule: it links the pull request to the card and closes the task when it is merged. See Git Workflow.
- **Handing back:** unassign yourself, drag the card back to Todo, and comment how far you got.

With Claude Code you can say it instead: "start task 12", "I'm blocked on 12 because …", "push". Claude moves the card for you.

## Definition of done
- [ ] Pushed to `main`, CI shows ✓
- [ ] Runs top to bottom after Restart kernel and run all, with packages in `requirements.txt`
- [ ] The closing comment says **how it works**, in your own words, in five bullets at most: what it does, why this way, where it could be wrong. You can say it out loud (see AI Agent Protocol)
- [ ] New data, models or libraries are in Credits
- [ ] Any new result is in Evaluation

## Priorities at the gates
- Before the MVP gate (Sat 21:00): P0 only.
- After the MVP gate: P1, most rubric points first.
- After feature freeze (Sun 14:00): only tasks labelled `testing` or `communication`, and bug fixes.
- P2 tasks still in Todo at freeze are dropped. Mention them in the write-up as next steps.

Up: [[Tasks]]
