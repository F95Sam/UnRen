@echo off




REM read from central location
set /p version=<version.txt
title "UnRen for Windows v%version%"


REM path check part 1
REM --------------------------------------------------------------------------------
:path_check
REM lets assume the ideal (script sits in the games base dir)
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


REM path check part 2
REM --------------------------------------------------------------------------------
:py_check
set "python_pth=%base_pth%lib\windows-i686\"
REM Future: On Renpy py3 we will have 64bit support for win
REM if "%PROCESSOR_ARCHITECTURE%" EQU "AMD64" (
REM     set "python_pth=%base_pth%lib\windows-x86-64\"
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


REM Bad end
REM --------------------------------------------------------------------------------
:error
echo/
echo    Terminating.
echo    If a reason was stated, correct the problem. If not check path
echo    and script for possible issues.
echo/
pause>nul|set/p=.            Press any key to exit...
exit 1


REM kingdom of python - lets go
REM --------------------------------------------------------------------------------
:run_py
"%python_pth%python.exe" "%~f0" %* & goto :eof
REM # place python code here
