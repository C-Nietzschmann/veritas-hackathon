# Setup

Ten minutes, once, before kickoff. When you're done, claim your Setup task on the [[Board.base|Board]].

## 1. Install
- [Git](https://git-scm.com/downloads) and [Obsidian](https://obsidian.md)
- A GitHub account. Send your username to the repo owner and accept the invite you get by email.

## 2. Get the repo
```bash
git clone https://github.com/C-Nietzschmann/veritas-hackathon.git
cd veritas-hackathon
git config --local include.path ../.gitalias
```
The last line switches on our `git sync` shortcut.

If the clone asks for a password and refuses yours: install [GitHub Desktop](https://desktop.github.com), sign in, and clone with *File → Clone repository*. Then run the `git config` line in the repo folder (*Repository → Open in Terminal*).

## 3. Open the vault
Obsidian → **Open folder as vault** → choose the `vault` folder **inside** `veritas-hackathon`.
You now see this note. The folder around it holds the code.

## 4. Try the loop once
1. Open your Setup task in `Tasks/`, put your handle in `owner`, set `status` to `doing`.
2. In the terminal, inside `veritas-hackathon`:
   ```bash
   git sync
   ```
3. Ask a teammate to run `git sync` too. Your name should now be on their board.

That is the whole workflow: change something, `git sync`. More in [[Sync]].

## 5. Read
[[Home]] → [[Rules]] → [[Timeline]] → [[Calls]] → [[Task Protocol]]. Fifteen minutes in total.
