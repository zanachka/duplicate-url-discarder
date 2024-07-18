import pytest
from url_matcher import Patterns

from duplicate_url_discarder.processors import (
    NormalizerProcessor,
    QueryRemovalExceptProcessor,
    QueryRemovalProcessor,
    get_processor,
)
from duplicate_url_discarder.rule import UrlRule


def test_get_processor():
    pattern = Patterns([])
    args = ("foo", "bar")

    rule = UrlRule(0, pattern, "queryRemoval", args)
    processor = get_processor(rule)
    assert type(processor) is QueryRemovalProcessor
    assert processor.args == args

    rule = UrlRule(0, pattern, "unknown", args)
    with pytest.raises(ValueError, match="No URL processor named unknown"):
        get_processor(rule)


@pytest.mark.parametrize(
    ["args", "url", "expected"],
    [
        ((), "http://foo.example?foo=1&bar", "http://foo.example?foo=1&bar"),
        (("a",), "http://foo.example?foo=1&bar", "http://foo.example?foo=1&bar"),
        (("foo",), "http://foo.example?foo=1&bar", "http://foo.example?bar"),
        (("bar",), "http://foo.example?foo=1&bar", "http://foo.example?foo=1"),
        (
            ("bar",),
            "http://foo.example?foo=1&foo=2&bar&bar=1",
            "http://foo.example?foo=1&foo=2",
        ),
        (
            ("bar",),
            "http://foo.example?foo=1&bar#bar=frag",
            "http://foo.example?foo=1#bar=frag",
        ),
        (("foo", "baz"), "http://foo.example?foo=1&bar", "http://foo.example?bar"),
        (("foo", "bar"), "http://foo.example?foo=1&bar", "http://foo.example"),
    ],
)
def test_query_removal(args, url, expected):
    processor = QueryRemovalProcessor(args)
    assert processor.process(url) == expected


def test_query_removal_validate_args():
    with pytest.raises(TypeError, match="strings, not <class 'bytes'>: b''"):
        QueryRemovalProcessor((b"",))
    with pytest.raises(TypeError, match="strings, not <class 'NoneType'>: None"):
        QueryRemovalProcessor(("a", None, ""))
    QueryRemovalProcessor(("",))
    QueryRemovalProcessor(())


@pytest.mark.parametrize(
    ["args", "url", "expected"],
    [
        ((), "http://foo.example?foo=1&bar", "http://foo.example"),
        (("a",), "http://foo.example?foo=1&bar", "http://foo.example"),
        (("foo",), "http://foo.example?foo=1&bar", "http://foo.example?foo=1"),
        (("bar",), "http://foo.example?foo=1&bar", "http://foo.example?bar"),
        (
            ("bar",),
            "http://foo.example?foo=1&foo=2&bar&bar=1",
            "http://foo.example?bar&bar=1",
        ),
        (
            ("bar",),
            "http://foo.example?foo=1&bar#foo=frag",
            "http://foo.example?bar#foo=frag",
        ),
        (("foo", "baz"), "http://foo.example?foo=1&bar", "http://foo.example?foo=1"),
        (
            ("foo", "bar"),
            "http://foo.example?foo=1&bar",
            "http://foo.example?foo=1&bar",
        ),
    ],
)
def test_query_removal_except(args, url, expected):
    processor = QueryRemovalExceptProcessor(args)
    assert processor.process(url) == expected


def test_query_removal_except_validate_args():
    with pytest.raises(TypeError, match="strings, not <class 'bytes'>: b''"):
        QueryRemovalExceptProcessor((b"",))
    with pytest.raises(TypeError, match="strings, not <class 'NoneType'>: None"):
        QueryRemovalExceptProcessor(("a", None, ""))
    QueryRemovalExceptProcessor(("",))
    QueryRemovalExceptProcessor(())


@pytest.mark.parametrize(
    ["input_url", "expected"],
    (
        ("https://example.com", "https://example.com"),
        ("https://example.com?arg=1#frag", "https://example.com?arg=1#frag"),
        ("https://www.example.com", "https://example.com"),
        ("https://www.example.com?arg=1#frag", "https://example.com?arg=1#frag"),
        ("https://www2.example.com", "https://example.com"),
        ("https://www.us.example.com?arg=1#frag", "https://us.example.com?arg=1#frag"),
        ("https://www2.uk.example.com", "https://uk.example.com"),
    ),
)
def test_normalize_processor_www_prefixes(input_url, expected):
    assert NormalizerProcessor(None).process(input_url) == expected


@pytest.mark.parametrize(
    ["input_url", "expected"],
    (
        ("https://example.com", "https://example.com"),
        ("https://example.com/", "https://example.com"),
        ("https://example.com//", "https://example.com"),
        ("https://example.com?arg=1#frag", "https://example.com?arg=1#frag"),
        ("https://example.com/?arg=1#frag", "https://example.com?arg=1#frag"),
        ("https://example.com//?arg=1#frag", "https://example.com?arg=1#frag"),
        ("https://us.example.com/?arg=1#frag", "https://us.example.com?arg=1#frag"),
        ("https://us.example.com//?arg=1#frag", "https://us.example.com?arg=1#frag"),
    ),
)
def test_normalize_processor_trailing_slashes(input_url, expected):
    assert NormalizerProcessor(None).process(input_url) == expected


def test_normalize_processor_validate_args():
    with pytest.raises(TypeError, match="normalizeUrl doesn't accept args, got: "):
        NormalizerProcessor(("",))

    NormalizerProcessor(())
    NormalizerProcessor(None)
