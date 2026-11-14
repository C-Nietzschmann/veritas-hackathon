# Pipeline

Up: [[Project]]

How a company number becomes a credit decision, without mixing up what we know with what we guess. Teal boxes with solid borders carry what sources state. Purple boxes with dashed borders carry what we infer, always with a probability.

```mermaid
flowchart TD
    S["Public sources<br/>raw files, hashed (R1)"]:::neutral
    I["Ingest adapter<br/>Companies House"]:::observed
    E["Evidence tables<br/>ADR-001 mentions + claims"]:::observed
    O["Observed graph<br/>ADR-002 claims only"]:::observed
    R["Entity resolution<br/>ADR-003 p(same person)"]:::inferred
    P["Predecessor risk<br/>ADR-004 formula, then worlds"]:::inferred
    D["Decision layer<br/>p(fail), then flag or clear"]:::inferred
    U["Operator interface<br/>solid facts, dashed guesses"]:::neutral
    V["Evaluation<br/>ours vs three baselines"]:::neutral
    S --> I --> E
    E -- claims --> O
    E -- mentions --> R
    O --> P
    R --> P
    P --> D
    O --> U
    D --> U
    D --> V
    classDef observed fill:#E1F5EE,stroke:#0F6E56,color:#085041
    classDef inferred fill:#EEEDFE,stroke:#534AB7,color:#3C3489,stroke-dasharray:5 3
    classDef neutral fill:#F1EFE8,stroke:#5F5E5A,color:#444441
```

## How it works
1. **Sources and ingest.** The adapter downloads the raw records into `data/raw/`, leaves them untouched and keeps each one's hash (R1).
2. **Evidence tables.** The adapter writes **mentions** (each company or person as one record names them, spelled as written) and **claims** (each relationship a record states, with its dates). Every row keeps its source (R2). ADR-001.
3. **Two paths.** Claims are filtered into the observed graph, which holds facts only (R3, ADR-002). Mentions go to entity resolution, which gives each pair of people a probability of being the same person and never merges them (R6, ADR-003).
4. **Predecessor risk.** This is the chance that at least one of the company's directors ran an earlier company that went insolvent: 1 − ∏(1 − pᵢ) over every candidate match. The formula is exact when the matches are independent. On Sunday, the one-identity rule (one director is only one person) replaces it, and we measure whether the flags improve (ADR-004).
5. **Decision.** A straight line fitted on the 2021 companies turns that chance into the chance the company fails. The user's three costs (a missed case, a wrong flag, asking) then give FLAG, CLEAR or NOT ENOUGH EVIDENCE (R8).
6. **Interface and evaluation.** The interface draws facts solid and guesses dashed, with the evidence one click away and names masked. Evaluation compares us on the same data with three baselines: flag nothing, same name means same person, and Companies House's own officer links. It trains on 2021 companies and tests on 2022 ones.

**In our case:** the query is a company number. Mentions are companies, directors and owners as Companies House records them. Claims are "is a director of" and "controls", with their dates. The hidden relationship we look for is a predecessor: an earlier company, run by the same people, that went insolvent.

The boxes we build, their files and who leads each: [[Modules]]
