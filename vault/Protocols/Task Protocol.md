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

## The flow

- **Claim:** assign yourself and drag the card to **In Progress**. Do this before you start, not after.
- **One card In Progress per person.** Finish or hand back before starting the next.
- **Blocked:** add the `blocked` label, write one comment saying on what, and say it on the call.
- **Done:** put `closes #12` in the message of the push that finishes it: `git sync "Add baseline, closes #12"`. GitHub closes the issue and the card moves to Done by itself. Then add your "How it works" comment (below) on the issue. A task with nothing to push: close the issue by hand.
- **Handing back:** unassign yourself, drag the card back to Todo, and comment how far you got.

With Claude Code you can say it instead: "start task 12", "I'm blocked on 12 because …", "push". Claude moves the card for you.

## Definition of done
- [ ] Pushed to `main`, CI shows ✓
- [ ] Runs in a fresh Colab session, not only on your machine
- [ ] The closing comment says **how it works**, in your own words, in five bullets at most: what it does, why this way, where it could be wrong. You can say it out loud (see AI Agent Protocol)
- [ ] New data, models or libraries are in Credits
- [ ] Any new result is in Evaluation

## Priorities at the gates
- Before the MVP gate (Sat 21:00): P0 only.
- After the MVP gate: P1, most rubric points first.
- After feature freeze (Sun 14:00): only tasks labelled `testing` or `communication`, and bug fixes.
- P2 tasks still in Todo at freeze are dropped. Mention them in the write-up as next steps.

Up: [[Tasks]]
