"""Verify that the built wheel contains the typed package and no corpus test inputs."""

from __future__ import annotations

import zipfile
from pathlib import Path


def main() -> int:
    wheels = sorted(Path("dist").glob("cyrisk_scenarios-0.1.0-*.whl"))
    if len(wheels) != 1:
        raise SystemExit("expected exactly one cyrisk_scenarios v0.1.0 wheel")
    with zipfile.ZipFile(wheels[0]) as archive:
        names = set(archive.namelist())
    required = {
        "cyrisk_scenarios/__init__.py",
        "cyrisk_scenarios/harness.py",
        "cyrisk_scenarios/models.py",
        "cyrisk_scenarios/py.typed",
    }
    missing = required - names
    if missing:
        raise SystemExit(f"wheel missing required content: {sorted(missing)}")
    forbidden = {
        name for name in names if name.startswith("fixtures/") or name.startswith("tests/")
    }
    if forbidden:
        raise SystemExit(f"wheel contains forbidden content: {sorted(forbidden)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
