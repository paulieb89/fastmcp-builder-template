from fastmcp_builder.server import check_prompt_name_format


def test_valid_name_passes():
    result = check_prompt_name_format("design_fastmcp_server")
    assert result.passed
    assert result.warnings == []


def test_empty_name_flagged():
    result = check_prompt_name_format("   ")
    assert not result.passed
    assert any("empty" in w.lower() for w in result.warnings)


def test_not_snake_case_flagged():
    result = check_prompt_name_format("MyPrompt")
    assert not result.passed
    assert any("snake_case" in w for w in result.warnings)


def test_too_short_flagged():
    result = check_prompt_name_format("ab")
    assert not result.passed
    assert any("short" in w for w in result.warnings)


def test_too_long_flagged():
    result = check_prompt_name_format("a" * 65)
    assert not result.passed
    assert any("long" in w for w in result.warnings)


def test_prompt_suffix_flagged():
    result = check_prompt_name_format("review_prompt")
    assert not result.passed
    assert any("_prompt" in w for w in result.warnings)
