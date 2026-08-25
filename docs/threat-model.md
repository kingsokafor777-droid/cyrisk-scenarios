# Threat Model

| Threat | Example | Mitigation and boundary |
|---|---|---|
| Real-data insertion | A fixture embeds an incident or customer amount. | Scope requires fictional metadata; corpus units disallow currency. |
| Silent input drift | A fixture changes while a benchmark still passes vaguely. | Canonical manifest and exact expected hashes. |
| Forecast overclaim | Synthetic range output is described as expected loss. | Documentation and result limitations deny forecast/financial meaning. |
| Unsound assumption | Non-synthetic source class appears in a positive case. | Corpus validation rejects non-synthetic sources. |
| Non-determinism | Seed or request details are inferred. | Request and seed are committed and hash-bound. |
