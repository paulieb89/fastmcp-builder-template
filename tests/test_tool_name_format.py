from fastmcp_builder.server import check_tool_name_format


def test_valid_name_passes():
    result = check_tool_name_format("check_uri_stability")
    assert result.passed
    assert result.warnings == []


def test_empty_name_flagged():
    result = check_tool_name_format("   ")
    assert not result.passed
    assert any("empty" in w.lower() for w in result.warnings)


def test_not_snake_case_flagged():
    result = check_tool_name_format("Tool")
    assert not result.passed
    assert any("snake_case" in w for w in result.warnings)


def test_too_short_flagged():
    result = check_tool_name_format("ab")
    assert not result.passed
    assert any("short" in w for w in result.warnings)


def test_too_long_flagged():
    result = check_tool_name_format("a" * 65)
    assert not result.passed
    assert any("long" in w for w in result.warnings)


def test_generic_name_flagged():
    result = check_tool_name_format("run")
    assert not result.passed
    assert any("generic" in w for w in result.warnings)


def test_tool_suffix_flagged():
    result = check_tool_name_format("my_tool")
    assert not result.passed
    assert any("_tool" in w for w in result.warnings)


def test_descriptive_name_passes():
    result = check_tool_name_format("validate_prompt_arguments")
    assert result.passed
