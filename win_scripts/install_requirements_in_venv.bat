@echo off
setlocal
set CURRENT_DIR=%~dp0..\
call "%CURRENT_DIR%venv\Scripts\activate.bat"
call pip install -r "%CURRENT_DIR%requirements.txt"
call deactivate
cmd \k
endlocal
