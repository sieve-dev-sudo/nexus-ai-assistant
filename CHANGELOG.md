# Changelog

All notable changes to this project are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/), and uses
[Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH).

## [Unreleased]

## [1.0.0] - 2026-08-13

### Added
- **Lesson Mode**: 11 ប្រធានបទ Python (basic → OOP), keyword-based lookup
- **Quiz Mode** (`/quiz <topic>`): សំណួរ multiple-choice, ពិន្ទុ, `/stop`
- **Progress Tracking** (`/progress`): កត់ត្រា topic ដែលបានរៀនរួច ទៅ local file
- **Fix Code Mode**: 19 rule សម្រាប់ detect/auto-fix កំហុស Python ទូទៅ
  (print typo, missing colon, `=` vs `==`, indentation, Python 2 syntax,
  invalid operators, keyword typo, f-string, mutable default, undefined
  name, off-by-one, `is` vs `==` ។ល។)
- **Copy Button**: ចម្លង code block ក្នុង chat ដោយចុចតែម្តង
- **Export Chat**: save conversation ជា file `.md`
- Python logo icon (custom, transparent background) ជំនួស emoji 🐍
- Developer credit ("Developed by Mr. Siev E") ក្នុង sidebar
- **pytest test suite**: 134+ test គ្របដណ្តប់ FixCode + Lesson engine
- **PyInstaller packaging**: build ជា standalone `.exe`
- MIT License

### Fixed
- Print-typo false positives (`sprint`, `point`, `greet`, `write` ។ល។
  ធ្លាប់ត្រូវបំផ្លាញដោយចៃដន្យ)
- Missing-colon detector ប៉ះពាល់ identifier ដូចជា `elsewhere`, `exceptions`
- `oop`/`loop` keyword collision (`"for loop"` ធ្លាប់ចាត់ទុកខុសជា OOP topic)
- Multi-line triple-quote docstring content ធ្លាប់ត្រូវកែខុសដោយ rule ផ្សេង
