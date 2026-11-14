Up: [[Log]]

## 2026-11-14 06:45
- **Task:** Setup (card on the board)
- **Did:** Cloned the repo, switched on `git sync`, set my git identity, signed in through GitHub Desktop, started this log.
- **AI used for:** Claude Code followed vault/Setup.md for me and ran this first `git sync`.
- **Next:** install Obsidian, open the vault, claim my Setup card, read Home and the first five Protocols.

## 2026-11-14 07:40
- **Task:** #4 Setup (card on the board)
- **Did:** Logged in to the GitHub CLI (with project access), claimed #4, removed its Colab box after the team dropped Colab, opened the vault in Obsidian, filled in my availability in Team.
- **Result:** notes only. #4 still open: reading the protocols and my role (decided on #3).
- **AI used for:** Claude Code read the whole vault, ran the GitHub login, moved and edited my card, reviewed the teammates' Colab change and wrote this entry.
- **Next:** kickoff call 08:00, agree roles (#3), close #4.
- **Blocked by:** nothing

## 2026-11-14 12:34
- **Task:** #60 API client (handed over) and #110 masking functions (cards on the board)
- **Did:** Built a draft `get()` for #60, then handed #60 to jonas, because his crawl (#24) already talks to the API and the team needs one client. Built `src/mask.py` for #110: `pseudonym()` (SHA-256, same name gives the same label) and `mask_postcode()` (district only), with 7 tests. Shipped as PR #136.
- **Result:** #110 closed, `main` green with 116 tests. Not wired into the adapter yet (#111).
- **AI used for:** Claude Code wrote the API client draft, the masking functions and their tests, shipped the PR and drafted the "How it works" note and this entry. I read the code and can explain it.
- **Next:** raise on the call: who wires masking into the adapter (#111), and whether company names named after their owner get masked. Then pick the next free card.
- **Blocked by:** nothing
