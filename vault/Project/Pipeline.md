# Pipeline

Up: [[Project]]

How a company number becomes a credit decision, without mixing up what we know with what we guess. Teal boxes with solid borders carry what sources state. Purple boxes with dashed borders carry what we infer, always with a probability.

```mermaid
flowchart TD
    S["Public sources<br/>raw files, hashed (R1)"]:::neutral
    I["Ingest adapters<br/>one per source"]:::observed
    E["Evidence tables<br/>ADR-001 mentions + claims"]:::observed
    O["Observed graph<br/>ADR-002 claims only"]:::observed
    R["Entity resolution<br/>ADR-003 p(same entity)"]:::inferred
    W["Possible worlds<br/>ADR-004 400 sampled runs"]:::inferred
    G["Inferred graph<br/>p and depends_on per link"]:::inferred
    D["Decision layer<br/>flag, clear or abstain"]:::inferred
    U["Operator interface<br/>solid facts, dashed guesses"]:::neutral
    V["Evaluation<br/>ours vs hard-merge baseline"]:::neutral
    S --> I --> E
    E -- claims --> O
    E -- mentions --> R
    O --> W
    R --> W
    W --> G --> D
    O --> U
    D --> U
    D --> V
    classDef observed fill:#E1F5EE,stroke:#0F6E56,color:#085041
    classDef inferred fill:#EEEDFE,stroke:#534AB7,color:#3C3489,stroke-dasharray:5 3
    classDef neutral fill:#F1EFE8,stroke:#5F5E5A,color:#444441
```

## How it works
1. **Sources and ingest.** One adapter per source downloads the raw records, keeps them untouched in `data/raw/` and hashes them (R1).
2. **Evidence tables.** The adapter writes **mentions** (each company or person as one record names them, spelled as written) and **claims** (each relationship a record states, with its dates). Every row keeps its source (R2). ADR-001.
3. **Two paths.** Claims go straight into the observed graph, which holds facts only (R3, ADR-002). Mentions go to entity resolution, which gives each pair a probability of being the same entity and never merges them (R6, ADR-003).
4. **Possible worlds.** We draw 400 versions of who is who from those probabilities, rerun the reasoning in each and average. Every inferred link ends up with a probability and a list of what it depends on (R4, R7, ADR-004).
5. **Decision.** The user's three costs (a wrong flag, a missed case, asking) turn the probability into FLAG, CLEAR or NOT ENOUGH EVIDENCE (R8).
6. **Interface and evaluation.** The interface draws facts solid and guesses dashed, with the evidence one click away. Evaluation runs the same pipeline with the hard-merge baseline swapped in at entity resolution (ADR-005), trained on earlier companies and tested on later ones.

**In our case:** the query is a company number. Mentions are companies, directors and owners as Companies House records them. Claims are "is a director of" and "controls", with their dates. The hidden relationship we look for is a predecessor: an earlier company, run by the same people, that went insolvent.

The boxes we build, their files and who leads each: [[Modules]]
