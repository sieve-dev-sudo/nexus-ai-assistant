"""
tests/test_lesson_engine.py
──────────────────────────────
Covers topic lookup (incl. the oop/loop keyword-collision regression),
Quiz mode's state machine, and Progress tracking's persistence.
"""
import json
import tempfile
from pathlib import Path

import pytest

from LessonCodePython.lesson_engine import (
    LessonEngine, TOPIC_ORDER, TOPIC_TITLES, TOPIC_ICONS, topic_label,
)
from LessonCodePython.theme import C


@pytest.fixture
def engine():
    """A LessonEngine with progress AND quiz-history written to
    throwaway temp files, so tests never touch the real
    ~/.nexus_ai/progress.json or quiz_history.json."""
    tmp = Path(tempfile.mkdtemp())
    return LessonEngine(
        progress_path=tmp / "progress.json",
        quiz_history_path=tmp / "quiz_history.json",
    )


# ── Topic lookup ──────────────────────────────────────────────────────────
def test_exact_key_lookup(engine):
    result = engine.get_response("basic")
    assert "Basic Python" in result


def test_exact_key_lookup_is_case_insensitive(engine):
    result = engine.get_response("Basic")
    assert "Basic Python" in result


@pytest.mark.parametrize("phrase", [
    "explain for loop",
    "for loop please",
    "a for loop example",
])
def test_loop_phrases_never_match_oop(engine, phrase):
    """Regression: 'loop' contains 'oop' as a substring, which used to
    wrongly route these into the OOP lesson instead of Loop."""
    result = engine.get_response(phrase)
    assert "Loop" in result
    assert "OOP" not in result


@pytest.mark.parametrize("phrase", [
    "explain oop please", "what is oop for", "class", "object", "inherit",
])
def test_real_oop_queries_still_match_oop(engine, phrase):
    result = engine.get_response(phrase)
    assert "OOP" in result


def test_unknown_input_falls_back_gracefully(engine):
    result = engine.get_response("asdkfjaslkdfj")
    assert isinstance(result, str)
    assert result  # non-empty


# ── Quiz mode ─────────────────────────────────────────────────────────────
@pytest.mark.parametrize("command", ["/quiz", "quiz", "/quiz list", "/quiz topics", "/quiz ?"])
def test_quiz_list_shows_every_lesson(engine, command):
    result = engine.get_response(command)
    assert "1. 🔰 Basic Python" in result
    assert "11. 🏛 OOP" in result
    assert engine._quiz_state is None   # just a menu, no quiz started


def test_quiz_start_presents_first_question(engine):
    result = engine.get_response("/quiz basic")
    assert "សំណួរ" in result
    assert "A." in result and "B." in result


def test_quiz_correct_answer_increments_score(engine):
    engine.get_response("/quiz basic")
    result = engine.get_response("B")  # basic Q1: answer index 1 = B
    assert "ត្រឹមត្រូវ" in result
    assert "សំណួរ 2/5" in result  # advances to the next question


def test_quiz_wrong_answer_shows_correct_one(engine):
    engine.get_response("/quiz basic")
    result = engine.get_response("A")  # basic Q1 answer is B -> wrong
    assert "មិនត្រឹមត្រូវ" in result
    assert "សំណួរ 2/5" in result


@pytest.mark.parametrize("bad", ["Z", "E", "hello", "AB", ""])
def test_quiz_invalid_answer_asks_again(engine, bad):
    """A non-letter answer re-asks the same question: no score lost,
    no skipping ahead."""
    engine.get_response("/quiz basic")
    result = engine.get_response(bad)
    assert "សូមឆ្លើយតែអក្សរ" in result
    assert "សំណួរ 1/5" in result
    # The quiz is still on Q1, so a correct answer now still scores.
    assert "សំណួរ 2/5" in engine.get_response("B")


def test_quiz_completes_with_final_score(engine):
    engine.get_response("/quiz basic")
    result = _answer_all(engine, correct=True)
    assert "Quiz 🔰 Basic Python បញ្ចប់" in result
    assert "5/5" in result


def test_quiz_stop_mid_quiz(engine):
    engine.get_response("/quiz basic")
    result = engine.get_response("/stop")
    assert "បញ្ឈប់" in result


def test_quiz_unknown_topic(engine):
    result = engine.get_response("/quiz not_a_real_topic")
    assert "គ្មាន Quiz" in result


def test_quiz_state_does_not_leak_into_next_lookup(engine):
    engine.get_response("/quiz basic")
    _answer_all(engine)  # quiz finishes
    result = engine.get_response("loop")
    assert "Loop" in result


