# Sync

The vault and the code are one git repo. Everyone has a full copy, and changes travel through GitHub. Nothing is shared until you sync.

## The one command
In a terminal, anywhere inside `veritas-hackathon`:
```bash
git sync
```
It saves everything you changed, fetches what the others changed, and uploads yours. For code, say what you did:
```bash
git sync "Add baseline model"
```
First time on a computer, switch the shortcut on (see [[Setup]]): `git config --local include.path ../.gitalias`

Using Claude Code? Say **push**. It does the bookkeeping too (task note, log), then syncs and confirms GitHub's checks.

Want to see the board without opening Obsidian? `git board`

## What sync checks first
Before anything is shared, `git sync` looks through your files and stops if it finds:
- a secrets file (`.env`) or something that looks like an API key
- leftover conflict markers from a merge
- a file over 5 MB (datasets and model weights don't belong in git)
- a notebook that is broken

It tells you which file. Fix it and run `git sync` again. GitHub runs the same check after every code push, plus the tests.

## When to sync
- **Before you start working**, so you have the latest.
- **Right after changing a task** (claimed it, blocked, done). The board is only as fresh as everyone's last sync.
- **When a piece of code works.** Every 30 to 60 minutes while building.
- **Before every check-in** and before you go offline.

## Why conflicts are rare here
- Tasks are one file each, and only the owner edits a task.
- Each person has their own log file in `Log/` and their own notebooks.
- Sync notes and the Phase line on Home are written by the coordinator only.
- Idea, Evaluation, Write-up and Demo Script each have one owner (see Team). To change someone else's note, tell them, or add a line starting with your handle at the bottom.

## If sync stops with a conflict
Git says `CONFLICT` and names a file. Two people changed the same lines.
1. Open the file. Find the block between `<<<<<<<` and `>>>>>>>`. Keep the lines you want from both halves and delete the three marker lines.
2. Then:
   ```bash
   git add -A
   git rebase --continue
   git push
   ```

If it's a notebook, or it looks scary: run `git rebase --abort` (this puts everything back as it was, nothing is lost) and ask on the call.

## What the shortcut runs
```bash
sh scripts/check.sh
git add -A
git commit -m "sync"
git pull --rebase
git push
```
You can type these yourself at any time. GitHub Desktop does the same with its Commit, Pull and Push buttons.

## Optional: sync from inside Obsidian
The community plugin **Git** adds a *Commit-and-sync* command to Obsidian, which does the same as `git sync`. If you install it, leave its automatic commit interval off: it would upload half-written code in the middle of your work.

## Phone
The vault doesn't sync to phones with this setup. On a phone, read the notes on github.com.
