"""
MCP Server for Outlook Email Integration using COM Interface

This server allows AI assistants to:
1. Retrieve incoming emails
2. Retrieve conversation history with specific students
3. Prepare draft responses
4. Send emails

Authentication is handled using Windows authentication with the local Outlook client
"""

import os
import logging
import asyncio
import traceback
from datetime import datetime
from typing import Dict, Any

# Import MCP server library
from mcp.server.fastmcp import FastMCP, Context
from dotenv import load_dotenv

# Import our modules
from src.outlook_client import OutlookClient
from src.outlook_client_part2 import OutlookClientPart2
from src.tools_email_retrieval import register_retrieval_tools
from src.tools_email_sending import register_sending_tools
from src.tools_attachments import register_attachment_tools

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("outlook-email-mcp")

# Initialize FastMCP server
mcp = FastMCP(
    "OutlookEmail",
    dependencies=["mcp", "pywin32", "python-dotenv"]
)

# Combine the OutlookClient classes
class CombinedOutlookClient(OutlookClient, OutlookClientPart2):
    """Complete Outlook client with all functionality"""
    pass

# Initialize the Outlook client globally
outlook_client = CombinedOutlookClient()

# Direct initialization function instead of using lifespan
async def initialize_outlook():
    """Initialize the Outlook client"""
    global outlook_client
    
    try:
        # Initialize connection
        success = await outlook_client.initialize()
        if not success:
            logger.error("Failed to initialize Outlook client")
            return False
        
        logger.info("Successfully connected to Outlook")
        return True
    except Exception as e:
        logger.error(f"Error initializing Outlook client: {e}")
        return False

# Run the server if executed directly
if __name__ == "__main__":
    logger.info("Starting Outlook Email MCP Server...")
    
    # Initialize Outlook connection synchronously
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(initialize_outlook())
    
    if success:
        # Register tools and resources with better error handling
        try:
            register_retrieval_tools(mcp, outlook_client)
            register_sending_tools(mcp, outlook_client)
            register_attachment_tools(mcp, outlook_client)
            logger.info("All MCP tools registered successfully")
        except Exception as e:
            logger.error(f"Error registering tools: {e}")
            logger.error(traceback.format_exc())
            logger.warning("Starting with limited functionality due to tool registration failure")
    else:
        logger.warning("Starting with limited functionality due to Outlook connection failure")
    
    # Run the MCP server
    mcp.run()
