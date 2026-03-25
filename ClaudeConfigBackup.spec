# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\CodeSpace\\claudeFi\\src\\main.py'],
    pathex=['D:\\CodeSpace\\claudeFi\\src'],
    binaries=[],
    datas=[('D:\\CodeSpace\\claudeFi\\config', 'config')],
    hiddenimports=['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.QtGui', 'app', 'gui', 'gui.main_window', 'gui.tabs', 'gui.tabs.backup_tab', 'gui.tabs.restore_tab', 'gui.tabs.history_tab', 'gui.tabs.settings_tab', 'gui.dialogs', 'gui.dialogs.login_dialog', 'gui.dialogs.preview_dialog', 'gui.widgets', 'gui.widgets.status_bar', 'gui.widgets.module_list', 'gui.widgets.sidebar', 'gui.styles', 'core', 'core.backup_manager', 'core.restore_manager', 'core.module_loader', 'core.exceptions', 'auth', 'auth.github_oauth', 'auth.token_manager', 'storage', 'storage.github_storage', 'storage.ssh_storage', 'storage.cloud_storage', 'storage.base', 'security', 'security.crypto', 'security.sensitive_filter', 'database', 'database.mysql_client', 'database.sqlite_cache', 'utils', 'utils.logger', 'utils.config', 'github', 'pymysql', 'cryptography', 'yaml', 'requests', 'paramiko'],
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
    icon=['D:\\CodeSpace\\claudeFi\\assets\\icon.ico'],
)
