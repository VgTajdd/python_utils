@echo off
setlocal
set CURRENT_DIR=%~dp0..\
call "%CURRENT_DIR%venv\Scripts\activate.bat"
call pip freeze > "%CURRENT_DIR%/requirements.txt"
call deactivate
endlocal
