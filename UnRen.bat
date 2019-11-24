@echo off
:: [DEV//WARN_START
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
:: DEV//WARN_END]
:: --------------------------------------------------------------------------------
:: Configuration:
::   Set a Quick Save and Quick Load hotkey - http://www.pygame.org/docs/ref/key.html
:: --------------------------------------------------------------------------------
set "quicksavekey=K_F5"
set "quickloadkey=K_F9"
:: --------------------------------------------------------------------------------
:: !! END CONFIG !!
:: --------------------------------------------------------------------------------
:: The following variables are Base64 encoded strings for unrpyc and rpatool
:: Due to batch limitations on variable lengths, they need to be split into
:: multiple variables, and joined later using powershell.
:: --------------------------------------------------------------------------------
:: unrpyc by CensoredUsername
::   https://github.com/CensoredUsername/unrpyc
:: Edited to ::ove multiprocessing and adjust output spacing [UNRPYC//SHA] [UNRPYC//DATE]
::   https://github.com/F95Sam/unrpyc
:: --------------------------------------------------------------------------------
:: set unrpyccab01=
[UNRPYC//BASE]
:: --------------------------------------------------------------------------------
:: rpatool by Shizmob [RPATOOL//SHA] [RPATOOL//DATE]
::   https://github.com/Shizmob/rpatool
:: --------------------------------------------------------------------------------
:: set rpatool01=
[RPATOOL//BASE]
:: --------------------------------------------------------------------------------
:: !! DO NOT EDIT BELOW THIS LINE !!
:: --------------------------------------------------------------------------------
set "version=0.11.0-dev ([DEV//BUILD_DATE])"
title UnRen.bat v%version%
:init
:: --------------------------------------------------------------------------------
:: Splash screen
:: --------------------------------------------------------------------------------
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

:: --------------------------------------------------------------------------------
:: Set up the work paths and assert script, python and powershell location
:: Note: 'if/else/else if' would be nice, but make just problems in batch
:: --------------------------------------------------------------------------------
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

:: --------------------------------------------------------------------------------
:: Menu selection
:: --------------------------------------------------------------------------------
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

:: --------------------------------------------------------------------------------
:: Write _rpatool.py from our base64 strings
:: --------------------------------------------------------------------------------
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

:: echo %rpatool%>> "%rpatool%.tmp"
[RPATOOL//MERGE]
set "rpatoolps=%rpatool:[=`[%"
set "rpatoolps=%rpatoolps:]=`]%"
set "rpatoolps=%rpatoolps:^=^^%"
set "rpatoolps=%rpatoolps:&=^&%"
powershell.exe -nologo -noprofile -noninteractive -command "& { [IO.File]::WriteAllBytes(\"%rpatoolps%\", [Convert]::FromBase64String([IO.File]::ReadAllText(\"%rpatoolps%.tmp\"))) }"

:: --------------------------------------------------------------------------------
:: Check if rpatool is there.
:: --------------------------------------------------------------------------------
if not exist "%rpatool%" (
	echo    ! Error: 'rpatool' is missing. Please check if UnRen and Powershell
	echo             are working correctly.
	echo/
	set err=1 & goto :rpatool_cleanup
)

:: --------------------------------------------------------------------------------
:: Unpack RPA
:: --------------------------------------------------------------------------------
echo/
echo   Searching for RPA packages
cd "%gamedir%"
for %%f in (*.rpa *.rpi *.rpc) do (
	echo    + Unpacking "%%~nf%%~xf" - %%~zf bytes
	"%pythondir%python.exe" -O "%rpatool%" -x "%%f"
)

:: --------------------------------------------------------------------------------
:: Clean up
:: --------------------------------------------------------------------------------
:rpatool_cleanup
echo/
echo   Cleaning up temporary files...
del "%rpatool%.tmp"
del "%rpatool%"
echo/
)
if not %err% == 0 goto :error
if not "%option%" == "9" goto :finish

:: --------------------------------------------------------------------------------
:: Write to temporary file first, then convert. Needed due to binary file
:: --------------------------------------------------------------------------------
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

:: echo %unrpyccab%>> "%unrpyccab%.tmp"
[UNRPYC//MERGE]
set "unrpyccabps=%unrpyccab:[=`[%"
set "unrpyccabps=%unrpyccabps:]=`]%"
set "unrpyccabps=%unrpyccabps:^=^^%"
set "unrpyccabps=%unrpyccabps:&=^&%"
powershell.exe -nologo -noprofile -noninteractive -command "& { [IO.File]::WriteAllBytes(\"%unrpyccabps%\", [Convert]::FromBase64String([IO.File]::ReadAllText(\"%unrpyccabps%.tmp\"))) }"

:: --------------------------------------------------------------------------------
:: Once converted, extract the cab file. Needs to be a cab file due to expand.exe
:: --------------------------------------------------------------------------------
echo/
echo   Extracting _unrpyc.cab...
mkdir "%decompilerdir%"
expand -F:* "%unrpyccab%" "%decompilerdir%" >nul
move "%decompilerdir%\unrpyc.py" "%unrpycpy%" >nul

:: --------------------------------------------------------------------------------
:: Check if unrpyc is there
:: --------------------------------------------------------------------------------
if not exist "%unrpycpy%" (
	echo    ! Error: 'unrpyc' is missing. Please check if UnRen and Powershell
	echo              are working correctly.
	echo/
	set err=1 & goto :unrpyc_cleanup
)

:: --------------------------------------------------------------------------------
:: Decompile rpyc files
:: --------------------------------------------------------------------------------
echo/
echo   Searching for rpyc files...
cd "%gamedir%"
for /r %%f in (*.rpyc) do (
	if not %%~nf == un (
		echo    + Decompiling "%%~nf%%~xf" - %%~zf bytes
		"%pythondir%python.exe" -O "%unrpycpy%" "%%f"
	)
)

:: --------------------------------------------------------------------------------
:: Clean up
:: --------------------------------------------------------------------------------
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
:: --------------------------------------------------------------------------------
:: Drop our console/dev mode enabler into the game folder
:: --------------------------------------------------------------------------------
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


:: --------------------------------------------------------------------------------
:: Drop our Quick Save/Load file into the game folder
:: --------------------------------------------------------------------------------
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

:: --------------------------------------------------------------------------------
:: Drop our skip file into the game folder
:: --------------------------------------------------------------------------------
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

:: --------------------------------------------------------------------------------
:: Drop our rollback file into the game folder
:: --------------------------------------------------------------------------------
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

:: --------------------------------------------------------------------------------
:: We are done
:: --------------------------------------------------------------------------------
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
exit 1

:: --------------------------------------------------------------------------------
:: Bad end
:: --------------------------------------------------------------------------------
:error
echo/
echo    Terminating.
echo    If a reason was stated correct the problem, if not check path
echo    and script for possible issues.
echo/
pause>nul|set/p=.            Press any key to exit...
exit 1
