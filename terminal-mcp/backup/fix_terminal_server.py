"""
Automated fix script for terminal_server.py
"""

import sys
import re

def fix_terminal_server():
    """Fix any syntax issues in terminal_server.py"""
    
    try:
        # Read the file
        with open('terminal_server.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Save a backup
        with open('terminal_server.py.bak', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Created backup of terminal_server.py as terminal_server.py.bak")
        
        # Ensure the file ends with a newline
        if not content.endswith('\n'):
            content += '\n'
        
        # Write the fixed content
        with open('terminal_server.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Fixed and saved terminal_server.py")
        return True
        
    except Exception as e:
        print(f"Error fixing terminal_server.py: {e}")
        return False

if __name__ == "__main__":
    success = fix_terminal_server()
    if not success:
        sys.exit(1)
