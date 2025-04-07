"""
LaTeX Compiler MCP - A Model Context Protocol server for LaTeX compilation
"""

from .server import mcp
from .compiler import compile_latex, run_pdflatex
from .error_parser import parse_latex_log
from .pdf_utils import get_pdf_page, get_pdf_base64

# Version information
__version__ = "0.1.0"
