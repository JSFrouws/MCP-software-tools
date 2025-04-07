"""
Error parsing and formatting functions for LaTeX compilation logs
"""

import re
from typing import List, Dict, Any

# Regex patterns for parsing LaTeX errors
ERROR_PATTERNS = {
    'basic_error': re.compile(r'! (.+?)\.(\n|$)'),
    'line_error': re.compile(r'l\.(\d+)'),
    'file_error': re.compile(r'([^()\s]+\.[^()\s]+):(\d+): (.+)'),
    'undefined_reference': re.compile(r'LaTeX Warning: Reference `([^\']+)\' on page \d+ undefined'),
    'undefined_citation': re.compile(r'LaTeX Warning: Citation `([^\']+)\' on page \d+ undefined'),
    'missing_package': re.compile(r'! LaTeX Error: File `([^\']+)\.sty\' not found'),
}

def parse_latex_log(log_text: str) -> List[Dict[str, Any]]:
    """
    Parse LaTeX log output to extract errors and warnings
    
    Args:
        log_text: The log text to parse
        
    Returns:
        List of error/warning dictionaries with relevant information
    """
    errors = []
    
    # Split log by lines
    lines = log_text.split('\n')
    
    # Track the current file being processed
    current_file = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for file changes
        if line.startswith('(') and '.tex' in line:
            # Extract the filename
            file_match = re.search(r'\(([^()]+\.tex)', line)
            if file_match:
                current_file = file_match.group(1)
        
        # Check for basic errors
        error_match = ERROR_PATTERNS['basic_error'].search(line)
        if error_match:
            error_msg = error_match.group(1).strip()
            error_data = {
                'type': 'error',
                'message': error_msg,
                'file': current_file
            }
            
            # Look for line number in the next few lines
            for j in range(i, min(i + 5, len(lines))):
                line_match = ERROR_PATTERNS['line_error'].search(lines[j])
                if line_match:
                    error_data['line'] = int(line_match.group(1))
                    break
            
            # Add context lines
            context_start = max(0, i - 2)
            context_end = min(len(lines), i + 3)
            error_data['context'] = '\n'.join(lines[context_start:context_end])
            
            errors.append(error_data)
        
        # Check for file-specific errors
        file_error_match = ERROR_PATTERNS['file_error'].search(line)
        if file_error_match:
            errors.append({
                'type': 'error',
                'file': file_error_match.group(1),
                'line': int(file_error_match.group(2)),
                'message': file_error_match.group(3),
                'context': line
            })
        
        # Check for undefined references
        ref_match = ERROR_PATTERNS['undefined_reference'].search(line)
        if ref_match:
            errors.append({
                'type': 'warning',
                'message': f"Undefined reference: {ref_match.group(1)}",
                'ref': ref_match.group(1),
                'file': current_file
            })
        
        # Check for undefined citations
        cite_match = ERROR_PATTERNS['undefined_citation'].search(line)
        if cite_match:
            errors.append({
                'type': 'warning',
                'message': f"Undefined citation: {cite_match.group(1)}",
                'citation': cite_match.group(1),
                'file': current_file
            })
        
        # Check for missing packages
        pkg_match = ERROR_PATTERNS['missing_package'].search(line)
        if pkg_match:
            errors.append({
                'type': 'error',
                'message': f"Missing package: {pkg_match.group(1)}",
                'package': pkg_match.group(1),
                'file': current_file
            })
        
        i += 1
    
    return errors
