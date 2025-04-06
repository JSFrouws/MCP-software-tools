# Terminal MCP Server

**Updated April 2025: Improved version with enhanced reliability**

This Model Context Protocol (MCP) server provides a truly persistent terminal session that can be accessed through Claude or other MCP clients. It creates a long-running shell process that maintains full state between commands, giving you a genuine terminal/shell experience through Claude.

## Key Features

- **Persistent Command Execution**: Execute commands in a terminal session with full state tracking
- **Working Directory Tracking**: Automatically keeps track of directory changes
- **Exit Code Handling**: Reports command success/failure with proper exit codes
- **Cross-Platform**: Works on Windows (CMD and PowerShell) and Linux/WSL

## Enhanced Persistence Features

This enhanced version includes advanced persistence mechanisms:

1. **System-Level Persistence**
   - Windows Service support for automatic startup
   - Docker containerization for cross-platform deployment
   - Startup task options for standard Windows users

2. **State Management**
   - Automatic state saving and restoration between sessions
   - State backups with rotation for recovery
   - Terminal session state preservation across restarts

3. **Health Monitoring**
   - Built-in health checks and monitoring
   - Performance metrics and diagnostics
   - Self-healing capabilities

4. **Robust Error Handling**
   - Improved signal handling and graceful shutdown
   - Automatic recovery from crashes
   - Detailed logging for troubleshooting

## Installation

### Prerequisites

- Python 3.9+
- MCP SDK (`pip install mcp`)
- UV package manager (recommended)
- For enhanced features: `pip install psutil pywin32` (Windows only)

### Setup Options

#### 1. Standard Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/terminal-mcp.git
cd terminal-mcp

# Run the setup script (Windows)
setup.bat

# Or install dependencies manually
uv venv
uv pip install -r requirements.txt

# Run the server
python terminal_server.py
```

#### 2. Windows Service Installation

```powershell
# Run as Administrator
.\Install-TerminalService.ps1 -Install

# Start the service
.\Install-TerminalService.ps1 -Start

# Check status
.\Install-TerminalService.ps1 -Status
```

#### 3. Docker Installation

```bash
# Build and start the container
docker-compose up -d

# Check container status
docker-compose ps

# View logs
docker-compose logs -f
```

#### 4. User-Level Startup (Non-Admin)

```cmd
# Create Windows startup task
create_startup_task.bat
```

## Usage

### Available Tools

#### `run_command`

Execute a command in the persistent terminal session:

```
Please run "ls -la" in the terminal.
```

#### `get_terminal_info`

Get detailed information about the current terminal session:

```
What's the current state of the terminal session?
```

#### `clear_history`

Clear the command history:

```
Please clear the terminal command history.
```

#### `backup_terminal_state`

Create a backup of the current terminal state:

```
Please create a backup of the terminal state.
```

### Interactive Commands

The server supports multi-step interactive workflows:

```
1. Please run "python" to start the Python interpreter
2. Now run "x = 10" as a Python command
3. Run "print(x * 5)" to see the result
4. Run "exit()" to exit the Python interpreter
```

### Switching Shells (Windows Only)

```
Please run "use powershell" in the terminal.
```

```
Please run "use cmd" in the terminal.
```

## Advanced Configuration

### Health Monitoring

The health monitoring system provides real-time insights into the server's status:

- HTTP endpoint: `terminal://health`
- Metrics: CPU usage, memory usage, uptime, response time
- Status: healthy, warning, error states with detailed diagnostics

### State Management

Terminal state is automatically preserved:

- State file: `state/terminal_state.json`
- Backups: `state/backups/terminal_state_YYYYMMDD_HHMMSS.json`
- Recovery: Automatic restoration from latest state on startup

### Docker Environment Variables

Customize the Docker deployment with these environment variables:

```yaml
environment:
  - MCP_PORT=8000             # Server port
  - BACKUP_INTERVAL=300       # State backup interval (seconds)
  - MAX_BACKUPS=10            # Number of backups to retain
  - LOG_LEVEL=INFO            # Logging verbosity
```

## Recent Fixes (April 2025)

### 1. Working Directory Tracking
- Fixed issue where the terminal wouldn't properly update its internal working directory state
- Now correctly reports current directory in all outputs

### 2. Exit Code Handling
- Fixed issue where commands would incorrectly report exit code 1 (failure) even when successful
- Improved command success/failure detection across all supported shells

### 3. Output Cleanup
- Fixed issue where internal marker text would appear in command output
- Improved command output formatting and cleanup

## Troubleshooting

### Windows Service Issues

Check the Windows service status:

```powershell
Get-Service TerminalMcpServer
```

Review service logs in Event Viewer > Windows Logs > Application.

### Docker Issues

Check container logs:

```bash
docker-compose logs -f
```

### Restoring From Backup

If needed, you can manually restore from a backup:

```python
from state_manager import StateManager

manager = StateManager()
manager.restore_from_backup()  # Latest backup
# Or specify a timestamp
# manager.restore_from_backup("20230101_120000")
```

## Resources and API Endpoints

- `terminal://info` - Detailed information about the terminal session
- `terminal://last_output` - Output from the last executed command
- `terminal://history` - Command history
- `terminal://env` - Current environment variables
- `terminal://health` - Health and diagnostics information

## License

MIT
