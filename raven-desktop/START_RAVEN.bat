@echo off
cd /d "%~dp0"

if not exist "electron\node_modules" (
    echo Installing Electron for first time, please wait...
    cd electron
    npm install
    cd ..
)

cd electron
start "" /B npx electron .
