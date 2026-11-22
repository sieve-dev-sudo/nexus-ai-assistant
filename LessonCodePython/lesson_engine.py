"""
LessonCodePython/lesson_engine.py — 11 topics + Quiz mode
Order matters: more-specific keywords first to avoid wrong matches.
"""
import json
import csv
import html
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Set, List, Dict, Any, Pattern, Tuple

LESSONS_PATH = Path(__file__).resolve().parent / "lessons.json"
QUIZ_PATH = Path(__file__).resolve().parent / "quizzes.json"
PROGRESS_PATH = Path.home() / ".nexus_ai" / "progress.json"
QUIZ_HISTORY_PATH = Path.home() / ".nexus_ai" / "quiz_history.json"

# ── ordered list so specific topics match BEFORE generic ones ─────────
# Each entry: (tuple_of_keywords, topic_key)
TOPIC_KEYWORDS = [
    # ── specific first ──────────────────────────────────────────────
    (("data structure", "tuple", "set", "dictionary", "dictionaries",
      "dict", "key value", "hashmap", "data_structure"), "data_structures"),
    (("*args", "**kwargs", "kwargs", "lambda", "higher order",
      "map(", "filter(", "advanced function", "default param",
      "functions_advanced", "function advanced"), "functions_advanced"),
    (("file handling", "file_handling", "open(", "readline", "readlines",
      "writelines", "encoding", "file mode", "read file", "write file",
      "append file", "csv", "txt file", "file"), "file_handling"),
    (("class", "object", "inherit", "__init__", "self.",
      "polymor", "encapsul", "instance of", "override",
      "magic method", "__str__", "super()", "oop"), "oop"),
    # ── generic topics after ────────────────────────────────────────
    (("basic", "comment", "indentation", "hello world", "syntax",
      "python basic", "first program"), "basic"),
    (("variable", "data type", "int(", "float(", "bool", "none",
      "type conversion", "ប្រភេទ", "var", "assign"), "variables"),
    (("operator", "arithmetic", "math", "calculation", "modulo",
      "floor div", "bitwise"), "operators"),
    (("if", "else:", "elif", "condition", "conditional",
      "ternary", "លក្ខខណ្ឌ"), "conditional"),
    (("loop", "for", "while", "iterate", "range(",
      "break", "continue", "repeat"), "loop"),
    (("array", "list", "append", "pop(", "sort(", "index", "slice",
      "បញ្ជី", "remove(", "insert("), "array"),
    (("function", "def", "return", "parameter", "argument",
      "អនុគមន៍", "func"), "function"),
]

# Keywords that are word *stems*: they may be followed by any letters
# ("inherit" -> "inheritance", "bool" -> "boolean"). Every other English
# keyword must match as a whole word (an optional s/es/ed/ing ending is
# allowed), so "set" no longer matches "reset"/"offset"/"settings",
# "dict" no longer matches "predict", and "class" no longer matches
# "classic".
STEM_KEYWORDS = {
    "inherit", "polymor", "encapsul", "bool", "assign",
    "default param", "floor div",
}


def _keyword_pattern(kw: str) -> str:
    """Build the regex for one keyword, adding word boundaries on each
    side that starts/ends with a letter, digit, or underscore.

    Khmer keywords keep plain substring matching, because Khmer is
    written without spaces between words (so word boundaries don't
    apply). Keywords that start/end with symbols ("map(", "self.",
    "*args") only get a boundary on their word-character side."""
    if not kw.isascii():
        return re.escape(kw)
    left = r"(?<!\w)" if (kw[0].isalnum() or kw[0] == "_") else ""
    if kw[-1].isalnum() or kw[-1] == "_":
        right = "" if kw in STEM_KEYWORDS else r"(?:s|es|ed|ing)?(?!\w)"
    else:
        right = ""
    return left + re.escape(kw) + right


# Pre-compiled once at import time: one combined regex per topic,
# kept in the same specific-first order as TOPIC_KEYWORDS.
TOPIC_PATTERNS: List[Tuple[Pattern[str], str]] = [
    (re.compile("|".join(_keyword_pattern(kw) for kw in keywords)), topic)
    for keywords, topic in TOPIC_KEYWORDS
]

