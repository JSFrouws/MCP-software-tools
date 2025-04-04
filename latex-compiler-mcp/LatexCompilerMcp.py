
MCP Server for LaTeX Compilation
Provides tools to compile LaTeX documents and process the results


import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import logging
import shutil
import base64
from datetime import datetime

from mcp.server.fastmcp import FastMCP, Context, Image
from pdf2image import convert_from_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(latex-compiler-mcp)

# Initialize FastMCP server
mcp = FastMCP(
    LaTeXCompiler,
    dependencies=[mcp, pdf2image, poppler-utils]
)

# Regex patterns for parsing LaTeX errors
ERROR_PATTERNS = {
    'basic_error' re.compile(r'! (.+).(n$)'),
    'line_error' re.compile(r'l.(d+)'),
    'file_error' re.compile(r'([^()s]+.[^()s]+)(d+) (.+)'),
    'undefined_reference' re.compile(r'LaTeX Warning Reference `([^']+)' on page d+ undefined'),
    'undefined_citation' re.compile(r'LaTeX Warning Citation `([^']+)' on page d+ undefined'),
    'missing_package' re.compile(r'! LaTeX Error File `([^']+).sty' not found'),
}

def parse_latex_log(log_text str) - List[Dict[str, Any]]
    Parse LaTeX log output to extract errors and warnings
    errors = []
    
    # Split log by lines
    lines = log_text.split('n')
    
    # Track the current file being processed
    current_file = None
    
    i = 0
    while i  len(lines)
        line = lines[i]
        
        # Check for file changes
        if line.startswith('(') and '.tex' in line
            # Extract the filename
            file_match = re.search(r'(([^()]+.tex)', line)
            if file_match
                current_file = file_match.group(1)
        
        # Check for basic errors
        error_match = ERROR_PATTERNS['basic_error'].search(line)
        if error_match
            error_msg = error_match.group(1).strip()
            error_data = {
                'type' 'error',
                'message' error_msg,
                'file' current_file
            }
            
            # Look for line number in the next few lines
            for j in range(i, min(i + 5, len(lines)))
                line_match = ERROR_PATTERNS['line_error'].search(lines[j])
                if line_match
                    error_data['line'] = int(line_match.group(1))
                    break
            
            # Add context lines
            context_start = max(0, i - 2)
            context_end = min(len(lines), i + 3)
            error_data['context'] = 'n'.join(lines[context_startcontext_end])
            
            errors.append(error_data)
        
        # Check for file-specific errors
        file_error_match = ERROR_PATTERNS['file_error'].search(line)
        if file_error_match
            errors.append({
                'type' 'error',
                'file' file_error_match.group(1),
                'line' int(file_error_match.group(2)),
                'message' file_error_match.group(3),
                'context' line
            })
        
        # Check for undefined references
        ref_match = ERROR_PATTERNS['undefined_reference'].search(line)
        if ref_match
            errors.append({
                'type' 'warning',
                'message' fUndefined reference {ref_match.group(1)},
                'ref' ref_match.group(1),
                'file' current_file
            })
        
        # Check for undefined citations
        cite_match = ERROR_PATTERNS['undefined_citation'].search(line)
        if cite_match
            errors.append({
                'type' 'warning',
                'message' fUndefined citation {cite_match.group(1)},
                'citation' cite_match.group(1),
                'file' current_file
            })
        
        # Check for missing packages
        pkg_match = ERROR_PATTERNS['missing_package'].search(line)
        if pkg_match
            errors.append({
                'type' 'error',
                'message' fMissing package {pkg_match.group(1)},
                'package' pkg_match.group(1),
                'file' current_file
            })
        
        i += 1
    
    return errors

def run_pdflatex(file_path str, output_dir Optional[str] = None, 
                 options Optional[List[str]] = None) - Tuple[bool, str, str]
    
    Run pdflatex on the given file
    
    Args
        file_path Path to the .tex file
        output_dir Directory to store output files (default same as input)
        options Additional pdflatex options
        
    Returns
        Tuple of (success, log_output, error_message)
    
    if not os.path.exists(file_path)
        return False, , fFile not found {file_path}
    
    # Ensure file has .tex extension
    if not file_path.lower().endswith('.tex')
        return False, , fNot a TeX file {file_path}
    
    # Determine the output directory
    if output_dir is None
        output_dir = os.path.dirname(file_path)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Build the command
    cmd = [pdflatex]
    
    # Add standard options
    cmd.extend([
        -interaction=nonstopmode,  # Don't stop on errors
        -synctex=1,                # Generate SyncTeX data
        -file-line-error,          # File and line error style
    ])
    
    # Add custom options
    if options
        cmd.extend(options)
    
    # Add output directory
    cmd.extend([f-output-directory={output_dir}])
    
    # Add the input file
    cmd.append(file_path)
    
    # Run the command
    try
        logger.info(fRunning command {' '.join(cmd)})
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        # Get the log file path
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        log_file = os.path.join(output_dir, f{base_name}.log)
        log_content = 
        
        # Read the log file if it exists
        if os.path.exists(log_file)
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f
                log_content = f.read()
        
        # Check if PDF was created
        pdf_file = os.path.join(output_dir, f{base_name}.pdf)
        success = os.path.exists(pdf_file)
        
        return success, log_content, result.stderr
        
    except Exception as e
        logger.error(fError running pdflatex {str(e)})
        return False, , str(e)

