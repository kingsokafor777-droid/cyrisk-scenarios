"""Pure local regression harness for sealed fictional scenarios."""

from __future__ import annotations

import json
from pathlib import Path

from cyrisk_core.models import SourceClass
from cyrisk_model.engine import analyze
from cyrisk_model.models import AnalysisRequest

from .models import (
    AdversarialResult,
    BenchmarkCaseResult,
    CorpusCase,
    CorpusManifest,
    CorpusResult,
    EntryKind,
)

ALLOWED_UNITS = frozenset({"events-per-year", "synthetic-index-units"})


class CorpusError(ValueError):
    """Base error for a deterministic corpus validation or regression failure."""


class CorpusQualityError(CorpusError):
    """A named assumption-quality boundary failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def load_manifest(path: Path) -> CorpusManifest:
    """Load a local fixture manifest without following URLs or remote includes."""

    return CorpusManifest.model_validate_json(path.read_text(encoding="utf-8"))


def load_case(path: Path) -> CorpusCase:
    """Load one local JSON case with strict unknown-field rejection."""

    return CorpusCase.model_validate(json.loads(path.read_text(encoding="utf-8")))


def validate_positive_case(case: CorpusCase) -> None:
    """Enforce corpus-specific synthetic, non-currency, complete-case assumptions."""

    scenario = case.scenario
    if scenario.source_class is not SourceClass.SYNTHETIC:
        raise CorpusQualityError("non_synthetic_source_forbidden")
    if any(factor.source_class is not SourceClass.SYNTHETIC for factor in scenario.factors):
        raise CorpusQualityError("non_synthetic_source_forbidden")
    if any(
        reference.source_class is not SourceClass.SYNTHETIC
        for reference in scenario.evidence_references
    ):
        raise CorpusQualityError("non_synthetic_source_forbidden")
    if scenario.loss_unit != "synthetic-index-units" or any(
        factor.unit not in ALLOWED_UNITS for factor in scenario.factors
    ):
        raise CorpusQualityError("currency_or_unknown_unit_forbidden")
    if case.model_request.completeness_status != "complete":
        raise CorpusQualityError("incomplete_benchmark_forbidden")
    expected = (case.expected_input_hash, case.expected_output_hash, case.expected_run_id)
    if any(value is None for value in expected):
        raise CorpusQualityError("missing_regression_expectation")


def _analysis_request(case: CorpusCase) -> AnalysisRequest:
    """Construct the released Model request only after corpus quality checks succeed."""

    return AnalysisRequest(scenario=case.scenario, **case.model_request.model_dump())


def _run_positive_case(case: CorpusCase) -> BenchmarkCaseResult:
    validate_positive_case(case)
    run = analyze(_analysis_request(case))
    expected = (case.expected_input_hash, case.expected_output_hash, case.expected_run_id)
    actual = (run.input_hash, run.output_hash, run.run_id)
    if actual != expected:
        raise CorpusError("regression_hash_mismatch")
    return BenchmarkCaseResult(
        case_id=case.case_id,
        input_hash=run.input_hash,
        output_hash=run.output_hash,
        run_id=run.run_id,
        limitation=case.limitation,
    )


def run_benchmark(manifest_path: Path) -> CorpusResult:
    """Run every declared positive/adversarial fixture in a deterministic lexical order."""

    manifest = load_manifest(manifest_path)
    if not manifest.verify_integrity():
        raise CorpusError("manifest_integrity_failure")
    root = manifest_path.parent
    positive: list[BenchmarkCaseResult] = []
    adversarial: list[AdversarialResult] = []
    for entry in sorted(manifest.entries, key=lambda item: item.case_id):
        case = load_case(root / entry.relative_path)
        if case.case_id != entry.case_id:
            raise CorpusError("manifest_case_id_mismatch")
        if entry.kind is EntryKind.POSITIVE:
            positive.append(_run_positive_case(case))
            continue
        try:
            validate_positive_case(case)
        except CorpusQualityError as error:
            if case.expected_rejection == error.code:
                adversarial.append(
                    AdversarialResult(case_id=case.case_id, rejection_code=error.code)
                )
                continue
            raise CorpusError("unexpected_adversarial_rejection") from error
        raise CorpusError("adversarial_case_was_accepted")
    return CorpusResult(
        corpus_id=manifest.corpus_id,
        manifest_hash=manifest.manifest_hash or "",
        positive_results=tuple(positive),
        adversarial_results=tuple(adversarial),
    )
