"""
tests/test_fix_code_engine.py
──────────────────────────────
Covers all 19 FixCode rules: unit tests for the individual rule
functions, plus integration tests through FixCodeEngine.get_response()
and the "real word / real code" regression suite built up while these
rules were developed (the safelists, word-boundary fixes, etc. all
exist because of a false positive found in exactly this kind of test).
"""
import pytest

from FixCode.fix_code_engine import (
    FixCodeEngine,
    _print_similarity,
    _fix_print_typos,
    _fix_print_case,
    _fix_semicolons,
    _fix_print_statement,
    _fix_invalid_operators,
    _fix_operators_in_line,
    _fix_keyword_typos,
    _fix_quotes_parens,
    _fix_line,
    _fix_missing_colons,
    _fix_logic_errors,
    _fix_indentation_issues,
    _fix_else_if,
    _fix_raw_input,
    _fix_increment_decrement,
    _fix_missing_fstring,
    _detect_mutable_defaults,
    _detect_undefined_names,
    _detect_off_by_one,
    _detect_is_literal,
)


# ── R0: print typo detection (similarity + safelist) ──────────────────
@pytest.mark.parametrize("word", [
    "printf", "Printtf", "prnit", "pritn", "prin", "prit",
])
def test_r0_flags_real_typos(word):
    assert _print_similarity(word) is True


@pytest.mark.parametrize("word", [
    "sprint", "reprint", "imprint", "footprint", "fingerprint",
    "blueprint", "point", "points", "paint", "misprint", "printer",
    "prints", "printed", "greet", "write", "great", "prime", "pride",
])
def test_r0_never_flags_real_words(word):
    assert _print_similarity(word) is False


def test_r0_fix_replaces_typo_call():
    code, issues = _fix_print_typos('printf("hi")')
    assert code == 'print("hi")'
    assert len(issues) == 1


def test_r0_does_not_touch_real_function_calls():
    code, issues = _fix_print_typos('sprint(x)\nfootprint(y)\npoint(1,2)')
    assert "sprint(x)" in code
    assert "footprint(y)" in code
    assert "point(1,2)" in code
    assert not issues


# ── R1: print case normalization ───────────────────────────────────────
def test_r1_fixes_case_variants():
    code, issues = _fix_print_case('Print("hi")\nPRINT("bye")')
    assert code == 'print("hi")\nprint("bye")'
    assert len(issues) == 2


# ── R2: trailing semicolons ─────────────────────────────────────────────
def test_r2_removes_trailing_semicolon():
    code, issues = _fix_semicolons("x = 5;")
    assert code == "x = 5"
    assert len(issues) == 1


def test_r2_leaves_lines_without_semicolon():
    code, issues = _fix_semicolons("x = 5")
    assert code == "x = 5"
    assert not issues


# ── R3: quotes / parens / brackets / braces + triple-quote blocks ─────
def test_r3_closes_unclosed_paren():
    fixed, issues, _ = _fix_line('print("hello', 1)
    assert fixed == 'print("hello")'
    assert len(issues) == 2  # unclosed quote + unclosed paren


def test_r3_closes_unclosed_bracket_and_brace():
    fixed, issues, _ = _fix_line("x = [1, 2, 3", 1)
    assert fixed == "x = [1, 2, 3]"
    fixed2, issues2, _ = _fix_line('d = {"a": 1', 1)
    assert fixed2 == 'd = {"a": 1}'


def test_r3_multiline_docstring_untouched():
    code = (
        'def f():\n'
        '    """\n'
        '    This has if x = 5 as example text, semicolons; and stuff.\n'
        '    """\n'
        '    return 1\n'
    )
    fixed, issues = _fix_quotes_parens(code)
    assert "if x = 5 as example text, semicolons; and stuff." in fixed
    assert not issues


def test_r3_unclosed_triple_quote_gets_closing_marker():
    fixed, issues = _fix_quotes_parens('x = """unterminated')
    assert fixed.endswith('"""')
    assert len(issues) == 1


# ── R5: missing colons (+ word-boundary safety) ─────────────────────────
@pytest.mark.parametrize("code,expected", [
    ("if x", "if x:"),
    ("elif x", "elif x:"),
    ("else", "else:"),
    ("for i in range(5)", "for i in range(5):"),
    ("while True", "while True:"),
    ("def f()", "def f():"),
    ("class Foo", "class Foo:"),
    ("try", "try:"),
    ("except ValueError", "except ValueError:"),
    ("finally", "finally:"),
])
def test_r5_adds_missing_colon(code, expected):
    fixed, issues = _fix_missing_colons(code)
    assert fixed == expected
    assert len(issues) == 1


