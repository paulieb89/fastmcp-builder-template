from __future__ import annotations

import re
from typing import Any

from .models import ManifestReview, ReviewFinding, Severity


_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]{2,63}$")
_STOP = {"a", "an", "and", "for", "from", "in", "of", "or", "the", "to", "with"}
_GENERIC_NAME_WORDS = {"tool", "resource", "prompt", "mcp", "fastmcp"}


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def review_fastmcp_manifest_data(manifest: dict[str, Any]) -> ManifestReview:
    findings: list[ReviewFinding] = []

    if not isinstance(manifest, dict):
        return ManifestReview(
            passed=False,
            findings=[
                ReviewFinding(
                    severity=Severity.HIGH,
                    code="manifest.not_object",
                    message="Manifest must be a JSON object.",
                    path="$",
                )
            ],
        )

    for key in ("name", "primitives"):
        if key not in manifest:
            findings.append(
                ReviewFinding(
                    severity=Severity.HIGH,
                    code=f"manifest.missing_{key}",
                    message=f"Manifest is missing required field '{key}'.",
                    path=f"$.{key}",
                )
            )

    name = manifest.get("name")
    if name is not None and (not isinstance(name, str) or not _NAME_PATTERN.match(name)):
        findings.append(
            ReviewFinding(
                severity=Severity.MEDIUM,
                code="manifest.name_format",
                message="Manifest name should be lowercase snake_case, 3-64 characters.",
                path="$.name",
            )
        )

    primitives = manifest.get("primitives", [])
    if not isinstance(primitives, list):
        findings.append(
            ReviewFinding(
                severity=Severity.HIGH,
                code="primitives.not_list",
                message="'primitives' must be a list.",
                path="$.primitives",
            )
        )
        primitives = []

    seen_names: set[str] = set()
    for index, primitive in enumerate(primitives):
        path = f"$.primitives[{index}]"
        if not isinstance(primitive, dict):
            findings.append(
                ReviewFinding(
                    severity=Severity.HIGH,
                    code="primitive.not_object",
                    message="Each primitive must be an object.",
                    path=path,
                )
            )
            continue

        kind = primitive.get("kind")
        primitive_name = primitive.get("name")
        description = primitive.get("description", "")

        if kind not in {"tool", "resource", "prompt"}:
            findings.append(
                ReviewFinding(
                    severity=Severity.HIGH,
                    code="primitive.invalid_kind",
                    message="Primitive kind must be one of: tool, resource, prompt.",
                    path=f"{path}.kind",
                )
            )

        if not isinstance(primitive_name, str) or not _NAME_PATTERN.match(primitive_name):
            findings.append(
                ReviewFinding(
                    severity=Severity.MEDIUM,
                    code="primitive.name_format",
                    message="Primitive name should be lowercase snake_case, 3-64 characters.",
                    path=f"{path}.name",
                )
            )
        elif primitive_name in seen_names:
            findings.append(
                ReviewFinding(
                    severity=Severity.HIGH,
                    code="primitive.duplicate_name",
                    message=f"Duplicate primitive name '{primitive_name}'.",
                    path=f"{path}.name",
                )
            )
        else:
            seen_names.add(primitive_name)

        if not isinstance(description, str) or len(description.strip()) < 20:
            findings.append(
                ReviewFinding(
                    severity=Severity.MEDIUM,
                    code="primitive.description_too_short",
                    message="Primitive descriptions should be specific enough for reliable use.",
                    path=f"{path}.description",
                )
            )

        if kind == "tool" and "parameters" not in primitive:
            findings.append(
                ReviewFinding(
                    severity=Severity.MEDIUM,
                    code="tool.missing_parameters",
                    message="Tools should declare parameters, even when the object is empty.",
                    path=f"{path}.parameters",
                )
            )

        if kind == "resource" and "uri" not in primitive:
            findings.append(
                ReviewFinding(
                    severity=Severity.HIGH,
                    code="resource.missing_uri",
                    message="Resources must declare a stable URI or URI pattern.",
                    path=f"{path}.uri",
                )
            )

        if kind == "prompt" and "arguments" not in primitive:
            findings.append(
                ReviewFinding(
                    severity=Severity.LOW,
                    code="prompt.missing_arguments",
                    message="Prompts should document their expected arguments, even if empty.",
                    path=f"{path}.arguments",
                )
            )

    return ManifestReview(
        passed=not any(finding.severity == Severity.HIGH for finding in findings),
        findings=findings,
    )


def description_quality(name: str, description: str, schema: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    normalized = description.strip().lower()

    if len(normalized) < 30:
        warnings.append("Description is short; include when to use the tool and what it returns.")
    if "and/or" in normalized or "etc" in normalized:
        warnings.append("Description uses ambiguous wording.")
    name_words = {w for w in name.split("_") if w and w not in _STOP and w not in _GENERIC_NAME_WORDS}
    description_words = _words(description)
    if name_words and not name_words.intersection(description_words):
        warnings.append("Description does not clearly connect to the tool name.")
    if schema.get("type") != "object":
        warnings.append("Schema should be a JSON object with named properties.")
    if not schema.get("properties"):
        warnings.append("Schema has no properties; confirm the tool truly needs no input.")

    return warnings
