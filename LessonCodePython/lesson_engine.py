"""
LessonCodePython/lesson_engine.py — 11 topics + Quiz mode
Order matters: more-specific keywords first to avoid wrong matches.
"""
import json
from pathlib import Path

LESSONS_PATH = Path(__file__).resolve().parent / "lessons.json"
QUIZ_PATH = Path(__file__).resolve().parent / "quizzes.json"
PROGRESS_PATH = Path.home() / ".nexus_ai" / "progress.json"

# ── ordered list so specific topics match BEFORE generic ones ─────────
# Each entry: (tuple_of_keywords, topic_key)
TOPIC_KEYWORDS = [
    # ── specific first ──────────────────────────────────────────────
    (("data structure", "tuple", "set", "dictionary", "dict", "key value",
      "hashmap", "data_structure"), "data_structures"),
    (("*args", "**kwargs", "kwargs", "lambda", "higher order",
      "map(", "filter(", "advanced function", "default param",
      "functions_advanced", "function advanced"), "functions_advanced"),
    (("file handling", "file_handling", "open(", "readline", "readlines",
      "writelines", "encoding", "file mode", "read file", "write file",
      "append file", "csv", "txt file"), "file_handling"),
    (("class", "object", "inherit", "__init__", "self.",
      "polymor", "encapsul", "instance of", "override",
      "magic method", "__str__", "super()", " oop "), "oop"),
    # ── generic topics after ────────────────────────────────────────
    (("basic", "comment", "indentation", "hello world", "syntax",
      "python basic", "first program"), "basic"),
    (("variable", "data type", "int(", "float(", "bool", "none",
      "type conversion", "ប្រភេទ", "var ", "assign"), "variables"),
    (("operator", "arithmetic", "math", "calculation", "modulo",
      "floor div", "bitwise", "operator"), "operators"),
    (("if ", "else:", "elif", "condition", "conditional",
      "ternary", "លក្ខខណ្ឌ"), "conditional"),
    (("for ", "while ", "iterate", "range(",
      "break", "continue", "repeat"), "loop"),
    (("array", "list", "append", "pop(", "sort(", "index", "slice",
      "បញ្ជី", "remove(", "insert("), "array"),
    (("function", "def ", "return", "parameter", "argument",
      "អនុគមន៍", "func"), "function"),
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


class LessonEngine:
    def __init__(self, path: Path = LESSONS_PATH, quiz_path: Path = QUIZ_PATH,
                 progress_path: Path = PROGRESS_PATH):
        self.lessons = json.loads(path.read_text(encoding="utf-8"))
        self.quizzes = (json.loads(quiz_path.read_text(encoding="utf-8"))
                         if quiz_path.exists() else {})
        self._quiz_state = None  # {"topic", "index", "score", "total"}
        self.progress_path = progress_path
        self.progress = self._load_progress()

    def _load_progress(self) -> set:
        try:
            if self.progress_path.exists():
                data = json.loads(self.progress_path.read_text(encoding="utf-8"))
                return set(data.get("completed", []))
        except (OSError, ValueError):
            pass
        return set()

    def _save_progress(self):
        try:
            self.progress_path.parent.mkdir(parents=True, exist_ok=True)
            self.progress_path.write_text(
                json.dumps({"completed": sorted(self.progress)},
                           ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass  # progress is a nice-to-have — never crash the app over it

    def _mark_completed(self, topic: str):
        if topic not in self.progress:
            self.progress.add(topic)
            self._save_progress()

    def _show_progress(self) -> str:
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

        # Keyword match — ordered list, first match wins
        for keywords, topic in TOPIC_KEYWORDS:
            if any(kw in lower for kw in keywords):
                if topic in self.lessons:
                    self._mark_completed(topic)
                    return self._render(self.lessons[topic])

        return self._fallback(user_input)

    # ── Quiz mode ───────────────────────────────────────────────────
    def _start_quiz(self, text: str) -> str:
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
        state = self._quiz_state
        q = self.quizzes[state["topic"]][state["index"]]
        options_text = "\n".join(
            f"  {chr(65 + i)}. {opt}" for i, opt in enumerate(q["options"])
        )
        return (f"❓ សំណួរ {state['index'] + 1}/{state['total']} "
                f"({state['topic']}):\n\n{q['question']}\n\n{options_text}\n\n"
                f"សូមឆ្លើយ A, B, C ឬ D (វាយ /stop ដើម្បីបញ្ឈប់)")

    def _handle_quiz_answer(self, text: str) -> str:
        state = self._quiz_state
        q = self.quizzes[state["topic"]][state["index"]]
        letter = text.strip().upper()[:1]
        chosen = ord(letter) - 65 if letter in "ABCD" else -1

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
            self._quiz_state = None
            return f"{feedback}\n{explain}\n\n🎉 Quiz បញ្ចប់! ពិន្ទុ: {score}/{total}"

        return f"{feedback}\n{explain}\n\n{self._present_question()}"

    @staticmethod
    def _render(entry) -> str:
        if isinstance(entry, dict):
            theory = entry.get("theory", "")
            example = entry.get("example", "")
            return f"{theory}\n\n📝 ឧទាហរណ៍ (Example):\n\n```python\n{example}\n```"
        return entry

    def _fallback(self, user_input: str) -> str:
        topics = [k for k in self.lessons if k != "/start"]
        listing = "\n".join(f"  • {t}" for t in topics)
        return (
            f'🤔 ខ្ញុំមិនយល់អំពីអ្វីដែលអ្នកសរសេរ: "{user_input[:60]}"\n\n'
            f"💡 Topics ({len(topics)}):\n\n{listing}\n\n"
            f"👉 វាយ /start ដើម្បីមើល menu ពេញ"
        )