@pytest.mark.parametrize("code", [
    "elsewhere = 5",
    "exceptions = []",
    "exception_handler = foo",
    "finally_flag = True",
    "trying = True",
    "defaults = {}",
    "classroom = 5",
])
def test_r5_never_touches_lookalike_identifiers(code):
    fixed, issues = _fix_missing_colons(code)
    assert fixed == code
    assert not issues


# ── R6: assignment (=) -> comparison (==) in conditions ────────────────
def test_r6_fixes_assignment_in_if():
    fixed, issues = _fix_logic_errors("if x = 5:\n    pass")
    assert "if x == 5:" in fixed
    assert len(issues) == 1


def test_r6_leaves_correct_comparisons_alone():
    fixed, issues = _fix_logic_errors("if x == 5:\n    pass")
    assert fixed == "if x == 5:\n    pass"
    assert not issues


# ── R7: tabs -> spaces (leading whitespace only) ────────────────────────
def test_r7_normalizes_mixed_indentation():
    code = "def f():\n\tx = 1\n    y = 2\n\treturn x + y"
    fixed, issues = _fix_indentation_issues(code)
    assert "\t" not in fixed
    assert len(issues) >= 1


def test_r7_never_touches_tabs_inside_string_content():
    code = 'x = "a\\tb"\nprint(x)'
    fixed, issues = _fix_indentation_issues(code)
    assert fixed == code


# ── R8: Python 2 print statement ────────────────────────────────────────
@pytest.mark.parametrize("code,expected_substr", [
    ('print "Hello"', 'print("Hello")'),
    ("print 'World'", "print('World')"),
    ('print "Sum:", x', 'print("Sum:", x)'),
])
def test_r8_wraps_python2_print(code, expected_substr):
    fixed, issues = _fix_print_statement(code)
    assert expected_substr in fixed
    assert len(issues) == 1


@pytest.mark.parametrize("code", [
    'print("already fine")',
    'print ("space before paren")',
    "print = 5",
    "print.something()",
    "print",
])
def test_r8_never_touches_non_statement_print(code):
    fixed, issues = _fix_print_statement(code)
    assert fixed == code
    assert not issues


# ── R9: invalid comparison operators (string-safe) ──────────────────────
@pytest.mark.parametrize("code,expected", [
    ("if x =< 5:", "if x <= 5:"),
    ("while y => 10:", "while y >= 10:"),
    ("if a <> b:", "if a != b:"),
])
def test_r9_fixes_invalid_operators(code, expected):
    fixed, issues = _fix_invalid_operators(code)
    assert fixed == expected
    assert len(issues) == 1


def test_r9_never_touches_operators_inside_strings():
    fixed, found = _fix_operators_in_line('print("a <> b")')
    assert fixed == 'print("a <> b")'
    assert not found


# ── R10: keyword misspellings (exact match only) ────────────────────────
@pytest.mark.parametrize("code,expected", [
    ("retrun 5", "return 5"),
    ("improt os", "import os"),
    ("x = flase", "x = False"),
    ("y = ture", "y = True"),
    ("calss Dog:", "class Dog:"),
])
def test_r10_fixes_keyword_typos(code, expected):
    fixed, issues = _fix_keyword_typos(code)
    assert fixed == expected


@pytest.mark.parametrize("code", [
    "class_name = 5",
    "# improt this comment should stay",
    "returning = 5",
])
def test_r10_never_touches_lookalike_identifiers_or_comments(code):
    fixed, issues = _fix_keyword_typos(code)
    assert fixed == code
    assert not issues


# ── R11: else if -> elif ─────────────────────────────────────────────────
def test_r11_fixes_else_if():
    fixed, issues = _fix_else_if("else if x > 5:")
    assert fixed == "elif x > 5:"
    assert len(issues) == 1


# ── R12: raw_input -> input ──────────────────────────────────────────────
def test_r12_fixes_raw_input():
    fixed, issues = _fix_raw_input('name = raw_input("Name: ")')
    assert fixed == 'name = input("Name: ")'
    assert len(issues) == 1


# ── R13: ++ / -- ──────────────────────────────────────────────────────────
@pytest.mark.parametrize("code,expected", [
    ("x++", "x += 1"),
    ("x--", "x -= 1"),
    ("++x", "x += 1"),
    ("--x", "x -= 1"),
])
def test_r13_fixes_inc_dec(code, expected):
    fixed, issues = _fix_increment_decrement(code)
    assert fixed == expected
    assert len(issues) == 1


