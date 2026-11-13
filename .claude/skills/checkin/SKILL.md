---
name: checkin
description: Prepare a team check-in - gathers what was pushed and finished since the last one, who is on what, what is blocked and whether main is green, then drafts the entry for Sync notes. Use when the user says check-in, checkin, standup, sync call, "what happened since", or a check-in time from the Timeline is due.
---

# Check-in

The team meets on a call at fixed times (see `vault/Protocols/Timeline.md`) for ten minutes. This routine does the collecting, so the call can be about decisions. How a check-in runs: `vault/Protocols/Calls.md`.

## 1. Gather the facts
Work out how many hours have passed since the previous check-in: look at the last `## <date> <time>` heading in `vault/Log/Sync notes.md`, or at the check-in times in the Timeline. If neither helps, use 4.

```bash
sh scripts/checkin.sh <hours>
```

It prints who pushed what, which tasks were finished, what is blocked, whether `main` is green, and the board.

## 2. Say it in five lines
Tell the user, in plain words, before writing anything:
- **Done:** tasks finished and what was pushed, per person.
- **In progress:** who is on which card. Point out anyone with more than one card In Progress, and anyone with none.
- **Blocked:** each blocked card and on what.
- **main:** green or red. If red, that is the first topic of the call.
- **Next gate:** the next gate from the Timeline, how long until then, and whether the open P0 cards can make it. If they can't, say which ones you would cut. This is a suggestion: the team decides.

Only report what the script printed or what is in the vault. Don't guess what someone did, and never invent a result.

## 3. Draft the entry
Draft an entry in the format of `vault/Templates/Check-in.md` (date and time, Done, Next, Blocked, main green, on track, cut or changed) and show it to the user.

`vault/Log/Sync notes.md` belongs to the coordinator (see `vault/Protocols/Team.md`).
- The user is the coordinator: after the call, apply their corrections, append the entry to the bottom of Sync notes, and share it with `git sync "Check-in <time>"`.
- The user is not the coordinator: don't write to Sync notes. Give them the draft to read out or paste into the team chat.

## 4. After the call
If the team decided something that changes someone's work, offer to write it up in `vault/Decisions/` from `vault/Templates/Decision.md`. If scope was cut, the dropped cards get a comment saying so and move back to Todo or are closed as "not planned" by their owner.
