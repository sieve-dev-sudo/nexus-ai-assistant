# Changelog

All notable changes to this project are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/), and uses
[Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH).

## [Unreleased]

### Changed
- PDF report redesign: white header with a thin accent line instead of
  a solid blue block (which showed thin white seams in some PDF
  viewers), 4 summary boxes (Topics done, Progress, Quizzes taken,
  Average score), and Topic Progress as a real table
  (# / Topic / Status / Best quiz) styled like the Quiz History table
- Page 1 now holds up to 4 quiz rows (was 3) before Quiz History moves
  to page 2

### Fixed
- Reset Progress now also clears the quiz history (and any quiz in
  progress); before, `/progress` and the PDF report still showed the
  old quiz scores after a reset

## [1.3.0] - November 25, 2026

### Added
- Export Report as a styled A4 PDF (summary cards, progress bar, a
  2-column topic grid that always fits on page 1, quiz history with
  colored scores); CSV is still available from the save dialog
- `tests/test_report.py` (11 tests) for the report content
- Every lesson quiz now has 5 questions (was 3): 22 new questions
- `/progress` is now a styled card that follows the dark/light theme:
  overall % with a progress bar, stat boxes (lessons done, quizzes
  taken, average score), one row per lesson with a ✔/○ status and its
  best quiz score in green/amber/red, and the suggested next lesson
- `/progress` works in the middle of a quiz without skipping a question

### Removed
- Export Chat (`.md`) button: Export Report (PDF) now covers saving
  your learning progress
- The 15-question mixed quiz: plain `/quiz` and `/quiz list` now show
  the numbered list of lesson quizzes, and old mixed-quiz history is
  ignored so it doesn't affect progress stats

### Changed
- One name per topic everywhere: the sidebar, `/start` menu, progress
  checklist, quiz list, quiz header and PDF report all use the same
  numbered "icon + title" (e.g. "5. 🔁 Loop") instead of a mix of raw
  keys like `functions_advanced` and different spellings
- `/progress` shows each topic's best quiz score
- `/quiz` accepts a number from the list (`/quiz 5`), the displayed
  title (`/quiz Data Structures`), keywords (`/quiz for loop`) and
  works without the slash (`quiz loop`); an unknown name shows the
  numbered list instead of a dead end
- Typing `/quiz <topic>` during a quiz switches to that quiz
- Typing a lesson's displayed title ("Functions Advanced",
  "Basic Python") opens that lesson
- Topic matching: the longest matched keyword now wins, so everyday
  words like "for" and "if" no longer beat real topic words
  ("Explain functions for beginners" opens Functions, not Loops)
- Quiz: an answer that isn't A/B/C/D asks the same question again
  instead of counting as wrong and skipping ahead

### Fixed
- Fix Code Output now follows the order the `print()` calls are
  written in; prints inside `if` / `for` / `def` blocks used to be
  listed after all the top-level prints
- App crash ("QThread: Destroyed while thread is still running") when a
  sidebar topic was clicked again before the previous reply finished
- Fix Code froze forever on huge numbers like `10**10**10` or
  `"a" * 10**9`; the static evaluator now caps `**` and `*`
- Input box stuck disabled forever if an engine raised an exception
- Clear Chat during a pending reply no longer adds the old reply to
  the new, empty chat
- Removed `ast.Num` / `ast.Str` (gone in Python 3.14), and narrowed
  `except BaseException` to `except Exception`
- Corrupted or hand-edited `settings.json` values can no longer crash
  the app at startup (theme and font scale are validated and clamped)
- User messages are always shown as plain text (typed HTML tags are no
  longer rendered)
- `nexus_ai.spec` reads the version from `version.py` instead of a
  hard-coded copy
- "how to open a file" and "what is a for loop" now find their lesson
- Lesson keywords now match whole words, so "reset", "predict" and
  "classic" no longer open the wrong topic
- Empty answer during a quiz no longer crashes the engine
- Keyboard shortcuts no longer stack up after changing the theme

## [1.2.0] - August 20, 2026

