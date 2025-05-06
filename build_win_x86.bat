@echo off
echo Building QR2Key (x86)
echo =====================

REM Create and activate virtual environment
python -m venv venv-x86
call venv-x86\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt
pip install -r requirements-win.txt
pip install pyinstaller

REM Build with PyInstaller
pyinstaller --clean ^
    --add-data "README.md;." ^
    --onefile ^
    --icon=NONE ^
    --name QR2Key-x86 ^
    --target-architecture x86 ^
    qr2key/main.py

echo Build completed, executable should be in dist/QR2Key-x86.exe
pause
