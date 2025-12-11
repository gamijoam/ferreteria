@echo off
echo ========================================
echo  POS Ultra - PySide6 + QML Version
echo ========================================
echo.

cd /d "%~dp0"
python src\main_qml.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo  Error al ejecutar la aplicacion
    echo ========================================
    echo.
    echo Verifica que PySide6 este instalado:
    echo   install_pyside6.bat
    echo.
    pause
)
