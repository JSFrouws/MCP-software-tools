"""
Test script for Terminal MCP Server
"""

import os
import sys
import platform
import datetime

print("Python Test Script for Terminal MCP Server")
print("-----------------------------------------")
print(f"Python version: {sys.version}")
print(f"Platform: {platform.system()} {platform.release()}")
print(f"Current time: {datetime.datetime.now().strftime('%H:%M:%S')}")
print(f"Current date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
print()

print("Current working directory:")
print(os.getcwd())
print()

print("Files in current directory:")
for i, item in enumerate(os.listdir('.'), 1):
    if os.path.isdir(item):
        print(f"{i}. [DIR] {item}")
    else:
        print(f"{i}. [FILE] {item}")
print()

# Create a temporary file
with open("temp_python_file.txt", "w") as f:
    f.write("Hello from Python via Terminal MCP!\n")
    f.write(f"Created at: {datetime.datetime.now()}\n")

print("Created a temporary file: temp_python_file.txt")
print("Contents:")
with open("temp_python_file.txt", "r") as f:
    print(f.read())

print("Done!")
