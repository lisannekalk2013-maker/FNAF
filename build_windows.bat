@echo off
setlocal
cd /d "%~dp0"
set "FNAF_PYTHON="
py -3.13 -c "import sys; sys.exit(sys.version_info[:2] != (3,13))" >nul 2>&1
if not errorlevel 1 goto use_launcher
python -c "import sys; sys.exit(sys.version_info[:2] != (3,13))" >nul 2>&1
if errorlevel 1 goto python_missing
set "FNAF_PYTHON=python"
goto prepare
:use_launcher
set "FNAF_PYTHON=py -3.13"
:prepare
if exist .venv-windows\Scripts\python.exe goto check_venv
%FNAF_PYTHON% -m venv .venv-windows
if errorlevel 1 goto failed
:check_venv
.venv-windows\Scripts\python.exe -c "import sys; sys.exit(sys.version_info[:2] != (3,13))"
if errorlevel 1 goto wrong_venv
.venv-windows\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto failed
.venv-windows\Scripts\python.exe -m pytest -q
if errorlevel 1 goto failed
.venv-windows\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --onedir --name FNAFDesktop --add-data "assets;assets" --add-data "settings.json;." --add-data "config.json;." --hidden-import comtypes.client run.py
if errorlevel 1 goto failed
.venv-windows\Scripts\python.exe tools\package_windows.py
if errorlevel 1 goto failed
echo.
echo ZIP: dist\FNAFDesktop-V3.0-Windows.zip
echo Gereed: dist\FNAFDesktop\FNAFDesktop.exe
echo Bewaar de hele map FNAFDesktop, inclusief _internal.
if /i not "%~1"=="--ci" pause
exit /b 0
:python_missing
echo Python 3.13 is niet gevonden. Installeer Python 3.13 64-bit met de Python Launcher of voeg Python toe aan PATH.
goto failed
:wrong_venv
echo .venv-windows gebruikt niet Python 3.13. Hernoem deze map en probeer opnieuw.
:failed
echo.
echo Bouwen mislukt. Lees de foutmelding hierboven.
if /i not "%~1"=="--ci" pause
exit /b 1
