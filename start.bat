@echo off
REM Serverni ishga tushirish — venv'ni o'zi topadi.
REM Ishlatish: start.bat  (yoki faylni ikki marta bosing)

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo venv topilmadi. Avval quyidagini bajaring:
    echo    python -m venv venv
    echo    venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo Server ishga tushmoqda...  http://127.0.0.1:8000/
echo Toxtatish: CTRL+C
echo.
venv\Scripts\python.exe manage.py runserver
pause
