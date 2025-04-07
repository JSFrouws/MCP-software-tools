# Generic MCP Tool Set

A modular collection of system administration and network tools using the Model Context Protocol (MCP).

## Overview

This project provides a framework for building and using various system administration tools through the Model Context Protocol. The architecture allows for easy addition of new tools as separate modules.

Currently implemented tools:
- **Network Ping Tool**: Ping devices on the network to check their availability
- **SSH Command Executor**: Execute commands and scripts on remote systems via SSH
- **Claude Manager**: Restart Claude Desktop to load new MCP servers
- **Tool Generator**: Create new MCP tool modules from templates

## Requirements

- Python 3.10+
- Model Context Protocol (MCP) library
- AsyncSSH for SSH operations
- Additional dependencies are listed in `requirements.txt`

## Installation

### Automatic Setup (Windows)

1. Run the included setup script:
   ```
   setup_and_run.bat
   ```

2. To both setup and run the server in one step:
   ```
   setup_and_run.bat run
   ```

### Manual Setup

1. Clone this repository
2. Create and activate a virtual environment using uv:
   ```
   uv venv
   .venv\Scripts\activate  # On Windows
   source .venv/bin/activate  # On Linux/Mac
   ```
3. Install dependencies:
   ```
   uv pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and customize as needed:
   ```
   copy .env.example .env  # On Windows
   cp .env.example .env  # On Linux/Mac
   ```

## Usage with Claude Desktop

To use this MCP server with Claude Desktop:

1. Edit your Claude Desktop configuration file to include this server:

```json
{
  "mcpServers": {
    "genericTools": {
      "command": "python",
      "args": [
        "C:/path/to/GenericMcpToolSet/main.py"
      ]
    }
  }
}
```

2. Restart Claude Desktop
3. You can now use the tools by asking Claude to:
   - Ping network devices
   - Execute SSH commands on remote servers
   - Restart Claude to load new MCP servers
   - Create new MCP tool modules

## Architecture

- `main.py`: Main MCP server that dynamically loads tools
- `tools/`: Directory containing all tool modules
  - `network_ping.py`: Network ping functionality
  - `ssh_executor.py`: SSH command execution
  
Each tool module contains a `register_tools(mcp)` function that registers its tools with the MCP server.

## Adding New Tools

To add a new tool:

1. Create a new Python file in the `tools/` directory
2. Implement the tool functions using the MCP decorator syntax
3. Include a `register_tools(mcp)` function
4. The main server will automatically load and register your tools

Example structure for a new tool module:

```python
def register_tools(mcp):
    @mcp.tool()
    def my_new_tool(param1, param2):
        """Tool documentation"""
        # Implementation
        return "Result"
```

## License

MIT License
