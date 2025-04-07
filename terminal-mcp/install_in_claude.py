"""
Helper script to install the Simple Terminal MCP Server in Claude Desktop
"""

import os
import sys
import json
import argparse
from pathlib import Path

def install_in_claude(name: str = "terminal"):
    """Install the terminal MCP server in Claude Desktop"""
    # Determine the Claude config file path
    if sys.platform == "win32":
        config_path = os.path.expandvars(r"%APPDATA%\Claude\claude_desktop_config.json")
    else:
        config_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
    
    # Check if the config file exists
    if not os.path.exists(config_path):
        # Create directory if needed
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        # Create a default config
        config = {"mcpServers": {}}
    else:
        # Read existing config
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {config_path}")
            print("Creating a new configuration...")
            config = {"mcpServers": {}}
        
        # Ensure mcpServers exists
        if "mcpServers" not in config:
            config["mcpServers"] = {}
    
    # Get absolute path to the terminal_server.py script
    script_path = Path(__file__).resolve().parent / "terminal_server.py"
    if not script_path.exists():
        print(f"Error: Could not find terminal_server.py at {script_path}")
        sys.exit(1)
    
    # Convert to string
    script_path_str = str(script_path)
    
    # Handle Windows path (use forward slashes in JSON)
    if sys.platform == "win32":
        script_path_str = script_path_str.replace("\\", "/")
    
    # Add terminal server configuration
    config["mcpServers"][name] = {
        "command": sys.executable,  # Use current Python executable
        "args": [script_path_str]
    }
    
    # Write back to the config file
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Terminal MCP Server installed as '{name}' in Claude Desktop.")
    print(f"Configuration saved to: {config_path}")
    print("Please restart Claude Desktop for the changes to take effect.")

def main():
    parser = argparse.ArgumentParser(description="Install Terminal MCP Server in Claude Desktop")
    parser.add_argument(
        "--name", 
        default="terminal",
        help="Name to use for the terminal server in the configuration (default: terminal)"
    )
    
    args = parser.parse_args()
    install_in_claude(args.name)

if __name__ == "__main__":
    main()
