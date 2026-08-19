# Changelog

All notable changes to this project are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/), and uses
[Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH).

## [Unreleased]

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
