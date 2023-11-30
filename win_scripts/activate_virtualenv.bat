@echo off
setlocal
set CURRENT_DIR=%~dp0..\
call "%CURRENT_DIR%venv\Scripts\activate.bat"
cd /d %CURRENT_DIR%
cmd /k
endlocal
