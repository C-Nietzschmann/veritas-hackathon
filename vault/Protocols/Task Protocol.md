# Task Protocol

Every piece of work is one note in `Tasks/`. One file per task means two people never edit the same file, so the board never has merge conflicts.

## Create a task
1. Right-click the `Tasks` folder → **New note**. Name it with a verb: `Load and clean dataset`, `Train baseline`, `Record demo video`.
2. Insert the template: command palette (`Cmd/Ctrl + P`) → **Templates: Insert template** → `Task`.
3. Fill in the properties at the top and one sentence under Goal.

A good task takes 1 to 3 hours and has a result you can show. Bigger than that: split it.

## Properties

| Property | Values | Meaning |
|---|---|---|
| `status` | `todo` `doing` `blocked` `done` | Where it is |
| `owner` | your handle from [[Team]] | Exactly one person. Empty means free to claim |
| `priority` | `P0` `P1` `P2` | P0: no demo without it. P1: makes it clearly better. P2: stretch |
| `rubric` | `technical` `originality` `impact` `testing` `communication` | Which criterion in [[Rubric]] it earns points for |
| `link` | link | The notebook or commit on GitHub, once there is one |

## The flow

`todo` → `doing` → `done`, with `blocked` as a side exit. After every change of status: `git sync`, so the others see it.

- **Claim:** put your handle in `owner`, set `status: doing`. Do this before you start, not after.
- **One `doing` per person.** Finish or hand back before starting the next.
- **Blocked:** set `status: blocked`, write one line under Notes saying on what, and say it on the call.
- **Done:** it's on `main` and `main` still runs. Set `status: done` and paste the notebook or commit link in `link`.
- **Handing back:** clear `owner`, set `status: todo`, and leave a note on how far you got.

## Definition of done
- [ ] Pushed to `main`, CI shows ✓
- [ ] Runs in a fresh Colab session, not only on your machine
- [ ] "How it works" in the task note is filled in and you can say it out loud (see [[AI Agent Protocol]])
- [ ] New data, models or libraries are in [[Credits]]
- [ ] Any new result is in [[Evaluation]]

## Priorities at the gates
- Before the MVP gate (Sat 21:00): P0 only.
- After the MVP gate: P1, most rubric points first.
- After feature freeze (Sun 14:00): only tasks with rubric `testing` or `communication`, and bug fixes.
- P2 tasks that are still `todo` at freeze are dropped. Mention them in the write-up as next steps.

## The board
[[Board.base|Board]] reads these properties. It has three views: **Open** (grouped by status), **By owner**, and **Done**. You can also change `status` and `owner` directly in the board table.
