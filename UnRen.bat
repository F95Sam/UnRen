@echo off
REM [DEV//WARN_START
title UnRen.bat Error
echo/
echo   Error!
echo/
echo   This is the development version of UnRen. This is non functional and not
echo   intended to be used by end users.
echo   Please use the release version instead, found in the F95zone thread:
echo/
echo   https://f95zone.to/threads/unren-bat-rpa-extractor-rpyc-decompiler-console-developer-menu-enabler.3083/
echo/
pause>nul|set/p=.  Press any key to exit...
echo/
pause
exit
REM DEV//WARN_END]
REM --------------------------------------------------------------------------------
REM Configuration:
REM   Set a Quick Save and Quick Load hotkey - http://www.pygame.org/docs/ref/key.html
REM --------------------------------------------------------------------------------
set "quicksavekey=K_F5"
set "quickloadkey=K_F9"
REM --------------------------------------------------------------------------------
REM !! END CONFIG !!
REM --------------------------------------------------------------------------------
REM The following variables are Base64 encoded strings for unrpyc and rpatool
REM Due to batch limitations on variable lengths, they need to be split into
REM multiple variables, and joined later using powershell.
REM --------------------------------------------------------------------------------
REM unrpyc by CensoredUsername
REM   https://github.com/CensoredUsername/unrpyc
REM Edited to remove multiprocessing and adjust output spacing [UNRPYC//SHA] [UNRPYC//DATE]
REM   https://github.com/F95Sam/unrpyc
REM --------------------------------------------------------------------------------
REM set unrpyccab01=
[UNRPYC//BASE]
REM --------------------------------------------------------------------------------
REM rpatool by Shizmob [RPATOOL//SHA] [RPATOOL//DATE]
REM   https://github.com/Shizmob/rpatool
REM --------------------------------------------------------------------------------
REM set rpatool01=
[RPATOOL//BASE]
REM --------------------------------------------------------------------------------
REM !! DO NOT EDIT BELOW THIS LINE !!
REM --------------------------------------------------------------------------------
set "version=0.9.0-dev ([DEV//BUILD_DATE])"
title UnRen.bat v%version%
:init
REM --------------------------------------------------------------------------------
REM Splash screen
REM --------------------------------------------------------------------------------
cls
echo/
echo     __  __      ____               __          __
echo    / / / /___  / __ \___  ____    / /_  ____ _/ /_
echo   / / / / __ \/ /_/ / _ \/ __ \  / __ \/ __ ^`/ __/
echo  / /_/ / / / / _^, _/  __/ / / / / /_/ / /_/ / /_
echo  \____/_/ /_/_/ ^|_^|\___/_/ /_(_)_.___/\__^,_/\__/ v%version%
echo   Sam @ www.f95zone.to
echo/
echo  ----------------------------------------------------
echo/

REM --------------------------------------------------------------------------------
REM Set up the work paths and assert script, python and powershell location
REM Note: 'if/else/else if' would be nice, but make just problems in batch
REM --------------------------------------------------------------------------------
set err=0
set err_msg="Unknown reason..."
set currentdir=%~dp0

if exist "game" if exist "lib" if exist "renpy" (
	set "pythondir=%currentdir%lib\windows-i686\"
	set "renpydir=%currentdir%renpy\"
	set "gamedir=%currentdir%game\"
	goto :path_ok
)

if exist "..\game" if exist "..\lib" if exist "..\renpy" (
	set "pythondir=%currentdir%..\lib\windows-i686\"
	set "renpydir=%currentdir%..\renpy\"
	set gamedir=%currentdir%
	goto :path_ok
)

echo    ! Error: The location of UnRen appears to be wrong. It should
echo             be in the game's root directory.
echo             (dirs 'game', 'lib', 'renpy' are present)
echo/
goto :error

:path_ok
if not exist "%pythondir%python.exe" (
	echo    ! Error: Cannot locate python.exe, unable to continue.
	echo             Are you sure we're in the game's root directory?
	echo/
	goto :error
)

if not exist "%SystemRoot%\system32\WindowsPowerShell\v1.0\powershell.exe" (
	echo    ! Error: Powershell is required, unable to continue.
	echo             This is included in Windows 7, 8, 10. XP/Vista users can
	echo             download it here: http://support.microsoft.com/kb/968929
	echo/
	goto :error
)

REM --------------------------------------------------------------------------------
REM Menu selection
REM --------------------------------------------------------------------------------
:menu
set exitoption=
echo   Available Options:
echo     1) Extract RPA packages
echo     2) Decompile rpyc files
echo     3) Enable Console and Developer Menu
echo     4) Enable Quick Save and Quick Load
echo     5) Force enable skipping of unseen content
echo     6) Force enable rollback (scroll wheel)
echo/
echo     9) All of the above
echo/
set /p option=.  Enter a number: 
echo/
echo  ----------------------------------------------------
echo/
if "%option%"=="1" goto :extract
if "%option%"=="2" goto :decompile
if "%option%"=="3" goto :console
if "%option%"=="4" goto :quick
if "%option%"=="5" goto :skip
if "%option%"=="6" goto :rollback
if "%option%"=="9" goto :extract
goto :init

REM --------------------------------------------------------------------------------
REM Write _rpatool.py from our base64 strings
REM --------------------------------------------------------------------------------
:extract
set "rpatool=%currentdir%_rpatool.py"
echo/
echo   Creating rpatool...
if exist "%rpatool%.tmp" (
	del "%rpatool%.tmp"
)
if exist "%rpatool%" (
	del "%rpatool%"
)

REM echo %rpatool%>> "%rpatool%.tmp"
[RPATOOL//MERGE]
set "rpatoolps=%rpatool:[=`[%"
set "rpatoolps=%rpatoolps:]=`]%"
set "rpatoolps=%rpatoolps:^=^^%"
set "rpatoolps=%rpatoolps:&=^&%"
powershell.exe -nologo -noprofile -noninteractive -command "& { [IO.File]REMWriteAllBytes(\"%rpatoolps%\", [Convert]REMFromBase64String([IO.File]REMReadAllText(\"%rpatoolps%.tmp\"))) }"

REM --------------------------------------------------------------------------------
REM Check if rpatool is there.
REM --------------------------------------------------------------------------------
if not exist "%rpatool%" (
	echo    ! Error: 'rpatool' is missing. Please check if UnRen and Powershell
	echo             are working correctly.
	echo/
	set err=1 & goto :rpatool_cleanup
)

REM --------------------------------------------------------------------------------
REM Unpack RPA
REM --------------------------------------------------------------------------------
echo/
echo   Searching for RPA packages
cd "%gamedir%"
for %%f in (*.rpa *.rpi *.rpc) do (
	echo    + Unpacking "%%~nf%%~xf" - %%~zf bytes
	"%pythondir%python.exe" -O "%rpatool%" -x "%%f"
)

REM --------------------------------------------------------------------------------
REM Clean up
REM --------------------------------------------------------------------------------
:rpatool_cleanup
echo/
echo   Cleaning up temporary files...
del "%rpatool%.tmp"
del "%rpatool%"
echo/
)
if not %err% == 0 goto :error
if not "%option%" == "9" goto :finish

REM --------------------------------------------------------------------------------
REM Write to temporary file first, then convert. Needed due to binary file
REM --------------------------------------------------------------------------------
:decompile
set "unrpyccab=%gamedir%..\_unrpyc.cab"
set "decompilerdir=%gamedir%..\decompiler"
set "unrpycpy=%gamedir%..\unrpyc.py"
echo/
echo   Creating _unrpyc.cab...
if exist "%unrpyccab%.tmp" (
	del "%unrpyccab%.tmp"
)
if exist "%unrpyccab%" (
	del "%unrpyccab%"
)
if exist "%unrpycpy%" (
	del "%unrpycpy%"
)
if exist "%decompilerdir%" (
	rmdir /Q /S "%decompilerdir%"
)

REM echo %unrpyccab%>> "%unrpyccab%.tmp"
[UNRPYC//MERGE]
set "unrpyccabps=%unrpyccab:[=`[%"
set "unrpyccabps=%unrpyccabps:]=`]%"
set "unrpyccabps=%unrpyccabps:^=^^%"
set "unrpyccabps=%unrpyccabps:&=^&%"
powershell.exe -nologo -noprofile -noninteractive -command "& { [IO.File]REMWriteAllBytes(\"%unrpyccabps%\", [Convert]REMFromBase64String([IO.File]REMReadAllText(\"%unrpyccabps%.tmp\"))) }"

REM --------------------------------------------------------------------------------
REM Once converted, extract the cab file. Needs to be a cab file due to expand.exe
REM --------------------------------------------------------------------------------
echo/
echo   Extracting _unrpyc.cab...
mkdir "%decompilerdir%"
expand -F:* "%unrpyccab%" "%decompilerdir%" >nul
move "%decompilerdir%\unrpyc.py" "%unrpycpy%" >nul

REM --------------------------------------------------------------------------------
REM Check if unrpyc is there
REM --------------------------------------------------------------------------------
if not exist "%unrpycpy%" (
	echo    ! Error: 'unrpyc' is missing. Please check if UnRen and Powershell
	echo              are working correctly.
	echo/
	set err=1 & goto :unrpyc_cleanup
)

REM --------------------------------------------------------------------------------
REM Decompile rpyc files
REM --------------------------------------------------------------------------------
echo/
echo   Searching for rpyc files...
cd "%gamedir%"
for /r %%f in (*.rpyc) do (
	if not %%~nf == un (
		echo    + Decompiling "%%~nf%%~xf" - %%~zf bytes
		"%pythondir%python.exe" -O "%unrpycpy%" "%%f"
	)
)

REM --------------------------------------------------------------------------------
REM Clean up
REM --------------------------------------------------------------------------------
:unrpyc_cleanup
echo/
echo   Cleaning up temporary files...
del "%unrpyccab%.tmp"
del "%unrpyccab%"
del "%unrpycpy%"
rmdir /Q /S "%decompilerdir%"

if not %err% == 0 goto :error
if not "%option%" == "9" goto :finish

:console
REM --------------------------------------------------------------------------------
REM Drop our console/dev mode enabler into the game folder
REM --------------------------------------------------------------------------------
echo/
echo   Creating Developer/Console file...
set "consolefile=%gamedir%unren-dev.rpy"
if exist "%consolefile%" (
	del "%consolefile%"
)

echo init 999 python:>> "%consolefile%"
echo   config.developer = True>> "%consolefile%"
echo   config.console = True>> "%consolefile%"

echo    + Console: SHIFT+O
echo    + Dev Menu: SHIFT+D

if not "%option%" == "9" goto :finish


REM --------------------------------------------------------------------------------
REM Drop our Quick Save/Load file into the game folder
REM --------------------------------------------------------------------------------
:quick
echo/
echo   Creating Quick Save/Quick Load file...
set "quickfile=%gamedir%unren-quick.rpy"
if exist "%quickfile%" (
	del "%quickfile%"
)

echo init 999 python:>> "%quickfile%"
echo   try:>> "%quickfile%"
echo     config.underlay[0].keymap['quickSave'] = QuickSave()>> "%quickfile%"
echo     config.keymap['quickSave'] = '%quicksavekey%'>> "%quickfile%"
echo     config.underlay[0].keymap['quickLoad'] = QuickLoad()>> "%quickfile%"
echo     config.keymap['quickLoad'] = '%quickloadkey%'>> "%quickfile%"
echo   except:>> "%quickfile%"
echo     pass>> "%quickfile%"

echo    Default hotkeys:
echo    + Quick Save: F5
echo    + Quick Load: F9

if not "%option%" == "9" goto :finish

REM --------------------------------------------------------------------------------
REM Drop our skip file into the game folder
REM --------------------------------------------------------------------------------
:skip
echo/
echo   Creating skip file...
set "skipfile=%gamedir%unren-skip.rpy"
if exist "%skipfile%" (
	del "%skipfile%"
)

echo init 999 python:>> "%skipfile%"
echo   _preferences.skip_unseen = True>> "%skipfile%"
echo   renpy.game.preferences.skip_unseen = True>> "%skipfile%"
echo   renpy.config.allow_skipping = True>> "%skipfile%"
echo   renpy.config.fast_skipping = True>> "%skipfile%"

echo    + You can now skip all text using TAB and CTRL keys

if not "%option%" == "9" goto :finish

REM --------------------------------------------------------------------------------
REM Drop our rollback file into the game folder
REM --------------------------------------------------------------------------------
:rollback
echo/
echo   Creating rollback file...
set "rollbackfile=%gamedir%unren-rollback.rpy"
if exist "%rollbackfile%" (
	del "%rollbackfile%"
)

echo init 999 python:>> "%rollbackfile%"
echo   renpy.config.rollback_enabled = True>> "%rollbackfile%"
echo   renpy.config.hard_rollback_limit = 256>> "%rollbackfile%"
echo   renpy.config.rollback_length = 256>> "%rollbackfile%"
echo   def unren_noblock( *args, **kwargs ):>> "%rollbackfile%"
echo     return>> "%rollbackfile%"
echo   renpy.block_rollback = unren_noblock>> "%rollbackfile%"
echo   try:>> "%rollbackfile%"
echo     config.keymap['rollback'] = [ 'K_PAGEUP', 'repeat_K_PAGEUP', 'K_AC_BACK', 'mousedown_4' ]>> "%rollbackfile%"
echo   except:>> "%rollbackfile%"
echo     pass>> "%rollbackfile%"

echo    + You can now rollback using the scrollwheel

REM --------------------------------------------------------------------------------
REM We are done
REM --------------------------------------------------------------------------------
:finish
echo  ----------------------------------------------------
echo/
echo    Finished!
echo/
echo    Enter "1" to go back to the menu, or any other
set /p exitoption=.   key to exit: 
echo/
echo  ----------------------------------------------------

if "%exitoption%"=="1" goto menu
exit 0

REM --------------------------------------------------------------------------------
REM Bad end
REM --------------------------------------------------------------------------------
:error
echo/
echo    Terminating.
echo    If a reason was stated correct the problem, if not check path
echo    and script for possible issues.
echo/
pause>nul|set/p=.            Press any key to exit...
exit 1
