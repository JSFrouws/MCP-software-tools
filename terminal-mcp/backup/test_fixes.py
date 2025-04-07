"""
Test script for terminal-mcp fixes
"""

import asyncio
import logging
import sys
from terminal_server import PersistentShell, terminal_state

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test-terminal-mcp")

async def test_directory_tracking():
    """Test working directory tracking"""
    print("\n=== Testing Directory Tracking ===")
    
    # Create a shell instance
    shell = PersistentShell()
    
    try:
        # Start the shell
        await shell.start()
        print(f"Initial working directory: {shell.cwd}")
        
        # Test directory change
        print("\nExecuting directory change...")
        result = await shell.execute("cd ..")
        print(f"New working directory: {shell.cwd}")
        print(f"terminal_state cwd: {terminal_state['cwd']}")
        
        # Verify that directories match
        if shell.cwd == terminal_state["cwd"]:
            print("✅ Working directory tracking OK - shell.cwd and terminal_state['cwd'] are in sync")
        else:
            print("❌ Working directory tracking FAILED - shell.cwd and terminal_state['cwd'] are out of sync")
    finally:
        await shell.stop()

async def test_exit_code_handling():
    """Test exit code handling"""
    print("\n=== Testing Exit Code Handling ===")
    
    # Create a shell instance
    shell = PersistentShell()
    
    try:
        # Start the shell
        await shell.start()
        
        # Test successful command
        print("\nExecuting successful command (dir)...")
        result = await shell.execute("dir")
        print(f"Exit code for successful command: {result['exit_code']}")
        
        if result["exit_code"] == 0:
            print("✅ Exit code handling OK - Successful command reported exit code 0")
        else:
            print(f"❌ Exit code handling FAILED - Successful command reported exit code {result['exit_code']}")
        
        # Test failing command
        print("\nExecuting failing command (dir nonexistentfolder)...")
        result = await shell.execute("dir nonexistentfolder")
        print(f"Exit code for failing command: {result['exit_code']}")
        
        if result["exit_code"] != 0:
            print("✅ Exit code handling OK - Failed command reported non-zero exit code")
        else:
            print(f"❌ Exit code handling FAILED - Failed command reported exit code {result['exit_code']}")
    finally:
        await shell.stop()

async def test_marker_cleanup():
    """Test marker cleanup in output"""
    print("\n=== Testing Marker Cleanup ===")
    
    # Create a shell instance
    shell = PersistentShell()
    
    try:
        # Start the shell
        await shell.start()
        
        # Execute a command
        print("\nExecuting command and checking for markers in output...")
        result = await shell.execute("echo Hello World")
        
        # Check for marker text
        stdout = result["stdout"]
        marker_patterns = ["CMD_DONE_", "PWD_DONE_", "###MARKER_START###", "###MARKER_END###", 
                          "###EXIT_START###", "###EXIT_END###"]
        
        has_markers = False
        for pattern in marker_patterns:
            if pattern in stdout:
                has_markers = True
                print(f"❌ Marker cleanup FAILED - Found '{pattern}' in output")
        
        if not has_markers:
            print("✅ Marker cleanup OK - No marker text found in output")
        
        print("\nCommand output:")
        print("---")
        print(stdout)
        print("---")
    finally:
        await shell.stop()

async def main():
    # Run all tests
    await test_directory_tracking()
    await test_exit_code_handling()
    await test_marker_cleanup()

if __name__ == "__main__":
    asyncio.run(main())
