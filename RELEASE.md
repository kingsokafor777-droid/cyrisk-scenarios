# Release Governance

## Candidate: v0.1.0

| Item | Verified local value |
|---|---|
| Package | `cyrisk-scenarios` v0.1.0 |
| Core compatibility pin | `cyrisk-core` commit `4d68f385ef382a6420466dff0196244a2c915f1f` |
| Model compatibility pin | `cyrisk-model` commit `47c8957e61ce66cdc455a1582429207f211cd802` |
| Corpus input schema | `cyrisk.scenarios/v1` |
| Fixture manifest SHA-256 | `e58fbd908a1f4ebbdb78e4ea1ae4d5fc774b994d28fe2240406f8d4f4d792cb0` |
| Positive-case fixture SHA-256 | `80244f5ae10250770ac880131dd94359b18cf1b1a388a2110d33146ad99aac32` |
| Expected-result fixture SHA-256 | `bb0d1c95ef7198a873ad854b3056b8a302c55a7597ddcb7a2d3d1b0ae06d5b09` |
| Local behavioral result | `make check` passed: fixture reproducibility, Ruff, strict mypy, 13 tests, and 97.28% branch-aware coverage |
| Wheel SHA-256 | `0caac88b61bdc350028c6eb9e5f62292ed680d58e0dfa39625d05e7bf61be5ee` |

Publication remains approval-gated. After explicit approval, the procedure must create the public
repository, tag the reviewed commit, attach the verified wheel, wait for successful hosted
`Quality`, Python 3.10–3.13, and `Analyze Python` checks, retrieve exact check contexts, apply the
protected-main policy, and synchronize the profile and program ledger.

This corpus validates only compatibility of sealed fictional fixtures. It does not support a claim
of real loss, forecast accuracy, control effectiveness, evidence truth, authorization, or a risk
decision. A CodeQL workflow result must not be used to claim an alert count unless the platform API
is accessible and independently returns that count.
