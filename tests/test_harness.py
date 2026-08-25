from __future__ import annotations

import json
from pathlib import Path

import pytest
from cyrisk_core.models import SourceClass
from pydantic import ValidationError

from cyrisk_scenarios.cli import main
from cyrisk_scenarios.harness import (
    CorpusError,
    CorpusQualityError,
    load_case,
    run_benchmark,
    validate_positive_case,
)
from cyrisk_scenarios.models import CorpusManifest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "fixtures" / "manifest.json"
POSITIVE_PATH = ROOT / "fixtures" / "cases" / "synthetic_service_case.json"


def copy_manifest(tmp_path: Path) -> Path:
    target = tmp_path / "manifest.json"
    target.write_text(MANIFEST_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    paths = (
        "cases/synthetic_service_case.json",
        "adversarial/non_synthetic_source.json",
        "adversarial/currency_unit.json",
    )
    for relative in paths:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            (ROOT / "fixtures" / relative).read_text(encoding="utf-8"), encoding="utf-8"
        )
    return target


def test_benchmark_is_deterministic_and_records_positive_and_adversarial_results() -> None:
    first = run_benchmark(MANIFEST_PATH)
    second = run_benchmark(MANIFEST_PATH)
    assert first == second
    assert [item.case_id for item in first.positive_results] == ["case_service"]
    assert {item.rejection_code for item in first.adversarial_results} == {
        "currency_or_unknown_unit_forbidden",
        "non_synthetic_source_forbidden",
    }
    assert "not forecast" in first.limitation


def test_manifest_requires_a_matching_integrity_hash(tmp_path: Path) -> None:
    manifest_path = copy_manifest(tmp_path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["manifest_hash"] = "0" * 64
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(CorpusError, match="manifest_integrity_failure"):
        run_benchmark(manifest_path)


def test_manifest_case_id_must_match_loaded_case(tmp_path: Path) -> None:
    manifest_path = copy_manifest(tmp_path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["entries"][1]["case_id"] = "case_other"
    payload["manifest_hash"] = CorpusManifest.model_validate(
        {**payload, "manifest_hash": None}
    ).computed_hash()
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(CorpusError, match="manifest_case_id_mismatch"):
        run_benchmark(manifest_path)


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        ("scenario_source", "non_synthetic_source_forbidden"),
        ("factor_source", "non_synthetic_source_forbidden"),
        ("evidence_source", "non_synthetic_source_forbidden"),
        ("currency", "currency_or_unknown_unit_forbidden"),
        ("partial", "incomplete_benchmark_forbidden"),
        ("missing_expected", "missing_regression_expectation"),
    ],
)
def test_positive_quality_boundaries_are_explicit(mutation: str, code: str) -> None:
    case = load_case(POSITIVE_PATH)
    payload = case.model_dump(mode="json")
    if mutation == "scenario_source":
        payload["scenario"]["source_class"] = "supplied"
    elif mutation == "factor_source":
        payload["scenario"]["factors"][0]["source_class"] = "supplied"
    elif mutation == "evidence_source":
        payload["scenario"]["evidence_references"][0]["source_class"] = "supplied"
    elif mutation == "currency":
        payload["scenario"]["loss_unit"] = "usd"
        payload["scenario"]["factors"][1]["unit"] = "usd"
    elif mutation == "partial":
        payload["model_request"]["completeness_status"] = "partial"
    else:
        payload["expected_input_hash"] = None
    with pytest.raises(CorpusQualityError, match=code):
        validate_positive_case(case.model_validate(payload))


def test_adversarial_case_acceptance_and_wrong_rejection_are_fail_closed(tmp_path: Path) -> None:
    manifest_path = copy_manifest(tmp_path)
    adversarial = tmp_path / "adversarial" / "currency_unit.json"
    payload = json.loads(adversarial.read_text(encoding="utf-8"))
    payload["expected_rejection"] = "wrong_code"
    adversarial.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(CorpusError, match="unexpected_adversarial_rejection"):
        run_benchmark(manifest_path)


def test_case_contract_rejects_unknown_content_and_manifest_enforces_unique_case_ids() -> None:
    payload = json.loads(POSITIVE_PATH.read_text(encoding="utf-8"))
    payload["raw_evidence"] = "forbidden"
    with pytest.raises(ValidationError):
        load_case_from_payload(payload)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["entries"].append(manifest["entries"][0])
    with pytest.raises(ValidationError, match="case_id values must be unique"):
        CorpusManifest.model_validate(manifest)


def load_case_from_payload(payload: dict[str, object]):
    from cyrisk_scenarios.models import CorpusCase

    return CorpusCase.model_validate(payload)


def test_cli_writes_local_result(tmp_path: Path) -> None:
    output_path = tmp_path / "result.json"
    assert main([str(MANIFEST_PATH), str(output_path)]) == 0
    output = json.loads(output_path.read_text(encoding="utf-8"))
    assert output["positive_results"][0]["case_id"] == "case_service"


def test_core_source_class_remains_enum_bound() -> None:
    assert SourceClass.SYNTHETIC.value == "synthetic"