### Added
- 22 more quiz questions (3 per topic, 33 total, up from 1 per topic)
- Complete type hints across `FixCode/fix_code_engine.py`,
  `LessonCodePython/lesson_engine.py`, and `settings_manager.py`
  (verified with `mypy`, 0 errors)
- 100% docstring coverage across every module, class, and function
- Test coverage reporting (`pytest-cov`, `.coveragerc`), plus 6 new tests
  for `settings_manager.py` (was 0% covered, now 100%); overall coverage
  is 82%
- `CONTRIBUTING.md`: setup, code style, commit convention, PR process
- About dialog (Version, Author, License)
- Live theme switching: Dark/Light and font size now apply immediately
  on Save, no app restart needed
- Python syntax highlighting in code blocks (keywords, strings,
  comments, numbers); "output" blocks stay plain text
- Undo for Clear Chat: a 10-second "Chat cleared" bar with an Undo
  button restores the conversation if clicked
- Export progress + quiz history as a `.csv` report
- macOS (`.app` bundle, `.icns` icon) and Linux build support in
  `nexus_ai.spec` (auto-detected by platform, same build command)

### Fixed
- Settings/About dialogs: mismatched dialog height silently collapsed
  info rows to 0px in Qt's layout engine
- `QFrame { ... }` stylesheet selector was leaking into child QLabels
  (QLabel is a QFrame subclass), making the About dialog's info card
  render empty
- Clear Chat: `deleteLater()` doesn't hide a widget immediately, so a
  just-cleared bubble could still flash on screen; now hidden right away
- Undo Clear Chat: showing the undo banner was accidentally discarding
  the very snapshot it needed to restore
- Tests completing a quiz were writing to the real
  `~/.nexus_ai/quiz_history.json` instead of a temp file

## [1.1.0] - August 14, 2026

### Added
- Custom Python logo icon (transparent background) replacing the 🐍 emoji,
  used in the sidebar, window/taskbar icon, and welcome message
- 11 new Fix Code rules (R9-R19): Python 2 `print`/`raw_input()` syntax,
  invalid comparison operators (`=<` `=>` `<>`), keyword misspellings,
  `else if`, `++`/`--`, unclosed `[` `]` `{` `}`, multi-line triple-quote
  string support, missing f-string prefix, and warn-only checks for
  mutable default arguments, undefined names, off-by-one loops, and
  `is`-vs-`==` literal comparisons
- Quiz Mode (`/quiz <topic>`) with scoring and `/stop`
- Progress Tracking (`/progress`), persisted to a local file
- Copy button on code blocks
- Export Chat to a `.md` file
- Clear Chat and Reset Progress buttons (both with confirmation)
- Settings panel: Dark/Light theme, font size 80%-150%
- Search box to filter lesson topics by name or keyword
- Keyboard shortcuts (Ctrl+K, Esc, Ctrl+L, Ctrl+,, Ctrl+F)
- Developer credit in the sidebar
- pytest test suite (134 tests) covering the FixCode and Lesson engines
- PyInstaller packaging (`nexus_ai.spec`) for a standalone executable
- MIT License

### Fixed
- Print-typo detector (R0) false-flagged real words (`sprint`, `point`,
  `greet`, `write`, `prime`, ...) as typos of `print`
- Missing-colon detector matched identifier prefixes (`elsewhere`,
  `exceptions`) instead of whole keywords
- `oop`/`loop` keyword collision routed "for loop" questions to the OOP
  lesson instead of Loop
- Multi-line triple-quoted docstring content could be misread/altered by
  other Fix Code rules
- Code block text and sidebar title were unreadable in Light theme
  (colors were following the theme instead of staying fixed/contrasting)

## [1.0.0] - August 1, 2026

### Added
- Lesson Mode: 11 Python topics with keyword-based lookup
  (`LessonCodePython/lesson_engine.py`, `lessons.json`)
- Fix Code Mode: base rule set (`FixCode/fix_code_engine.py`)
  - print typo/case fixes, trailing semicolons
  - unclosed quotes/parens, missing colons
  - `=`-vs-`==` detection, indentation issue detection
  - AST-based output estimation
- PyQt5 desktop UI: sidebar, chat panel, message bubbles, input bar
