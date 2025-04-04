import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import functions to test
from latex_compiler_mcp import parse_latex_log, run_pdflatex

class TestLatexCompiler:
    def test_parse_latex_log(self):
        # Create a sample log content
        log_content = """
This is pdfTeX, Version 3.141592653-2.6-1.40.22 (MiKTeX 21.3)
entering extended mode
(./test.tex
LaTeX2e <2020-10-01> patch level 4
! Undefined control sequence.
l.10 \\nonexistentcommand
                        
LaTeX Warning: Reference `nonexistent' on page 1 undefined
LaTeX Warning: Citation `missing' on page 1 undefined
! LaTeX Error: File `nonexistentpackage.sty' not found.
        """
        
        # Parse the log
        errors = parse_latex_log(log_content)
        
        # Check that we correctly identified errors and warnings
        assert len(errors) > 0
        
        # Check for undefined control sequence
        error_types = [e['type'] for e in errors]
        error_messages = [e['message'] for e in errors]
        
        assert 'error' in error_types
        assert 'warning' in error_types
        assert any('Undefined control sequence' in msg for msg in error_messages)
        assert any('Reference' in msg for msg in error_messages)
        assert any('Citation' in msg for msg in error_messages)
        assert any('nonexistentpackage' in msg for msg in error_messages)
    
    @pytest.mark.skipif(shutil.which('pdflatex') is None, 
                      reason="pdflatex not installed")
    def test_run_pdflatex(self):
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple LaTeX file
            tex_path = os.path.join(tmpdir, 'test.tex')
            with open(tex_path, 'w') as f:
                f.write(r"""
\documentclass{article}
\begin{document}
Hello, world!
\end{document}
                """)
            
            # Run pdflatex
            success, log, error = run_pdflatex(tex_path, tmpdir)
            
            # Check that it compiled successfully
            assert success
            assert os.path.exists(os.path.join(tmpdir, 'test.pdf'))
