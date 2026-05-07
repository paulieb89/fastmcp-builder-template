from pydantic import BaseModel


class ReviewResult(BaseModel):
    passed: bool
    warnings: list[str]


def review_description(description: str) -> ReviewResult:
    warnings = []
    if len(description.strip()) < 30:
        warnings.append("Description is too short.")
    return ReviewResult(passed=not warnings, warnings=warnings)
