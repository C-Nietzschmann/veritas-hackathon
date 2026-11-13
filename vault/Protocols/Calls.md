# Calls

We work remotely on a WhatsApp group call and chat. This is how we keep it useful and quiet.

## The open call
- During work blocks the call stays open and everyone is **muted by default**. It's a shared room, not a meeting.
- Unmute for: a question, "I'm blocked", "I'm about to push something that affects you", "main is broken".
- A discussion between two people that passes five minutes moves to a separate call, so the third person can keep working.
- Leaving for more than 15 minutes? Write it in the chat: `AWAY until 15:30`.
- If screen sharing on WhatsApp is too blurry to read code, paste the code or the link in the chat or switch to Google Meet for that one conversation.

## Check-ins
At the fixed times in [[Timeline]]. Ten minutes maximum, the coordinator runs them.

Each person, one minute, three sentences:
1. **Done** since the last check-in
2. **Next** until the next one
3. **Blocked** by anything?

Then together:
4. Look at the [board](https://github.com/users/C-Nietzschmann/projects/3). Is it true? Fix it now.
5. Is `main` green?
6. Are we on track for the next gate? If not, what do we cut?

The coordinator writes three lines per check-in in [[Sync notes]]. With Claude Code, say **check-in** a minute before: it collects what was finished and pushed since the last one, who is on what, what is blocked and whether `main` is green, and drafts the entry for you to correct. Problems that need more than two minutes are solved after the check-in by the people involved.

## Chat rules
Start messages with a tag so they can be found later:

| Tag | Meaning |
|---|---|
| `BLOCKED:` | I can't continue without help |
| `MAIN BROKEN:` | Stop pushing code. See Git Workflow |
| `PUSHED:` | I pushed something that changes what you use. Run `git sync` |
| `DECISION?` | I need a quick yes or no from the team |
| `AWAY until HH:MM` | Not reachable |

What does **not** live in WhatsApp:
- **Code.** It goes in the repo.
- **Decisions.** The chat is where we agree, `Decisions/` is where it counts.
- **Tasks.** "Can you do X?" becomes a card on the board or it will be forgotten.
- **Keys and passwords.** Never.

## When someone goes quiet
No reaction for 30 minutes during a work block while their task is `doing`: call them. If they're unreachable, the coordinator may reassign the task. Nobody should feel bad about either side of this.