@pytest.mark.parametrize("topic", [
    "basic", "variables", "operators", "conditional", "loop", "array",
    "function", "data_structures", "functions_advanced", "file_handling", "oop",
])
def test_every_topic_has_a_working_quiz(engine, topic):
    result = engine.get_response(f"/quiz {topic}")
    assert "សំណួរ" in result
    engine.get_response("/stop")


# ── Progress tracking ─────────────────────────────────────────────────────
def test_progress_starts_empty(engine):
    result = engine.get_response("/progress")
    assert "0/11" in result


def test_viewing_a_topic_marks_it_complete(engine):
    engine.get_response("basic")
    rows = {r["key"]: r for r in engine.progress_rows()}
    assert rows["basic"]["done"] is True
    assert rows["loop"]["done"] is False
    assert "1/11" in engine.get_response("/progress")


def test_progress_persists_across_engine_instances():
    progress_path = Path(tempfile.mkdtemp()) / "progress.json"
    e1 = LessonEngine(progress_path=progress_path)
    e1.get_response("basic")
    e1.get_response("loop")

    e2 = LessonEngine(progress_path=progress_path)
    result = e2.get_response("/progress")
    done = {r["key"] for r in e2.progress_rows() if r["done"]}
    assert done == {"basic", "loop"}
    assert "2/11" in result


def test_progress_file_is_valid_json_on_disk():
    progress_path = Path(tempfile.mkdtemp()) / "progress.json"
    e = LessonEngine(progress_path=progress_path)
    e.get_response("variables")
    data = json.loads(progress_path.read_text(encoding="utf-8"))
    assert "variables" in data["completed"]


def test_keyword_match_also_marks_progress(engine):
    engine.get_response("explain for loop")  # keyword match, not exact key
    assert {r["key"] for r in engine.progress_rows() if r["done"]} == {"loop"}


# ── Quiz history + export report ──────────────────────────────────────────
def test_completing_a_quiz_records_history(engine):
    engine.get_response("/quiz basic")
    _answer_all(engine, correct=True)  # finishes the 5-question quiz
    assert len(engine.quiz_history) == 1
    attempt = engine.quiz_history[0]
    assert attempt["topic"] == "basic"
    assert attempt["score"] == 5
    assert attempt["total"] == 5


def test_stopping_a_quiz_early_does_not_record_history(engine):
    engine.get_response("/quiz basic")
    engine.get_response("B")
    engine.get_response("/stop")
    assert engine.quiz_history == []


def test_quiz_history_persists_across_engine_instances():
    tmp = Path(tempfile.mkdtemp())
    e1 = LessonEngine(progress_path=tmp / "p.json", quiz_history_path=tmp / "qh.json")
    e1.get_response("/quiz basic")
    _answer_all(e1)

    e2 = LessonEngine(progress_path=tmp / "p.json", quiz_history_path=tmp / "qh.json")
    assert len(e2.quiz_history) == 1
    assert e2.quiz_history[0]["topic"] == "basic"


def test_export_report_writes_csv(engine, tmp_path):
    engine.get_response("basic")  # marks progress
    engine.get_response("/quiz loop")
    _answer_all(engine, correct=True)  # completes a quiz -> history entry

    out = tmp_path / "report.csv"
    ok = engine.export_report(str(out))
    assert ok is True
    content = out.read_text(encoding="utf-8")
    assert "=== Progress ===" in content
    assert "basic,Yes" in content
    assert "=== Quiz History ===" in content
    assert "loop" in content
    assert ",5,5" in content  # score,total


def test_export_report_handles_bad_path_gracefully(engine):
    bad_path = "/nonexistent_dir_xyz/report.csv"
    ok = engine.export_report(bad_path)
    assert ok is False


# ── Topic matching: longest keyword wins ─────────────────────────────────
@pytest.mark.parametrize("text, topic", [
    ("Explain functions for beginners", "function"),   # not loop ("for")
    ("if you can, explain lists", "array"),             # not conditional ("if")
    ("how to open a file", "file_handling"),            # used to hit the fallback
    ("what is a for loop", "loop"),
    ("Explain Python data structures: list, tuple, set, dictionary", "data_structures"),
    ("Explain Python advanced functions: args kwargs lambda", "functions_advanced"),
])
def test_longest_keyword_wins(engine, text, topic):
    expected = engine._render(engine.lessons[topic])
    assert engine.get_response(text) == expected


# ── One topic name everywhere ────────────────────────────────────────────
@pytest.mark.parametrize("key", TOPIC_ORDER)
def test_lesson_heading_matches_topic_label(engine, key):
    """Each lesson heading in lessons.json starts with the same
    "<icon> <title>" used by progress, quiz and the /start menu."""
    heading = engine.lessons[key]["theory"].splitlines()[0]
    assert heading.startswith(topic_label(key)), heading


