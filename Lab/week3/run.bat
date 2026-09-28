@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

set "PYTHON_EXE=%~dp0..\..\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

"%PYTHON_EXE%" -c "import matplotlib" >nul 2>&1
if errorlevel 1 (
    echo Matplotlib is not available. Run: pip install -r requirements.txt
    exit /b 1
)

"%PYTHON_EXE%" "%~dp0src\text_styles.py"
exit /b %errorlevel%
