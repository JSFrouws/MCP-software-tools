"""
Claude Manager - MCP tool for managing Claude Desktop

This tool provides functions to restart Claude and manage its configuration.
"""

import asyncio
import logging
import os
import platform
import subprocess
import json
import time
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP, Context

logger = logging.getLogger("GenericMcpToolSet.claude_manager")

def register_tools(mcp: FastMCP):
    """Register all tools in this module with the MCP server"""
    
    @mcp.tool()
    async def restart_claude(
        wait_time: int = 5,
        ctx: Context = None
    ) -> str:
        """
        Restart the Claude Desktop application to load new MCP servers
        
        Args:
            wait_time: Time to wait before restarting Claude (in seconds)
        
        Returns:
            Status of the restart operation
        """
        logger.info(f"Restarting Claude Desktop with wait_time={wait_time}")
        
        if ctx:
            ctx.info("Preparing to restart Claude Desktop...")
        
        try:
            system = platform.system().lower()
            
            # Find Claude process and restart it
            if system == "windows":
                # Get Claude's process information
                if ctx:
                    ctx.info("Finding Claude process...")
                
                # Find Claude Desktop process
                process = await asyncio.create_subprocess_shell(
                    'tasklist /FI "IMAGENAME eq Claude.exe" /FO CSV /NH',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if b"Claude.exe" in stdout:
                    if ctx:
                        ctx.info(f"Claude Desktop found. Will restart in {wait_time} seconds...")
                    
                    # First, close Claude nicely
                    result = "Claude Desktop will be restarted.\n\n"
                    result += f"The application will close in {wait_time} seconds.\n"
                    result += "Please wait while Claude restarts...\n\n"
                    result += "After restart, you can continue your conversation normally."
                    
                    # Create a detached process that will wait and then restart Claude
                    # This is done in a separate process to allow Claude to fully shut down
                    restart_cmd = (
                        f'powershell -Command "'
                        f'Start-Sleep -Seconds {wait_time}; '
                        f'taskkill /F /IM Claude.exe; '
                        f'Start-Sleep -Seconds 2; '
                        f'Start-Process \\"$env:LOCALAPPDATA\\Claude\\Claude.exe\\"'
                        f'"'
                    )
                    
                    # Execute the restart command as a detached process
                    subprocess.Popen(
                        restart_cmd,
                        shell=True,
                        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                    
                    return result
                else:
                    return "Claude Desktop process not found. It may not be running or has a different process name."
                
            elif system == "darwin":  # macOS
                # macOS implementation
                if ctx:
                    ctx.info("Finding Claude process on macOS...")
                
                # Find Claude process
                process = await asyncio.create_subprocess_shell(
                    'pgrep -x "Claude"',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if stdout.strip():
                    if ctx:
                        ctx.info(f"Claude Desktop found. Will restart in {wait_time} seconds...")
                    
                    result = "Claude Desktop will be restarted.\n\n"
                    result += f"The application will close in {wait_time} seconds.\n"
                    result += "Please wait while Claude restarts...\n\n"
                    result += "After restart, you can continue your conversation normally."
                    
                    # Create a detached process for restarting
                    restart_cmd = (
                        f'sleep {wait_time} && '
                        f'killall Claude && '
                        f'sleep 2 && '
                        f'open -a Claude'
                    )
                    
                    # Execute the restart command
                    subprocess.Popen(
                        restart_cmd,
                        shell=True,
                        start_new_session=True
                    )
                    
                    return result
                else:
                    return "Claude Desktop process not found. It may not be running or has a different process name."
            else:
                return f"Unsupported operating system: {system}. This tool only works on Windows and macOS."
            
        except Exception as e:
            logger.error(f"Error restarting Claude: {e}")
            return f"Error restarting Claude: {str(e)}"
    
    @mcp.tool()
    async def check_claude_config(ctx: Context = None) -> str:
        """
        Check Claude Desktop's configuration for MCP servers
        
        Returns:
            Information about the current Claude Desktop configuration
        """
        logger.info("Checking Claude Desktop configuration")
        
        if ctx:
            ctx.info("Locating Claude Desktop configuration file...")
        
        try:
            system = platform.system().lower()
            config_path = ""
            
            if system == "windows":
                config_path = os.path.join(os.environ.get("APPDATA", ""), "Claude", "claude_desktop_config.json")
            elif system == "darwin":  # macOS
                config_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
            else:
                return f"Unsupported operating system: {system}. This tool only works on Windows and macOS."
            
            if ctx:
                ctx.info(f"Looking for config at: {config_path}")
            
            # Check if the config file exists
            if not os.path.exists(config_path):
                return f"Claude Desktop configuration file not found at: {config_path}"
            
            # Read the configuration
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check for MCP servers configuration
            if "mcpServers" not in config:
                return "No MCP servers configured in Claude Desktop."
            
            mcp_servers = config["mcpServers"]
            server_count = len(mcp_servers)
            
            # Format the output
            result = f"# Claude Desktop MCP Configuration\n\n"
            result += f"Found {server_count} configured MCP servers:\n\n"
            
            for server_name, server_config in mcp_servers.items():
                result += f"## {server_name}\n"
                result += f"- Command: `{server_config.get('command', 'N/A')}`\n"
                
                if "args" in server_config:
                    args = server_config["args"]
                    result += f"- Arguments: `{' '.join(args)}`\n"
                
                if "env" in server_config:
                    env_vars = server_config["env"]
                    result += f"- Environment Variables: {len(env_vars)} defined\n"
                
                result += "\n"
            
            return result
            
        except json.JSONDecodeError:
            return f"Error parsing Claude Desktop configuration: Invalid JSON format"
        except Exception as e:
            logger.error(f"Error checking Claude config: {e}")
            return f"Error checking Claude Desktop configuration: {str(e)}"
