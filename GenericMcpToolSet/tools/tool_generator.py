"""
MCP Tool Generator - Tool for creating new MCP tools

This tool helps create new MCP tool modules by generating template code.
"""

import os
import logging
import asyncio
import platform
import subprocess
from datetime import datetime
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP, Context

logger = logging.getLogger("GenericMcpToolSet.tool_generator")

# Template for a new tool module
TOOL_MODULE_TEMPLATE = '''"""
{module_name} - {module_description}

{module_long_description}
"""

import logging
from typing import Optional, Dict, Any, List
from mcp.server.fastmcp import FastMCP, Context

logger = logging.getLogger("GenericMcpToolSet.{module_name_lower}")

def register_tools(mcp: FastMCP):
    """Register all tools in this module with the MCP server"""
    
    @mcp.tool()
    async def {tool_function_name}(
        {tool_parameters}
        ctx: Context = None
    ) -> str:
        """
        {tool_description}
        
        Args:
{tool_args_doc}
        
        Returns:
            Result of the operation
        """
        logger.info(f"Executing {tool_function_name}")
        
        if ctx:
            ctx.info("Starting {tool_function_name}...")
        
        try:
            # TODO: Implement your tool logic here
            result = "Tool execution successful!\\n\\n"
            result += "Replace this with your actual implementation."
            
            return result
            
        except Exception as e:
            logger.error(f"Error in {tool_function_name}: {{e}}")
            return f"Error in {tool_function_name}: {{str(e)}}"
'''

def register_tools(mcp: FastMCP):
    """Register all tools in this module with the MCP server"""
    
    @mcp.tool()
    async def create_mcp_tool(
        module_name: str,
        module_description: str,
        tool_function_name: str,
        tool_description: str,
        parameters: str = "param1: str, param2: int = 0,",
        long_description: Optional[str] = None,
        ctx: Context = None
    ) -> str:
        """
        Create a new MCP tool module from a template
        
        Args:
            module_name: Name of the new module (e.g., 'file_manager')
            module_description: Short description of the module
            tool_function_name: Name of the main tool function
            tool_description: Description of the tool function
            parameters: Parameters for the tool function (with types)
            long_description: Optional longer description of the module
        
        Returns:
            Status of the tool creation operation
        """
        logger.info(f"Creating new MCP tool: {module_name} with function {tool_function_name}")
        
        if ctx:
            ctx.info(f"Creating new MCP tool module: {module_name}")
        
        try:
            # Get the tools directory path
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            tools_dir = os.path.join(current_dir, "tools")
            
            # Create filename - lowercase with underscores
            module_name_lower = module_name.lower().replace(" ", "_")
            filename = f"{module_name_lower}.py"
            file_path = os.path.join(tools_dir, filename)
            
            # Check if file already exists
            if os.path.exists(file_path):
                return f"Error: Tool module '{filename}' already exists. Choose a different name or delete the existing file."
            
            # Process parameters for documentation
            param_lines = []
            for param in parameters.split(","):
                param = param.strip()
                if not param:
                    continue
                    
                # Extract parameter name
                param_name = param.split(":")[0].strip()
                param_lines.append(f"            {param_name}: Description of {param_name}")
            
            # Create parameter documentation
            tool_args_doc = "\n".join(param_lines)
            
            # If no long description, use the short one
            if not long_description:
                long_description = module_description
            
            # Create the content from template
            content = TOOL_MODULE_TEMPLATE.format(
                module_name=module_name,
                module_name_lower=module_name_lower,
                module_description=module_description,
                module_long_description=long_description,
                tool_function_name=tool_function_name,
                tool_description=tool_description,
                tool_parameters=parameters,
                tool_args_doc=tool_args_doc
            )
            
            # Write the file
            with open(file_path, 'w') as f:
                f.write(content)
            
            # Success message with next steps
            result = f"Successfully created new MCP tool module: {filename}\n\n"
            result += f"Full path: {file_path}\n\n"
            result += "Next steps:\n"
            result += "1. Edit the file to implement your tool's functionality\n"
            result += "2. Replace the TODO comment with your actual code\n"
            result += "3. Restart the MCP server (or use the restart_claude tool)\n"
            result += "4. Test your new tool by asking Claude to use it\n\n"
            result += "Your tool is already registered and will be loaded automatically."
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating MCP tool: {e}")
            return f"Error creating MCP tool: {str(e)}"
    
    @mcp.tool()
    async def list_available_tools(ctx: Context = None) -> str:
        """
        List all available MCP tools in the current installation
        
        Returns:
            A formatted list of all available tools
        """
        logger.info("Listing available MCP tools")
        
        if ctx:
            ctx.info("Scanning for available MCP tools...")
        
        try:
            # Get the tools directory path
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            tools_dir = os.path.join(current_dir, "tools")
            
            result = "# Available MCP Tools\n\n"
            
            tool_modules = []
            tool_functions = {}
            
            # Scan the tools directory
            for filename in os.listdir(tools_dir):
                if filename.endswith(".py") and not filename.startswith("__"):
                    module_name = filename[:-3]
                    tool_modules.append(module_name)
                    
                    # Read the file to find tool functions
                    file_path = os.path.join(tools_dir, filename)
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    # Extract tool functions (simple parsing, not perfect)
                    functions = []
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if "@mcp.tool()" in line and i < len(lines) - 1:
                            # Look for function definition
                            for j in range(i+1, min(i+5, len(lines))):
                                if "def " in lines[j]:
                                    func_line = lines[j].strip()
                                    func_name = func_line.split("def ")[1].split("(")[0].strip()
                                    functions.append(func_name)
                                    break
                    
                    tool_functions[module_name] = functions
            
            # Format the output
            for module in sorted(tool_modules):
                result += f"## {module}\n"
                
                # Get module file to extract description
                module_path = os.path.join(tools_dir, f"{module}.py")
                description = "No description available"
                
                with open(module_path, 'r') as f:
                    content = f.readlines()
                    for line in content[:10]:  # Look at first 10 lines
                        if line.startswith('"""') and len(content) > 1:
                            # Extract description from docstring
                            description = line.strip('"""').strip()
                            break
                
                result += f"{description}\n\n"
                result += "**Available tools:**\n"
                
                for func in tool_functions.get(module, []):
                    result += f"- `{func}`\n"
                
                result += "\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return f"Error listing available tools: {str(e)}"
