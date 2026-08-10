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
"""

import re
import ast
import operator

START_TRIGGERS = ("/start", "/help", "help", "menu")

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


# ── R3: unclosed quotes / parens
def _fix_quotes_parens(code: str):
    issues = []
    lines = code.splitlines()
    result = []
    for lineno, line in enumerate(lines, 1):
        fixed_line, li = _fix_line(line, lineno)
        issues.extend(li)
        result.append(fixed_line)
    return "\n".join(result), issues


def _fix_line(line: str, lineno: int):
    issues = []
    in_str = False
    q_char = None
    depth = 0
    i = 0
    chars = list(line)
    while i < len(chars):
        c = chars[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == q_char:
                in_str = False
                q_char = None
        else:
            if c in ('"', "'"):
                in_str = True
                q_char = c
            elif c == "(":
                depth += 1
            elif c == ")":
                depth = max(depth - 1, 0)
        i += 1
    added = []
    if in_str:
        added.append(q_char)
        issues.append((lineno,
                       f"Quote '{q_char}' មិនបានបិទ string",
                       f"បន្ថែម '{q_char}' នៅចុង"))
    if depth > 0:
        added.extend([")"] * depth)
        issues.append((lineno,
                       f"'(' {depth} ដងមិនបានបិទ",
                       f"បន្ថែម '{')' * depth}' នៅចុង"))
    return line + "".join(added), issues


# ── R5: detect missing colons after control flow statements
def _fix_missing_colons(code: str):
    """Detect if/elif/else/for/while/def/class missing colon and add it."""
    issues = []
    lines = code.splitlines()
    result = []
    control_keywords = ("if ", "elif ", "else", "for ", "while ", "def ", "class ")
    for lineno, line in enumerate(lines, 1):
        stripped = line.rstrip()
        lstr = stripped.lstrip()
        is_control = any(lstr.startswith(kw) for kw in control_keywords)
        if is_control and stripped and not stripped.endswith(":"):
            if not lstr.startswith("#"):
                result.append(stripped + ":")
                kw = next((kw for kw in control_keywords if lstr.startswith(kw)), "statement")
                issues.append((lineno,
                               f"'{kw.strip()}' statement គ្មាន ':' នៅចុង",
                               "បន្ថែម ':' នៅចុងបន្ទាត់"))
            else:
                result.append(line)
        else:
            result.append(line)
    return "\n".join(result), issues


# ── R6: detect common logic errors (assignment in condition)
def _detect_logic_errors(code: str):
    issues = []
    lines = code.splitlines()
    for lineno, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("if ") or stripped.startswith("while "):
            cond_part = line
            if " = " in cond_part and "==" not in cond_part and "!=" not in cond_part:
                issues.append((lineno,
                               "អាច assignment (=) ក្នុង condition — ប្រហែលជាចង់ប្រើ '=='",
                               "ផ្លាស់ប្តូរ '=' ទៅ '==' ប្រសិនជាចង់ប្រៀបធៀប"))
    return issues


# ── R7: detect indentation issues (mixed tabs/spaces or inconsistent indent)
def _detect_indentation_issues(code: str):
    issues = []
    lines = code.splitlines()
    indent_types = set()
    indent_levels = []
    for lineno, line in enumerate(lines, 1):
        if not line.strip():
            continue
        leading = line[:len(line) - len(line.lstrip('\t '))]
        if '\t' in leading:
            indent_types.add('tabs')
        if leading.startswith(' '):
            indent_types.add('spaces')
        count = leading.count(' ') + leading.count('\t') * 8
        indent_levels.append(count)
    if len(indent_types) > 1:
        issues.append((1,
                       "Mixed tabs and spaces detected : ប្រើ spaces ផ្ទាល់ខ្លួន",
                       "ប្រើ spaces មួយគ្រប់គ្រាន់ (ទូទៅ 4 spaces) និងចៀសវាង tabs"))
    prev = 0
    for idx, lvl in enumerate(indent_levels, 1):
        if lvl - prev > 12:
            issues.append((idx,
                           "Indentation jump too large : ប្រហែលមាន indentation មិនត្រឹមត្រូវ",
                           "ពិនិត្យ spacing និង align blocks"))
        prev = lvl
    return issues


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

    code, i3 = _fix_quotes_parens(code)
    issues.extend(i3)

    code, i4 = _fix_missing_colons(code)
    issues.extend(i4)

    i5 = _detect_logic_errors(code)
    issues.extend(i5)

    i6 = _detect_indentation_issues(code)
    issues.extend(i6)

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
