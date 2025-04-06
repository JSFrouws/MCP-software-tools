"""
Simplified Terminal MCP Server
"""

import os
import sys
import platform
import asyncio
import re
import logging
import time
import subprocess
from  textwrap import indent
from typing import Dict, Any
from datetime import datetime

from mcp.server.fastmcp import FastMCP, Context

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("simple-terminal-mcp")

# Determine the OS
IS_WINDOWS = platform.system() == "Windows"

# Terminal state
terminal_state = {
    "cwd": os.path.expanduser('~'),
    "history": [],
    "command_count": 0,
    "platform": platform.system(),
    "last_command": "",
    "last_output": "",
    "session_start": datetime.now().isoformat()
}

# Create MCP server
mcp = FastMCP("SimpleTerminal", dependencies=["mcp"])

@mcp.tool()
async def run_command(command: str, ctx: Context) -> str:
    """
    Execute a command in the terminal
    
    Args:
        command: Command to execute
    """
    global terminal_state
    
    # Add to history
    terminal_state["history"].append(command)
    terminal_state["command_count"] += 1
    
    # Execute the command
    result = await execute_command(command)
    
    # Format output
    output = []
    output.append(f"$ {command}")
    output.append("")
    
    # Add stdout if present
    if result["stdout"]:
        output.append(result["stdout"].rstrip())
    
    # Add stderr if present
    if result["stderr"]:
        output.append("STDERR:")
        output.append(result["stderr"].rstrip())
    
    # Add exit code and execution time
    output.append("")
    output.append(f"Exit Code: {result['exit_code']}")
    output.append(f"Execution Time: {result['execution_time']:.3f} seconds")
    output.append(f"Working Directory: {terminal_state['cwd']}")
    
    # Compile output
    final_output = "\n".join(output)
    terminal_state["last_output"] = final_output
    
    return final_output

@mcp.tool()
async def get_terminal_info() -> str:
    """
    Get information about the terminal session
    """
    global terminal_state
    
    # Format output
    output = []
    output.append("# Terminal Session Information")
    output.append("")
    output.append(f"Platform: {terminal_state['platform']}")
    output.append(f"Session Started: {terminal_state['session_start']}")
    output.append(f"Commands Executed: {terminal_state['command_count']}")
    output.append(f"Current Directory: {terminal_state['cwd']}")
    
    # Add command history
    output.append("")
    output.append("## Command History")
    
    history = terminal_state["history"]
    if history:
        for i, cmd in enumerate(history[-10:], 1):
            output.append(f"{i}. {cmd}")
    else:
        output.append("No commands have been executed yet.")
    
    return "\n".join(output)

