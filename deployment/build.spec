# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../src', 'src')
    ],
    hiddenimports=[
        'sqlalchemy.sql.default_comparator',
        'reportlab',
        'reportlab.graphics.barcode',
        'reportlab.pdfbase',
        'reportlab.pdfgen',
        'PIL',
        'escpos',
        'usb',
        'sqlite3',
        'PyQt6',
        'pandas',
        'openpyxl'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FerreteriaERP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True if you want to see the console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None # You can add an icon here later: icon='../assets/icon.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FerreteriaERP',
)
