@echo off
setlocal

cd /d "C:\Users\Falec\OneDrive\Documentos\Python\BlueSentinel_SOC"

if not exist "logs" mkdir "logs"

set "LAUNCHER_LOG=logs\launcher.log"
set "VENV_PYTHON=C:\Users\Falec\OneDrive\Documentos\Python\BlueSentinel_SOC\venv\Scripts\python.exe"

>> "%LAUNCHER_LOG%" echo ============================================================
>> "%LAUNCHER_LOG%" echo [%date% %time%] STARTING BlueSentinel SOC
>> "%LAUNCHER_LOG%" echo [%date% %time%] LAUNCHER v5.0
>> "%LAUNCHER_LOG%" echo Working directory: %cd%

if not exist "%VENV_PYTHON%" (
    >> "%LAUNCHER_LOG%" echo [%date% %time%] ERROR: python executable not found: %VENV_PYTHON%
    >> "%LAUNCHER_LOG%" echo ============================================================
    >> "%LAUNCHER_LOG%" echo.
    exit /b 1
)

>> "%LAUNCHER_LOG%" echo Python: %VENV_PYTHON%

for /f "delims=" %%i in ('"%VENV_PYTHON%" --version 2^>^&1') do (
    >> "%LAUNCHER_LOG%" echo Python version: %%i
)

>> "%LAUNCHER_LOG%" echo [%date% %time%] BEFORE PYTHON EXECUTION

"%VENV_PYTHON%" -m modules.scheduler.scheduler
set "EXIT_CODE=%ERRORLEVEL%"

>> "%LAUNCHER_LOG%" echo [%date% %time%] AFTER PYTHON EXECUTION ^| exit_code=%EXIT_CODE%
>> "%LAUNCHER_LOG%" echo [%date% %time%] FINISHED BlueSentinel SOC ^| exit_code=%EXIT_CODE%
>> "%LAUNCHER_LOG%" echo ============================================================
>> "%LAUNCHER_LOG%" echo.

exit /b %EXIT_CODE%