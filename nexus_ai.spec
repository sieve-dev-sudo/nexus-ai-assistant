# nexus_ai.spec
# Build a standalone executable with:  pyinstaller nexus_ai.spec
# Works unmodified on Windows, macOS, and Linux — the icon format and
# (on macOS) the .app bundle step are chosen automatically below based
# on sys.platform, since .spec files are plain Python executed by
# PyInstaller itself.
#
# Bundles the JSON lesson/quiz data and the Python logo PNG as data
# files, at the same relative paths the code already expects via
# Path(__file__).resolve().parent — so no code changes were needed.

import sys

block_cipher = None

if sys.platform == "darwin":
    ICON_PATH = "assets/python_logo.icns"
elif sys.platform == "win32":
    ICON_PATH = "assets/python_logo.ico"
else:  # Linux and everything else — PyInstaller ignores `icon` here
    ICON_PATH = None  # anyway; see the .desktop file note in README

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('LessonCodePython/lessons.json', 'LessonCodePython'),
        ('LessonCodePython/quizzes.json', 'LessonCodePython'),
        ('assets/python_logo.png', 'assets'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NexusAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # no terminal window on launch
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH,
)

# macOS only: wrap the executable in a proper double-clickable .app
# bundle with its own Info.plist (name, version, bundle identifier).
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name='NexusAI.app',
        icon=ICON_PATH,
        bundle_identifier='com.sievdevkhmer.nexusai',
        info_plist={
            'CFBundleName': 'Nexus AI',
            'CFBundleDisplayName': 'Nexus AI — Python Assistant',
            'CFBundleShortVersionString': '1.1.0',
            'NSHighResolutionCapable': True,
        },
    )