def test_every_topic_has_title_and_icon():
    assert set(TOPIC_TITLES) == set(TOPIC_ORDER) == set(TOPIC_ICONS)


def test_start_menu_lists_every_topic_by_label(engine):
    menu = engine.get_response("/start")
    for num, key in enumerate(TOPIC_ORDER, start=1):
        assert f"{num}. {topic_label(key)}" in menu


def test_progress_shows_labels_not_raw_keys(engine):
    result = engine.get_response("/progress")
    assert "functions_advanced" not in result
    assert "🔧 Functions Advanced" in result
    assert ">9.<" in result


def test_progress_shows_best_quiz_score(engine):
    engine.get_response("/quiz basic")
    _answer_all(engine, correct=True)
    rows = {r["key"]: r for r in engine.progress_rows()}
    assert rows["basic"]["best"] == 100
    assert rows["loop"]["best"] is None
    assert ">100%<" in engine.get_response("/progress")


def test_quiz_header_uses_label(engine):
    result = engine.get_response("/quiz functions_advanced")
    assert result.startswith("📝 Quiz: 🔧 Functions Advanced")


def test_quiz_stop_names_the_topic(engine):
    engine.get_response("/quiz loop")
    assert "🔁 Loop" in engine.get_response("/stop")


# ── /quiz accepts the names people actually type ─────────────────────────
@pytest.mark.parametrize("command, topic", [
    ("/quiz 5", "loop"),                         # number from the list
    ("/quiz5", "loop"),
    ("/quiz 11", "oop"),
    ("/quiz Loops", "loop"),                     # plural / capitals
    ("/quiz for loop", "loop"),                  # keyword
    ("/quiz data structures", "data_structures"),
    ("/quiz Functions Advanced", "functions_advanced"),
    ("/quiz file handling", "file_handling"),
    ("/quiz file-handling", "file_handling"),
    ("/quiz Basic Python", "basic"),             # displayed title
    ("/quiz Variables & Data Types", "variables"),
    ("/quiz 🔁 Loop", "loop"),                   # title copied with its icon
    ("quiz loop", "loop"),                       # without the slash
    ("quiz me on classes", "oop"),
])
def test_quiz_accepts_names_numbers_and_keywords(engine, command, topic):
    result = engine.get_response(command)
    assert result.startswith(f"📝 Quiz: {topic_label(topic)}"), result


@pytest.mark.parametrize("bad", ["/quiz 0", "/quiz 99", "/quiz pizza"])
def test_unknown_quiz_shows_the_numbered_list(engine, bad):
    result = engine.get_response(bad)
    assert "គ្មាន Quiz" in result
    assert "5. 🔁 Loop" in result


def test_quiz_command_mid_quiz_switches_quiz(engine):
    engine.get_response("/quiz loop")
    result = engine.get_response("/quiz oop")
    assert result.startswith("📝 Quiz: 🏛 OOP")


@pytest.mark.parametrize("text, topic", [
    ("data structures", "data_structures"),
    ("Functions Advanced", "functions_advanced"),
    ("Basic Python", "basic"),
    ("File Handling", "file_handling"),
])
def test_typing_a_lesson_name_opens_it(engine, text, topic):
    assert engine.get_response(text) == engine._render(engine.lessons[topic])


# ── Helpers ──────────────────────────────────────────────────────────────
def _answer_all(engine, correct=True):
    """Answer every remaining question (right or wrong); return the last reply."""
    reply = ""
    while engine._quiz_state is not None:
        q = engine._quiz_state["questions"][engine._quiz_state["index"]]
        right = "ABCD"[q["answer"]]
        wrong = "ABCD"[(q["answer"] + 1) % len(q["options"])]
        reply = engine.get_response(right if correct else wrong)
    return reply


# ── /progress card ───────────────────────────────────────────────────────
def test_progress_rows_follow_topic_order(engine):
    rows = engine.progress_rows()
    assert [r["key"] for r in rows] == TOPIC_ORDER
    assert [r["num"] for r in rows] == list(range(1, 12))
    assert all(r["label"] == topic_label(r["key"]) for r in rows)


def test_progress_card_is_rich_text_with_every_lesson(engine):
    result = engine.get_response("/progress")
    assert result.startswith("<p")                  # rendered as HTML by Qt
    assert "Variables &amp; Data Types" in result   # "&" escaped
    for row in engine.progress_rows():
        assert f">{row['num']}.<" in result


