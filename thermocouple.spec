# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['TE.py'],
    pathex=['D:\\C++'],
    binaries=[],
    datas=[('thermocouple_data.json', '.')],
    hiddenimports=[
        'tkinter',
        'json',
        'pathlib',
        'typing',
        '_tkinter',
        'tkinter.ttk'
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HotCouple',  # 使用不同的名称避免冲突
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
