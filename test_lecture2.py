"""Tests for the Session 2 data engine: strip_boilerplate and tokenize.

You do not run this file directly. The notebook runs it for you with

    pytest.main(["-q", "-p", "no:cacheprovider", "-k", "tokenize", "test_lecture2.py"])

and pytest checks the functions *you* defined in the notebook. If you made a
different cleaning decision on purpose (say, mother-in-law stays one word),
change the expected answer here -- and be ready to defend it.
"""
import __main__

import pytest


def notebook_function(name):
    """Fetch a function defined in the notebook, or fail with a clear message."""
    func = getattr(__main__, name, None)
    if func is None:
        pytest.fail("`%s` is not defined -- run the cell that defines it first" % name)
    return func


# ---------------------------------------------------------------------------
# strip_boilerplate
# ---------------------------------------------------------------------------

START = "*** START OF THE PROJECT GUTENBERG EBOOK PRIDE AND PREJUDICE ***"
END = "*** END OF THE PROJECT GUTENBERG EBOOK PRIDE AND PREJUDICE ***"


def body_lines(result):
    """Split the result into lines, ignoring one trailing newline either way."""
    assert isinstance(result, str), "strip_boilerplate must return a string, got %r" % (result,)
    return result.rstrip("\n").split("\n")


def test_strip_boilerplate_keeps_only_the_book():
    text = "\n".join([
        "The Project Gutenberg eBook of Pride and Prejudice",
        "Release date: June 1, 1998",
        START,
        "It is a truth universally acknowledged,",
        "that a single man in possession of a good fortune,",
        END,
        "Updated editions will replace the previous one.",
    ])
    result = notebook_function("strip_boilerplate")(text)
    assert body_lines(result) == [
        "It is a truth universally acknowledged,",
        "that a single man in possession of a good fortune,",
    ]


def test_strip_boilerplate_drops_the_marker_lines_themselves():
    text = "\n".join(["header", START, "body", END, "footer"])
    result = notebook_function("strip_boilerplate")(text)
    assert "*** START" not in result
    assert "*** END" not in result


def test_strip_boilerplate_keeps_blank_lines_inside_the_book():
    text = "\n".join([START, "Chapter 1", "", "It is a truth", END])
    result = notebook_function("strip_boilerplate")(text)
    assert body_lines(result) == ["Chapter 1", "", "It is a truth"]


def test_strip_boilerplate_without_end_marker_keeps_the_rest():
    text = "\n".join(["header", START, "line one", "line two"])
    result = notebook_function("strip_boilerplate")(text)
    assert body_lines(result) == ["line one", "line two"]


def test_strip_boilerplate_without_start_marker_returns_text_unchanged(capsys):
    text = "A file that is not from Project Gutenberg.\nNo markers here."
    result = notebook_function("strip_boilerplate")(text)
    assert result == text
    printed = capsys.readouterr().out
    assert printed.strip() != "", "expected a warning to be printed when no start marker is found"


# ---------------------------------------------------------------------------
# tokenize
# ---------------------------------------------------------------------------

# (raw text, expected tokens)
TOKENIZE_CASES = [
    ("“It",              ["it"]),                    # curly opening quote
    ("Mr.",                   ["mr"]),                    # trailing full stop
    ("mother-in-law",         ["mother", "in", "law"]),   # hyphenated compound
    ("don’t",            ["don't"]),                 # curly apostrophe -> ASCII
    ("1813",                  []),                        # numbers dropped
    ("_Netherfield_",         ["netherfield"]),           # Gutenberg italics
    ("www.gutenberg.org",     ["wwwgutenbergorg"]),       # dots removed
    ("--",                    []),                        # punctuation only
    ("’tis",             ["tis"]),                   # leading apostrophe stripped
    ("Bennet,”",         ["bennet"]),                # comma + closing quote
    ("",                      []),                        # empty input
    ("It is a truth universally acknowledged,",
     ["it", "is", "a", "truth", "universally", "acknowledged"]),  # order kept
]


@pytest.mark.parametrize("raw, expected", TOKENIZE_CASES)
def test_tokenize(raw, expected):
    assert notebook_function("tokenize")(raw) == expected


def test_tokenize_both_apostrophes_give_the_same_word():
    tokenize = notebook_function("tokenize")
    ascii_version = tokenize("don't")
    assert isinstance(ascii_version, list), "tokenize must return a list, got %r" % (ascii_version,)
    assert ascii_version == tokenize("don’t")
