<div align="center">

# Nexus AI : Python Assistant

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![Rule-Based](https://img.shields.io/badge/AI-Rule--Based-orange?style=for-the-badge)
![Topics](https://img.shields.io/badge/TOPICS-11-6f42c1?style=for-the-badge)
![Offline](https://img.shields.io/badge/Offline-Yes-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-1.2.0-informational?style=for-the-badge)

```
███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗     █████╗ ██╗    ██████╗ ██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗
████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝    ██╔══██╗██║    ██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║
██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗    ███████║██║    ██████╔╝ ╚████╔╝    ██║   ███████║██║   ██║██╔██╗ ██║
██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║    ██╔══██║██║    ██╔═══╝   ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗██║
██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║    ██║  ██║██║    ██║        ██║      ██║   ██║  ██║╚██████╔╝██║ ╚████║
╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝    ╚═╝  ╚═╝╚═╝    ╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
```

</div>

---

## ✨ Features

- 📚 **Lesson Mode** : សួរសំណួរ ឬជ្រើសរើស Topic ពី Sidebar ដើម្បីរៀន Python ( 11 ប្រធានបទ )
- 📝 **Quiz Mode** : វាយ `/quiz <topic>` ដើម្បីធ្វើតេស្តចំណេះដឹង multiple-choice (3 សំណួរ/topic, 33 សរុប)
- 📊 **Progress Tracking** : វាយ `/progress` ដើម្បីមើលថា topic ណាបានរៀនរួច (local file, គ្មាន account)
- 🛠 **Fix Code Mode** : Paste កូដ Python ចូល App នឹងវិភាគ រកកំហុស និងកែឱ្យស្វ័យប្រវត្តិ
- 📋 **Copy Button** : ចម្លង code block ក្នុង chat ដោយចុចតែម្តង
- 🎨 **Syntax Highlighting** : ពណ៌ keyword/string/comment/number ក្នុង code block ដូច VS Code
- 💾 **Export Chat** : Save conversation ជា file `.md`
- 📑 **Export Report** : Export progress + quiz history ជា file `.csv`
- 🗑️ **Clear Chat** : លុប conversation បច្ចុប្បន្នចោល (មាន Undo 10 វិនាទី)
- 🔄 **Reset Progress** : លុបវឌ្ឍនភាពការសិក្សាចោល (មាន confirmation)
- ⚙️ **Settings** : ប្តូរ Theme (Dark/Light) និង Font size
- ℹ️ **About Dialog** : មើល Version, Author, License
- 🔍 **Search Lessons** : ស្វែងរក topic ដោយផ្ទាល់ពី Sidebar (តាមឈ្មោះ ឬ keyword ខាងក្នុង)
- ⌨️ **Keyboard Shortcuts** : `Ctrl+K`, `Esc`, `Ctrl+L`, `Ctrl+,`, `Ctrl+F`
- 🎨 UI រចនាបែប Dark Theme ស្រដៀង Chat App សម័យទំនើប
- ⚡ ដំណើរការលឿន ព្រោះគ្មាន API call ខាងក្រៅ

---

## 📁 Project Structure

```
Nexus-AI-Assistant/
├── FixCode/
│   └── fix_code_engine.py        → Logic កែកូដ ( regex + AST, type-hinted, mypy-clean )
├── LessonCodePython/
│   ├── lesson_engine.py          → Logic ផ្គូផ្គង keyword → topic + Quiz mode
│   ├── lessons.json              → ខ្លឹមសារមេរៀនទាំង 11
│   ├── quizzes.json              → សំណួរ Quiz តាម topic
│   ├── settings_manager.py       → Theme/Font settings persistence
│   ├── version.py                → App version (single source of truth)
│   └── theme.py                  → ពណ៌ (Dark/Light) និង Font កំណត់រួម
├── ui/
│   ├── main_window.py            → បង្អួចមេ + Keyboard shortcuts
│   ├── sidebar.py                → ម៉ឺនុយឆ្វេង + Search topics
│   ├── chat_panel.py             → ផ្ទាំង Chat
│   ├── message_bubble.py         → Bubble សារ
│   ├── input_bar.py              → ប្រអប់វាយអក្សរ
│   ├── icons.py                  → Python logo icon loader
│   ├── settings_dialog.py        → Settings dialog (Theme/Font)
│   ├── about_dialog.py           → About dialog (Version/Author/License)
│   └── avatars.py                → រូបតំណាង
├── assets/
│   ├── python_logo.png           → Python logo (icon source)
│   ├── python_logo.ico           → Icon សម្រាប់ Windows build
│   └── python_logo.icns          → Icon សម្រាប់ macOS build
├── tests/
│   ├── test_fix_code_engine.py   → Test សម្រាប់ FixCode 19 rule
│   ├── test_lesson_engine.py     → Test សម្រាប់ Lesson/Quiz/Progress
│   └── test_settings_manager.py  → Test សម្រាប់ Settings persistence
├── conftest.py                   → Path setup សម្រាប់ pytest
├── pytest.ini                    → Pytest config
├── .coveragerc                   → Coverage.py config
├── nexus_ai.spec                 → PyInstaller build config
├── main.py                       → ចំណុចចូល ( Entry point )
├── README.md
├── CHANGELOG.md                  → History នៃការផ្លាស់ប្តូរតាម version
├── CONTRIBUTING.md                → Guide សម្រាប់អ្នកចង់ contribute
├── LICENSE                       → MIT License
├── requirements.txt              → Dependencies
└── requirements-dev.txt          → Dependencies សម្រាប់ testing
```

---

## 🚀 How to Run

1. Clone ឬ download repository នេះ
2. ដំឡើង dependencies ៖ `pip install -r requirements.txt`
3. ដំណើរការ App ៖ `python main.py`

---

## 📚 Lesson Mode : Topics

| Key                   | ពិពណ៌នា                                           |
|-----------------------|---------------------------------------------------|
| `basic`               | ចំណេះដឹងមូលដ្ឋាន Python, comment, syntax           |
| `variables`           | Variables & Data Types                            |
| `operators`           | Arithmetic / Bitwise Operators                    |
| `conditional`         | if / elif / else                                  |
| `loop`                | for / while, break, continue                      |
| `array`               | List: append, pop, sort, slice                    |
| `function`            | def, return, parameters                           |
| `data_structures`     | tuple, set, dictionary                            |
| `functions_advanced`  | *args, **kwargs, lambda                           |
| `file_handling`       | open(), read/write file                           |
| `oop`                 | class, object, inheritance, `__init__`            |

**របៀបប្រើ:** វាយឈ្មោះ topic ដោយផ្ទាល់ ឬពាក្យគន្លឹះពាក់ព័ន្ធ ក្នុង chat box, ឬវាយ `/start` ដើម្បីមើល menu ពេញ។

📝 **Quiz:** វាយ `/quiz <topic>` (ឧ. `/quiz loop`) ដើម្បីធ្វើតេស្តចំណេះដឹង៖ **3 សំណួរ multiple-choice/topic**, ឆ្លើយ A/B/C/D, វាយ `/stop` ដើម្បីបញ្ឈប់ពាក់កណ្តាល។

📊 **Progress:** វាយ `/progress` ដើម្បីមើលថា topic ណាបានរៀនរួច (កត់ត្រាទុកស្វ័យប្រវត្តិពេលមើលមេរៀន)។

---

## 🛠 Fix Code Mode : អ្វីខ្លះដែលកែបាន

1. **Typo នៃ `print()`** : ដូចជា `printf(`, `Printtf(`, `PrInt(`
2. **Case ខុស** : `Print()`, `PRINT()` → `print()`
3. **សញ្ញា `;`** នៅចុងបន្ទាត់ ( មិនចាំបាច់ក្នុង Python )
4. **Quote / Parenthesis** មិនបានបិទ
5. **`:` បាត់** ក្រោយ if / elif / else / for / while / def / class
6. **Logic error** : ប្រើ `=` ជំនួស `==` ក្នុង condition
7. **Indentation** : លាយ tabs និង spaces, ឬ indent មិនប្រក្រតី
8. **គណនា Output** : ប៉ាន់ស្មានលទ្ធផលពី `print()` ដោយប្រើ Python AST
9. **Python 2 print statement** : `print "x"` → `print("x")`
10. **Invalid comparison operators** : `=<` `=>` `<>` → `<=` `>=` `!=`
11. **Keyword misspellings** : `retrun`, `improt`, `flase`, `ture`, `els` ជាដើម
12. **`else if`** → `elif`
13. **Python 2 `raw_input()`** → `input()`
14. **`++` / `--`** → `+= 1` / `-= 1`
15. **f-string ភ្លេច `f`** : `"Hi {name}"` → `f"Hi {name}"`
16. **Mutable default argument** : `def f(x=[]):` ព្រមាន
17. **Undefined name** : ប្រើ variable/function ដែលមិនឃើញកន្លែង define ព្រមាន
18. **Off-by-one loop** : `range(len(x)+1)`, `i <= len(x)` ព្រមាន
19. **`is` vs `==`** : ប្រៀបធៀប literal ដោយ `is` (`x is 5`) ព្រមាន

**របៀបប្រើ:** Paste កូដ Python ចូល input bar រួចចុច Send ( Shift+Enter = ចុះបន្ទាត់ថ្មី ) ។

---

## 💾 Chat Tools

- **📋 Copy Button** : លេចឡើងនៅជ្រុងខាងលើស្តាំ code block ណាមួយ ចុចដើម្បីចម្លងកូដទាំងមូល
- **🎨 Syntax Highlighting** : code block ក្នុង chat បង្ហាញពណ៌ keyword/string/comment/number ស្វ័យប្រវត្តិ (block ដែលដាក់ tag `output` នៅតែពណ៌ស ធម្មតា)
- **💾 Export Chat** : ចុច button "Export Chat" នៅផ្នែកខាងក្រោម Sidebar ដើម្បី save conversation ទាំងមូល (រួម welcome message) ជា file `.md`
- **📑 Export Report** : ចុច button "Export Report" ដើម្បី save progress checklist + quiz history ទាំងអស់ជា file `.csv`
- **🗑️ Clear Chat** : ចុច button "Clear Chat" ដើម្បីលុប conversation បច្ចុប្បន្នចោល (មាន confirmation dialog + **Undo 10 វិនាទី** បើក្រោយពីលុបចោល ចង់ស្តារត្រឡប់វិញ)
- **🔄 Reset Progress** : ចុច button "Reset Progress" ដើម្បីលុបវឌ្ឍនភាពការសិក្សាទាំងអស់ចោល (មាន confirmation dialog)

---

## ⚙️ Settings

ចុច "⚙️ Settings" ក្នុង Sidebar ដើម្បីប្តូរ៖
- **Theme** : Dark ឬ Light
- **Font Size** : 80% - 150%

*ការផ្លាស់ប្តូរដំណើរការភ្លាមៗ, មិនចាំបាច់ restart App ទេ។*

---

## ℹ️ About

ចុច "ℹ️ About" ក្នុង Sidebar ដើម្បីមើល Version, Author, និង License របស់ project ។

---

## 🔍 Search Lessons

ប្រអប់ "🔍 Search topics…" នៅខាងលើ Topics list អាចស្វែងរកបាន ទាំងតាម **ឈ្មោះ topic** និង **keyword ខាងក្នុង** (ឧ. វាយ "class" ឬ "lambda" នឹងបង្ហាញ topic ត្រូវគ្នាភ្លាមៗ)។

---

## ⌨️ Keyboard Shortcuts

| Key | មុខងារ |
|---|---|
| `Ctrl+K` | Focus ទៅ input box |
| `Esc` | Clear អក្សរដែលកំពុងវាយក្នុង input |
| `Ctrl+L` | Clear Chat |
| `Ctrl+,` | បើក Settings |
| `Ctrl+F` | Focus ទៅ Search topics box |

---

## 🎨 Theme

ពណ៌ និង Font ទាំងអស់ត្រូវបានកំណត់នៅកន្លែងតែមួយ (`LessonCodePython/theme.py`) ធ្វើឱ្យងាយស្រួល Customize ទម្រង់ UI ទាំងមូល។

---

## ✅ Testing & Code Quality

Project នេះមាន automated test (pytest) គ្របដណ្តប់ FixCode engine (19 rule) និង Lesson engine (topic lookup, Quiz, Progress)៖ សរុប **146 test** ។ Core logic (`FixCode/`, `LessonCodePython/`) មាន **type hint ពេញលេញ** (mypy-verified, 0 error), **docstring coverage 100%**, និង **test coverage 82%** (`pytest-cov`) ។

```bash
pip install -r requirements-dev.txt
pytest                                    # run test ធម្មតា
pytest --cov --cov-report=term-missing    # + coverage report
pytest --cov --cov-report=html            # + HTML report (htmlcov/index.html)
```

---

## 📦 Build ជា Standalone App (Windows / macOS / Linux)

មិនចាំបាច់ឲ្យ user ដំឡើង Python ខ្លួនឯងទេ៖ build ជា executable តែមួយឯកតា៖

```bash
pip install -r requirements-dev.txt
pyinstaller nexus_ai.spec
```

Command ដដែលនេះ ដំណើរការលើ **ទាំង ៣ platform** (icon format ជ្រើសរើសដោយស្វ័យប្រវត្តិតាម OS)៖

| Platform | Output |
|---|---|
| Windows | `dist/NexusAI.exe` |
| macOS | `dist/NexusAI.app` (double-click បាន ដូច App ធម្មតា) |
| Linux | `dist/NexusAI` (binary ដំណើរការភ្លាមៗ) |

Data file ទាំងអស់ (lessons.json, quizzes.json, python logo) ត្រូវបាន bundle ចូលរួចហើយ, copy folder ចេញទៅម៉ាស៊ីនផ្សេង (platform ដូចគ្នា) បាន run ភ្លាមៗដោយមិនចាំបាច់ install Python ។

---

## 📝 Notes

- App នេះមិនតម្រូវឱ្យមាន Internet ឬ API Key ទេ ( 100% Local Logic )
- សម្រាប់គោលបំណងសិក្សា / Demo : មិនមែនជា AI Model ពិតប្រាកដ (LLM) ទេ គឺជា Rule-based system
- Desktop AI Chatbot Application សម្រាប់បង្រៀន និងកែកូដ Python សាងសង់ដោយ **PyQt5**
- App នេះដំណើរការជា **Rule-based AI** ១០០% ក្នុងម៉ាស៊ីន Local និង គ្មានការហៅ API ខាងក្រៅ ឬប្រើ Internet ទេ។

---

## 📄 License

Project នេះស្ថិតក្រោម [MIT License](LICENSE) ។ អាចប្រើ កែច្នៃ និងចែកចាយបានដោយសេរី។

---

## 📜 Changelog

មើលការផ្លាស់ប្តូរតាម version ទាំងអស់នៅ [CHANGELOG.md](CHANGELOG.md) ។

---

## 🤝 Contributing

ចង់ជួយ contribute? សូមអាន [CONTRIBUTING.md](CONTRIBUTING.md) សម្រាប់ code style, របៀប run test, និង PR process ។

---

## 👤 Author

Developed by **Mr. Siev E**
