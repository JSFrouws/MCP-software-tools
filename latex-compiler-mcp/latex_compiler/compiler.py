"""
LaTeX compilation functions and utilities
"""

import os
import subprocess
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .error_parser import parse_latex_log

# Configure logging
logger = logging.getLogger("latex-compiler-mcp")

def run_pdflatex(file_path: str, output_dir: Optional[str] = None, 
                 options: Optional[List[str]] = None) -> Tuple[bool, str, str]:
    """
    Run pdflatex on the given file
    
    Args:
        file_path: Path to the .tex file
        output_dir: Directory to store output files (default: same as input)
        options: Additional pdflatex options
        
    Returns:
        Tuple of (success, log_output, error_message)
    """
    if not os.path.exists(file_path):
        return False, "", f"File not found: {file_path}"
    
    # Ensure file has .tex extension
    if not file_path.lower().endswith('.tex'):
        return False, "", f"Not a TeX file: {file_path}"
    
    # Determine the output directory
    if output_dir is None:
        output_dir = os.path.dirname(file_path)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Build the command
    cmd = ["pdflatex"]
    
    # Add standard options
    cmd.extend([
        "-interaction=nonstopmode",  # Don't stop on errors
        "-synctex=1",                # Generate SyncTeX data
        "-file-line-error",          # File and line error style
    ])
    
    # Add custom options
    if options:
        cmd.extend(options)
    
    # Add output directory
    cmd.extend([f"-output-directory={output_dir}"])
    
    # Add the input file
    cmd.append(file_path)
    
    # Run the command
    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        # Get the log file path
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        log_file = os.path.join(output_dir, f"{base_name}.log")
        log_content = ""
        
        # Read the log file if it exists
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
        
        # Check if PDF was created
        pdf_file = os.path.join(output_dir, f"{base_name}.pdf")
        success = os.path.exists(pdf_file)
        
        return success, log_content, result.stderr
        
    except Exception as e:
        logger.error(f"Error running pdflatex: {str(e)}")
        return False, "", str(e)

def compile_latex(file_path: str, output_dir: Optional[str] = None, 
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
    # Normalize path
    file_path = os.path.abspath(file_path)
    
    if output_dir:
        output_dir = os.path.abspath(output_dir)
    else:
        output_dir = os.path.dirname(file_path)
    
    # Check if the file exists
    if not os.path.exists(file_path):
        return f"Error: File not found: {file_path}"
    
    start_time = datetime.now()
    
    # Run pdflatex multiple times if requested
    all_errors = []
    final_success = False
    log_content = ""
    
    for run in range(1, runs + 1):
        logger.info(f"Starting compilation run {run}/{runs}")
        
        success, log_content, error_msg = run_pdflatex(file_path, output_dir)
        
        # Parse errors from the log
        errors = parse_latex_log(log_content)
        all_errors.extend(errors)
        
        # Update success flag
        final_success = success
        
        # If there are fatal errors, no need to continue
        if not success and any(e['type'] == 'error' for e in errors):
            break
    
    # Clean auxiliary files if requested
    if clean and final_success:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        for ext in ['.aux', '.log', '.out', '.toc', '.lof', '.lot', '.bbl', '.blg', '.synctex.gz']:
            aux_file = os.path.join(output_dir, f"{base_name}{ext}")
            if os.path.exists(aux_file):
                os.remove(aux_file)
    
    # Prepare the result message
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    if final_success:
        result = f"✓ Compilation successful! ({elapsed_time:.2f} seconds, {runs} runs)\n"
        
        # Add the path to the output PDF
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
        result += f"PDF created: {pdf_path}\n"
        
        # Add any warnings
        warnings = [e for e in all_errors if e['type'] == 'warning']
        if warnings:
            result += f"\nWarnings ({len(warnings)}):\n"
            for i, warning in enumerate(warnings[:10], 1):
                result += f"{i}. {warning['message']}\n"
            
            if len(warnings) > 10:
                result += f"...and {len(warnings) - 10} more warnings\n"
    else:
        result = f"✗ Compilation failed after {elapsed_time:.2f} seconds\n\n"
        
        # Add errors
        errors = [e for e in all_errors if e['type'] == 'error']
        if errors:
            result += f"Errors ({len(errors)}):\n"
            for i, error in enumerate(errors[:5], 1):
                if 'line' in error:
                    result += f"{i}. Line {error['line']}: {error['message']}\n"
                    if 'context' in error:
                        result += f"   Context: {error['context']}\n"
                else:
                    result += f"{i}. {error['message']}\n"
            
            if len(errors) > 5:
                result += f"...and {len(errors) - 5} more errors\n"
        
        # Include error message from stderr if available
        if error_msg and not any(e['type'] == 'error' for e in all_errors):
            result += f"\nAdditional error message:\n{error_msg}\n"
    
    return result

def get_log_file(file_path: str) -> str:
    """
    Get the LaTeX compilation log file
    
    Args:
        file_path: Path to the .tex file
    """
    # Normalize path
    file_path = os.path.abspath(file_path)
    
    # Get the log path
    output_dir = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    log_path = os.path.join(output_dir, f"{base_name}.log")
    
    # Check if the log exists
    if not os.path.exists(log_path):
        return f"Error: Log file not found: {log_path}"
    
    # Read the log
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as log_file:
            log_content = log_file.read()
        
        return log_content
    except Exception as e:
        logger.error(f"Error reading log file: {str(e)}")
        return f"Error reading log file: {str(e)}"
