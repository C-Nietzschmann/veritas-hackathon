# ADR-002 Separate observed and inferred graphs

Up: [[Decisions]]

- **Date:** 2026-11-14 07:09
- **Decided by:** proposed by jonas. Confirm or change on the kickoff call (task #16)
- **Status:** proposed

## Decision
We keep two graphs that never mix. The **observed graph** holds only relationships a source states. The **inferred graph** holds only links the system proposes, each with its probability, the method that made it and what it depends on.

- Nodes in both are mentions (ADR-001).
- Observed edges are claims, one for one.
- Inferred edges are "same entity?" links from entity resolution (ADR-003) and hidden relationships from inference.

## Why
This is R3 made structural. With one graph and an "inferred" flag, a single forgotten filter in a query or a plot shows a guess as a fact. With two graphs, that mistake can't happen by accident.

It also keeps evaluation clean: only the inferred graph is scored.

The alternative was one graph with a flag on each edge. It's less code, but it's exactly the failure R3 forbids.

## What it changes
- Graph construction builds the observed graph from claims only, and nothing else writes to it.
- Entity resolution and inference write only to the inferred graph. Every inferred edge carries `p`, `method` and `depends_on` (ADR-004).
- An entity in the interface is a group of mentions joined by "same entity?" links. The grouping is a view computed from the probabilities, never stored as a fact.
- The interface draws the two kinds differently. Observed edges are solid, with their source one click away. Inferred edges are dashed, with their uncertainty shown in words or bands rather than false decimals.
- Evaluation scores the inferred graph only, against links held out by date.

Next: [[ADR-003 Probabilistic entity resolution]]
