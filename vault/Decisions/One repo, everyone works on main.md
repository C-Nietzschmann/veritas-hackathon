# One repo, everyone works on main

- **Date:** 2026-11-13
- **Decided by:** setup, before kickoff
- **Status:** decided

## Decision
Code and vault live in one repo, `veritas-hackathon`, with the vault in `vault/`. Everyone pushes straight to `main` with `git sync`. No pull requests.

## Why
- One thing to clone, one command to learn. For three people over one weekend, simple wins.
- The task board is only useful if everyone sees the same one. That needs all of us on the same branch.
- The repo shows how we worked: decisions, evaluation log, what failed. That supports the "Testing and honesty" and "Communication" criteria.

The alternative was two repos (a private vault next to the code) with pull requests for code. Safer for `main`, but more to set up and explain.

## What we give up, and what replaces it
- **Nothing checks code before it lands on `main`.** Replaced by: the rule "push only what runs", automatic checks after every code push, and `git revert` when something breaks. See [[Git Workflow]].
- **The vault becomes public with the repo.** So: handles instead of full names, and no school, phone numbers, emails or private links in any note. See [[Rules]].
