# No fixed roles, everyone claims their own cards

Up: [[Decisions]]

- **Date:** 2026-11-14 08:10
- **Decided by:** jonas
- **Status:** decided

## Decision
Nobody has a fixed role or lane this weekend. Everyone claims their own cards on the board, one at a time, in the order in Plan.

## Why
- Whoever is free takes the next card that unblocks the most, so nobody waits on "their" lane while another lane is stuck.
- The modular design already keeps us out of each other's code: boxes only meet through the shared tables (ADR-005), so we don't need roles for that.

The alternative was three fixed lanes (data, model, story). Ownership is clearer that way, but one slow lane stalls everyone behind it.

## What it changes
- The role table in Team stays empty. Whoever holds a box's card owns that file until the card is done.
- At every check-in we look at who holds what, and rebalance if one person carries most of the P0 work.
- Tests come from someone else: whoever builds the schema doesn't write the rule tests.
