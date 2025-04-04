# LaTeX Compiler MCP

An MCP (Model Context Protocol) server for compiling LaTeX documents and processing errors.

## Features

- **LaTeX Compilation**: Compile `.tex` files using `pdflatex`
- **Error Processing**: Parse and format LaTeX compilation errors
- **PDF Visualization**: Convert PDF pages to images for viewing
- **Log Analysis**: Extract and process LaTeX log files

## Installation

```bash
# Install the package
pip install -e .

# If on Windows, ensure poppler is installed for PDF to image conversion
# You can download it from: https://github.com/oschwartz10612/poppler-windows/releases
# Add the bin/ directory to your PATH
```

## Requirements

- Python 3.7 or higher
- pdflatex/TeXLive installed and available in PATH
- Poppler (for PDF to image conversion)
- MCP client (e.g., Claude Desktop, or any client that supports MCP)

## Usage as MCP Server

For Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "latex": {
      "command": "python",
      "args": ["-m", "latex_compiler_mcp"],
      "env": {}
    }
  }
}
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

## Example Usage

Once configured, you can ask Claude:

- "Compile my LaTeX document at C:/path/to/document.tex"
- "Show me the first page of the compiled PDF"
- "What errors are in my LaTeX document?"

## License

MIT
