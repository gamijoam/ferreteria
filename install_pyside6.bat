@echo off
echo ========================================
echo  PySide6 Installation Script
echo ========================================
echo.
echo This script will install PySide6 and PySide6-Addons
echo.
echo Attempting installation...
echo.

pip install --upgrade pip
pip install PySide6 PySide6-Addons

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo  Installation failed with SSL error
    echo ========================================
    echo.
    echo Trying alternative method...
    echo.
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org PySide6 PySide6-Addons
)

echo.
echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo You can now run the application with:
echo   python src/main_qml.py
echo.
pause
