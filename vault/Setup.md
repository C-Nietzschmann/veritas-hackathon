# Setup

Ten minutes, once, before kickoff. Your checklist for this is your Setup card on the [board](https://github.com/users/C-Nietzschmann/projects/3). Tick its boxes as you go and close it when you're done.

## 1. Install
- [Git](https://git-scm.com/downloads) and [Obsidian](https://obsidian.md)
- A GitHub account. Send your username to the repo owner and accept the invite you get by email.
- The [GitHub CLI](https://cli.github.com), then run `gh auth login` once. It signs Git in to GitHub (a password doesn't work for pushing), and Claude Code uses it to check CI after a push.

## 2. Get the repo
```bash
git clone https://github.com/C-Nietzschmann/veritas-hackathon.git
cd veritas-hackathon
git config --local include.path ../.gitalias
git config user.name "<your handle>"
git config user.email "<your GitHub no-reply address>"
```
The third line switches on our `git sync` shortcut. The last two say who your commits are from. Without them a fresh Git install refuses to commit, and `git sync` stops halfway. Your no-reply address is on GitHub under Settings → Emails.

If the clone asks for a password and refuses yours: run `gh auth login` (step 1) and try again. Or install [GitHub Desktop](https://desktop.github.com), sign in, and clone with *File → Clone repository*. Then run the `git config` lines in the repo folder (*Repository → Open in Terminal*).

## 3. Open the vault
Obsidian → **Open folder as vault** → choose the `veritas-hackathon` folder you just cloned.
The notes are in the `vault` folder in the left sidebar. Click the bookmark icon for the shortcuts: Home, Workflow map, Rules, Timeline, Idea, and the board on GitHub.

## 4. Try the loop once
1. Open your log file in `vault/Log/` (create `<handle>.md` starting with the line `Up: [[Log]]`) and write one line.
2. In the terminal, inside `veritas-hackathon`:
   ```bash
   git sync
   ```
3. Look at the repo on github.com: your file is there. Ask a teammate to run `git sync`, and it appears in their Obsidian.
4. Open the [board](https://github.com/users/C-Nietzschmann/projects/3), assign your Setup card to yourself and drag it to In Progress.

That is the whole workflow: change something, `git sync`. More in [[Sync]], and the big picture is on the [[Workflow map.canvas|Workflow map]].

## Using Claude Code?
Open it in the `veritas-hackathon` folder and accept the project's settings when it asks. It reads `CLAUDE.md` and follows our protocols. At the start of every session it gets the team's latest changes and looks at the board by itself. When you want to share your work, say **push**: it checks the work, updates your task and log, syncs, and tells you whether GitHub's checks passed.

## 5. Read
[[Home]], then the first five notes in [[Protocols]]: Rules, Timeline, Team, Calls, Task Protocol. Fifteen minutes in total.
