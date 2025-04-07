"""
Generic MCP Tool Set - Main Server

This server provides a collection of network and system administration tools
using the Model Context Protocol (MCP).
"""

from mcp.server.fastmcp import FastMCP, Context
import asyncio
import logging
import importlib
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GenericMcpToolSet")

# Initialize FastMCP server
mcp = FastMCP(
    "GenericMcpToolSet",
    dependencies=["mcp", "asyncssh", "python-dotenv"]
)

# Dynamically load all tools from the tools directory
def load_tools():
    """Dynamically load and register all tools from the tools directory"""
    tools_dir = os.path.join(os.path.dirname(__file__), "tools")
    sys.path.insert(0, os.path.dirname(__file__))
    
    logger.info(f"Loading tools from {tools_dir}")
    
    # Iterate through all .py files in the tools directory
    for filename in os.listdir(tools_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"tools.{filename[:-3]}"
            logger.info(f"Loading module: {module_name}")
            
            try:
                # Import the module
                module = importlib.import_module(module_name)
                
                # Look for a register_tools function
                if hasattr(module, "register_tools"):
                    module.register_tools(mcp)
                    logger.info(f"Successfully registered tools from {module_name}")
                else:
                    logger.warning(f"Module {module_name} does not have a register_tools function")
            except Exception as e:
                logger.error(f"Error loading module {module_name}: {e}")

# Load tools at startup
# Note: This directly loads tools instead of using @mcp.lifespan() which may not be
# available in all versions of the MCP SDK (caused AttributeError)
logger.info("Initializing Generic MCP Tool Set")
load_tools()
logger.info("All tools loaded successfully")

if __name__ == "__main__":
    mcp.run()
