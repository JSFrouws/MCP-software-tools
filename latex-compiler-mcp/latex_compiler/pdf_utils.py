"""
PDF handling and image conversion utilities
"""

import os
import io
import logging
import base64
from typing import Optional

from pdf2image import convert_from_path
from mcp.server.fastmcp import Image

# Configure logging
logger = logging.getLogger("latex-compiler-mcp")

def get_pdf_page(file_path: str, page: str) -> Image:
    """
    Get a specific page from the compiled PDF as an image
    
    Args:
        file_path: Path to the .tex file
        page: Page number or 'all' for first page
    """
    # Normalize path
    file_path = os.path.abspath(file_path)
    
    # Get the PDF path
    output_dir = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
    
    # Check if the PDF exists
    if not os.path.exists(pdf_path):
        raise ValueError(f"PDF not found: {pdf_path}. Run compile_latex tool first.")
    
    # Determine which page to convert
    page_num = 0 if page == 'all' else int(page) - 1
    
    # Convert the page to an image
    try:
        images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
        
        if not images:
            raise ValueError(f"Page {page} not found in PDF")
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        images[0].save(img_byte_arr, format='PNG')
        
        return Image(data=img_byte_arr.getvalue(), format="png")
    except Exception as e:
        logger.error(f"Error converting PDF page to image: {str(e)}")
        raise ValueError(f"Error converting PDF page to image: {str(e)}")

def get_pdf_base64(file_path: str) -> str:
    """
    Get the compiled PDF as a base64 encoded string
    
    Args:
        file_path: Path to the .tex file
    """
    # Normalize path
    file_path = os.path.abspath(file_path)
    
    # Get the PDF path
    output_dir = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
    
    # Check if the PDF exists
    if not os.path.exists(pdf_path):
        return f"Error: PDF not found: {pdf_path}. Run compile_latex tool first."
    
    # Encode the PDF
    try:
        with open(pdf_path, 'rb') as pdf_file:
            encoded_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
        
        return encoded_pdf
    except Exception as e:
        logger.error(f"Error encoding PDF: {str(e)}")
        return f"Error encoding PDF: {str(e)}"
