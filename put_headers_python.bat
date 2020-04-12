@echo off
setlocal
set CURRENT_DIR=%~dp0
call "%CURRENT_DIR%/venv/Scripts/activate.bat"
call python put_headers_python.py "%CURRENT_DIR%/dir"
call deactivate
endlocal
cmd /k