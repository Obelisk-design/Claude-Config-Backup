# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\CodeSpace\\claudeFi\\src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\CodeSpace\\claudeFi\\config', 'config')],
    hiddenimports=['PyQt5.sip', 'PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.QtGui', 'PyQt5.QtSvg', 'github', 'pymysql', 'cryptography', 'yaml', 'requests', 'paramiko'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ClaudeConfigBackup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
