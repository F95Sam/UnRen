1>2# : ^
"""
@echo off
setlocal enabledelayedexpansion

echo Here is much space for endless speeches about this cool app
echo Or not...


set version=version=0.12.0-alpha
title "UnRen for Windows v%version%"
mode con: cols=90 lines=50


REM Kingdom of python --- lets go
REM --------------------------------------------------------------------------------
"python" -xEO "%~f0" %* & exit /b !errorlevel!
"""
batch_placeholder
