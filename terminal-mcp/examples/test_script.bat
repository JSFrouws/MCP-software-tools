@echo off
echo This is a test script for the Terminal MCP Server
echo Current time: %TIME%
echo Current date: %DATE%
echo.
echo Environment variables:
echo ---------------------
set
echo.
echo Creating a temporary file...
echo Hello from Terminal MCP > temp_file.txt
echo File created!
echo.
echo Contents of temp_file.txt:
type temp_file.txt
echo.
echo Done!