@mcp.tool()
def compile_latex(file_path str, output_dir Optional[str] = None, 
                 runs int = 1, clean bool = False) - str
    
    Compile a LaTeX document using pdflatex
    
    Args
        file_path Path to the .tex file
        output_dir Directory for output files (default same directory as input)
        runs Number of compilation runs (for references, citations, etc.)
        clean Whether to clean auxiliary files after compilation
    
    Returns
        Compilation results as a formatted string
    
    # Normalize path
    file_path = os.path.abspath(file_path)
    
    if output_dir
        output_dir = os.path.abspath(output_dir)
    else
        output_dir = os.path.dirname(file_path)
    
    # Check if the file exists
    if not os.path.exists(file_path)
        return fError File not found {file_path}
    
    start_time = datetime.now()
    
    # Run pdflatex multiple times if requested
    all_errors = []
    final_success = False
    log_content = 
    
    for run in range(1, runs + 1)
        logger.info(fStarting compilation run {run}{runs})
        
        success, log_content, error_msg = run_pdflatex(file_path, output_dir)
        
        # Parse errors from the log
        errors = parse_latex_log(log_content)
        all_errors.extend(errors)
        
        # Update success flag
        final_success = success
        
        # If there are fatal errors, no need to continue
        if not success and any(e['type'] == 'error' for e in errors)
            break
    
    # Clean auxiliary files if requested
    if clean and final_success
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        for ext in ['.aux', '.log', '.out', '.toc', '.lof', '.lot', '.bbl', '.blg', '.synctex.gz']
            aux_file = os.path.join(output_dir, f{base_name}{ext})
            if os.path.exists(aux_file)
                os.remove(aux_file)
    
    # Prepare the result message
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    if final_success
        result = f✓ Compilation successful! ({elapsed_time.2f} seconds, {runs} runs)n
        
        # Add the path to the output PDF
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        pdf_path = os.path.join(output_dir, f{base_name}.pdf)
        result += fPDF created {pdf_path}n
        
        # Add any warnings
        warnings = [e for e in all_errors if e['type'] == 'warning']
        if warnings
            result += fnWarnings ({len(warnings)})n
            for i, warning in enumerate(warnings[10], 1)
                result += f{i}. {warning['message']}n
            
            if len(warnings)  10
                result += f...and {len(warnings) - 10} more warningsn
    else
        result = f✗ Compilation failed after {elapsed_time.2f} secondsnn
        
        # Add errors
        errors = [e for e in all_errors if e['type'] == 'error']
        if errors
            result += fErrors ({len(errors)})n
            for i, error in enumerate(errors[5], 1)
                if 'line' in error
                    result += f{i}. Line {error['line']} {error['message']}n
                    if 'context' in error
                        result += f   Context {error['context']}n
                else
                    result += f{i}. {error['message']}n
            
            if len(errors)  5
                result += f...and {len(errors) - 5} more errorsn
        
        # Include error message from stderr if available
        if error_msg and not any(e['type'] == 'error' for e in all_errors)
            result += fnAdditional error messagen{error_msg}n
    
    return result

@mcp.resource(latex{file_path}pdf{page})
def get_pdf_page(file_path str, page str) - Image
    
    Get a specific page from the compiled PDF as an image
    
    Args
        file_path Path to the .tex file
        page Page number or 'all' for first page
    
    # Normalize path
    file_path = os.path.abspath(file_path)
    
    # Get the PDF path
    output_dir = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    pdf_path = os.path.join(output_dir, f{base_name}.pdf)
    
    # Check if the PDF exists
    if not os.path.exists(pdf_path)
        raise ValueError(fPDF not found {pdf_path}. Run compile_latex tool first.)
    
    # Determine which page to convert
    page_num = 0 if page == 'all' else int(page) - 1
    
    # Convert the page to an image
    try
        images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
        
        if not images
            raise ValueError(fPage {page} not found in PDF)
        
        # Convert to bytes
        import io
        img_byte_arr = io.BytesIO()
        images[0].save(img_byte_arr, format='PNG')
        
        return Image(data=img_byte_arr.getvalue(), format=png)
    except Exception as e
        logger.error(fError converting PDF page to image {str(e)})
        raise ValueError(fError converting PDF page to image {str(e)})

@mcp.tool()
def get_pdf_base64(file_path str) - str
    
    Get the compiled PDF as a base64 encoded string
    
    Args
        file_path Path to the .tex file
    
    # Normalize path
    file_path = os.path.abspath(file_path)
    
    # Get the PDF path
    output_dir = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    pdf_path = os.path.join(output_dir, f{base_name}.pdf)
    
    # Check if the PDF exists
    if not os.path.exists(pdf_path)
        return fError PDF not found {pdf_path}. Run compile_latex tool first.
    
    # Encode the PDF
    try
        with open(pdf_path, 'rb') as pdf_file
            encoded_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
        
        return encoded_pdf
    except Exception as e
        logger.error(fError encoding PDF {str(e)})
        return fError encoding PDF {str(e)}

@mcp.tool()
def get_log_file(file_path str) - str
    
    Get the LaTeX compilation log file
    
    Args
        file_path Path to the .tex file
    
    # Normalize path
    file_path = os.path.abspath(file_path)
    
    # Get the log path
    output_dir = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    log_path = os.path.join(output_dir, f{base_name}.log)
    
    # Check if the log exists
    if not os.path.exists(log_path)
        return fError Log file not found {log_path}
    
    # Read the log
    try
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as log_file
            log_content = log_file.read()
        
        return log_content
    except Exception as e
        logger.error(fError reading log file {str(e)})
        return fError reading log file {str(e)}

# Run the server if executed directly
if __name__ == __main__
    mcp.run()