def test_progress_card_suggests_next_lesson(engine):
    engine.get_response("basic")
    engine.get_response("variables")
    assert "មេរៀនបន្ទាប់: <b>3. 🔢 Operators</b>" in engine.get_response("/progress")


def test_progress_card_congratulates_when_all_done(engine):
    for key in TOPIC_ORDER:
        engine.get_response(key)
    result = engine.get_response("/progress")
    assert "11/11" in result and "100%" in result
    assert "អបអរសាទរ" in result
    assert "មេរៀនបន្ទាប់" not in result


def test_progress_card_stats(engine):
    engine.get_response("/quiz basic")
    _answer_all(engine, correct=True)    # 100%
    engine.get_response("/quiz loop")
    _answer_all(engine, correct=False)   # 0%
    s = engine.report_summary()
    assert (s["quizzes_taken"], s["average_pct"]) == (2, 50)
    result = engine.get_response("/progress")
    assert f">{s['quizzes_taken']}<" in result
    assert f">{s['average_pct']}%<" in result


@pytest.mark.parametrize("pct, color_key", [(100, "green"), (60, "amber"), (40, "red")])
def test_progress_score_colors(engine, pct, color_key):
    engine.quiz_history = [{"timestamp": "x", "topic": "basic",
                            "score": round(pct * 5 / 100), "total": 5}]
    result = engine.get_response("/progress")
    color = {"green": C["accent_green"], "amber": "#f59e0b", "red": "#ef4444"}[color_key]
    assert f'<b style="color:{color};">{pct}%</b>' in result


# ── Quiz content: 5 questions per lesson ─────────────────────────────────
@pytest.mark.parametrize("topic", TOPIC_ORDER)
def test_every_lesson_has_5_valid_questions(engine, topic):
    questions = engine.quizzes[topic]
    assert len(questions) == 5
    for q in questions:
        assert q["question"].strip() and q["explain"].strip()
        assert len(q["options"]) == 4
        assert len(set(q["options"])) == 4           # no duplicate options
        assert 0 <= q["answer"] < 4


def test_no_question_is_repeated():
    texts = [q["question"] for qs in LessonEngine().quizzes.values() for q in qs]
    assert len(texts) == len(set(texts))


@pytest.mark.parametrize("topic", TOPIC_ORDER)
def test_every_lesson_quiz_can_be_completed(engine, topic):
    engine.get_response(f"/quiz {topic}")
    assert "សំណួរ 1/5" in engine._present_question()
    assert "ពិន្ទុ: 5/5" in _answer_all(engine, correct=True)


def test_old_mixed_quiz_history_is_ignored(tmp_path):
    """History saved by the removed 15-question quiz (topic "all") is
    dropped on load, so it can't skew the progress stats."""
    path = tmp_path / "qh.json"
    path.write_text(json.dumps({"attempts": [
        {"timestamp": "x", "topic": "all", "score": 15, "total": 15},
        {"timestamp": "y", "topic": "loop", "score": 2, "total": 5},
    ]}), encoding="utf-8")
    e = LessonEngine(progress_path=tmp_path / "p.json", quiz_history_path=path)
    assert [a["topic"] for a in e.quiz_history] == ["loop"]
    assert e.report_summary()["quizzes_taken"] == 1


def test_progress_mid_quiz_keeps_quiz_going(engine):
    engine.get_response("/quiz loop")
    result = engine.get_response("/progress")
    assert "វឌ្ឍនភាពការសិក្សា" in result and "នៅបន្ត" in result
    assert engine._quiz_state["index"] == 0          # nothing skipped
    assert "សំណួរ 2/5" in engine.get_response("C")    # loop Q1 answer is C


# ── Reset Progress clears everything the report shows ───────────────────
def test_reset_clears_quiz_history_and_report(tmp_path):
    e = LessonEngine(progress_path=tmp_path / "p.json",
                     quiz_history_path=tmp_path / "q.json")
    e.get_response("basic")
    e.get_response("/quiz basic")
    _answer_all(e, correct=True)
    e.get_response("/quiz loop")      # a quiz still in progress
    assert e.quiz_history and e.progress

    e.reset_progress()

    assert e.progress == set() and e.quiz_history == []
    assert e._quiz_state is None
    s = e.report_summary()
    assert (s["done"], s["quizzes_taken"], s["average_pct"]) == (0, 0, None)
    assert s["best_by_topic"] == {}
    assert "No quizzes taken yet" in e.build_report_html()

    # And it stays cleared after restarting the app.
    e2 = LessonEngine(progress_path=tmp_path / "p.json",
                      quiz_history_path=tmp_path / "q.json")
    assert e2.progress == set() and e2.quiz_history == []
