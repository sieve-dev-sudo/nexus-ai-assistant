"""
tests/test_report.py — PDF report content (LessonEngine.report_summary
and build_report_html). The HTML builder is pure Python, so these tests
don't need Qt; the Qt PDF writer itself is smoke-tested only when PyQt5
is importable.
"""
import pytest

from LessonCodePython.lesson_engine import LessonEngine, TOPIC_ORDER, TOPIC_TITLES


@pytest.fixture
def engine(tmp_path):
    """A LessonEngine whose progress/history files live in a temp dir."""
    return LessonEngine(progress_path=tmp_path / "progress.json",
                        quiz_history_path=tmp_path / "quiz_history.json")


def _add_attempt(engine, topic, score, total=3, ts="2026-11-18 22:30:12"):
    """Append one fake quiz attempt to the engine's history."""
    engine.quiz_history.append(
        {"timestamp": ts, "topic": topic, "score": score, "total": total})


def test_summary_empty(engine):
    s = engine.report_summary()
    assert s["done"] == 0
    assert s["total"] == len(TOPIC_ORDER)
    assert s["progress_pct"] == 0
    assert s["quizzes_taken"] == 0
    assert s["average_pct"] is None
    assert s["best_by_topic"] == {}


def test_summary_counts_and_best_score(engine):
    engine.progress = {"basic", "loop"}
    _add_attempt(engine, "loop", 1)
    _add_attempt(engine, "loop", 3)
    _add_attempt(engine, "basic", 2)
    s = engine.report_summary()
    assert s["done"] == 2
    assert s["progress_pct"] == round(2 / len(TOPIC_ORDER) * 100)
    assert s["quizzes_taken"] == 3
    assert s["average_pct"] == round((33 + 100 + 67) / 3)
    assert s["best_by_topic"] == {"loop": 100, "basic": 67}


def test_summary_ignores_unknown_progress_keys(engine):
    engine.progress = {"basic", "not_a_topic"}
    assert engine.report_summary()["done"] == 1


def test_summary_zero_total_attempt_does_not_crash(engine):
    _add_attempt(engine, "loop", 0, total=0)
    assert engine.report_summary()["average_pct"] == 0


def test_html_lists_every_topic_title(engine):
    out = engine.build_report_html()
    for key in TOPIC_ORDER:
        assert TOPIC_TITLES[key].replace("&", "&amp;") in out


def test_html_shows_version_and_author(engine):
    out = engine.build_report_html(version="1.2.0")
    assert "v1.2.0" in out
    assert "Mr. Siev E" in out


def test_html_empty_history_message(engine):
    assert "No quizzes taken yet" in engine.build_report_html()


def test_html_history_newest_first(engine):
    _add_attempt(engine, "basic", 3, ts="2026-11-10 09:00:00")
    _add_attempt(engine, "loop", 2, ts="2026-11-18 22:30:00")
    out = engine.build_report_html()
    assert out.index("2026-11-18 22:30") < out.index("2026-11-10 09:00")


def test_html_escapes_data_from_history_file(engine):
    """quiz_history.json is a file on disk: a tampered topic name must
    not inject markup into the report."""
    _add_attempt(engine, "<b>evil</b>", 1)
    out = engine.build_report_html()
    assert "<b>evil</b>" not in out
    assert "&lt;b&gt;evil&lt;/b&gt;" in out


def test_pdf_file_is_written(engine, tmp_path):
    """Smoke test for the Qt PDF writer (skipped when PyQt5 isn't installed)."""
    pytest.importorskip("PyQt5")
    import os
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt5.QtWidgets import QApplication
    from ui.report_pdf import export_pdf

    app = QApplication.instance() or QApplication([])  # must exist for Qt painting
    assert app is not None
    _add_attempt(engine, "loop", 3)
    path = tmp_path / "report.pdf"
    assert export_pdf(engine.build_report_html("1.2.0"), str(path)) is True
    assert path.read_bytes()[:5] == b"%PDF-"


def test_long_history_starts_on_new_page(engine):
    """Up to 3 quizzes fit on page 1; more start Quiz History on page 2
    so the table is never split with an empty band under the topic grid."""
    for _ in range(3):
        _add_attempt(engine, "loop", 2)
    assert "page-break-before:always" not in engine.build_report_html()
    _add_attempt(engine, "loop", 2)
    assert "page-break-before:always" in engine.build_report_html()
