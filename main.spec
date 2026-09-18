# -*- mode: python ; coding: utf-8 -*-

import os
import shutil
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

# Exit out if SPECPATH is under 10 characters under the assumption that something has gone wrong
if len(SPECPATH) < 10:
    print("[OoTMM ER Plotter] SPECPATH was less than 10 characters long, suggesting some sort of problem. Aborting rest of deployment to protect your file system. Value of SPECPATH is: '" + SPECPATH + "'")
    print("If you wish to build this project near your filesystem root, edit main.spec to remove this check.")
    exit()


######################################################
# get gravis files for embedding in the executable
datas = collect_data_files("gravis")

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
    name='OoTMM-ER-Plotter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Our main directories
project_dir = Path(SPECPATH)
dist_dir = project_dir / 'dist'

# Copy "ootmm" folder to be immediately accessible by the .exe
print("[OoTMM ER Plotter] Custom main.spec action: copying './ootmm/' folder to './dist/ootmm")
shutil.copytree(project_dir / 'ootmm', dist_dir / 'ootmm', dirs_exist_ok=True)

# Copy default config files to './dist/'
print("[OoTMM ER Plotter] Custom main.spec action: copying default config files to dist/ folder")
copyFiles = ["config.yml", "config-bigger-er.yml"]
for file in copyFiles:
    shutil.copyfile(project_dir / file, dist_dir / file)
