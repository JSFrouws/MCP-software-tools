"""
Simple test to identify issues in terminal_server.py
"""

import sys

try:
    import terminal_server
    print("Successfully imported terminal_server.py")
except Exception as e:
    print(f"Error importing terminal_server.py: {e}", file=sys.stderr)
    print(f"Exception type: {type(e)}", file=sys.stderr)
    
    # Get line information if available
    import traceback
    traceback.print_exc()
