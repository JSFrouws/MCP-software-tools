"""
Network Ping Tool - MCP tool for pinging network devices

This tool provides functions to ping devices on the network and check their availability.
"""

import asyncio
import platform
import subprocess
import logging
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP, Context

logger = logging.getLogger("GenericMcpToolSet.network_ping")

def register_tools(mcp: FastMCP):
    """Register all tools in this module with the MCP server"""
    
    @mcp.tool()
    async def ping_device(
        host: str,
        count: int = 4,
        timeout: int = 5,
        ctx: Context = None
    ) -> str:
        """
        Ping a network device to check if it's online
        
        Args:
            host: The hostname or IP address to ping
            count: Number of ping packets to send (default: 4)
            timeout: Timeout in seconds (default: 5)
        
        Returns:
            Result of the ping operation
        """
        logger.info(f"Pinging {host} with count={count}, timeout={timeout}")
        
        if ctx:
            ctx.info(f"Starting ping to {host}...")
        
        try:
            # Determine the correct ping command based on the operating system
            system = platform.system().lower()
            
            if system == "windows":
                # Windows ping command
                args = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
            else:
                # Linux/Unix ping command
                args = ["ping", "-c", str(count), "-W", str(timeout), host]
            
            if ctx:
                ctx.info(f"Executing: {' '.join(args)}")
            
            # Run ping command and capture output
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                result = f"Device {host} is reachable.\n\n{stdout.decode()}"
                if ctx:
                    ctx.info(f"Ping to {host} successful")
            else:
                result = f"Device {host} is unreachable.\n\n{stdout.decode()}\n{stderr.decode()}"
                if ctx:
                    ctx.info(f"Ping to {host} failed")
            
            return result
            
        except Exception as e:
            logger.error(f"Error pinging {host}: {e}")
            return f"Error pinging {host}: {str(e)}"
    
    @mcp.tool()
    async def ping_multiple_devices(
        hosts: str,
        count: int = 2,
        timeout: int = 3,
        ctx: Context = None
    ) -> str:
        """
        Ping multiple network devices to check if they're online
        
        Args:
            hosts: Comma-separated list of hostnames or IP addresses
            count: Number of ping packets to send to each host (default: 2)
            timeout: Timeout in seconds (default: 3)
        
        Returns:
            Results of all ping operations
        """
        host_list = [h.strip() for h in hosts.split(",") if h.strip()]
        
        if not host_list:
            return "No valid hosts provided"
        
        if ctx:
            ctx.info(f"Starting ping to multiple devices: {host_list}")
        
        results = []
        total = len(host_list)
        
        for i, host in enumerate(host_list):
            if ctx:
                # Report progress
                await ctx.report_progress(i, total)
                ctx.info(f"Pinging {host} ({i+1}/{total})")
            
            # Call the single ping function
            result = await ping_device(host, count, timeout)
            results.append(f"### Device: {host}\n{result}\n")
            
            # Small delay between pings
            await asyncio.sleep(0.5)
        
        if ctx:
            await ctx.report_progress(total, total)
            ctx.info("All ping operations completed")
        
        return "\n".join(results)
