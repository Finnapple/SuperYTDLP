@echo off
chcp 65001 >nul

echo.
echo [*] Creating Python virtual environment...
python -m venv ytdlp
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    echo Please make sure Python is installed
    pause
    exit /b 1
)

echo [*] Activating virtual environment...
call ytdlp\Scripts\activate.bat

echo [*] Upgrading pip...
python -m pip install --upgrade pip

echo [*] Installing requirements...
pip install -r requirements.txt

echo.
echo [SUCCESS] Setup completed!
echo.
echo To activate the virtual environment, run:
echo ytdlp\Scripts\activate.bat
echo.

pause