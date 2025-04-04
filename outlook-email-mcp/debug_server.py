"""
Debug script to troubleshoot MCP server issues
"""
import os
import sys
import logging
import inspect
import asyncio
import win32com.client

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("debug")

def check_outlook_com():
    """Check if Outlook COM interface is accessible"""
    logger.info("Checking Outlook COM interface...")
    
    try:
        # Create Outlook application object
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        
        # Get inbox folder
        inbox = namespace.GetDefaultFolder(6)  # 6 = olFolderInbox
        
        logger.info(f"Successfully connected to Outlook")
        logger.info(f"Inbox contains {inbox.Items.Count} items")
        
        return True
    except Exception as e:
        logger.error(f"Error connecting to Outlook COM: {e}")
        return False

def check_imports():
    """Check if all required modules can be imported"""
    logger.info("Checking imports...")
    required_modules = [
        "mcp.server.fastmcp",
        "win32com.client",
        "dotenv",
        "asyncio"
    ]
    
    success = True
    for module_name in required_modules:
        try:
            __import__(module_name)
            logger.info(f"✓ {module_name}")
        except ImportError as e:
            logger.error(f"✗ {module_name}: {e}")
            success = False
    
    return success

def check_source_files():
    """Check if all source files exist and can be imported"""
    logger.info("Checking source files...")
    
    source_files = [
        "src/outlook_client.py",
        "src/outlook_client_part2.py",
        "src/tools_email_retrieval.py",
        "src/tools_email_sending.py",
        "outlook_email_server.py"
    ]
    
    success = True
    for file_path in source_files:
        if os.path.exists(file_path):
            logger.info(f"✓ {file_path}")
        else:
            logger.error(f"✗ {file_path} not found")
            success = False
    
    return success

def check_registration_functions():
    """Check if registration functions are properly defined"""
    logger.info("Checking registration functions...")
    
    try:
        # Import the modules
        sys.path.insert(0, os.path.dirname(__file__))
        from src.tools_email_retrieval import register_retrieval_tools
        from src.tools_email_sending import register_sending_tools
        
        # Check if they're functions
        if callable(register_retrieval_tools) and callable(register_sending_tools):
            logger.info("✓ Registration functions are properly defined")
            
            # Check function signatures
            retrieval_sig = inspect.signature(register_retrieval_tools)
            sending_sig = inspect.signature(register_sending_tools)
            
            logger.info(f"register_retrieval_tools parameters: {retrieval_sig}")
            logger.info(f"register_sending_tools parameters: {sending_sig}")
            
            return True
        else:
            logger.error("✗ Registration functions are not callable")
            return False
    except Exception as e:
        logger.error(f"Error checking registration functions: {e}")
        return False

async def debug_client_initialization():
    """Debug the Outlook client initialization"""
    logger.info("Debugging Outlook client initialization...")
    
    try:
        # Import the client class
        from src.outlook_client import OutlookClient
        from src.outlook_client_part2 import OutlookClientPart2
        
        # Create the combined class
        class CombinedClient(OutlookClient, OutlookClientPart2):
            pass
        
        # Create an instance
        client = CombinedClient()
        
        # Test initialization
        success = await client.initialize()
        
        if success:
            logger.info("✓ Outlook client initialized successfully")
            
            # Test get_inbox_messages
            messages = await client.get_inbox_messages(limit=5)
            logger.info(f"Retrieved {len(messages)} messages")
            
            return True
        else:
            logger.error("✗ Outlook client initialization failed")
            return False
    except Exception as e:
        logger.error(f"Error during client initialization: {e}")
        return False

def main():
    """Run all debug checks"""
    logger.info("Starting MCP server debug...")
    
    # Run checks
    checks = [
        ("Outlook COM interface", check_outlook_com()),
        ("Required imports", check_imports()),
        ("Source files", check_source_files()),
        ("Registration functions", check_registration_functions()),
        ("Client initialization", asyncio.run(debug_client_initialization()))
    ]
    
    # Print summary
    logger.info("\n--- Debug Summary ---")
    
    all_success = True
    for name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {name}")
        if not result:
            all_success = False
    
    if all_success:
        logger.info("\nAll checks passed! The server should be working correctly.")
        logger.info("If Claude still doesn't show the tools, try restarting the Claude app.")
    else:
        logger.info("\nSome checks failed. Please address the issues mentioned above.")
    
    return all_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
