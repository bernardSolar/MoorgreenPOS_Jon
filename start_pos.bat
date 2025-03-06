@echo off
echo Checking for existing MoorGreen POS instance...

REM Check if the process is already running
tasklist /FI "WINDOWTITLE eq MoorGreen POS*" 2>NUL | find /I /N "cmd.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo MoorGreen POS is already running!
    echo Please use the existing window or close it first.
    pause
    exit
)

REM If not running, start it with a specific window title
title MoorGreen POS
echo Starting MoorGreen POS System...
start /B MoorGreen_POS.exe