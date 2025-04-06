@echo off
echo Setting up Terminal MCP Project

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.9+ and ensure it's in your system PATH.
    exit /b 1
)

REM Create virtual environment
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment and install dependencies
call .venv\Scripts\activate

REM Upgrade pip and install dependencies
uv pip install mcp psutil pywin32

REM Create requirements.txt for future reference
echo mcp
echo psutil
echo pywin32 > requirements.txt

echo Project setup complete!
echo To run the server, use: .venv\Scripts\python terminal_server.py

pause