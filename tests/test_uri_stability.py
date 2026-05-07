from fastmcp_builder.server import check_uri_stability


def test_stable_uri_passes():
    result = check_uri_stability("fastmcp-builder://docs/{slug}")
    assert result.passed
    assert result.warnings == []


def test_http_uri_flagged():
    result = check_uri_stability("https://example.com/docs")
    assert not result.passed
    assert any("HTTP" in w or "HTTPS" in w for w in result.warnings)


def test_query_string_flagged():
    result = check_uri_stability("myscheme://docs?page=1")
    assert not result.passed
    assert any("query" in w.lower() for w in result.warnings)


def test_volatile_token_flagged():
    result = check_uri_stability("myscheme://data/{timestamp}")
    assert not result.passed
    assert any("timestamp" in w for w in result.warnings)


def test_bare_id_token_flagged():
    result = check_uri_stability("myscheme://items/{id}")
    assert not result.passed
    assert any("{id}" in w for w in result.warnings)


def test_descriptive_id_token_passes():
    result = check_uri_stability("myscheme://items/{widget_id}")
    assert result.passed


def test_empty_uri_flagged():
    result = check_uri_stability("   ")
    assert not result.passed
    assert any("empty" in w.lower() for w in result.warnings)
