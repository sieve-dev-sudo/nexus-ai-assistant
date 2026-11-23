<div align="center">

# Nexus AI : Python Assistant

</div>

## 🛠️ Tech Stack

**ភាសាសរសេរកូដ និង ឧបករណ៍**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-41CD52?style=flat&logo=qt&logoColor=white)
![JSON](https://img.shields.io/badge/JSON-000000?style=flat&logo=json&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat&logo=pytest&logoColor=white)
![PyInstaller](https://img.shields.io/badge/PyInstaller-Build-blue?style=flat)
![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?style=flat&logo=visualstudiocode&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat)

---

## ✨ Features

- **Lesson Mode**: រៀន Python 11 មេរៀន តាំងពីមូលដ្ឋានរហូតដល់ OOP ដោយវាយឈ្មោះមេរៀន ពាក្យគន្លឹះ ឬចុចពី Sidebar
- **Quiz Mode**: Quiz multiple-choice **5 សំណួរ** សម្រាប់មេរៀននីមួយៗ (**55 សំណួរ**សរុប) ឆ្លើយ A/B/C/D ហើយមានការពន្យល់ក្រោយចម្លើយនីមួយៗ
- **Flexible Quiz Command**: ចាប់ផ្តើម Quiz បានតាមលេខ (`/quiz 5`) ឈ្មោះមេរៀន (`/quiz Data Structures`) ឬពាក្យគន្លឹះ (`/quiz for loop`)
- **Progress Card**: `/progress` បង្ហាញកាតស្អាតមាន progress bar ស្ថិតិ ពិន្ទុ Quiz ល្អបំផុតតាមមេរៀន (ពណ៌ បៃតង/លឿង/ក្រហម) 
- **Fix Code Mode**: Paste កូដ Python ចូល App នឹងរកកំហុស **19 ប្រភេទ** កែឲ្យស្វ័យប្រវត្តិ និងប៉ាន់ស្មាន Output
- **Export Report**: Export វឌ្ឍនភាព និងប្រវត្តិ Quiz ជា **PDF** A4 ស្អាតៗ (ឬ `.csv` សម្រាប់ Excel)
- **Syntax Highlighting + Copy Button**: Code block ក្នុង chat មានពណ៌ដូច VS Code និងប៊ូតុងចម្លងកូដដោយចុចតែម្តង
- **Search Topics**: ស្វែងរកមេរៀនពី Sidebar តាមឈ្មោះ ឬពាក្យគន្លឹះខាងក្នុង (ឧ. "lambda", "class")
- **Settings**: ប្តូរ Theme **Dark/Light** និង Font size 80% ដល់ 150% ដំណើរការភ្លាមៗ មិនបាច់ restart
- **Clear Chat + Undo**: លុប conversation ចោល ហើយអាច Undo វិញបានក្នុង 10 វិនាទី
- **Keyboard Shortcuts**: `Ctrl+K`, `Esc`, `Ctrl+L`, `Ctrl+,`, `Ctrl+F`
- **100% Offline**: Rule-based AI ដំណើរការក្នុងម៉ាស៊ីនទាំងស្រុង គ្មាន Internet គ្មាន API key ហើយលឿន

---

## 💬 Chat Commands

| Command | មុខងារ |
|---|---|
| `/start` | បង្ហាញម៉ឺនុយពេញ និងបញ្ជីមេរៀនទាំង 11 |
| ឈ្មោះមេរៀន ឬពាក្យគន្លឹះ | បើកមេរៀន (ឧ. `loop`, `Basic Python`, `what is a class`) |
| `/quiz list` | បង្ហាញបញ្ជី Quiz តាមមេរៀន (`/quiz` តែឯងក៏បាន) |
| `/quiz 5` ឬ `/quiz loop` | ចាប់ផ្តើម Quiz មេរៀនទី 5 (5 សំណួរ) |
| `A` `B` `C` `D` | ឆ្លើយសំណួរ Quiz |
| `/stop` | បញ្ឈប់ Quiz ពាក់កណ្តាល |
| `/progress` | មើលកាតវឌ្ឍនភាពការសិក្សា |

---

## 📚 Lessons & Quiz

| លេខ | មេរៀន | ខ្លឹមសារ |
|---|---|---|
| `1` | 🔰 Basic Python | comment, indentation, `print()`, case-sensitive |
| `2` | 📦 Variables & Data Types | `int`, `float`, `str`, `bool`, type conversion |
| `3` | 🔢 Operators | arithmetic, comparison, logical |
| `4` | 🔀 Conditional | `if` / `elif` / `else` |
| `5` | 🔁 Loop | `for` / `while`, `range()`, `break`, `continue` |
| `6` | 📋 Array | list: `append`, `pop`, index, slice |
| `7` | ⚙️ Function | `def`, `return`, parameters |
| `8` | 🗂 Data Structures | tuple, set, dictionary |
| `9` | 🔧 Functions Advanced | `*args`, `**kwargs`, `lambda`, `map()` |
| `10` | 📁 File Handling | `open()`, read/write/append, `with` |
| `11` | 🏛 OOP | class, object, `__init__`, inheritance |

មេរៀនណាដែលបានមើលរួច នឹងត្រូវកត់ត្រាក្នុង Progress ដោយស្វ័យប្រវត្តិ (រក្សាទុកក្នុងម៉ាស៊ីន គ្មាន account)។

---

## 🛠 Fix Code Mode

**Fix Code Mode** ជួយរកកំហុសក្នុងកូដ Python ពន្យល់ថាខុសត្រង់ណា និងកែឲ្យដោយស្វ័យប្រវត្តិ។ App វិភាគកូដតែប៉ុណ្ណោះ មិនដំណើរការ (run) កូដរបស់អ្នកពិតប្រាកដទេ ដូច្នេះមានសុវត្ថិភាព និងដំណើរការ Offline។

### របៀបប្រើ

1. ចុច **🛠 Fix Code** នៅផ្នែក MODE ក្នុង Sidebar
2. Paste កូដ Python ចូលប្រអប់វាយអក្សរ (`Shift+Enter` = ចុះបន្ទាត់ថ្មី)
3. ចុច **Send** ឬ `Enter`

### 📋 ចម្លើយមាន 3 ផ្នែក

| ផ្នែក | អ្វីដែលបង្ហាញ |
|---|---|
| 🔍 **Error ដែលរកឃើញ** | បញ្ជីកំហុសនីមួយៗ៖ លេខបន្ទាត់ (Line), មូលហេតុ និងវិធីកែ (⚙️) |
| ✅ **Fixed Code** | កូដដែលកែរួច អាចចុច Copy យកទៅប្រើបានភ្លាម |
| 📤 **Output** | លទ្ធផលដែល `print()` នឹងបង្ហាញ (`?` = គណនាមិនបាន) |

### ឧទាហរណ៍

កូដដែល Paste ចូល (មានកំហុស 5)៖

```python
name = "Dara"
if name = "Dara"
    Print("Hi {name}");
```

App ឆ្លើយតប៖

```text
🔍 Error ដែលរកឃើញ (5):
  1. Line 3: 'Print' ខុស case → ត្រូវជា 'print'
  2. Line 3: ';' នៅចុងបន្ទាត់ : Python មិនប្រើ ';'
  3. Line 3: String មាន {...} ប៉ុន្តែភ្លេច 'f' prefix
  4. Line 2: 'if' statement គ្មាន ':' នៅចុង
  5. Line 2: ប្រើ '=' ក្នុង condition : ប្រហែលជាចង់ប្រើ '=='

✅ Fixed Code:
name = "Dara"
if name == "Dara":
    print(f"Hi {name}")

📤 Output:
Hi Dara
```

### 🧩 កំហុស 19 ប្រភេទដែល App ស្គាល់

| # | កំហុស | ខុស | ត្រូវ |
|---|---|---|---|
| 1 | `:` បាត់ក្រោយ `if` `elif` `else` `for` `while` `def` `class` | `if x > 5` | `if x > 5:` |
| 2 | សញ្ញា `;` នៅចុងបន្ទាត់ | `print("Hi");` | `print("Hi")` |
| 3 | Quote ឬ វង់ក្រចក មិនបានបិទ | `print("Hi"` | `print("Hi")` |
| 4 | Indentation ខុស (លាយ Tab និង Space) | Tab + Space | 4 spaces |
| 5 | Typo នៃ `print` | `printf(` `Printtf(` | `print(` |
| 6 | អក្សរធំ/តូចខុស | `Print()` `PRINT()` | `print()` |
| 7 | Keyword សរសេរខុស | `retrun` `improt` `ture` | `return` `import` `True` |
| 8 | `else if` | `else if x:` | `elif x:` |
| 9 | f-string ភ្លេច `f` | `"Hi {name}"` | `f"Hi {name}"` |
| 10 | `=` ក្នុង condition | `if x = 5:` | `if x == 5:` |
| 11 | Comparison operator ខុស | `=<` `=>` `<>` | `<=` `>=` `!=` |
| 12 | `++` / `--` មិនមានក្នុង Python | `x++` | `x += 1` |
| 13 | Python 2 print statement | `print "Hi"` | `print("Hi")` |
| 14 | Python 2 `raw_input()` | `raw_input()` | `input()` |
| 15 | Mutable default argument | `def f(x=[]):` | ព្រមាន : ប្រើ `x=None` |
| 16 | Variable មិនទាន់ define | `print(y)` | ព្រមាន : បង្កើត `y` ជាមុន |
| 17 | Off-by-one ក្នុង loop | `range(len(x) + 1)` | ព្រមាន : `range(len(x))` |
| 18 | `is` ជាមួយតម្លៃ | `if x is 5:` | ព្រមាន : `if x == 5:` |
| 19 | ប៉ាន់ស្មាន Output | `print(2 + 3)` | 📤 Output : `5` |

**ព្រមាន** = App ប្រាប់ឲ្យពិនិត្យ ប៉ុន្តែមិនកែកូដឲ្យទេ ព្រោះអាស្រ័យលើគោលបំណងរបស់អ្នក។

---

## ⌨️ Keyboard Shortcuts

| Key | មុខងារ |
|---|---|
| `Ctrl+K` | Focus ទៅ input box |
| `Esc` | លុបអក្សរដែលកំពុងវាយក្នុង input |
| `Ctrl+L` | Clear Chat |
| `Ctrl+,` | បើក Settings |
| `Ctrl+F` | Focus ទៅ Search topics |

---

## 📁 Project Structure

```
nexus-ai-assistant/
├── FixCode/
│   └── fix_code_engine.py    → រកកំហុស និងកែកូដ (regex + AST)
├── LessonCodePython/
│   ├── lesson_engine.py      → ផ្គូផ្គងមេរៀន, Quiz, Progress, Report
│   ├── lessons.json          → ខ្លឹមសារមេរៀនទាំង 11
│   ├── quizzes.json          → សំណួរ Quiz (5 សំណួរ/មេរៀន)
│   ├── settings_manager.py   → រក្សាទុក Theme/Font settings
│   ├── theme.py              → ពណ៌ Dark/Light និង Font
│   └── version.py            → App version
├── ui/
│   ├── main_window.py        → បង្អួចមេ + Keyboard shortcuts
│   ├── sidebar.py            → ម៉ឺនុយឆ្វេង + Search topics
│   ├── chat_panel.py         → ផ្ទាំង Chat (background thread)
│   ├── message_bubble.py     → Bubble សារ + Code block
│   ├── input_bar.py          → ប្រអប់វាយអក្សរ
│   ├── report_pdf.py         → Export Report ជា PDF
│   ├── settings_dialog.py    → Settings dialog
│   ├── about_dialog.py       → About dialog
│   ├── icons.py              → Python logo icon
│   └── avatars.py            → រូបតំណាង
├── assets/                   → Python logo (.png, .ico, .icns)
├── tests/
│   ├── test_fix_code_engine.py
│   ├── test_lesson_engine.py
│   ├── test_report.py
│   └── test_settings_manager.py
├── main.py                   → entry point
├── nexus_ai.spec             → PyInstaller build config
├── requirements.txt
├── requirements-dev.txt
├── CHANGELOG.md
├── LICENSE
└── README.md
```

---

## 🚀 How to Run

1. Clone Repository :

   ```bash
   git clone <url-repo> nexus-ai-assistant
   cd nexus-ai-assistant
   ```

2. Install Dependencies :

   ```bash
   pip install -r requirements.txt
   ```

3. Run App :

   ```bash
   python main.py
   ```

   វាយ `/start` ដើម្បីមើលម៉ឺនុយ ឬជ្រើសមេរៀនពី Sidebar ហើយប្តូរទៅ **Fix Code** mode ដើម្បីកែកូដ

4. ដើម្បី Run Tests :

   ```bash
   pip install -r requirements-dev.txt
   pytest -v
   pytest --cov --cov-report=term-missing   # + coverage report
   ```

5. Build ជា Standalone App (មិនបាច់ដំឡើង Python) :

   ```bash
   pip install -r requirements-dev.txt
   pyinstaller nexus_ai.spec
   ```

   | Platform | Output |
   |---|---|
   | Windows | `dist/NexusAI.exe` |
   | macOS | `dist/NexusAI.app` |
   | Linux | `dist/NexusAI` |

---

## 📄 License

**MIT License :** អ្នកអាចប្រើ ចម្លង កែប្រែ និងចែកចាយកូដនេះដោយសេរី ឲ្យតែរក្សាទុកសេចក្តីជូនដំណឹង Copyright។ មើលព័ត៌មានលម្អិតក្នុងឯកសារ [LICENSE](LICENSE)។ ការផ្លាស់ប្តូរតាម version មើលនៅ [CHANGELOG.md](CHANGELOG.md)។

---

## 👤 Author

**Built with ❤️ and code by Mr. Siev E**