START_TRIGGERS = ("/start", "/help", "help", "menu", "start", "មុខងារ")
QUIZ_STOP_TRIGGERS = ("/stop", "/exit", "stop quiz", "បញ្ឈប់")
PROGRESS_TRIGGERS = ("/progress", "progress")

# Fixed order for the progress checklist, independent of lessons.json's
# own key ordering (which starts with "/start").
TOPIC_ORDER = [
    "basic", "variables", "operators", "conditional", "loop", "array",
    "function", "data_structures", "functions_advanced", "file_handling", "oop",
]

# Human-readable topic names for the PDF report (plain English, no
# emoji, so they render with any system font).
TOPIC_TITLES = {
    "basic":              "Python Basics",
    "variables":          "Variables & Data Types",
    "operators":          "Operators",
    "conditional":        "Conditionals (if / else)",
    "loop":               "Loops (for / while)",
    "array":              "Lists (Array)",
    "function":           "Functions",
    "data_structures":    "Data Structures",
    "functions_advanced": "Advanced Functions",
    "file_handling":      "File Handling",
    "oop":                "OOP (Classes & Objects)",
}

# Colors used by the PDF report (light, print-friendly palette that
# matches the app's blue accent).
_R = {
    "accent":   "#2563eb",
    "accent_d": "#1d4ed8",
    "yellow":   "#ffd343",
    "text":     "#16161f",
    "muted":    "#6b6b85",
    "line":     "#e2e2ec",
    "row_alt":  "#f7f7fb",
    "track":    "#e5e7f0",
    "green":    "#059669",
    "green_bg": "#d1fae5",
    "amber":    "#b45309",
    "amber_bg": "#fef3c7",
    "red":      "#b91c1c",
    "red_bg":   "#fee2e2",
    "grey_bg":  "#ededf3",
    "empty_bg": "#eef3ff",
}


def _score_colors(pct: int) -> Tuple[str, str]:
    """Return (text, background) badge colors for a quiz percentage."""
    if pct >= 80:
        return _R["green"], _R["green_bg"]
    if pct >= 50:
        return _R["amber"], _R["amber_bg"]
    return _R["red"], _R["red_bg"]


def _badge(text: str, fg: str, bg: str) -> str:
    """A small colored pill, built as a one-cell table (Qt's rich-text
    engine ignores padding on inline <span> elements)."""
    return (f'<table cellspacing="0" cellpadding="3" style="background-color:{bg};">'
            f'<tr><td style="color:{fg}; font-weight:600; font-size:8.5pt; '
            f'white-space:nowrap;">'
            f'&nbsp;{text}&nbsp;</td></tr></table>')


