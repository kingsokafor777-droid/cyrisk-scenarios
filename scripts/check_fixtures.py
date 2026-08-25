"""Verify that committed corpus inputs and expected output remain deterministic."""

from __future__ import annotations

from pathlib import Path

from cyrisk_scenarios.harness import run_benchmark

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "fixtures" / "manifest.json"
RESULT_PATH = ROOT / "fixtures" / "expected_result.json"


def main() -> int:
    actual = run_benchmark(MANIFEST_PATH).model_dump_json(indent=2) + "\n"
    expected = RESULT_PATH.read_text(encoding="utf-8")
    if actual != expected:
        raise SystemExit(
            "sealed fixture benchmark differs; review before deliberately regenerating"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
