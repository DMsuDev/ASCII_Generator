@echo off
:: Cambia "venv" por el nombre de tu carpeta si es diferente
if not exist ".venv\Scripts\Activate.ps1" (
    echo ERROR: No se encuentra el entorno virtual en .\venv\
    echo.
    pause
    exit /b 1
)

:: Esta es la forma más fiable de activar el entorno desde .bat
call ".venv\Scripts\activate.bat"