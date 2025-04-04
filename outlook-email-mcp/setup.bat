@echo off
echo Setting up Outlook Email MCP Server...
echo.

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

:: Activate virtual environment and install dependencies
echo.
echo Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo Testing Outlook connection...
python test_outlook_connection.py

echo.
echo If the connection test was successful, you can now configure Claude Desktop to use this server.
echo See the README.md file for details on how to set up Claude Desktop.
echo.
echo Press any key to exit...
pause > nul
