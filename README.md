# Cyrisk Scenario Corpus

> **A sealed corpus of fictional, non-currency scenarios and deterministic regression expectations—not a source of real cyber loss data, a forecast, a benchmark of organizational performance, or financial advice.**

`cyrisk-scenarios` owns reproducible synthetic inputs for the released Cyrisk Core and Model
contracts. Each positive case supplies a fully explicit Core `RiskScenario`, a seeded Model
`AnalysisRequest`, and expected hashes. Each adversarial case carries a declared rejection code.

| Corpus element | What it proves | What it does not prove |
|---|---|---|
| Sealed synthetic case | A deterministic contract path remains stable. | Real-world frequency, loss, control effect, or business impact. |
| Regression hash | Supplied fixture/output compatibility. | Model correctness outside the fictional fixture. |
| Adversarial case | A named quality boundary is rejected. | Completeness against all malformed or unsafe inputs. |

The corpus is pinned to [`cyrisk-core` v0.1.0](https://github.com/kingsokafor777-droid/cyrisk-core/releases/tag/v0.1.0)
commit `4d68f385ef382a6420466dff0196244a2c915f1f` and
[`cyrisk-model` v0.1.0](https://github.com/kingsokafor777-droid/cyrisk-model/releases/tag/v0.1.0)
commit `47c8957e61ce66cdc455a1582429207f211cd802`.

The positive corpus permits only the explicit units `events-per-year` and `synthetic-index-units`.
It rejects currency-labelled or non-synthetic inputs. The local harness neither retrieves data nor
makes a control, risk, financial, authorization, or operational decision.
