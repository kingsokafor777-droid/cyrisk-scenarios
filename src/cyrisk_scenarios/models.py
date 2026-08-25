"""Strict contracts for a payload-free, sealed synthetic scenario corpus."""

from __future__ import annotations

from enum import Enum
from typing import Final, Literal

from cyrisk_core.canonical import content_hash
from cyrisk_core.models import RiskScenario
from pydantic import BaseModel, ConfigDict, Field, field_validator

CORPUS_SCHEMA_VERSION: Final[Literal["cyrisk.scenarios/v1"]] = "cyrisk.scenarios/v1"
HASH_PATTERN = r"^[a-f0-9]{64}$"
COMMIT_PATTERN = r"^[a-f0-9]{40}$"
ID_PATTERN = r"^[a-z][a-z0-9_-]{2,63}$"


class StrictModel(BaseModel):
    """Fail closed so corpus inputs never become an unbounded data-ingestion format."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class EntryKind(str, Enum):
    POSITIVE = "positive"
    ADVERSARIAL = "adversarial"


class CorpusEntry(StrictModel):
    """An intentionally local, repository-relative fixture reference."""

    case_id: str = Field(pattern=ID_PATTERN)
    kind: EntryKind
    relative_path: str = Field(pattern=r"^(cases|adversarial)/[a-z0-9_-]+\.json$")


class CorpusManifest(StrictModel):
    """Versioned fixture index whose hash covers every declared entry."""

    schema_version: Literal["cyrisk.scenarios/v1"] = CORPUS_SCHEMA_VERSION
    corpus_id: str = Field(pattern=ID_PATTERN)
    core_commit: str = Field(pattern=COMMIT_PATTERN)
    model_commit: str = Field(pattern=COMMIT_PATTERN)
    entries: tuple[CorpusEntry, ...] = Field(min_length=1)
    manifest_hash: str | None = Field(default=None, pattern=HASH_PATTERN)

    @field_validator("entries")
    @classmethod
    def unique_case_ids(cls, value: tuple[CorpusEntry, ...]) -> tuple[CorpusEntry, ...]:
        identifiers = [item.case_id for item in value]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("corpus entry case_id values must be unique")
        return value

    def computed_hash(self) -> str:
        return content_hash(self.model_dump(mode="json", exclude={"manifest_hash"}))

    def verify_integrity(self) -> bool:
        return self.manifest_hash is not None and self.manifest_hash == self.computed_hash()


class ModelRequestFields(StrictModel):
    """Explicit model fields excluding the case-owned scenario object."""

    request_id: str = Field(pattern=ID_PATTERN)
    frequency_factor_id: str = Field(pattern=ID_PATTERN)
    loss_factor_ids: tuple[str, ...] = Field(min_length=1)
    deterministic_seed: int = Field(ge=0, le=2_147_483_647)
    sample_count: int = Field(ge=100, le=100_000)
    model_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    completeness_status: Literal["complete", "partial", "insufficient"]
    limitations: str = Field(min_length=1, max_length=500)


class CorpusCase(StrictModel):
    """One fictional case with declared benchmark expectations or rejection semantics."""

    schema_version: Literal["cyrisk.scenarios/v1"] = CORPUS_SCHEMA_VERSION
    case_id: str = Field(pattern=ID_PATTERN)
    title: str = Field(min_length=1, max_length=160)
    scenario: RiskScenario
    model_request: ModelRequestFields
    expected_input_hash: str | None = Field(default=None, pattern=HASH_PATTERN)
    expected_output_hash: str | None = Field(default=None, pattern=HASH_PATTERN)
    expected_run_id: str | None = Field(default=None, pattern=ID_PATTERN)
    expected_rejection: str | None = Field(default=None, pattern=r"^[a-z_]{3,80}$")
    limitation: str = Field(min_length=1, max_length=500)


class BenchmarkCaseResult(StrictModel):
    """A deterministic compatibility record with no interpretation of synthetic values."""

    case_id: str = Field(pattern=ID_PATTERN)
    input_hash: str = Field(pattern=HASH_PATTERN)
    output_hash: str = Field(pattern=HASH_PATTERN)
    run_id: str = Field(pattern=ID_PATTERN)
    limitation: str = Field(min_length=1, max_length=500)


class AdversarialResult(StrictModel):
    """Evidence that a named quality boundary rejected a fictional bad case."""

    case_id: str = Field(pattern=ID_PATTERN)
    rejection_code: str = Field(pattern=r"^[a-z_]{3,80}$")


class CorpusResult(StrictModel):
    """Ordered local regression result, not a risk, control, or decision artifact."""

    schema_version: Literal["cyrisk.scenarios/v1"] = CORPUS_SCHEMA_VERSION
    corpus_id: str = Field(pattern=ID_PATTERN)
    manifest_hash: str = Field(pattern=HASH_PATTERN)
    positive_results: tuple[BenchmarkCaseResult, ...]
    adversarial_results: tuple[AdversarialResult, ...]
    limitation: str = (
        "Corpus outputs prove only deterministic compatibility of sealed fictional fixtures; "
        "they do not forecast, estimate loss, validate evidence, establish control effect, "
        "or make a decision."
    )