# ── R15: missing f-string prefix (with .format() safety guard) ──────────
def test_r15_adds_missing_f_prefix():
    fixed, issues = _fix_missing_fstring('print("Hello {name}")')
    assert fixed == 'print(f"Hello {name}")'
    assert len(issues) == 1


def test_r15_never_touches_dot_format_usage():
    code = 'print("Hello {name}".format(name=x))'
    fixed, issues = _fix_missing_fstring(code)
    assert fixed == code
    assert not issues


def test_r15_never_touches_existing_fstring():
    code = 'print(f"already an fstring {x}")'
    fixed, issues = _fix_missing_fstring(code)
    assert fixed == code


# ── R16: mutable default argument (detect only) ──────────────────────────
def test_r16_warns_on_mutable_default():
    issues = _detect_mutable_defaults("def f(x=[]):")
    assert len(issues) == 1


def test_r16_silent_on_immutable_defaults():
    issues = _detect_mutable_defaults("def f(x=None):")
    assert not issues


# ── R17: undefined name (whole-file bag model, detect only) ─────────────
def test_r17_flags_never_defined_name():
    issues = _detect_undefined_names("print(totally_undefined_var)")
    assert len(issues) == 1


def test_r17_silent_on_defined_names():
    code = "x = 5\nprint(x)\nfor i in range(3):\n    print(i)"
    issues = _detect_undefined_names(code)
    assert not issues


def test_r17_silent_on_forward_references_in_same_file():
    code = (
        "def outer():\n"
        "    def inner():\n"
        "        return helper()\n"
        "    def helper():\n"
        "        return 1\n"
        "    return inner()\n"
    )
    issues = _detect_undefined_names(code)
    assert not issues


# ── R18: off-by-one loop risk (detect only) ──────────────────────────────
def test_r18_flags_range_len_plus_one():
    issues = _detect_off_by_one("for i in range(len(arr) + 1):")
    assert len(issues) == 1


def test_r18_silent_on_correct_range():
    issues = _detect_off_by_one("for i in range(len(arr)):")
    assert not issues


# ── R19: is/is not compared against a literal (detect only) ─────────────
def test_r19_flags_is_literal():
    issues = _detect_is_literal("if x is 5:\n    pass")
    assert len(issues) == 1


@pytest.mark.parametrize("code", [
    "if x is None:\n    pass",
    "if x is True:\n    pass",
    "if a is b:\n    pass",
])
def test_r19_silent_on_legitimate_is_usage(code):
    issues = _detect_is_literal(code)
    assert not issues


# ── Integration tests through the full engine ────────────────────────────
class TestFixCodeEngineIntegration:
    def setup_method(self):
        self.engine = FixCodeEngine()

    def test_original_conversation_bug_report(self):
        """The exact example that kicked off the FixCode rewrite:
        print typo, missing colon, = vs ==, trailing semicolon."""
        code = (
            'printf("Hello")\n'
            'x = 5\n'
            'if x = 5\n'
            '    print(x, "world")\n'
            'y = 10;\n'
        )
        result = self.engine.get_response(code)
        assert 'print("Hello")' in result
        assert "if x == 5:" in result
        assert "y = 10\n" in result or result.strip().endswith("y = 10")

    def test_real_word_identifiers_survive_the_full_pipeline(self):
        code = (
            "def sprint(d): return d\n"
            "point = (1,2)\n"
            "exceptions = []\n"
            "elsewhere = 5\n"
            "print(sprint(5))\n"
            "print(point)\n"
        )
        result = self.engine.get_response(code)
        for safe in ("def sprint", "point = (1,2)", "exceptions = []",
                     "elsewhere = 5"):
            assert safe in result

    def test_docstring_content_is_never_rewritten(self):
        code = (
            'def f():\n'
            '    """\n'
            '    This has if x = 5 as example text, semicolons; and stuff.\n'
            '    """\n'
            '    return 1\n'
        )
        result = self.engine.get_response(code)
        assert "if x = 5 as example text, semicolons; and stuff." in result

    def test_python2_beginner_snippet(self):
        code = 'print "Hello, World!"\nname = "Dara"\nprint "Hi", name'
        result = self.engine.get_response(code)
        assert 'print("Hello, World!")' in result
        assert 'print("Hi", name)' in result

    def test_start_trigger_returns_instructions(self):
        result = self.engine.get_response("/start")
        assert "Fix Code Mode" in result

    def test_empty_input_returns_instructions(self):
        result = self.engine.get_response("")
        assert "Fix Code Mode" in result
