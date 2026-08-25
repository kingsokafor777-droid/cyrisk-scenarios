"""Deliberately generate sealed expectations from the released local contracts."""

from __future__ import annotations

import json
from pathlib import Path

from cyrisk_core.canonical import content_hash
from cyrisk_model.engine import analyze
from cyrisk_model.models import AnalysisRequest

from cyrisk_scenarios.harness import run_benchmark
from cyrisk_scenarios.models import CorpusCase

ROOT = Path(__file__).resolve().parents[1]
CASE_PATH = ROOT / "fixtures" / "cases" / "synthetic_service_case.json"
MANIFEST_PATH = ROOT / "fixtures" / "manifest.json"
RESULT_PATH = ROOT / "fixtures" / "expected_result.json"


def main() -> int:
    payload = json.loads(CASE_PATH.read_text(encoding="utf-8"))
    case = CorpusCase.model_validate(payload)
    request = AnalysisRequest(scenario=case.scenario, **case.model_request.model_dump())
    run = analyze(request)
    payload.update(
        expected_input_hash=run.input_hash,
        expected_output_hash=run.output_hash,
        expected_run_id=run.run_id,
    )
    CASE_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest_without_hash = {
        key: value for key, value in manifest.items() if key != "manifest_hash"
    }
    manifest["manifest_hash"] = content_hash(manifest_without_hash)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    result = run_benchmark(MANIFEST_PATH)
    RESULT_PATH.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
