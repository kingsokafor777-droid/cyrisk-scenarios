"""Sealed fictional scenarios and deterministic compatibility benchmarks for Cyrisk."""

from .harness import run_benchmark
from .models import CorpusManifest, CorpusResult

__all__ = ["CorpusManifest", "CorpusResult", "run_benchmark"]
