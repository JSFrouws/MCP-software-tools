"""
MCP server implementation for LaTeX compilation
"""

import logging
from mcp.server.fastmcp import FastMCP

from .compiler import compile_latex, get_log_file
from .pdf_utils import get_pdf_page, get_pdf_base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("latex-compiler-mcp")

# Initialize FastMCP server
mcp = FastMCP(
    "LaTeXCompiler",
    dependencies=["mcp", "pdf2image", "poppler-utils"]
)

# Register tools
@mcp.tool()
def compile_latex_tool(file_path: str, output_dir: str = None, 
                      runs: int = 1, clean: bool = False) -> str:
    """
    Compile a LaTeX document using pdflatex
    
    Args:
        file_path: Path to the .tex file
        output_dir: Directory for output files (default: same directory as input)
        runs: Number of compilation runs (for references, citations, etc.)
        clean: Whether to clean auxiliary files after compilation
    
    Returns:
        Compilation results as a formatted string
    """
    return compile_latex(file_path, output_dir, runs, clean)

@mcp.tool()
def get_pdf_base64_tool(file_path: str) -> str:
    """
    Get the compiled PDF as a base64 encoded string
    
    Args:
        file_path: Path to the .tex file
    """
    return get_pdf_base64(file_path)

@mcp.tool()
def get_log_file_tool(file_path: str) -> str:
    """
    Get the LaTeX compilation log file
    
    Args:
        file_path: Path to the .tex file
    """
    return get_log_file(file_path)

# Register resources
@mcp.resource("latex://{file_path}/pdf/{page}")
def get_pdf_page_resource(file_path: str, page: str):
    """
    Get a specific page from the compiled PDF as an image
    
    Args:
        file_path: Path to the .tex file
        page: Page number or 'all' for first page
    """
    return get_pdf_page(file_path, page)
