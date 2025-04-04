"""
Test script to check if MCP tools are properly registered
"""
import sys
import os
import logging
import importlib.util

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def main():
    """Check if the MCP tools are properly registered"""
    logger.info("Checking MCP tools registration...")
    
    # Check if the server module can be imported
    try:
        # Import the server module
        spec = importlib.util.spec_from_file_location("server", "outlook_email_server.py")
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        
        # Access the MCP server instance
        mcp = server.mcp
        
        # Check for registered resources
        resources = mcp.resources if hasattr(mcp, 'resources') else []
        logger.info(f"Registered resources: {len(resources)}")
        for resource in resources:
            logger.info(f"  - {resource}")
        
        # Check for registered tools
        tools = mcp.tools if hasattr(mcp, 'tools') else []
        logger.info(f"Registered tools: {len(tools)}")
        for tool in tools:
            logger.info(f"  - {tool}")
        
        # Check for registered prompts
        prompts = mcp.prompts if hasattr(mcp, 'prompts') else []
        logger.info(f"Registered prompts: {len(prompts)}")
        for prompt in prompts:
            logger.info(f"  - {prompt}")
        
        if not resources and not tools and not prompts:
            logger.error("No tools, resources, or prompts are registered!")
            logger.info("Please check that the registration functions are being called correctly.")
            return False
        
        logger.info("Tools registration check completed successfully.")
        return True
    
    except Exception as e:
        logger.error(f"Error checking tools: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
