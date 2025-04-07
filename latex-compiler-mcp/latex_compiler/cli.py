"""
Command-line interface for the LaTeX Compiler MCP
"""

import os
import sys
import argparse
import logging
from typing import List, Optional

from .server import mcp
from .compiler import compile_latex

def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the LaTeX Compiler MCP CLI
    """
    parser = argparse.ArgumentParser(
        description="LaTeX Compiler MCP Server"
    )
    
    # Create subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Add 'run' command
    run_parser = subparsers.add_parser("run", help="Run the MCP server")
    run_parser.add_argument(
        "--host", 
        default="127.0.0.1", 
        help="Host to bind the server to (if using HTTP transport)"
    )
    run_parser.add_argument(
        "--port", 
        type=int, 
        default=3000, 
        help="Port to bind the server to (if using HTTP transport)"
    )
    run_parser.add_argument(
        "--transport", 
        choices=["stdio", "http"], 
        default="stdio", 
        help="Transport to use for the MCP server"
    )
    
    # Add 'compile' command
    compile_parser = subparsers.add_parser("compile", help="Compile a LaTeX file")
    compile_parser.add_argument(
        "file_path", 
        help="Path to the LaTeX file to compile"
    )
    compile_parser.add_argument(
        "--output-dir", 
        "-o", 
        help="Directory to store output files"
    )
    compile_parser.add_argument(
        "--runs", 
        "-r", 
        type=int, 
        default=1, 
        help="Number of compilation runs"
    )
    compile_parser.add_argument(
        "--clean", 
        "-c", 
        action="store_true", 
        help="Clean auxiliary files after compilation"
    )
    
    # Parse the arguments
    args = parser.parse_args(args)
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Handle commands
    if args.command == "run":
        # Run the MCP server
        if args.transport == "stdio":
            print("Starting LaTeX Compiler MCP server using stdio transport...", file=sys.stderr)
            mcp.run(transport="stdio")
        elif args.transport == "http":
            print(f"Starting LaTeX Compiler MCP server on http://{args.host}:{args.port}...", file=sys.stderr)
            mcp.run(transport="http", host=args.host, port=args.port)
    
    elif args.command == "compile":
        # Compile the LaTeX file
        result = compile_latex(
            args.file_path,
            args.output_dir,
            args.runs,
            args.clean
        )
        print(result)
    
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
