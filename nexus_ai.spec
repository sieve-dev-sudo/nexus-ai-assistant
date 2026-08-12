# nexus_ai.spec
# Build a standalone executable with:  pyinstaller nexus_ai.spec
#
# Bundles the JSON lesson/quiz data and the Python logo PNG as data
# files, at the same relative paths the code already expects via
# Path(__file__).resolve().parent — so no code changes were needed.

block_cipher = None

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
    icon='assets/python_logo.ico',
)
