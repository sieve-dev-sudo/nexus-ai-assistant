"""
FixCode/fix_code_engine.py  — 100% LOCAL, no API
Rules:
  R0. Any word ending with ( that is NOT a known builtin/keyword
      but looks like a typo of print → replace with print(
      e.g. printf(  Printtf(  PrInt(  prnit(  → print(
  R1. Normalize print case variants → print
  R2. Remove trailing semicolons
  R3. Fix unclosed quotes / parentheses
  R4. Evaluate and show output of print() calls
  R8. Fix Python 2-style print statement: print "x" → print("x")
  R9. Fix invalid comparison operators: =< => <> → <= >= !=
  R10. Fix common keyword misspellings (exact match): retrun → return, etc.
  R11. Fix `else if` (C/JS style) → `elif`
  R12. Fix Python 2 `raw_input(` → `input(`
  R13. Fix `++` / `--` → `+= 1` / `-= 1` (no increment/decrement in Python)
  R14. Fix unclosed `[` `]` and `{` `}` (extends R3's paren logic)
  R15. Fix missing f-string prefix: "{x}" → f"{x}"
  R16. Warn: mutable default argument def f(x=[]): (detect only)
  R17. Warn: name used but never defined/imported in file (detect only)
  R18. Warn: off-by-one loop risk — range(len(x)+1), <= len(x) (detect only)
  R19. Warn: `is`/`is not` compared against a literal (detect only)
"""

import re
import ast
import builtins as _builtins_mod
import operator

START_TRIGGERS = ("/start", "/help", "help", "menu")

_BUILTIN_NAMES = set(dir(_builtins_mod))

INSTRUCTIONS = (
    "🛠 Fix Code Mode (LOCAL) : AI នឹងវិភាគ Python code ហើយ:\n\n"
    "  1️⃣  ស្វែងរក Error ទាំងអស់\n"
    "  2️⃣  បង្ហាញ Fixed Code ដែលបានកែពេញលេញ\n"
    "  3️⃣  គណនា Output ដែលនឹងបានបន្ទាប់ពី run\n\n"
    "📋 Paste កូដ Python ចូល input bar ហើយចុច Send!\n"
    "   (Shift+Enter = ចុះបន្ទាត់ថ្មី)\n\n"
)

# ── known Python builtins / keywords that start calls (never replace these)
_KNOWN_CALLS = {
    "print", "input", "int", "float", "str", "bool", "list", "tuple", "set", "dict",
    "len", "range", "type", "isinstance", "hasattr", "getattr", "setattr", "open",
    "enumerate", "zip", "map", "filter", "sorted", "reversed", "sum", "min", "max",
    "abs", "round", "pow", "hex", "oct", "bin", "chr", "ord", "repr", "id", "hash",
    "all", "any", "iter", "next", "vars", "dir", "help", "exit", "quit",
    "if", "for", "while", "def", "class", "return", "import", "from", "with", "try",
    "except", "finally", "raise", "pass", "break", "continue", "lambda", "yield",
    "and", "or", "not", "in", "is", "True", "False", "None", "super", "self",
    "append", "insert", "remove", "pop", "sort", "clear", "extend", "update",
    "format", "join", "split", "strip", "replace", "find", "upper", "lower",
}

# ── similarity: does a token "look like" a print typo?
#   Strategy: Levenshtein edit distance to "print" must be small (≤2),
#   which is far stricter than "shares 3 of 5 letters in any order"
#   (the old rule flagged real words like sprint/point/paint as typos).
#   Real words that happen to sit close to "print" in edit-distance
#   terms are also hard-excluded via a safelist below.
def _levenshtein(a: str, b: str) -> int:
    """Standard edit distance (insertions, deletions, substitutions)."""
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        curr = [i] + [0] * lb
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            curr[j] = min(
                prev[j] + 1,        # deletion
                curr[j - 1] + 1,    # insertion
                prev[j - 1] + cost,  # substitution
            )
        prev = curr
    return prev[lb]


# Real identifiers/words that legitimately contain or resemble "print" —
# never flag these as a typo, no matter how close the edit distance is.
_PRINT_SAFE_WORDS = {
    "sprint", "sprints", "sprinted", "sprinting",
    "reprint", "reprints", "imprint", "imprints",
    "footprint", "footprints", "fingerprint", "fingerprints",
    "blueprint", "blueprints", "misprint", "misprints", "offprint",
    "eprint", "preprint", "preprints", "printer", "printers",
    "printable", "printout", "printouts", "printing",
    "prints", "printed",
    "point", "points", "pointer", "pointers", "midpoint", "endpoint",
    "endpoints", "checkpoint", "checkpoints", "breakpoint", "breakpoints",
    "viewpoint", "waypoint", "pinpoint", "standpoint",
    "paint", "paints", "painter",
    "prime", "primes", "pride",
}