# Helper function to execute commands
async def execute_command(command: str) -> Dict[str, Any]:
    """Execute a command and return the result"""
    global terminal_state
    
    result = {
        "stdout": "",
        "stderr": "",
        "exit_code": 0,
        "command": command,
        "execution_time": 0,
        "timestamp": datetime.now().isoformat(),
    }
    
    # Track current directory
    cwd = terminal_state["cwd"]
    
    start_time = time.time()
    
    try:
        # Create command with markers for proper output handling
        cmd_time = int(time.time())
        marker = f"CMD_DONE_{cmd_time}"
        
        # Create a temporary batch file for Windows to capture exit code properly
        if IS_WINDOWS:
            shell_cmd = "cmd.exe"
            batch_file = f"temp_cmd_{cmd_time}.bat"
            with open(batch_file, "w") as f:
                f.write(f"@echo off\n{command}\necho ###EXIT_START###EXIT:%ERRORLEVEL%###EXIT_END###\n")
            marker_cmd = f"call {batch_file} & echo ###MARKER_START###{marker}###MARKER_END### & del {batch_file}"
        else:
            shell_cmd = "/bin/bash"
            marker_cmd = f"{command}; err=$?; echo '###MARKER_START###{marker}###MARKER_END###'; echo '###EXIT_START###EXIT:'$err'###EXIT_END###'"
        
        # Execute the command
        process = await asyncio.create_subprocess_shell(
            marker_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True,
            cwd=cwd
        )
        
        # Get output
        stdout_data, stderr_data = await process.communicate()
        
        # Decode output
        stdout = stdout_data.decode('utf-8', errors='replace')
        stderr = stderr_data.decode('utf-8', errors='replace')
        
        # Extract exit code
        exit_code = 0
        exit_code_match = re.search(r"###EXIT_START###EXIT:([^#]*)###EXIT_END###", stdout)
        if exit_code_match:
            try:
                exit_code_str = exit_code_match.group(1).strip()
                # Try to parse as integer
                try:
                    exit_code = int(exit_code_str)
                except ValueError:
                    # If not a valid integer, use non-zero code for errors
                    exit_code = 1 if exit_code_str.lower() not in ['0', 'true', 'false'] else 0
            except Exception as e:
                logger.error(f"Error parsing exit code: {e}")
                # Use process returncode as fallback
                exit_code = process.returncode or 1
        else:
            # If the marker isn't found, check stderr for common error messages
            if stderr and any(err_msg in stderr.lower() for err_msg in [
                'not recognized', 'not found', 'permission denied', 
                'access is denied', 'cannot find', 'failed']):
                exit_code = 1
            else:
                # Fallback to process returncode
                exit_code = process.returncode
        
        # Clean output by removing markers
        stdout = re.sub(r"###MARKER_START###.*?###MARKER_END###", "", stdout)
        stdout = re.sub(r"###EXIT_START###.*?###EXIT_END###", "", stdout)
        
        # Fill result
        result["stdout"] = stdout
        result["stderr"] = stderr
        result["exit_code"] = exit_code
        
        # Update working directory for directory change commands
        if command.strip().startswith("cd ") and exit_code == 0:
            # Get target directory from command
            target_dir = command.strip()[3:].strip()
            
            # Handle relative paths
            if not os.path.isabs(target_dir):
                target_dir = os.path.normpath(os.path.join(cwd, target_dir))
            
            # Check if directory exists
            if os.path.isdir(target_dir):
                # Update current working directory
                terminal_state["cwd"] = target_dir
                logger.info(f"Changed directory to: {target_dir}")
        
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        result["stderr"] = f"Error: {str(e)}"
        result["exit_code"] = 1
    
    # Calculate execution time
    result["execution_time"] = time.time() - start_time
    
    return result

# Resource to get terminal information
@mcp.resource("terminal://info")
def get_terminal_resource_info() -> str:
    """Resource that provides information about the terminal session"""
    global terminal_state
    
    import json
    return json.dumps(terminal_state, indent=2, default=str)

# Resource to get last output
@mcp.resource("terminal://last_output")
def get_last_output() -> str:
    """Get the output of the last executed command"""
    global terminal_state
    
    if not terminal_state["last_output"]:
        return "No commands have been executed yet."
    
    return terminal_state["last_output"]

@mcp.tool()
def runPythonCodeSnippet(code: str) -> str:
    """
    Run code provided as a string using a subprocess.

    Args:
        code (str): The code to run.

    Returns:
        str: The output of the code.

    NOTE: These packages are installed and can be imported, let me know if you miss anything:
    """
    result = subprocess.run(['python', '-c', code], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode('utf-8') or result.stderr.decode('utf-8')

packages = subprocess.run(["uv", "pip", "list"], stdout=subprocess.PIPE)
setattr(runPythonCodeSnippet, "__doc__", runPythonCodeSnippet.__doc__ + "\n" + indent(packages.stdout.decode('utf-8'), " "*4))

# Main entry point
if __name__ == "__main__":
    logger.info(f"Starting Simple Terminal MCP Server. Platform: {platform.system()}")
    logger.info(f"Initial working directory: {terminal_state['cwd']}")
    mcp.run()
