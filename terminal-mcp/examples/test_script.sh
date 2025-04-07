#!/bin/bash
echo "This is a test script for the Terminal MCP Server"
echo "Current time: $(date +%T)"
echo "Current date: $(date +%D)"
echo ""
echo "Environment variables:"
echo "---------------------"
env
echo ""
echo "Creating a temporary file..."
echo "Hello from Terminal MCP" > temp_file.txt
echo "File created!"
echo ""
echo "Contents of temp_file.txt:"
cat temp_file.txt
echo ""
echo "Done!"