def _print_similarity(word: str) -> bool:
    """Return True if word is a plausible typo of 'print'."""
    w = word.lower()
    if w == "print":
        return False
    if word in _KNOWN_CALLS or w in _KNOWN_CALLS:
        return False
    if w in _PRINT_SAFE_WORDS:
        return False
    if not (3 <= len(w) <= 9):
        return False
    return _levenshtein(w, "print") <= 2


# Matches any identifier immediately followed by (
_CALL_RE = re.compile(r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\(')


def _fix_print_typos(code: str):
    """R0: replace print-like typos (printf, Printtf, prnit …) with print."""
    issues = []
    lines = code.splitlines()
    result = []
    for lineno, line in enumerate(lines, 1):
        def _repl(m):
            word = m.group(1)
            if _print_similarity(word):
                issues.append((lineno,
                               f"'{word}(...)' មិនមែន Python function : "
                               f"ប្រហែលជា typo នៃ print()",
                               f"{word}(  →  print("))
                return "print("
            return m.group(0)
        new_line = _CALL_RE.sub(_repl, line)
        result.append(new_line)
    return "\n".join(result), issues


# ── R1: remaining case variants of print (Print, PRINT, PrInT …)
_PRINT_CASE_RE = re.compile(r'\b(print)\s*\(', re.IGNORECASE)


def _fix_print_case(code: str):
    issues = []
    lines = code.splitlines()
    result = []
    for lineno, line in enumerate(lines, 1):
        def _repl(m):
            word = m.group(1)
            if word != "print":
                issues.append((lineno,
                               f"'{word}' ខុស case → ត្រូវជា 'print' (Python case-sensitive)",
                               f"{word}(  →  print("))
            return "print("
        new_line = _PRINT_CASE_RE.sub(_repl, line)
        result.append(new_line)
    return "\n".join(result), issues


# ── R2: trailing semicolons
_SEMI_RE = re.compile(r';\s*$')


def _fix_semicolons(code: str):
    issues = []
    lines = code.splitlines()
    result = []
    for lineno, line in enumerate(lines, 1):
        s = line.rstrip()
        if _SEMI_RE.search(s):
            result.append(_SEMI_RE.sub("", s))
            issues.append((lineno,
                           "';' នៅចុងបន្ទាត់ : Python មិនប្រើ ';' ដើម្បីបញ្ចប់ statement",
                           "លុប ';' ចេញ"))
        else:
            result.append(line)
    return "\n".join(result), issues


# ── R8: Python 2-style print statement (no parentheses)
#   print "x"        →  print("x")
#   print x, y        →  print(x, y)
#   print "Sum:", x    →  print("Sum:", x)
# Case-insensitive so it also normalises `Print "x"` in one shot.
_PY2_PRINT_RE = re.compile(r'^(\s*)print(?![A-Za-z0-9_(])\s+(\S.*)$', re.IGNORECASE)

# Things that legitimately follow the word "print" without being
# Python-2 print arguments — must NOT be wrapped in print(...).
_PY2_PRINT_SKIP_PREFIXES = ("=", "==", "!=", "<=", ">=", "+=", "-=", "*=",
                             "/=", "//=", "%=", "**=", ".", ",")


def _fix_print_statement(code: str):
    """R8: detect & wrap Python 2-style `print` statements."""
    issues = []
    lines = code.splitlines()
    result = []
    for lineno, line in enumerate(lines, 1):
        m = _PY2_PRINT_RE.match(line)
        if not m:
            result.append(line)
            continue

        indent, args = m.group(1), m.group(2).rstrip()

        # Already a call with a space before '(' → e.g. `print ("x")`; leave it.
        if args.startswith("("):
            result.append(line)
            continue

        # `print = 5`, `print.something`, `print == x` etc are not the
        # Python 2 statement — they're valid code that merely starts
        # with the word "print". Leave untouched.
        if any(args.startswith(p) for p in _PY2_PRINT_SKIP_PREFIXES):
            result.append(line)
            continue

        new_line = f"{indent}print({args})"
        result.append(new_line)
        issues.append((lineno,
                       "Python 2 print statement (គ្មាន វង់ក្រចក) : "
                       "Python 3 តម្រូវឲ្យប្រើ print(...)",
                       f"print {args}  →  print({args})"))
    return "\n".join(result), issues

# ── R9: invalid / legacy comparison operators
_INVALID_OPS = {
    "=<": "<=",
    "=>": ">=",
    "<>": "!=",
}


def _fix_invalid_operators(code: str):
    """R9: `=<` `=>` `<>` (wrong order / Python-2 leftovers) → valid ops."""
    issues = []
    lines = code.splitlines()
    result = []
    for lineno, line in enumerate(lines, 1):
        fixed_line, found = _fix_operators_in_line(line)
        result.append(fixed_line)
        for old, new in found:
            issues.append((lineno,
                           f"'{old}' មិនមែន operator ត្រឹមត្រូវក្នុង Python : "
                           f"ប្រហែលជាចង់ប្រើ '{new}'",
                           f"{old}  →  {new}"))
    return "\n".join(result), issues


def _fix_operators_in_line(line: str):
    """Replace invalid operators, but never inside string literals."""
    found = []
    in_str = False
    q_char = None
    out = []
    i = 0
    n = len(line)
    while i < n:
        c = line[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(line[i + 1])
                i += 2
                continue
            if c == q_char:
                in_str = False
                q_char = None
            i += 1
            continue

        if c in ('"', "'"):
            in_str = True
            q_char = c
            out.append(c)
            i += 1
            continue

        two = line[i:i + 2]
        if two in _INVALID_OPS:
            out.append(_INVALID_OPS[two])
            found.append((two, _INVALID_OPS[two]))
            i += 2
            continue

        out.append(c)
        i += 1
    return "".join(out), found


# ── R10: common keyword misspellings (exact match only — no fuzzy
# matching here, unlike R0, so this can never mangle a real identifier
# that merely looks similar).
_KEYWORD_TYPOS = {
    # return
    "retrun": "return", "retrn": "return", "rturn": "return",
    "reutrn": "return",
    # import
    "improt": "import", "imoprt": "import", "iport": "import",
    "impotr": "import",
    # booleans
    "flase": "False", "Flase": "False", "FLASE": "False",
    "ture": "True", "Ture": "True",
    # else
    "els": "else",
    # while
    "wile": "while", "whlie": "while",
    # class
    "calss": "class", "clas": "class",
    # def
    "dfe": "def",
}

_KEYWORD_TYPO_RE = re.compile(
    r'\b(' + '|'.join(re.escape(k) for k in _KEYWORD_TYPOS) + r')\b'
)


def _fix_keyword_typos(code: str):
    """R10: exact-match dictionary of common keyword misspellings."""
    issues = []
    lines = code.splitlines()
    result = []
    for lineno, line in enumerate(lines, 1):
        # Skip whole-line comments outright — never touch comment text.
        if line.lstrip().startswith("#"):
            result.append(line)
            continue

        def _repl(m):
            typo = m.group(1)
            correct = _KEYWORD_TYPOS[typo]
            issues.append((lineno,
                           f"'{typo}' ប្រហែលជា typo នៃ keyword '{correct}'",
                           f"{typo}  →  {correct}"))
            return correct

        new_line = _KEYWORD_TYPO_RE.sub(_repl, line)
        result.append(new_line)
    return "\n".join(result), issues


# ── R3: unclosed quotes / parens (+ triple-quote block awareness)
def _fix_quotes_parens(code: str):
    """Fix unclosed quotes/parens. Triple-quoted strings (\"\"\"...\"\"\")
    are recognised as ONE block that can legitimately span many lines —
    content inside an open triple-quote is left completely untouched
    (it's documentation, not code to fix) instead of being mis-parsed
    one line at a time."""
    issues = []
    lines = code.splitlines()
    result = []
    triple_marker = None  # None, or the open '"""'/"'''" we're inside

    for lineno, line in enumerate(lines, 1):
        if triple_marker:
            close_idx = line.find(triple_marker)
            if close_idx == -1:
                # entire line is inside the triple-quoted string — leave as-is
                result.append(line)
                continue
            # string closes partway through this line; only the remainder
            # after the closing marker is real code that needs checking
            head = line[:close_idx + 3]
            tail = line[close_idx + 3:]
            triple_marker = None
            fixed_tail, li, still_open = _fix_line(tail, lineno)
            issues.extend(li)
            result.append(head + fixed_tail)
            triple_marker = still_open
            continue

        fixed_line, li, still_open = _fix_line(line, lineno)
        issues.extend(li)
        result.append(fixed_line)
        triple_marker = still_open

    if triple_marker:
        result.append(triple_marker)
        issues.append((len(lines),
                       f"Triple-quote string ({triple_marker}) មិនបានបិទ",
                       f"បន្ថែម {triple_marker} នៅចុង file"))

    return "\n".join(result), issues


def _fix_line(line: str, lineno: int):
    """Scan one line for unclosed quotes/parens/brackets/braces. Triple-quote
    markers (\"\"\" or \'\'\') are matched as a 3-char unit, distinct from a
    normal single quote, so a docstring's internal apostrophes/quotes
    don't confuse the balance. Returns (fixed_line, issues,
    open_triple_marker_or_None) — the third value tells the caller the
    triple-quoted string is still open at end-of-line and must continue
    on the next line."""
    issues = []
    in_str = False
    q_char = None
    paren_depth = 0
    bracket_depth = 0
    brace_depth = 0
    i = 0
    n = len(line)
    out = []
    triple_open = None

    while i < n:
        c = line[i]

        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(line[i + 1])
                i += 2
                continue
            if c == q_char:
                in_str = False
                q_char = None
            i += 1
            continue

        if c in ('"', "'"):
            triple = c * 3
            if line[i:i + 3] == triple:
                close_pos = line.find(triple, i + 3)
                if close_pos != -1:
                    out.append(line[i:close_pos + 3])
                    i = close_pos + 3
                else:
                    out.append(line[i:])
                    triple_open = triple
                    i = n
                continue
            in_str = True
            q_char = c
            out.append(c)
            i += 1
            continue

        if c == "(":
            paren_depth += 1
        elif c == ")":
            paren_depth = max(paren_depth - 1, 0)
        elif c == "[":
            bracket_depth += 1
        elif c == "]":
            bracket_depth = max(bracket_depth - 1, 0)
        elif c == "{":
            brace_depth += 1
        elif c == "}":
            brace_depth = max(brace_depth - 1, 0)
        out.append(c)
        i += 1

    added = []
    if in_str:
        added.append(q_char)
        issues.append((lineno,
                       f"Quote '{q_char}' មិនបានបិទ string",
                       f"បន្ថែម '{q_char}' នៅចុង"))
    if paren_depth > 0:
        added.extend([")"] * paren_depth)
        issues.append((lineno,
                       f"'(' {paren_depth} ដងមិនបានបិទ",
                       f"បន្ថែម '{')' * paren_depth}' នៅចុង"))
    if bracket_depth > 0:
        added.extend(["]"] * bracket_depth)
        issues.append((lineno,
                       f"'[' {bracket_depth} ដងមិនបានបិទ",
                       f"បន្ថែម '{']' * bracket_depth}' នៅចុង"))
    if brace_depth > 0:
        added.extend(["}"] * brace_depth)
        issues.append((lineno,
                       f"'{{' {brace_depth} ដងមិនបានបិទ",
                       f"បន្ថែម '{'}' * brace_depth}' នៅចុង"))
    return "".join(out) + "".join(added), issues, triple_open


# ── R15: forgotten `f` prefix on a string containing {placeholder}
#   "Hello {name}"  →  f"Hello {name}"
# Only single/double-quoted (non-triple) strings are checked. Two
# safety guards keep this from breaking legitimate code:
#   1. Strings immediately followed by `.format(` are left alone —
#      that's the deliberate .format() style, not a forgotten f.
#   2. Byte-string / already-f-string prefixes are never touched.
_STRING_LITERAL_RE = re.compile(
    r'(?P<prefix>[A-Za-z]{0,2})(?P<q>"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'
)
_PLACEHOLDER_RE = re.compile(r'\{[A-Za-z_][^{}]*\}')


def _fix_missing_fstring(code: str):
    """R15: add a missing `f` prefix to a string that has a {placeholder}
    but isn't an f-string (and isn't feeding a later .format() call)."""
    issues = []
    lines = code.splitlines()
    result = []
    for lineno, line in enumerate(lines, 1):
        if line.lstrip().startswith("#"):
            result.append(line)
            continue

        def _repl(m):
            prefix = m.group('prefix')
            q = m.group('q')
            if 'f' in prefix.lower() or 'b' in prefix.lower():
                return m.group(0)
            if not _PLACEHOLDER_RE.search(q):
                return m.group(0)
            after = line[m.end():].lstrip()
            if after.startswith(".format("):
                return m.group(0)
            new_prefix = prefix + "f"
            issues.append((lineno,
                           "String មាន {...} placeholder ប៉ុន្តែភ្លេច 'f' prefix",
                           f"{prefix}{q[:12]}...  →  {new_prefix}{q[:12]}..."))
            return new_prefix + q

        new_line = _STRING_LITERAL_RE.sub(_repl, line)
        result.append(new_line)
    return "\n".join(result), issues


# ── R11: `else if` (C/JS style) → `elif`
_ELSE_IF_RE = re.compile(r'^(\s*)else\s+if\b(.*)$')


def _fix_else_if(code: str):
    """R11: `else if x:` → `elif x:` (invalid in Python — no 'else if')."""
    issues = []
    lines = code.splitlines()
    result = []
    for lineno, line in enumerate(lines, 1):
        m = _ELSE_IF_RE.match(line)
        if m and not line.lstrip().startswith("#"):
            indent, rest = m.group(1), m.group(2)
            new_line = f"{indent}elif{rest}"
            result.append(new_line)
            issues.append((lineno,
                           "'else if' មិនមែន Python syntax : Python ប្រើ 'elif'",
                           "else if  →  elif"))
        else:
            result.append(line)
    return "\n".join(result), issues


# ── R12: Python 2 `raw_input(` → `input(`
_RAW_INPUT_RE = re.compile(r'\braw_input\s*\(')


def _fix_raw_input(code: str):
    """R12: `raw_input(` (Python 2) → `input(` (Python 3)."""
    issues = []
    lines = code.splitlines()
    result = []
    for lineno, line in enumerate(lines, 1):
        if _RAW_INPUT_RE.search(line) and not line.lstrip().startswith("#"):
            new_line = _RAW_INPUT_RE.sub("input(", line)
            result.append(new_line)
            issues.append((lineno,
                           "'raw_input()' ជា Python 2 : Python 3 ប្រើ 'input()'",
                           "raw_input(  →  input("))
        else:
            result.append(line)
    return "\n".join(result), issues


# ── R13: `++` / `--` (Python has no increment/decrement operators)
_INCDEC_POSTFIX_RE = re.compile(r'\b([A-Za-z_][A-Za-z0-9_]*)\s*(\+\+|--)')
_INCDEC_PREFIX_RE = re.compile(r'(\+\+|--)\s*([A-Za-z_][A-Za-z0-9_]*)\b')


def _fix_increment_decrement(code: str):
    """R13: `x++`/`x--`/`++x`/`--x` → `x += 1` / `x -= 1`."""
    issues = []
    lines = code.splitlines()
    result = []
    for lineno, line in enumerate(lines, 1):
        if line.lstrip().startswith("#"):
            result.append(line)
            continue
        new_line = line
        found = []

        def _repl_post(m):
            name, op = m.group(1), m.group(2)
            found.append((f"{name}{op}", f"{name} {'+=' if op == '++' else '-='} 1"))
            return f"{name} {'+=' if op == '++' else '-='} 1"

        new_line = _INCDEC_POSTFIX_RE.sub(_repl_post, new_line)

        def _repl_pre(m):
            op, name = m.group(1), m.group(2)
            found.append((f"{op}{name}", f"{name} {'+=' if op == '++' else '-='} 1"))
            return f"{name} {'+=' if op == '++' else '-='} 1"

        new_line = _INCDEC_PREFIX_RE.sub(_repl_pre, new_line)

        result.append(new_line)
        for old, new in found:
            issues.append((lineno,
                           f"'{old}' Python គ្មាន increment/decrement operator",
                           f"{old}  →  {new}"))
    return "\n".join(result), issues


# ── R16: mutable default argument (classic Python gotcha)
#   def f(x=[]):  /  def f(x={}):
# Detect-only: a correct fix needs to restructure the function body
# (x=None, then `if x is None: x = []` inside), not just the
# signature — that's too invasive to safely auto-rewrite, so this
# rule warns instead of silently changing behaviour.
_DEF_PARAMS_RE = re.compile(r'^\s*def\s+\w+\s*\((.*)\)\s*:?\s*$')


def _split_params(params: str):
    """Split a parameter list on top-level commas only (ignores commas
    nested inside [], {}, () — e.g. inside a default value)."""
    depth = 0
    current = []
    parts = []
    for ch in params:
        if ch in '([{':
            depth += 1
        elif ch in ')]}':
            depth -= 1
        if ch == ',' and depth == 0:
            parts.append(''.join(current))
            current = []
        else:
            current.append(ch)
    if current:
        parts.append(''.join(current))
    return parts


def _detect_mutable_defaults(code: str):
    """R16: warn about mutable (list/dict) default argument values."""
    issues = []
    lines = code.splitlines()
    for lineno, line in enumerate(lines, 1):
        m = _DEF_PARAMS_RE.match(line)
        if not m:
            continue
        for part in _split_params(m.group(1)):
            part = part.strip()
            if '=' not in part:
                continue
            name, _, default = part.partition('=')
            name, default = name.strip(), default.strip()
            if default.startswith('[') or default.startswith('{'):
                issues.append((lineno,
                               f"Default argument '{name}={default}' ជា mutable "
                               f"(list/dict) — នឹងចែករំលែក state រវាង function call គ្នា",
                               f"ប្តូរទៅ '{name}=None' រួច 'if {name} is None: "
                               f"{name} = {default}' ខាងក្នុង function"))
    return issues


# ── R17: possibly-undefined name (detect only)
#   Uses a simplified "whole-file bag of names" model rather than true
#   per-scope resolution: a name defined ANYWHERE in the file (any
#   function, any assignment) counts as defined everywhere. This is
#   deliberately permissive — it will miss some real scope bugs, but
#   it will never falsely warn about a name that legitimately exists
#   somewhere in the file, which matters far more for a "just warn"
#   feature than catching every edge case.
_EXTRA_KNOWN_NAMES = {"self", "cls", "__name__", "__file__", "__doc__",
                      "__class__", "__module__", "__qualname__"}


def _collect_defined_names(tree) -> set:
    defined = set(_EXTRA_KNOWN_NAMES)

    def add_target(node):
        if isinstance(node, ast.Name):
            defined.add(node.id)
        elif isinstance(node, (ast.Tuple, ast.List)):
            for el in node.elts:
                add_target(el)
        elif isinstance(node, ast.Starred):
            add_target(node.value)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defined.add(node.name)
            a = node.args
            for arglist in (a.posonlyargs, a.args, a.kwonlyargs):
                for arg in arglist:
                    defined.add(arg.arg)
            if a.vararg:
                defined.add(a.vararg.arg)
            if a.kwarg:
                defined.add(a.kwarg.arg)
        elif isinstance(node, ast.Lambda):
            a = node.args
            for arglist in (a.posonlyargs, a.args, a.kwonlyargs):
                for arg in arglist:
                    defined.add(arg.arg)
            if a.vararg:
                defined.add(a.vararg.arg)
            if a.kwarg:
                defined.add(a.kwarg.arg)
        elif isinstance(node, ast.ClassDef):
            defined.add(node.name)
        elif isinstance(node, (ast.Assign,)):
            for t in node.targets:
                add_target(t)
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
            add_target(node.target)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            add_target(node.target)
        elif isinstance(node, ast.comprehension):
            add_target(node.target)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                if item.optional_vars:
                    add_target(item.optional_vars)
        elif isinstance(node, ast.ExceptHandler):
            if node.name:
                defined.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                defined.add(alias.asname or alias.name.split(".")[0])
        elif hasattr(ast, "NamedExpr") and isinstance(node, ast.NamedExpr):
            add_target(node.target)

    return defined


def _detect_undefined_names(code: str):
    """R17: warn about a name that's used but never defined/imported
    anywhere in the file, and isn't a Python builtin."""
    issues = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return issues

    defined = _collect_defined_names(tree)
    seen = {}  # name -> first lineno used
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id not in seen or node.lineno < seen[node.id]:
                seen[node.id] = node.lineno

    for name, lineno in sorted(seen.items(), key=lambda kv: kv[1]):
        if name in defined or name in _BUILTIN_NAMES:
            continue
        issues.append((lineno,
                       f"'{name}' ត្រូវបានប្រើ ប៉ុន្តែមិនឃើញកន្លែង define/import ក្នុង file នេះ",
                       f"ពិនិត្យ spelling ឬ ត្រូវ import / assign '{name}' មុននឹងប្រើ"))
    return issues


# ── R18: off-by-one loop risk (detect only)
_RANGE_LEN_PLUS1_RE = re.compile(r'\brange\s*\(\s*len\([^()]*\)\s*\+\s*1\s*\)')
_LE_LEN_RE = re.compile(r'[A-Za-z_][A-Za-z0-9_]*\s*<=\s*len\(')


def _detect_off_by_one(code: str):
    """R18: `range(len(x) + 1)` and `i <= len(x)` are classic off-by-one
    patterns — valid indices only go up to len(x) - 1."""
    issues = []
    lines = code.splitlines()
    for lineno, line in enumerate(lines, 1):
        if line.lstrip().startswith("#"):
            continue
        if _RANGE_LEN_PLUS1_RE.search(line):
            issues.append((lineno,
                           "'range(len(x) + 1)' ប្រហែលជា off-by-one : "
                           "loop នឹង index លើសព្រំដែន (out of range)",
                           "ពិនិត្យថាតើចង់ប្រើ 'range(len(x))' ធម្មតាឬអត់"))
        if _LE_LEN_RE.search(line):
            issues.append((lineno,
                           "'<= len(x)' ក្នុង condition ប្រហែលជា off-by-one : "
                           "index ត្រឹមត្រូវគឺ 0..len(x)-1",
                           "ពិនិត្យថាតើគួរប្រើ '< len(x)' ជំនួសឬអត់"))
    return issues


# ── R19: `is` / `is not` compared against a literal — should be == / !=
def _detect_is_literal(code: str):
    """R19: `x is 5`, `x is "a"` etc. `is` checks object identity, not
    value equality; comparing against a literal is almost always a bug
    (it can even give inconsistent results depending on Python's
    internal small-int/string caching)."""
    issues = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return issues

    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        prev = node.left
        for op, comp in zip(node.ops, node.comparators):
            if isinstance(op, (ast.Is, ast.IsNot)):
                for side in (prev, comp):
                    if (isinstance(side, ast.Constant)
                            and isinstance(side.value, (int, float, str, bytes))
                            and not isinstance(side.value, bool)):
                        kw = "is not" if isinstance(op, ast.IsNot) else "is"
                        suggested = "!=" if kw == "is not" else "=="
                        issues.append((node.lineno,
                                       f"'{kw}' ប្រៀបធៀបជាមួយ literal ({side.value!r}) : "
                                       f"'is' ត្រួតពិនិត្យ object identity មិនមែនតម្លៃ",
                                       f"ប្តូរ '{kw}' ទៅ '{suggested}' "
                                       f"ប្រសិនជាចង់ប្រៀបធៀបតម្លៃ"))
                        break
            prev = comp
    return issues


# ── R5: detect missing colons after control flow statements
#   Uses a \b word-boundary regex (not startswith) so that identifiers
#   which merely begin with a keyword — `elsewhere = 5`, `exceptions = []`,
#   `finally_flag = True` — are never mistaken for the keyword itself.
_CONTROL_KEYWORDS_RE = re.compile(
    r'^(if|elif|else|for|while|def|class|try|except|finally)\b'
)


def _fix_missing_colons(code: str):
    """Detect if/elif/else/for/while/def/class/try/except/finally missing ':'."""
    issues = []
    lines = code.splitlines()
    result = []
    for lineno, line in enumerate(lines, 1):
        stripped = line.rstrip()
        lstr = stripped.lstrip()
        m = _CONTROL_KEYWORDS_RE.match(lstr)
        if m and stripped and not stripped.endswith(":"):
            if not lstr.startswith("#"):
                result.append(stripped + ":")
                issues.append((lineno,
                               f"'{m.group(1)}' statement គ្មាន ':' នៅចុង",
                               "បន្ថែម ':' នៅចុងបន្ទាត់"))
            else:
                result.append(line)
        else:
            result.append(line)
    return "\n".join(result), issues


# ── R6: assignment (=) instead of comparison (==) inside if/while
def _fix_logic_errors(code: str):
    """Detect AND fix `=` where `==` was almost certainly intended."""
    issues = []
    lines = code.splitlines()
    result = []
    for lineno, line in enumerate(lines, 1):
        stripped = line.lstrip()
        is_condition = stripped.startswith("if ") or stripped.startswith("while ")
        # " = " (spaced, single '=') never matches inside ==, !=, <=, >=,
        # or +=/-=/etc, so this is safe to detect on the raw line.
        if is_condition and " = " in line and "==" not in line and "!=" not in line:
            new_line = line.replace(" = ", " == ")
            result.append(new_line)
            issues.append((lineno,
                           "អាច assignment (=) ក្នុង condition — ប្រហែលជាចង់ប្រើ '=='",
                           "ផ្លាស់ប្តូរ '=' ទៅ '==' ក្នុង condition"))
        else:
            result.append(line)
    return "\n".join(result), issues


# ── R7: mixed tabs/spaces (normalizes tabs → 4 spaces) + big indent jumps
def _fix_indentation_issues(code: str):
    """Detect AND fix mixed tabs/spaces; only touches leading whitespace —
    tabs inside string content elsewhere on a line are never touched."""
    issues = []
    lines = code.splitlines()

    indent_types = set()
    for line in lines:
        if not line.strip():
            continue
        leading = line[:len(line) - len(line.lstrip('\t '))]
        if '\t' in leading:
            indent_types.add('tabs')
        if leading.startswith(' '):
            indent_types.add('spaces')
    mixed = len(indent_types) > 1

    result = []
    for line in lines:
        if not line.strip():
            result.append(line)
            continue
        content = line.lstrip('\t ')
        leading = line[:len(line) - len(content)]
        if '\t' in leading:
            leading = leading.replace('\t', '    ')
        result.append(leading + content)

    if mixed:
        issues.append((1,
                       "Mixed tabs and spaces detected : បានប្តូរ tab ទាំងអស់ទៅ 4 spaces",
                       "tab  →  4 spaces (ស្វ័យប្រវត្តិ)"))

    indent_levels = []
    for line in result:
        if not line.strip():
            continue
        leading = line[:len(line) - len(line.lstrip(' '))]
        indent_levels.append(len(leading))
    prev = 0
    for idx, lvl in enumerate(indent_levels, 1):
        if lvl - prev > 12:
            issues.append((idx,
                           "Indentation jump too large : ប្រហែលមាន indentation មិនត្រឹមត្រូវ",
                           "ពិនិត្យ spacing និង align blocks"))
        prev = lvl
    return "\n".join(result), issues


def _compute_output(code: str) -> list:
    output = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    env = {}
    _collect_vars(tree, env)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Expr):
            continue
        call = node.value
        if not (isinstance(call, ast.Call) and _is_print(call)):
            continue
        sep = " "
        for kw in call.keywords:
            if kw.arg == "sep":
                v = _eval(kw.value, env)
                if v is not None:
                    sep = str(v)
        parts = [str(_eval(a, env) if _eval(a, env) is not None else "?")
                 for a in call.args]
        output.append(sep.join(parts))
    return output


def _is_print(call):
    return isinstance(call.func, ast.Name) and call.func.id == "print"


def _collect_vars(tree, env):
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    v = _eval(node.value, env)
                    if v is not None:
                        env[t.id] = v
        elif isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Name):
                name = node.target.id
                rval = _eval(node.value, env)
                if name in env and rval is not None:
                    try:
                        fn = {ast.Add: operator.add, ast.Sub: operator.sub,
                              ast.Mult: operator.mul, ast.Div: operator.truediv,
                              ast.FloorDiv: operator.floordiv,
                              ast.Mod: operator.mod, ast.Pow: operator.pow
                              }.get(type(node.op))
                        if fn:
                            env[name] = fn(env[name], rval)
                    except BaseException:
                        pass


_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod, ast.Pow: operator.pow}
_CMP_OPS = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.Is: operator.is_,
    ast.IsNot: operator.is_not,
    ast.In: lambda a, b: a in b,
    ast.NotIn: lambda a, b: a not in b,
}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg, ast.Not: operator.not_}


