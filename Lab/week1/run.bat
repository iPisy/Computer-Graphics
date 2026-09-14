@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

set "PYTHON_EXE=%~dp0..\..\.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    where python >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python was not found.
        echo Install Python or create the project virtual environment first.
        goto :error
    )
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Pillow is not installed for the selected Python interpreter.
    echo Run: "%PYTHON_EXE%" -m pip install -r "%~dp0requirements.txt"
    goto :error
)

echo [1/2] Running circle.py ...
echo Close the Circle window to continue.
"%PYTHON_EXE%" "%~dp0src\circle.py"
if errorlevel 1 goto :error

echo.
echo [2/2] Running koch_curve.py ...
echo Close the Koch Snowflake window to finish.
"%PYTHON_EXE%" "%~dp0src\koch_curve.py"
if errorlevel 1 goto :error

echo.
echo Finished. Images were saved in "%~dp0docs\images".
pause
exit /b 0

:error
echo.
echo Lab1 did not finish successfully. Review the error message above.
pause
exit /b 1
