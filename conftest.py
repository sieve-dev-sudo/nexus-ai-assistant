"""
conftest.py — makes the project root importable from tests/, so
`import FixCode.fix_code_engine` and `import LessonCodePython.lesson_engine`
work regardless of where pytest is invoked from.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
