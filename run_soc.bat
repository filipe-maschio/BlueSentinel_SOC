@echo off

cd /d "C:\Users\Falec\OneDrive\Documentos\Python\BlueSentinel_SOC"

echo. >> logs\execution.log
echo ============================================================ >> logs\execution.log
for /f "tokens=1-3 delims=:," %%a in ("%time%") do (
    echo [%date% %%a:%%b:%%c] STARTING BlueSentinel SOC >> logs\execution.log
)
echo ============================================================ >> logs\execution.log

call venv\Scripts\activate

python -m modules.scheduler.scheduler

for /f "tokens=1-3 delims=:," %%a in ("%time%") do (
    echo [%date% %%a:%%b:%%c] FINISHED BlueSentinel SOC >> logs\execution.log
)
echo ============================================================ >> logs\execution.log
echo. >> logs\execution.log

exit