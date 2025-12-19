@echo off
TITLE Sistema de Ferreteria - Debug Mode
echo ===================================================
echo   DEBUG LAUNCHER
echo ===================================================
echo.
echo Este script mantiene la consola abierta para ver errores.
echo.

python Launcher.pyw

echo.
echo ===================================================
echo   EL PROGRAMA SE HA CERRADO
echo ===================================================
echo.
if exist "%TEMP%\ferreteria_launcher.log" (
    echo CONTENIDO DEL LOG (%TEMP%\ferreteria_launcher.log):
    echo ---------------------------------------------------
    type "%TEMP%\ferreteria_launcher.log"
    echo ---------------------------------------------------
)
echo.
pause