def _eval(node, env):
    try:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.Str):
            return node.s
        if isinstance(node, ast.Name):
            return env.get(node.id)
        if isinstance(node, ast.BinOp):
            l, r = _eval(node.left, env), _eval(node.right, env)
            if l is None or r is None:
                return None
            fn = _OPS.get(type(node.op))
            return fn(l, r) if fn else None
        if isinstance(node, ast.BoolOp):
            values = [_eval(v, env) for v in node.values]
            if any(v is None for v in values):
                return None
            if isinstance(node.op, ast.And):
                return all(values)
            if isinstance(node.op, ast.Or):
                return any(values)
            return None
        if isinstance(node, ast.UnaryOp):
            v = _eval(node.operand, env)
            fn = _UNARY.get(type(node.op))
            return fn(v) if fn and v is not None else None
        if isinstance(node, ast.Compare):
            left = _eval(node.left, env)
            if left is None:
                return None
            current = left
            for op, comparator in zip(node.ops, node.comparators):
                right = _eval(comparator, env)
                if right is None:
                    return None
                fn = _CMP_OPS.get(type(op))
                if not fn or not fn(current, right):
                    return False
                current = right
            return True
        if isinstance(node, ast.JoinedStr):
            parts = []
            for v in node.values:
                if isinstance(v, ast.Constant):
                    parts.append(str(v.value))
                elif isinstance(v, ast.FormattedValue):
                    inner = _eval(v.value, env)
                    parts.append(str(inner) if inner is not None else "?")
            return "".join(parts)
    except BaseException:
        pass
    return None


