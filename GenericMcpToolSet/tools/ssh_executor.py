"""
SSH Command Executor - MCP tool for executing commands over SSH

This tool provides functions to execute commands on remote systems via SSH.
"""

import asyncio
import logging
import asyncssh
from typing import Optional, Dict, Any, List
from mcp.server.fastmcp import FastMCP, Context

logger = logging.getLogger("GenericMcpToolSet.ssh_executor")

def register_tools(mcp: FastMCP):
    """Register all tools in this module with the MCP server"""
    
    @mcp.tool()
    async def execute_ssh_command(
        host: str,
        command: str,
        username: str,
        password: Optional[str] = None,
        port: int = 22,
        private_key_path: Optional[str] = None,
        timeout: int = 30,
        ctx: Context = None
    ) -> str:
        """
        Execute a command on a remote system via SSH
        
        Args:
            host: Hostname or IP address of the remote system
            command: Command to execute
            username: SSH username
            password: SSH password (optional if using private key)
            port: SSH port (default: 22)
            private_key_path: Path to private key file (optional)
            timeout: Connection timeout in seconds (default: 30)
        
        Returns:
            Output of the executed command
        """
        logger.info(f"Executing SSH command on {host}: {command}")
        
        if ctx:
            ctx.info(f"Connecting to {host} as {username}...")
        
        try:
            # Set up SSH connection parameters
            conn_params = {
                'host': host,
                'port': port,
                'username': username,
                'password': password if password else None,
                'known_hosts': None  # Skip known hosts check for simplicity
            }
            
            # Use private key if provided
            if private_key_path:
                if ctx:
                    ctx.info(f"Using private key from {private_key_path}")
                try:
                    conn_params['client_keys'] = [private_key_path]
                except Exception as e:
                    logger.error(f"Error loading private key: {e}")
                    return f"Error loading private key: {str(e)}"
            
            # Connect to the SSH server
            if ctx:
                ctx.info(f"Connecting to {host}:{port}...")
            
            async with asyncssh.connect(**conn_params) as conn:
                if ctx:
                    ctx.info(f"Connected. Executing command: {command}")
                
                # Execute the command
                result = await conn.run(command, timeout=timeout)
                
                # Prepare the output
                output = f"Command: {command}\n\n"
                
                if result.exit_status == 0:
                    output += "Status: Success\n\n"
                else:
                    output += f"Status: Failed (exit code: {result.exit_status})\n\n"
                
                if result.stdout:
                    output += f"STDOUT:\n{result.stdout}\n\n"
                
                if result.stderr:
                    output += f"STDERR:\n{result.stderr}\n"
                
                if ctx:
                    ctx.info(f"Command completed with exit code: {result.exit_status}")
                
                return output
                
        except asyncssh.Error as e:
            logger.error(f"SSH connection error: {e}")
            return f"SSH connection error: {str(e)}"
        except asyncio.TimeoutError:
            logger.error(f"Connection to {host} timed out")
            return f"Connection to {host} timed out after {timeout} seconds"
        except Exception as e:
            logger.error(f"Error executing SSH command: {e}")
            return f"Error executing SSH command: {str(e)}"
    
    @mcp.tool()
    async def execute_ssh_script(
        host: str,
        script_content: str,
        username: str,
        password: Optional[str] = None,
        port: int = 22,
        private_key_path: Optional[str] = None,
        timeout: int = 60,
        ctx: Context = None
    ) -> str:
        """
        Execute a multi-line script on a remote system via SSH
        
        Args:
            host: Hostname or IP address of the remote system
            script_content: Content of the script to execute
            username: SSH username
            password: SSH password (optional if using private key)
            port: SSH port (default: 22)
            private_key_path: Path to private key file (optional)
            timeout: Script execution timeout in seconds (default: 60)
        
        Returns:
            Output of the executed script
        """
        logger.info(f"Executing SSH script on {host}")
        
        if ctx:
            ctx.info(f"Preparing to execute script on {host}...")
        
        try:
            # Set up SSH connection parameters
            conn_params = {
                'host': host,
                'port': port,
                'username': username,
                'password': password if password else None,
                'known_hosts': None  # Skip known hosts check for simplicity
            }
            
            # Use private key if provided
            if private_key_path:
                if ctx:
                    ctx.info(f"Using private key from {private_key_path}")
                try:
                    conn_params['client_keys'] = [private_key_path]
                except Exception as e:
                    logger.error(f"Error loading private key: {e}")
                    return f"Error loading private key: {str(e)}"
            
            # Connect to the SSH server
            if ctx:
                ctx.info(f"Connecting to {host}:{port}...")
            
            async with asyncssh.connect(**conn_params) as conn:
                if ctx:
                    ctx.info("Connected. Creating temporary script...")
                
                # Create a temporary script on the remote system
                temp_script = "temp_script_" + ''.join([str(x) for x in asyncio.get_event_loop().time_ns()])
                
                # Upload the script
                upload_cmd = f"cat > /tmp/{temp_script} << 'EOF'\n{script_content}\nEOF\nchmod +x /tmp/{temp_script}"
                upload_result = await conn.run(upload_cmd)
                
                if upload_result.exit_status != 0:
                    logger.error(f"Failed to create temporary script: {upload_result.stderr}")
                    return f"Failed to create temporary script:\n{upload_result.stderr}"
                
                if ctx:
                    ctx.info(f"Executing script /tmp/{temp_script}...")
                
                # Execute the script
                exec_result = await conn.run(f"/bin/bash /tmp/{temp_script}", timeout=timeout)
                
                # Clean up
                await conn.run(f"rm -f /tmp/{temp_script}")
                
                # Prepare the output
                output = f"Script execution on {host}:\n\n"
                
                if exec_result.exit_status == 0:
                    output += "Status: Success\n\n"
                else:
                    output += f"Status: Failed (exit code: {exec_result.exit_status})\n\n"
                
                if exec_result.stdout:
                    output += f"STDOUT:\n{exec_result.stdout}\n\n"
                
                if exec_result.stderr:
                    output += f"STDERR:\n{exec_result.stderr}\n"
                
                if ctx:
                    ctx.info(f"Script execution completed with exit code: {exec_result.exit_status}")
                
                return output
                
        except asyncssh.Error as e:
            logger.error(f"SSH connection error: {e}")
            return f"SSH connection error: {str(e)}"
        except asyncio.TimeoutError:
            logger.error(f"Script execution timed out")
            return f"Script execution timed out after {timeout} seconds"
        except Exception as e:
            logger.error(f"Error executing SSH script: {e}")
            return f"Error executing SSH script: {str(e)}"
