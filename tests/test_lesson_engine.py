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

from LessonCodePython.lesson_engine import LessonEngine


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
def test_quiz_lists_topics_with_no_argument(engine):
    result = engine.get_response("/quiz")
    assert "basic" in result


def test_quiz_start_presents_first_question(engine):
    result = engine.get_response("/quiz basic")
    assert "សំណួរ" in result
    assert "A." in result and "B." in result


def test_quiz_correct_answer_increments_score(engine):
    engine.get_response("/quiz basic")
    result = engine.get_response("B")  # basic Q1: answer index 1 = B
    assert "ត្រឹមត្រូវ" in result
    assert "សំណួរ 2/3" in result  # advances to the next question


def test_quiz_wrong_answer_shows_correct_one(engine):
    engine.get_response("/quiz basic")
    result = engine.get_response("Z")  # not a valid option -> counted wrong
    assert "មិនត្រឹមត្រូវ" in result
    assert "សំណួរ 2/3" in result


def test_quiz_completes_with_final_score(engine):
    engine.get_response("/quiz basic")
    engine.get_response("B")  # Q1 correct
    engine.get_response("B")  # Q2 correct
    result = engine.get_response("A")  # Q3 correct
    assert "Quiz បញ្ចប់" in result
    assert "3/3" in result


def test_quiz_stop_mid_quiz(engine):
    engine.get_response("/quiz basic")
    result = engine.get_response("/stop")
    assert "បញ្ឈប់" in result


def test_quiz_unknown_topic(engine):
    result = engine.get_response("/quiz not_a_real_topic")
    assert "គ្មាន Quiz" in result


def test_quiz_state_does_not_leak_into_next_lookup(engine):
    engine.get_response("/quiz basic")
    engine.get_response("B")  # Q1
    engine.get_response("B")  # Q2
    engine.get_response("A")  # Q3 — quiz finishes
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
    result = engine.get_response("/progress")
    assert "✅ basic" in result


def test_progress_persists_across_engine_instances():
    progress_path = Path(tempfile.mkdtemp()) / "progress.json"
    e1 = LessonEngine(progress_path=progress_path)
    e1.get_response("basic")
    e1.get_response("loop")

    e2 = LessonEngine(progress_path=progress_path)
    result = e2.get_response("/progress")
    assert "✅ basic" in result
    assert "✅ loop" in result
    assert "2/11" in result


def test_progress_file_is_valid_json_on_disk():
    progress_path = Path(tempfile.mkdtemp()) / "progress.json"
    e = LessonEngine(progress_path=progress_path)
    e.get_response("variables")
    data = json.loads(progress_path.read_text(encoding="utf-8"))
    assert "variables" in data["completed"]


def test_keyword_match_also_marks_progress(engine):
    engine.get_response("explain for loop")  # keyword match, not exact key
    result = engine.get_response("/progress")
    assert "✅ loop" in result


# ── Quiz history + export report ──────────────────────────────────────────
def test_completing_a_quiz_records_history(engine):
    engine.get_response("/quiz basic")
    engine.get_response("B")
    engine.get_response("B")
    engine.get_response("A")  # finishes the 3-question quiz
    assert len(engine.quiz_history) == 1
    attempt = engine.quiz_history[0]
    assert attempt["topic"] == "basic"
    assert attempt["score"] == 3
    assert attempt["total"] == 3


def test_stopping_a_quiz_early_does_not_record_history(engine):
    engine.get_response("/quiz basic")
    engine.get_response("B")
    engine.get_response("/stop")
    assert engine.quiz_history == []


def test_quiz_history_persists_across_engine_instances():
    tmp = Path(tempfile.mkdtemp())
    e1 = LessonEngine(progress_path=tmp / "p.json", quiz_history_path=tmp / "qh.json")
    e1.get_response("/quiz basic")
    e1.get_response("B")
    e1.get_response("B")
    e1.get_response("A")

    e2 = LessonEngine(progress_path=tmp / "p.json", quiz_history_path=tmp / "qh.json")
    assert len(e2.quiz_history) == 1
    assert e2.quiz_history[0]["topic"] == "basic"


def test_export_report_writes_csv(engine, tmp_path):
    engine.get_response("basic")  # marks progress
    engine.get_response("/quiz loop")
    engine.get_response("B")
    engine.get_response("B")
    engine.get_response("A")  # completes a quiz -> history entry

    out = tmp_path / "report.csv"
    ok = engine.export_report(str(out))
    assert ok is True
    content = out.read_text(encoding="utf-8")
    assert "=== Progress ===" in content
    assert "basic,Yes" in content
    assert "=== Quiz History ===" in content
    assert "loop" in content
    assert "3" in content  # score


def test_export_report_handles_bad_path_gracefully(engine):
    bad_path = "/nonexistent_dir_xyz/report.csv"
    ok = engine.export_report(bad_path)
    assert ok is False
