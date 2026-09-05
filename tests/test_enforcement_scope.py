import pytest

from law_and_order.enforcement import parse_enforcement_channels


def test_empty_config_disables_enforcement_everywhere():
    assert parse_enforcement_channels("") == frozenset()


def test_single_channel_parses():
    assert parse_enforcement_channels("1478480447431376966") == frozenset({1478480447431376966})


def test_multiple_channels_parse():
    assert parse_enforcement_channels("123,456") == frozenset({123, 456})


def test_whitespace_is_tolerated():
    assert parse_enforcement_channels(" 123 , 456 ") == frozenset({123, 456})


def test_trailing_comma_is_tolerated():
    assert parse_enforcement_channels("123,") == frozenset({123})


def test_duplicates_collapse():
    assert parse_enforcement_channels("123,123") == frozenset({123})


def test_malformed_entry_fails_fast():
    with pytest.raises(ValueError):
        parse_enforcement_channels("123,not-a-channel")


def test_parse_is_deterministic():
    raw = "123,456"
    assert parse_enforcement_channels(raw) == parse_enforcement_channels(raw)
