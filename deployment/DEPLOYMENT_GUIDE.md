# Guía de Despliegue - Ferretería ERP

Esta guía explica cómo generar el ejecutable (.exe) para instalar el sistema en la computadora del cliente.

## Requisitos Previos

Asegúrate de tener instalada la librería `pyinstaller`:

```bash
pip install pyinstaller
```

## Generar el Ejecutable

Hemos preparado un archivo de configuración (`deployment/build.spec`) para facilitar este proceso.

1. Abre una terminal en la carpeta raíz del proyecto (`ferreteria`).
2. Ejecuta el siguiente comando:

```bash
pyinstaller deployment/build.spec
```

O simplemente ejecuta el script de ayuda (si lo has creado):

```bash
python deployment/build_exe.py
```

## Resultado

Una vez finalizado el proceso, encontrarás dos carpetas nuevas en `deployment/dist`:

- `deployment/dist/FerreteriaERP/`: Contiene el ejecutable y todos los archivos necesarios.

## Instalación en el Cliente

1. **Copiar Archivos:**
   Copia la carpeta completa `FerreteriaERP` (ubicada en `deployment/dist/`) a la computadora del cliente (ej. en `C:\FerreteriaERP`).

2. **Base de Datos:**
   - El sistema buscará automáticamente un archivo `ferreteria.db` dentro de la carpeta del programa.
   - Si es una instalación nueva, el sistema creará una base de datos vacía al iniciar.
   - Si quieres migrar datos, copia tu archivo `ferreteria.db` local a la carpeta del cliente.

3. **Configuración (.env):**
   - El sistema ya no depende estrictamente del archivo `.env` para la base de datos (usa SQLite por defecto).
   - Sin embargo, si necesitas configuraciones especiales, puedes crear un archivo `.env` en la misma carpeta del ejecutable.

4. **Crear Acceso Directo:**
   - Haz clic derecho en `FerreteriaERP.exe` -> "Enviar a" -> "Escritorio (crear acceso directo)".

## Solución de Problemas

- **Error de "No module named..."**: Si al abrir el exe falta alguna librería, agrégala a la lista `hiddenimports` en `deployment/build.spec` y vuelve a generar el exe.
- **Imágenes/Logos no cargan**: Asegúrate de que las rutas de las imágenes sean accesibles o estén configuradas correctamente en el sistema.
