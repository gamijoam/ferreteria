
import os
import shutil
import subprocess
import sys

# Get the directory of this script
base_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(base_dir)
spec_file = os.path.join(base_dir, 'build.spec')
launcher_script = os.path.join(project_root, 'src', 'launcher.py')
version_file = os.path.join(project_root, 'landing_page', 'version.json')
dist_dir = os.path.join(base_dir, 'dist')
build_dir = os.path.join(base_dir, 'build')

# Helper to run commands
def run_command(cmd_list, description):
    print(f"\n=== {description} ===")
    try:
        # Use python -m PyInstaller to ensure we use the same python env
        full_cmd = [sys.executable, '-m', 'PyInstaller'] + cmd_list
        subprocess.check_call(full_cmd)
        print("✅ Completado.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        sys.exit(1)

# 1. Main App
run_command([
    spec_file,
    '--distpath', dist_dir,
    '--workpath', build_dir,
    '--noconfirm',
    '--clean'
], "Construyendo Aplicación Principal (FerreteriaApp)")

# 2. Launcher
run_command([
    launcher_script,
    '--name', 'Launcher',
    '--onefile',
    '--noconsole',
    '--distpath', dist_dir,
    '--workpath', build_dir,
    '--icon', os.path.join(base_dir, 'assets', 'icon.ico'),
    '--hidden-import', 'tkinter',
    '--hidden-import', 'PIL.ImageTk', 
    '--noconfirm'
], "Construyendo Launcher (Actualizador)")


print("\n=== 3. Finalizando Configuración ===")

# Copiar version.json a la raíz de la distribución (junto al Launcher)
if os.path.exists(version_file):
    shutil.copy(version_file, dist_dir)
    print(f"Copiado: version.json -> {dist_dir}")

# Renombrar Launcher.exe a algo más amigable si se desea, ej 'Ferreteria_Start.exe'
# O dejar como Launcher.exe

print("\n=== CONSTRUCCIÓN COMPLETADA EXITOSAMENTE ===")
print(f"Ubicación: {dist_dir}")
print("Archivos clave:")
print(f"  - [Ejecutable Usuario]: {os.path.join(dist_dir, 'Launcher.exe')}")
print(f"  - [Sistema Interno]:    {os.path.join(dist_dir, 'InventarioSoft', 'InventarioSoft.exe')}")
print(f"  - [Config Versión]:     {os.path.join(dist_dir, 'version.json')}")
