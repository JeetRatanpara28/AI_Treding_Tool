@echo off
REM Defaults to offline status. After approving public data access:
REM dailytask.bat swing --allow-network
"C:\AI-Trading-Bot\.venv\Scripts\python.exe" -X utf8 "%~dp0scripts\research.py" %*
exit /b %ERRORLEVEL%
