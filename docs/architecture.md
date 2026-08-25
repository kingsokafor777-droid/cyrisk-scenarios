# Architecture

The corpus loader reads a declared fixture manifest, validates each positive case as a Core scenario
and Model request, applies corpus-specific synthetic/non-currency quality rules, and runs the Model
with the declared seed. The harness verifies stable input/output hashes and reports an ordered,
payload-free result. Adversarial cases are expected to be rejected with a named quality code.

| Boundary | Enforced behavior |
|---|---|
| Source material | Committed fictional JSON only; no API, database, collector, or upload path. |
| Quantitative unit | `events-per-year` plus `synthetic-index-units` only; currency labels are rejected. |
| Determinism | Each Model request supplies its own seed and expected hashes. |
| Corpus intent | Regression compatibility and assumption-boundary checks, not prediction or calibration. |
