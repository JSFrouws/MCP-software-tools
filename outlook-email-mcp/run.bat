@echo off
echo Starting Outlook Email MCP Server with debugging...
echo.

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Debug first
echo Running debug checks...
python debug_server.py

:: Check if tools are registered
echo.
echo Checking tool registration...
python check_tools.py

:: Run the server with verbose logging
echo.
echo Starting MCP server...
set PYTHONUNBUFFERED=1
python -u outlook_email_server.py

echo.
echo Server stopped.
echo Press any key to exit...
pause > nul