# ── main pipeline
def _analyze(code: str) -> str:
    issues = []

    code, i0 = _fix_print_typos(code)
    issues.extend(i0)

    code, i1 = _fix_print_case(code)
    issues.extend(i1)

    code, i2 = _fix_semicolons(code)
    issues.extend(i2)

    code, i7 = _fix_print_statement(code)
    issues.extend(i7)

    code, i8 = _fix_invalid_operators(code)
    issues.extend(i8)

    code, i9 = _fix_keyword_typos(code)
    issues.extend(i9)

    code, i10 = _fix_else_if(code)
    issues.extend(i10)

    code, i11 = _fix_raw_input(code)
    issues.extend(i11)

    code, i12 = _fix_increment_decrement(code)
    issues.extend(i12)

    code, i3 = _fix_quotes_parens(code)
    issues.extend(i3)

    code, i13 = _fix_missing_fstring(code)
    issues.extend(i13)

    i14 = _detect_mutable_defaults(code)
    issues.extend(i14)

    code, i4 = _fix_missing_colons(code)
    issues.extend(i4)

    code, i5 = _fix_logic_errors(code)
    issues.extend(i5)

    code, i6 = _fix_indentation_issues(code)
    issues.extend(i6)

    i15 = _detect_undefined_names(code)
    issues.extend(i15)

    i16 = _detect_off_by_one(code)
    issues.extend(i16)

    i17 = _detect_is_literal(code)
    issues.extend(i17)

    output_lines = _compute_output(code)

    parts = []
    if not issues:
        parts.append("✅ មិនឃើញបញ្ហាណាមួយ!")
    else:
        parts.append(f"🔍 Error ដែលរកឃើញ ({len(issues)}):\n")
        for idx, (ln, err, fix) in enumerate(issues, 1):
            parts.append(f"  {idx}. Line {ln}: {err}")
            if fix:
                parts.append(f"     ⚙️  កែ: {fix}")

    parts.append(f"\n✅ Fixed Code:\n```python\n{code}\n```")

    out_text = "\n".join(output_lines) if output_lines else "No output"
    parts.append(f"\n📤 Output:\n```\n{out_text}\n```")

    return "\n".join(parts)


class FixCodeEngine:
    def get_response(self, user_input: str) -> str:
        s = user_input.strip()
        if not s or s.lower() in START_TRIGGERS:
            return INSTRUCTIONS
        return _analyze(s)
