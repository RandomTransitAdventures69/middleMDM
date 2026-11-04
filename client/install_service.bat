@echo off
echo Installing middleMDM service...
cd /d "%~dp0"
python middlemdm.py --service install
python middlemdm.py --service start
echo Service installed and started.
pause
