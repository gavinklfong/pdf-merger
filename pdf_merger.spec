# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all PyQt6 data files and hidden imports
pyqt6_data = collect_data_files('PyQt6')
pyqt6_submodules = collect_submodules('PyQt6')

# Collect PyPDF2 hidden imports if needed
pypdf2_submodules = collect_submodules('PyPDF2')

block_cipher = None

a = Analysis(
    ['pdf_merger.py'],        # your main script
    pathex=[],
    binaries=[],
    datas=pyqt6_data,
    hiddenimports=pyqt6_submodules + pypdf2_submodules,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PDFMerger',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,        # False hides console window
    icon='app_icon.ico'   # optional: your .ico file
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PDFMerger'
)
