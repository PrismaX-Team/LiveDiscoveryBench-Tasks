# Campaign Brief

You are supporting a low-resource protein stability campaign. For each anonymized wild-type protein episode, you have a legal single-mutant design space and a small historical pilot assay table. The goal is to nominate variants for limited wet-lab measurement rounds, learn from the returned measurements, and produce an actionable handoff for the next experimental decision.

Your campaign has three rounds. In each round, submit 16 variants per episode for wet-lab measurement. After each round, update your assumptions about which mutation classes, local sequence contexts, regions, or positions appear promising or risky.

At the end, submit two distinct portfolios:

- `final_validated_batch.csv`: variants already measured during this campaign that are worth downstream confirmation or handoff.
- `final_prospective_batch.csv`: variants not yet measured in this campaign that should be prioritized in a follow-up wet-lab round.

A strong campaign should balance exploitation, exploration, diversity, risk control, and explicit hypothesis testing. The full wet-lab measurement table is hidden; the framework-managed `validation` action reveals measurements only for a valid batch of variants you nominate.
