import PyInstaller.__main__
import os

# Get the directory of this script
base_dir = os.path.dirname(os.path.abspath(__file__))
spec_file = os.path.join(base_dir, 'build.spec')

print("Iniciando construcción del ejecutable...")
print(f"Usando especificación: {spec_file}")

PyInstaller.__main__.run([
    spec_file,
    '--distpath', os.path.join(base_dir, 'dist'),
    '--workpath', os.path.join(base_dir, 'build'),
    '--noconfirm',
    '--clean'
])

print("\nConstrucción finalizada.")
print(f"El ejecutable se encuentra en: {os.path.join(base_dir, 'dist', 'InventarioSoft')}")
