@echo off
echo Installing middleMDM service...
cd /d "%~dp0"
set "AGENT=%~dp0middlemdm-agent-windows-x64.exe"
if exist "%AGENT%" (
    "%AGENT%" --service install
    "%AGENT%" --service start
) else (
    python "%~dp0middlemdm.py" --service install
    python "%~dp0middlemdm.py" --service start
)
echo Service installed and started.
pause
