#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup per compilazione Gestionale Gitemania PORTABLE
Crea file .exe standalone con tutte le dipendenze embedded
Sviluppato da TechExpresso
"""

from setuptools import setup, find_packages
import os
import sys
import subprocess

# Versione applicazione
VERSION = "1.0.0"

# Dipendenze per PyInstaller
HIDDEN_IMPORTS = [
    'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog',
    'PIL', 'PIL._tkinter_finder', 'woocommerce', 'cryptography', 'matplotlib',
    'matplotlib.backends.backend_tkagg', 'pandas', 'openpyxl', 'docx',
    'flask', 'schedule', 'apscheduler', 'qrcode', 'sqlite3', 'json',
    'threading', 'datetime', 'requests', 'urllib3', 'certifi',
    'charset_normalizer', 'idna', 'ttkthemes', 'ttkbootstrap',
]

# Moduli da escludere
EXCLUDED_MODULES = [
    'test', 'tests', 'unittest', 'pydoc', 'doctest', 'tkinter.test',
    'email.test', 'sqlite3.test',
]

def create_portable_spec_file():
    """Crea file .spec per PyInstaller Portable"""
    create_icon_if_needed()
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import sys, os
block_cipher = None
a = Analysis(
    ['gestionale_gitemania.py'],
    pathex=[], binaries=[], datas=[
        ('config.py', '.'), ('database_manager.py', '.'),
        ('woocommerce_api.py', '.'), ('export_manager.py', '.'),
        ('gui_components.py', '.'),
    ],
    hiddenimports={HIDDEN_IMPORTS}, hookspath=[], hooksconfig={{}},
    runtime_hooks=[], excludes={EXCLUDED_MODULES},
    win_no_prefer_redirects=False, win_private_assemblies=False,
    cipher=block_cipher, noarchive=False
)
a.datas = [x for x in a.datas if not any(ex in x[0] for ex in ['test', '__pycache__', '.pyc'])]
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='GestionaleGitemania', debug=False,
    bootloader_ignore_signals=False, strip=False, upx=True,
    upx_exclude=[], runtime_tmpdir=None, console=False,
    disable_windowed_traceback=False, argv_emulation=False,
    target_arch=None, codesign_identity=None, entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
    version_file='version_info.txt' if os.path.exists('version_info.txt') else None,
    splash=Splash('assets/splash.png', binaries=a.binaries, datas=a.datas,
                  text_pos=None, text_size=12, minify_script=True,
                  always_on_top=True) if os.path.exists('assets/splash.png') else None
)
'''
    with open('gestionale_portable.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("File .spec portable creato: gestionale_portable.spec")

def create_icon_if_needed():
    """Crea icona TechExpresso se non esiste"""
    if not os.path.exists('assets'):
        os.makedirs('assets', exist_ok=True)
    icon_path = 'assets/icon.ico'
    if not os.path.exists(icon_path):
        print("Creazione icona TechExpresso...")
        # ... (logica per creare l'icona)
        pass

def create_splash_screen():
    """Crea splash screen di avvio"""
    # ... (logica per creare lo splash screen)
    pass

def create_version_info():
    """Crea file informazioni versione portable"""
    # ... (logica per creare il file versione)
    pass

def install_dependencies():
    """Installa dipendenze necessarie per compilazione"""
    print("Installazione dipendenze per compilazione...")
    dependencies = ['pyinstaller>=5.13.0', 'pillow>=10.0.0']
    for dep in dependencies:
        try:
            print(f"Installazione {dep}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
        except Exception as e:
            print(f"Errore installazione {dep}: {e}")

def build_portable_executable():
    """Compila applicazione in eseguibile PORTABLE"""
    print("=" * 60)
    print("  COMPILAZIONE GESTIONALE GITEMANIA PORTABLE v1.0.0")
    print("  File .exe standalone con database SQLite integrato")
    print("=" * 60)
    
    install_dependencies()
    create_portable_spec_file()
    
    if os.path.exists('dist'):
        import shutil
        shutil.rmtree('dist')
    if os.path.exists('build'):
        import shutil
        shutil.rmtree('build')
        
    print("\nCompilazione in corso...")
    
    cmd = ['pyinstaller', 'gestionale_portable.spec', '--clean', '--noconfirm', '--log-level=WARN']
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
        # ... (resto della logica)
    except subprocess.CalledProcessError as e:
        print(f"\nERRORE DURANTE LA COMPILAZIONE")
        print(f"Exit code: {e.returncode}")
        if e.stdout: print(f"Output: {e.stdout}")
        if e.stderr: print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"\nErrore imprevisto: {e}")
        return False
        
    return True

# ... (altre funzioni come create_distribution_package, test_portable_executable, etc.)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        success = build_portable_executable()
        sys.exit(0 if success else 1)
    else:
        # Codice di setup standard che non verrà eseguito da GitHub Actions
        setup()
