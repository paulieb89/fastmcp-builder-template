import pytest

import notes_server
from notes_server import note_by_name, notes_index, summarise_note


# ---------------------------------------------------------------------------
# Resource: notes://index
# ---------------------------------------------------------------------------


def test_notes_index_returns_string():
    result = notes_index()
    assert isinstance(result, str)


def test_notes_index_contains_sample_notes():
    result = notes_index()
    assert "getting-started" in result
    assert "architecture" in result


def test_notes_index_entries_are_sorted():
    entries = notes_index().splitlines()
    assert entries == sorted(entries)


# ---------------------------------------------------------------------------
# Resource: notes://{name}
# ---------------------------------------------------------------------------


def test_note_by_name_returns_content():
    content = note_by_name("getting-started")
    assert "Getting Started" in content


def test_note_by_name_raises_file_not_found_for_missing():
    with pytest.raises(FileNotFoundError):
        note_by_name("does-not-exist")


def test_note_by_name_raises_value_error_for_path_traversal():
    with pytest.raises(ValueError):
        note_by_name("../../etc/passwd")


def test_note_by_name_raises_value_error_for_absolute_path():
    with pytest.raises(ValueError):
        note_by_name("/etc/passwd")


# ---------------------------------------------------------------------------
# Tool: summarise_note
# ---------------------------------------------------------------------------


def test_summarise_note_includes_headings_section():
    result = summarise_note("getting-started")
    assert "## Headings" in result


def test_summarise_note_includes_top_level_heading():
    result = summarise_note("getting-started")
    assert "# Getting Started" in result


def test_summarise_note_includes_opening_paragraph():
    result = summarise_note("getting-started")
    assert "## Opening paragraph" in result


def test_summarise_note_raises_file_not_found_for_missing():
    with pytest.raises(FileNotFoundError):
        summarise_note("no-such-note")


def test_summarise_note_raises_value_error_for_path_traversal():
    with pytest.raises(ValueError):
        summarise_note("../notes_server")


def test_summarise_note_architecture_has_multiple_headings():
    result = summarise_note("architecture")
    assert result.count("#") > 2


# ---------------------------------------------------------------------------
# Empty-note edge case (tmp directory override)
# ---------------------------------------------------------------------------


def test_summarise_note_returns_empty_message_for_blank_note(tmp_path, monkeypatch):
    (tmp_path / "blank.md").write_text("", encoding="utf-8")
    monkeypatch.setattr(notes_server, "NOTES_DIR", tmp_path)
    result = notes_server.summarise_note("blank")
    assert result == "(empty note)"


def test_notes_index_returns_empty_message_when_no_notes(tmp_path, monkeypatch):
    monkeypatch.setattr(notes_server, "NOTES_DIR", tmp_path)
    result = notes_server.notes_index()
    assert result == "(no notes found)"
