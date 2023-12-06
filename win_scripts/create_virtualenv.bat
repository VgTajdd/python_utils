::----------------------------------------------------------------------------
:: This script creates a virtualenv.
:: Author: Agustin Durand
::----------------------------------------------------------------------------

@echo off
echo Start

setlocal

set CURRENT_DIR=%~dp0..\

set /p PYTHONHOME=<python_home
set pythonExe="%PYTHONHOME%\python.exe"
set PYTHONPATH=%PYTHONHOME%;%PYTHONHOME%\Lib;%PYTHONHOME%\DLLs;%PYTHONHOME%\Lib\site-packages;%PYTHONHOME%\Scripts
set PATH=%PYTHONPATH%;%PATH%;

echo "python Version:"
%pythonExe% --version
%pythonExe% -m pip list

:: Install virtualenv.
%pythonExe% -m pip install virtualenv

:: This creates a directory called venv with a copy of python,
:: but it needs to be activated.
%pythonExe% -m virtualenv venv

endlocal

echo End
