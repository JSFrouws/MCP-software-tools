"""
Check for syntax issues in terminal_server.py
"""

import ast
import sys
import tokenize
import io

def check_syntax(filename):
    """Check a Python file for syntax errors"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            source = file.read()
        
        print(f"Read {len(source)} characters from {filename}")
        
        # Try to tokenize the file first to find basic issues
        try:
            tokens = list(tokenize.tokenize(io.BytesIO(source.encode('utf-8')).readline))
            print(f"Successfully tokenized the file with {len(tokens)} tokens")
        except tokenize.TokenError as e:
            print(f"❌ Tokenization error: {e}")
            return False
        except IndentationError as e:
            print(f"❌ Indentation error during tokenization at line {e.lineno}, column {e.offset}")
            print(f"   {e.text.strip()}")
            print(f"   {' ' * (e.offset-1)}^")
            print(f"   {e.msg}")
            return False
        
        # Try to parse the file
        try:
            tree = ast.parse(source)
            print(f"✅ Successfully parsed the file without syntax errors")
            
            # Basic validation of the AST
            nodes = list(ast.walk(tree))
            print(f"Found {len(nodes)} AST nodes")
            
            return True
        except SyntaxError as e:
            print(f"❌ Syntax error at line {e.lineno}, column {e.offset}")
            print(f"   {e.text.strip() if e.text else ''}")
            if e.offset:
                print(f"   {' ' * (e.offset-1)}^")
            print(f"   {e.msg}")
            return False
        except IndentationError as e:
            print(f"❌ Indentation error at line {e.lineno}, column {e.offset}")
            print(f"   {e.text.strip()}")
            print(f"   {' ' * (e.offset-1)}^")
            print(f"   {e.msg}")
            return False
    except Exception as e:
        print(f"❌ Error reading or processing {filename}: {e}")
        return False

def check_line_by_line(filename):
    """Check each line individually for issues"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        print(f"Checking {len(lines)} lines in {filename}")
        
        for i, line in enumerate(lines, 1):
            # Check for common issues
            if line.strip() and not line.endswith('\n'):
                print(f"Warning: Line {i} doesn't end with a newline")
            
            # Check indentation consistency
            indent = len(line) - len(line.lstrip())
            if indent % 4 != 0 and line.strip() and not line.strip().startswith('#'):
                print(f"Warning: Line {i} has an indent of {indent} spaces (not divisible by 4)")
                print(f"   {line.rstrip()}")
            
            # Check for tabs mixed with spaces
            if '\t' in line.rstrip('\r\n'):
                print(f"Warning: Line {i} contains tabs")
                print(f"   {line.rstrip()}")
    except Exception as e:
        print(f"Error checking lines: {e}")

if __name__ == '__main__':
    # Redirect output to file
    original_stdout = sys.stdout
    with open('syntax_check_results.txt', 'w') as f:
        sys.stdout = f
        
        filename = 'terminal_server.py'
        if len(sys.argv) > 1:
            filename = sys.argv[1]
        
        print(f"=== Checking syntax for {filename} ===")
        syntax_ok = check_syntax(filename)
        
        print("\n=== Checking line by line for {filename} ===")
        check_line_by_line(filename)
    
    # Restore stdout
    sys.stdout = original_stdout
    print(f"Results written to syntax_check_results.txt")
    
    if not syntax_ok:
        sys.exit(1)
