from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class PrimitiveKind(str, Enum):
    TOOL = "tool"
    RESOURCE = "resource"
    PROMPT = "prompt"


class Severity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PrimitiveClassification(BaseModel):
    recommendation: PrimitiveKind
    rationale: str
    confidence: float = Field(ge=0, le=1)
    alternatives: list[str] = Field(default_factory=list)


class ReviewFinding(BaseModel):
    severity: Severity
    code: str
    message: str
    path: str


class ManifestReview(BaseModel):
    passed: bool
    findings: list[ReviewFinding] = Field(default_factory=list)


class SilentErrorReport(BaseModel):
    """Source-level scan for the silent-failure-conversion anti-pattern.

    Findings reuse ReviewFinding so the design-review skill can merge them
    with manifest review output and sort uniformly by severity.
    """
    passed: bool
    findings: list[ReviewFinding] = Field(default_factory=list)


class ParameterSpec(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True


class ToolContract(BaseModel):
    name: str
    description: str
    parameters: list[ParameterSpec]
    return_shape: dict[str, str]
    error_cases: list[str]


class ResourceContract(BaseModel):
    uri_pattern: str
    mime_type: str
    read_behavior: str
    caching_notes: str


class PromptContract(BaseModel):
    name: str
    arguments: list[ParameterSpec]
    template_outline: list[str]


class ServerPlan(BaseModel):
    goal: str
    files: list[str]
    checklist: list[str]
    primitives: list[PrimitiveKind]


class DescriptionQualityReport(BaseModel):
    passed: bool
    warnings: list[str] = Field(default_factory=list)


class ErrorDesignReport(BaseModel):
    validation_errors: list[str] = Field(default_factory=list)
    transient_errors: list[str] = Field(default_factory=list)
    permission_errors: list[str] = Field(default_factory=list)
    business_errors: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class UriStabilityReport(BaseModel):
    passed: bool
    warnings: list[str] = Field(default_factory=list)


class ToolNameReport(BaseModel):
    passed: bool
    warnings: list[str] = Field(default_factory=list)


class PromptNameReport(BaseModel):
    passed: bool
    warnings: list[str] = Field(default_factory=list)


JsonObject = dict[str, Any]
ControlPattern = Literal["model", "client", "user", "unknown"]
