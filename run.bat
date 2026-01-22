@echo off
:: This is for not showing the command of the batch file

:: start → Open a new window to run a specified program or command
:: cmd /k → Carries out the command specified by string but remains
:: ^&^ → allows the command to continue on multiple lines (more readable)
:: cd /d "%~dp0" → Change directory to the location of this batch file

start "My Python Application" cmd /k ^
    cd /d "%~dp0" ^&^
    python src/app.py ^&^
    echo. ^&^
    python test/clean.py ^&^
    echo Press any key to exit... ^&^
    pause