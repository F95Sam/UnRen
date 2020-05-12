1>2# : ^
"""
@echo off
setlocal enabledelayedexpansion

echo Here is much space for endless speeches
echo Or not...





set version=version=0.12.0-alpha
title "UnRen for Windows v%version%"
mode con: cols=90 lines=50

REM path check
REM --------------------------------------------------------------------------------
:path_check
REM lets assume the ideal (script sits in the games base-dir)
set base_pth=%~dp0

if exist "game" if exist "lib" if exist "renpy" (
	goto :py_check
)
REM or if one below we shorten the path
if exist "..\game" if exist "..\lib" if exist "..\renpy" (
    for %%X in ("%base_pth:~0,-1%") do set base_pth=%%~dpX
	goto :py_check
)

echo    ! Error: The location of UnRen appears to be wrong. It should
echo             be in the game's base directory.
echo             (dirs 'game', 'lib', 'renpy' are present)
echo/
goto :error


REM py check
REM --------------------------------------------------------------------------------
:py_check
set python_pth="%base_pth%lib\windows-i686\"
REM Future: On Renpy 8 (py3) we will have 64bit support for win
REM if "%PROCESSOR_ARCHITECTURE%" EQU "AMD64" (
REM     set "python_pth=%base_pth%lib\windows-x86_64\"
REM ) else (
REM     set "python_pth=%base_pth%lib\windows-i686\"
REM )

if not exist "%python_pth%python.exe" (
	echo    ! Error: Cannot locate python.exe, unable to continue.
	echo             Is the correct python version for your computer in 
    echo             the "%base_pth%lib" directory?
	echo/
	goto :error
)

goto :run_py


REM It got awry
REM --------------------------------------------------------------------------------
:error
echo/
echo    Terminating.
echo    If a reason was stated, correct the problem. If not check path
echo    and script for possible issues.
echo/
pause>nul|set/p=.            Press any key to exit...
exit 1


REM Kingdom of python --- lets go
REM --------------------------------------------------------------------------------
:run_py
REM Works in 7
"%python_pth%python.exe" -xEO "%~f0" %* & exit /b !errorlevel!
"""
batch_placeholder
