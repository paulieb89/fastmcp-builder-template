from pathlib import Path


def read_local_note(path: Path) -> str:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved.name)
    return resolved.read_text(encoding="utf-8")
