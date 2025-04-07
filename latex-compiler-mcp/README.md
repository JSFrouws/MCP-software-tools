# LaTeX Compiler MCP

An MCP (Model Context Protocol) server for compiling LaTeX documents and processing errors.

## Features

- **LaTeX Compilation**: Compile `.tex` files using `pdflatex`
- **Error Processing**: Parse and format LaTeX compilation errors
- **PDF Visualization**: Convert PDF pages to images for viewing
- **Log Analysis**: Extract and process LaTeX log files

## Installation

### Using the setup script

The easiest way to install and set up the environment is using the provided setup script:

```batch
# Run the setup script
setup.bat
```

This will:
1. Create a virtual environment using UV
2. Install all dependencies
3. Check for LaTeX and Poppler installations
4. Verify the environment is working

### Manual installation

```bash
# Create a virtual environment
uv venv

# Activate the environment
.venv\Scripts\activate

# Install in development mode
uv pip install -e .
```

### Additional requirements

- **pdflatex**: Install a LaTeX distribution like [MiKTeX](https://miktex.org/) or [TeX Live](https://www.tug.org/texlive/)
- **Poppler**: Required for PDF to image conversion
  - For Windows, download from: https://github.com/oschwartz10612/poppler-windows/releases
  - Add the bin/ directory to your PATH

## Usage

### As an MCP Server

For Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "latex": {
      "command": ".venv\\Scripts\\latex-compiler-mcp",
      "args": ["run"],
      "env": {}
    }
  }
}
```

### Command-line usage

```bash
# Run the MCP server
latex-compiler-mcp run

# Specify a different transport
latex-compiler-mcp run --transport http --host 127.0.0.1 --port 3000

# Compile a LaTeX file directly
latex-compiler-mcp compile path/to/document.tex

# Compile with multiple runs (for references/citations)
latex-compiler-mcp compile path/to/document.tex --runs 2

# Compile and clean auxiliary files
latex-compiler-mcp compile path/to/document.tex --clean
```

## MCP Tools and Resources

### Tools

- `compile_latex`: Compile a LaTeX document
  - Arguments:
    - `file_path`: Path to the .tex file
    - `output_dir` (optional): Directory for output files
    - `runs` (optional): Number of compilation runs (default: 1)
    - `clean` (optional): Whether to clean auxiliary files (default: false)

- `get_pdf_base64`: Get the compiled PDF as a base64 encoded string
  - Arguments:
    - `file_path`: Path to the .tex file

- `get_log_file`: Get the LaTeX compilation log file
  - Arguments:
    - `file_path`: Path to the .tex file

### Resources

- `latex://{file_path}/pdf/{page}`: Get a specific page from the compiled PDF as an image
  - `file_path`: Path to the .tex file
  - `page`: Page number or 'all' for first page

## Example Usage with Claude

Once configured, you can ask Claude:

- "Compile my LaTeX document at C:/path/to/document.tex"
- "Show me the first page of the compiled PDF"
- "What errors are in my LaTeX document?"
- "Compile this LaTeX file with multiple passes to resolve references"

## Project Structure

```
latex-compiler-mcp/
├── latex_compiler/          # Main package
│   ├── __init__.py          # Package initialization
│   ├── cli.py               # Command-line interface
│   ├── compiler.py          # LaTeX compilation functions
│   ├── error_parser.py      # Error parsing and formatting
│   ├── pdf_utils.py         # PDF conversion utilities
│   └── server.py            # MCP server implementation
├── examples/                # Example LaTeX files
│   ├── example.tex          # Simple LaTeX example
│   └── example_with_errors.tex  # Example with deliberate errors
├── tests/                   # Test suite
│   └── test_latex_compiler.py
├── setup.py                 # Package setup configuration
├── setup.bat                # Windows environment setup script
├── README.md                # This file
└── LICENSE                  # MIT License
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
