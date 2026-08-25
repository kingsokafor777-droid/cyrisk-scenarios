"""Local JSON verification CLI; no network, storage, or credential surface."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from .harness import run_benchmark


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify sealed Cyrisk synthetic scenario fixtures."
    )
    parser.add_argument("manifest", type=Path, help="Local corpus manifest JSON path")
    parser.add_argument("output", type=Path, help="Local corpus result JSON path")
    args = parser.parse_args(argv)
    result = run_benchmark(args.manifest)
    args.output.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
