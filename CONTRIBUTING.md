# Contributing to Nexus AI

សូមអរគុណដែលចាប់អារម្មណ៍ចង់ជួយ contribute! ឯកសារនេះពន្យល់ពីរបៀប setup, code style, និង process សម្រាប់ផ្ញើ Pull Request។

---

## 🚀 Getting Started

```bash
git clone <url>
cd folder
pip install -r requirements-dev.txt
```

សាកល្បង run App:
```bash
python main.py
```

សាកល្បង run test (ត្រូវ **pass ទាំងអស់** មុននឹង commit):
```bash
pytest
pytest --cov --cov-report=term-missing   # ជាមួយ coverage report
```

---

## 📁 តើកូដត្រូវដាក់កន្លែងណា

| ចង់បន្ថែម... | ដាក់ចូល |
|---|---|
| Fix Code rule ថ្មី | `FixCode/fix_code_engine.py` |
| Lesson topic ថ្មី | `LessonCodePython/lessons.json` |
| Quiz question ថ្មី | `LessonCodePython/quizzes.json` |
| UI component ថ្មី | `ui/` |
| Test ថ្មី | `tests/test_*.py` (ត្រូវផ្គូផ្គងឈ្មោះ module ដែល test) |

---

## 🎨 Code Style

- **Type hints**: function/method ថ្មីទាំងអស់ក្នុង `FixCode/` និង `LessonCodePython/` ត្រូវមាន type hint ពេញលេញ (parameter + return type)។ សាកល្បងជាមួយ `mypy`:
  ```bash
  mypy FixCode/fix_code_engine.py LessonCodePython/lesson_engine.py --ignore-missing-imports
  ```
- **Docstrings**: function/class/module ថ្មីទាំងអស់ត្រូវមាន docstring មួយបន្ទាត់យ៉ាងហោចណាស់ ពន្យល់ពី **អ្វី** និង **ហេតុអ្វី** (មិនមែនត្រឹមតែសរសេរឡើងវិញនូវឈ្មោះ function ទេ)។
- **Comment ជាភាសាខ្មែរ ឬអង់គ្លេស** ទាំងពីរអាចប្រើបាន៖ code base បច្ចុប្បន្នលាយគ្នា (khmer សម្រាប់ user-facing text, English សម្រាប់ code comment) ។ សូមរក្សា convention នេះ។
- **គ្មាន logic ថ្មីដែលគ្មាន test**៖ មើលផ្នែក "Adding a new Fix Code rule" ខាងក្រោម។

---

## ✅ Adding a new Fix Code rule

Fix Code rule នីមួយៗគួរតែធ្វើតាមគំរូនេះ (មើល R9-R19 ជាឧទាហរណ៍)៖

1. សរសេរ function ថ្មី (ឧ. `_fix_my_new_rule` សម្រាប់ auto-fix, ឬ `_detect_my_new_rule` សម្រាប់ warn-only)
2. **Auto-fix vs warn-only**: បើកែបានដោយសុវត្ថិភាព (single-line replacement) → auto-fix។ បើត្រូវការផ្លាស់ប្តូរ logic/structure (ឧ. mutable default argument) → warn-only ប៉ុណ្ណោះ។
3. **គិតពី false positive សិន**: មុនដាក់ auto-fix ណាមួយ សួរខ្លួនឯងថា "តើ real identifier/word ណាមួយអាចត្រូវប៉ះពាល់ខុសដោយចៃដន្យទេ?" (ឧ. `sprint`/`point` vs `print` typo detection, មើល `_PRINT_SAFE_WORDS`)
4. Hook ចូល `_analyze()` pipeline តាមលំដាប់សមរម្យ
5. បន្ថែម rule ចូល docstring header ខាងលើ file
6. សរសេរ test ក្នុង `tests/test_fix_code_engine.py`៖ ករណីគួរ fix, ករណីមិនគួរប៉ះពាល់ (real word safety), integration test
7. Update `README.md` (Fix Code Mode section) និង `CHANGELOG.md`

---

## 📝 Commit Message Convention

ប្រើ prefix ខាងក្រោម (ដូច [Conventional Commits](https://www.conventionalcommits.org/))៖

| Prefix | ប្រើពេលណា |
|---|---|
| `feat:` | Feature ថ្មី |
| `fix:` | កែ bug |
| `docs:` | ផ្លាស់ប្តូរ documentation (README, CHANGELOG, docstring) |
| `test:` | បន្ថែម/កែ test |
| `chore:` | Maintenance (dependency, config, cleanup) |
| `build:` | ផ្លាស់ប្តូរ build/packaging (PyInstaller ។ល។) |
| `ci:` | ផ្លាស់ប្តូរ CI/CD |

ឧទាហរណ៍: `feat: add search box to filter lesson topics`

---

## 🌿 Branch Naming

```
feature/<short-description>    # ឧ. feature/syntax-highlighting
fix/<short-description>        # ឧ. fix/quiz-score-bug
docs/<short-description>       # ឧ. docs/update-readme
```

---

## 🔀 Pull Request Process

1. Fork repository ហើយបង្កើត branch ថ្មីពី `main`
2. សរសេរកូដ + test
3. ប្រាកដថា `pytest` និង `mypy` **pass ទាំងអស់**
4. Update `README.md`/`CHANGELOG.md` ប្រសិនបើពាក់ព័ន្ធ
5. ផ្ញើ PR ជាមួយពិពណ៌នាច្បាស់លាស់ថាកែអ្វី ហេតុអ្វី
6. រង់ចាំ review