class LessonEngine:
    """Public entry point for Lesson mode: routes chat messages to a topic lesson, a quiz question/answer, or a progress report."""
    def __init__(self, path: Path = LESSONS_PATH, quiz_path: Path = QUIZ_PATH,
                 progress_path: Path = PROGRESS_PATH,
                 quiz_history_path: Path = QUIZ_HISTORY_PATH) -> None:
        """Load lesson/quiz content and any previously saved progress from disk."""
        self.lessons: Dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        self.quizzes: Dict[str, Any] = (
            json.loads(quiz_path.read_text(encoding="utf-8"))
            if quiz_path.exists() else {}
        )
        self._quiz_state: Optional[Dict[str, Any]] = None  # {"topic","index","score","total"}
        self.progress_path = progress_path
        self.progress: Set[str] = self._load_progress()
        self.quiz_history_path = quiz_history_path
        self.quiz_history: List[Dict[str, Any]] = self._load_quiz_history()

    def _load_progress(self) -> Set[str]:
        """Read the saved set of completed topics from disk, or start empty if there's no file yet."""
        try:
            if self.progress_path.exists():
                data = json.loads(self.progress_path.read_text(encoding="utf-8"))
                return set(data.get("completed", []))
        except (OSError, ValueError):
            pass
        return set()

    def _save_progress(self) -> None:
        """Persist the current set of completed topics to disk (best-effort — never raises)."""
        try:
            self.progress_path.parent.mkdir(parents=True, exist_ok=True)
            self.progress_path.write_text(
                json.dumps({"completed": sorted(self.progress)},
                           ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass  # progress is a nice-to-have — never crash the app over it

    def _mark_completed(self, topic: str) -> None:
        """Record a topic as viewed/completed and persist it, if not already recorded."""
        if topic not in self.progress:
            self.progress.add(topic)
            self._save_progress()

    def reset_progress(self) -> None:
        """Public: clear all tracked progress (used by the sidebar's
        'Reset Progress' button)."""
        self.progress = set()
        self._save_progress()

    def _load_quiz_history(self) -> List[Dict[str, Any]]:
        """Read past completed-quiz records from disk, or start empty."""
        try:
            if self.quiz_history_path.exists():
                data = json.loads(self.quiz_history_path.read_text(encoding="utf-8"))
                return list(data.get("attempts", []))
        except (OSError, ValueError):
            pass
        return []

    def _save_quiz_history(self) -> None:
        """Persist quiz_history to disk (best-effort — never raises)."""
        try:
            self.quiz_history_path.parent.mkdir(parents=True, exist_ok=True)
            self.quiz_history_path.write_text(
                json.dumps({"attempts": self.quiz_history}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

    def _record_quiz_attempt(self, topic: str, score: int, total: int) -> None:
        """Append one completed-quiz result and persist it."""
        self.quiz_history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "topic": topic,
            "score": score,
            "total": total,
        })
        self._save_quiz_history()

    def export_report(self, filepath: str) -> bool:
        """Write a CSV report combining the progress checklist and the
        full quiz-attempt history. Returns True on success."""
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["=== Progress ==="])
                writer.writerow(["Topic", "Completed"])
                for key in TOPIC_ORDER:
                    writer.writerow([key, "Yes" if key in self.progress else "No"])

                writer.writerow([])
                writer.writerow(["=== Quiz History ==="])
                writer.writerow(["Timestamp", "Topic", "Score", "Total", "Percent"])
                for attempt in self.quiz_history:
                    total = attempt["total"]
                    pct = round(attempt["score"] / total * 100) if total else 0
                    writer.writerow([
                        attempt["timestamp"], attempt["topic"],
                        attempt["score"], total, f"{pct}%",
                    ])
            return True
        except OSError:
            return False

    # ── PDF report ──────────────────────────────────────────────────
    @staticmethod
    def _attempt_pct(attempt: Dict[str, Any]) -> int:
        """Percentage score of one quiz attempt (0 if total is 0/missing)."""
        total = attempt.get("total") or 0
        return round(attempt.get("score", 0) / total * 100) if total else 0

    def report_summary(self) -> Dict[str, Any]:
        """Numbers shown at the top of the PDF report: progress counts,
        quiz count, average score, and each topic's best quiz score."""
        done = len(self.progress & set(TOPIC_ORDER))
        total = len(TOPIC_ORDER)
        percents = [self._attempt_pct(a) for a in self.quiz_history]
        best: Dict[str, int] = {}
        for attempt in self.quiz_history:
            topic = str(attempt.get("topic", ""))
            best[topic] = max(best.get(topic, 0), self._attempt_pct(attempt))
        return {
            "done": done,
            "total": total,
            "progress_pct": round(done / total * 100) if total else 0,
            "quizzes_taken": len(self.quiz_history),
            "average_pct": round(sum(percents) / len(percents)) if percents else None,
            "best_by_topic": best,
        }

    def build_report_html(self, version: str = "", author: str = "Mr. Siev E") -> str:
        """Build the learning report as HTML for Qt's rich-text engine
        (QTextDocument), which the UI then prints to a PDF file.

        Kept Qt-free on purpose so it stays unit-testable. Uses only the
        HTML/CSS subset QTextDocument supports: tables for layout,
        background colors and font styles (no flexbox, no border-radius).

        Layout is compact on purpose: header, summary and the whole
        topic grid fit on page 1, so the topic list is never split
        across two pages. A long quiz history continues on page 2,
        with its column headings repeated (<thead>)."""
        s = self.report_summary()
        now = datetime.now().strftime("%d %B %Y, %H:%M")
        avg = f"{s['average_pct']}%" if s["average_pct"] is not None else "–"
        ver = f" &nbsp;·&nbsp; v{html.escape(version)}" if version else ""
        nowrap = "white-space:nowrap;"

        def stat(value: str, label: str) -> str:
            """One summary card: a big number with a short label under it."""
            return (f'<td width="33%" style="background-color:{_R["row_alt"]};">'
                    f'<p style="font-size:19pt; font-weight:700; color:{_R["accent"]}; '
                    f'margin:0;">{value}</p>'
                    f'<p style="font-size:8.5pt; color:{_R["muted"]}; margin:0; {nowrap}">'
                    f'{label}</p></td>')

        def section(title: str, note: str, new_page: bool = False) -> str:
            """Section heading: bold title on the left, a muted note on
            the right, and a thin accent rule underneath. new_page=True
            starts the section at the top of a fresh page."""
            brk = " page-break-before:always;" if new_page else ""
            return (
                f'<table width="100%" cellspacing="0" cellpadding="0" '
                f'style="margin-top:16px;{brk}"><tr>'
                f'<td style="font-size:12.5pt; font-weight:700; color:{_R["text"]};">'
                f'{title}</td>'
                f'<td align="right" style="font-size:8.5pt; color:{_R["muted"]}; {nowrap}">'
                f'{note}</td></tr></table>'
                f'<table width="100%" cellspacing="0" cellpadding="0" '
                f'style="margin-top:4px; margin-bottom:6px;"><tr>'
                f'<td width="12%" style="background-color:{_R["accent"]}; font-size:2pt;">'
                f'&nbsp;</td>'
                f'<td style="background-color:{_R["line"]}; font-size:2pt;">&nbsp;</td>'
                f'</tr></table>'
            )

        def topic_card(num: int, key: str) -> str:
            """One topic tile for the 2-column grid: number chip, name,
            best quiz score (if any) and a Done / To do pill."""
            done = key in self.progress
            chip_bg = _R["accent"] if done else _R["grey_bg"]
            chip_fg = "#ffffff" if done else _R["muted"]
            pill = (_badge("Done", _R["green"], _R["green_bg"]) if done
                    else _badge("To do", _R["muted"], _R["grey_bg"]))
            # Second line only when there's a quiz score to show, so
            # tiles stay short and the whole grid fits on page 1.
            sub = ""
            if key in s["best_by_topic"]:
                best = s["best_by_topic"][key]
                fg, _ = _score_colors(best)
                sub = (f'<p style="font-size:8pt; color:{_R["muted"]}; margin:0;">'
                       f'Best quiz: <span style="color:{fg}; font-weight:700;">'
                       f'{best}%</span></p>')
            return (
                f'<table width="100%" cellspacing="0" cellpadding="5" '
                f'style="background-color:{_R["row_alt"]};"><tr>'
                f'<td width="26" align="center" style="background-color:{chip_bg}; '
                f'color:{chip_fg}; font-weight:700; font-size:9pt; {nowrap}">{num}</td>'
                f'<td><p style="font-size:9.5pt; font-weight:600; margin:0;">'
                f'{html.escape(TOPIC_TITLES.get(key, key))}</p>{sub}</td>'
                f'<td width="58" align="right">{pill}</td>'
                f'</tr></table>'
            )

        # Progress bar: a 2-cell table, the filled cell's width = progress %.
        pct = s["progress_pct"]
        filled = (f'<td width="{pct}%" style="background-color:{_R["accent"]}; '
                  f'font-size:5pt;">&nbsp;</td>' if pct > 0 else "")
        empty = (f'<td style="background-color:{_R["track"]}; font-size:5pt;">&nbsp;</td>'
                 if pct < 100 else "")

        # Topic grid: left column = first half, right column = second half,
        # so numbers read top-to-bottom like a normal list.
        half = (len(TOPIC_ORDER) + 1) // 2
        left, right = TOPIC_ORDER[:half], TOPIC_ORDER[half:]
        grid_rows = []
        for r in range(half):
            lcell = topic_card(r + 1, left[r])
            rcell = topic_card(half + r + 1, right[r]) if r < len(right) else "&nbsp;"
            grid_rows.append(f'<tr><td width="50%">{lcell}</td>'
                             f'<td width="50%">{rcell}</td></tr>')
        topic_grid = ('<table width="100%" cellspacing="0" cellpadding="3">'
                      + "".join(grid_rows) + "</table>")

        # Page 1 only has room for about 3 quiz rows under the topic grid.
        # A table split across pages leaves an ugly empty band, so a
        # longer history starts on page 2 instead, in one piece.
        history_on_new_page = len(self.quiz_history) > 3

        if self.quiz_history:
            quiz_rows = []
            # Newest first: that's what someone reading a report wants.
            # White rows with a thin divider (no zebra background): when a
            # long table breaks across pages, Qt stretches the last row's
            # background down to the page bottom, which looked like an
            # empty grey band.
            cell = f'border-bottom:1px solid {_R["line"]};'
            for a in reversed(self.quiz_history):
                p = self._attempt_pct(a)
                fg, badge_bg = _score_colors(p)
                topic = str(a.get("topic", ""))
                quiz_rows.append(
                    f'<tr><td style="color:{_R["muted"]}; {nowrap} {cell}">'
                    f'{html.escape(str(a.get("timestamp", ""))[:16])}</td>'
                    f'<td style="{nowrap} {cell}">'
                    f'{html.escape(TOPIC_TITLES.get(topic, topic))}</td>'
                    f'<td align="center" style="{nowrap} {cell}">'
                    f'{a.get("score", 0)} / {a.get("total", 0)}</td>'
                    f'<td align="right" style="{cell}">'
                    f'{_badge(f"{p}%", fg, badge_bg)}</td></tr>'
                )
            quiz_block = (
                f'<table width="100%" cellspacing="0" cellpadding="6" '
                f'style="border-collapse:collapse;">'
                f'<thead><tr style="background-color:{_R["accent"]}; color:#ffffff; '
                f'font-weight:600; font-size:9pt;">'
                f'<td width="30%">Date</td><td width="40%">Topic</td>'
                f'<td width="12%" align="center">Score</td>'
                f'<td width="18%" align="right">Result</td></tr></thead>'
                + "".join(quiz_rows) + "</table>"
            )
            quiz_note = f"{len(self.quiz_history)} attempt" + (
                "s" if len(self.quiz_history) != 1 else "")
        else:
            quiz_block = (
                f'<table width="100%" cellspacing="0" cellpadding="14" '
                f'style="background-color:{_R["empty_bg"]};"><tr><td align="center">'
                f'<p style="font-size:10.5pt; font-weight:700; color:{_R["accent_d"]}; '
                f'margin:0;">No quizzes taken yet</p>'
                f'<p style="font-size:9pt; color:{_R["muted"]}; margin:0;">'
                f'Type <b style="color:{_R["text"]};">/quiz &lt;topic&gt;</b> in the app '
                f'to test yourself. Your results will appear here.</p>'
                f'</td></tr></table>'
            )
            quiz_note = "0 attempts"

        return f"""
<html><body style="font-family:'Segoe UI','Helvetica Neue',Arial,sans-serif;
                   font-size:10pt; color:{_R['text']};">

<table width="100%" cellspacing="0" cellpadding="16"
       style="background-color:{_R['accent_d']};">
<tr><td>
  <p style="font-size:9pt; color:{_R['yellow']}; font-weight:700; margin:0;">
    NEXUS AI &nbsp;:&nbsp; PYTHON ASSISTANT</p>
  <p style="font-size:22pt; color:#ffffff; font-weight:700; margin:0;">
    Learning Report</p>
  <p style="font-size:9pt; color:#dbe4ff; margin:0;">Generated {now}{ver}</p>
</td></tr></table>

<table width="100%" cellspacing="6" cellpadding="10" style="margin-top:8px;"><tr>
  {stat(f"{s['done']}/{s['total']}", "Topics done")}
  {stat(str(s['quizzes_taken']), "Quizzes taken")}
  {stat(avg, "Average score")}
</tr></table>

<table width="100%" cellspacing="0" cellpadding="0" style="margin-top:4px;"><tr>
  <td style="font-size:8.5pt; color:{_R['muted']};">Overall progress</td>
  <td align="right" style="font-size:8.5pt; font-weight:700;">{pct}%</td>
</tr></table>
<table width="100%" cellspacing="0" cellpadding="1" style="margin-top:3px;">
  <tr>{filled}{empty}</tr></table>

{section("Topic Progress", f"{s['done']} of {s['total']} completed")}
{topic_grid}

{section("Quiz History", quiz_note, new_page=history_on_new_page)}
{quiz_block}

<table width="100%" cellspacing="0" cellpadding="0" style="margin-top:18px;"><tr>
  <td style="background-color:{_R['line']}; font-size:1pt;">&nbsp;</td></tr></table>
<table width="100%" cellspacing="0" cellpadding="0" style="margin-top:6px;"><tr>
  <td style="font-size:8pt; color:{_R['muted']};">
    <b style="color:{_R['accent_d']};">Nexus AI</b> &nbsp;·&nbsp; 100% offline Python tutor</td>
  <td align="right" style="font-size:8pt; color:{_R['muted']};">
    Developed by {html.escape(author)}</td>
</tr></table>
</body></html>"""

    def _show_progress(self) -> str:
        """Build the progress checklist text (✅/⬜ per topic, plus a completion percentage)."""
        lines = []
        for key in TOPIC_ORDER:
            mark = "✅" if key in self.progress else "⬜"
            lines.append(f"  {mark} {key}")
        done = len(self.progress & set(TOPIC_ORDER))
        total = len(TOPIC_ORDER)
        pct = round(done / total * 100) if total else 0
        return (f"📊 វឌ្ឍនភាពការសិក្សា: {done}/{total} ({pct}%)\n\n"
                + "\n".join(lines))

    def get_response(self, user_input: str) -> str:
        """Route one chat message to a quiz answer, a quiz start, a progress report, a lesson lookup, or the fallback message."""
        text = user_input.strip()
        lower = text.lower()

        # An active quiz takes priority — the next message is an answer,
        # not a new lesson lookup.
        if self._quiz_state is not None:
            if lower in QUIZ_STOP_TRIGGERS:
                state = self._quiz_state
                self._quiz_state = None
                return (f"🛑 បញ្ឈប់ Quiz ។ ពិន្ទុ: "
                        f"{state['score']}/{state['index']}")
            return self._handle_quiz_answer(text)

        if lower.startswith("/quiz"):
            return self._start_quiz(text)

        if lower in PROGRESS_TRIGGERS:
            return self._show_progress()

        if lower in START_TRIGGERS:
            return self._render(self.lessons["/start"])

        # Exact key match (user typed the key directly)
        for key, value in self.lessons.items():
            if key != "/start" and lower == key:
                self._mark_completed(key)
                return self._render(value)

        # Keyword match: the topic whose matched keyword is the longest
        # wins, so a short everyday word like "for" or "if" can't beat a
        # real topic word ("Explain functions for beginners" is about
        # functions, not loops). Ties go to the earlier, more specific
        # topic in TOPIC_KEYWORDS.
        topic = self._match_topic(lower)
        if topic is not None:
            self._mark_completed(topic)
            return self._render(self.lessons[topic])

        return self._fallback(user_input)

    def _match_topic(self, lower: str) -> Optional[str]:
        """Return the best-matching lesson topic for the text, or None."""
        best_topic: Optional[str] = None
        best_len = 0
        for pattern, topic in TOPIC_PATTERNS:
            if topic not in self.lessons:
                continue
            longest = max((len(m.group(0)) for m in pattern.finditer(lower)),
                          default=0)
            if longest > best_len:  # strict ">" keeps the earlier topic on a tie
                best_topic, best_len = topic, longest
        return best_topic

    # ── Quiz mode ───────────────────────────────────────────────────
    def _start_quiz(self, text: str) -> str:
        """Begin a quiz for the requested topic, or list available quiz topics if none was given."""
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            topics = ", ".join(sorted(self.quizzes.keys()))
            return (f"📝 វាយ '/quiz <topic>' ដើម្បីចាប់ផ្តើម Quiz ។\n\n"
                     f"Topics ដែលមាន Quiz: {topics}")
        topic = parts[1].strip().lower()
        questions = self.quizzes.get(topic)
        if not questions:
            return f"❌ គ្មាន Quiz សម្រាប់ '{topic}' ទេ។ សូមសាកល្បង topic ផ្សេង។"
        self._quiz_state = {"topic": topic, "index": 0,
                             "score": 0, "total": len(questions)}
        return self._present_question()

    def _present_question(self) -> str:
        """Format the current quiz question with its lettered answer options."""
        state = self._quiz_state
        assert state is not None  # only called while a quiz is active
        q = self.quizzes[state["topic"]][state["index"]]
        options_text = "\n".join(
            f"  {chr(65 + i)}. {opt}" for i, opt in enumerate(q["options"])
        )
        return (f"❓ សំណួរ {state['index'] + 1}/{state['total']} "
                f"({state['topic']}):\n\n{q['question']}\n\n{options_text}\n\n"
                f"សូមឆ្លើយ A, B, C ឬ D (វាយ /stop ដើម្បីបញ្ឈប់)")

    def _handle_quiz_answer(self, text: str) -> str:
        """Score the given answer against the current quiz question, then advance to the next question or finish the quiz."""
        state = self._quiz_state
        assert state is not None  # only called while a quiz is active
        q = self.quizzes[state["topic"]][state["index"]]
        answer = text.strip().upper()
        letters = tuple(chr(65 + i) for i in range(len(q["options"])))
        # Only a single option letter counts as an answer. Anything else
        # (a typo like "E", or a whole sentence) asks the same question
        # again instead of silently counting it as wrong.
        if answer not in letters:
            return (f"⚠️ សូមឆ្លើយតែអក្សរ {', '.join(letters)} ប៉ុណ្ណោះ "
                    f"(វាយ /stop ដើម្បីបញ្ឈប់)\n\n{self._present_question()}")
        chosen = ord(answer) - 65

        if chosen == q["answer"]:
            state["score"] += 1
            feedback = "✅ ត្រឹមត្រូវ!"
        else:
            correct_letter = chr(65 + q["answer"])
            feedback = (f"❌ មិនត្រឹមត្រូវ។ ចម្លើយត្រឹមត្រូវ: "
                        f"{correct_letter}. {q['options'][q['answer']]}")
        explain = q.get("explain", "")
        state["index"] += 1

        if state["index"] >= state["total"]:
            score, total = state["score"], state["total"]
            self._record_quiz_attempt(state["topic"], score, total)
            self._quiz_state = None
            return f"{feedback}\n{explain}\n\n🎉 Quiz បញ្ចប់! ពិន្ទុ: {score}/{total}"

        return f"{feedback}\n{explain}\n\n{self._present_question()}"

    @staticmethod
    def _render(entry: Any) -> str:
        """Format a lesson entry's theory text plus its runnable example, if any."""
        if isinstance(entry, dict):
            theory = entry.get("theory", "")
            example = entry.get("example", "")
            return f"{theory}\n\n📝 ឧទាហរណ៍ (Example):\n\n```python\n{example}\n```"
        return entry

    def _fallback(self, user_input: str) -> str:
        """Response used when the input matches no command, topic, or keyword."""
        topics = [k for k in self.lessons if k != "/start"]
        listing = "\n".join(f"  • {t}" for t in topics)
        return (
            f'🤔 ខ្ញុំមិនយល់អំពីអ្វីដែលអ្នកសរសេរ: "{user_input[:60]}"\n\n'
            f"💡 Topics ({len(topics)}):\n\n{listing}\n\n"
            f"👉 វាយ /start ដើម្បីមើល menu ពេញ"
        )
