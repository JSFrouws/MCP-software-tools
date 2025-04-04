# Outlook Email MCP Server

An MCP server that allows Claude and other AI assistants to interact with your Outlook emails directly through the Windows COM interface.

## Features

- Retrieve incoming emails from your inbox
- Get conversation history with specific students/contacts
- Create draft email responses for your review
- Send emails directly (with your approval)
- Zip folders and attach them to emails
- Search for specific emails by keyword or sender

## Requirements

- Windows OS (this server uses the Windows COM interface)
- Outlook desktop application installed and configured
- Python 3.8 or higher
- pywin32 package

## Setup Instructions

### 1. Ensure Outlook is Properly Configured

1. Make sure Outlook is installed and set up with your email account
2. Ensure you can send and receive emails normally through the Outlook application

### 2. Install Dependencies

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Test the Server

You can run the server directly to test if it can connect to Outlook:

```bash
# Make sure your virtual environment is activated
python outlook_email_server.py
```

If successful, you should see:
```
Successfully connected to Outlook
All MCP tools registered successfully
```

### 4. Configure Claude for Desktop

1. Add this server to your Claude for Desktop config:

```json
{
  "mcpServers": {
    "outlook-email": {
      "command": "C:\\path\\to\\venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\outlook_email_server.py"]
    }
  }
}
```

## Usage

Once configured, you can ask Claude things like:

- "Show me my recent emails"
- "Get my conversation history with student@example.com"
- "Help me write a response to John's email about the midterm exam"
- "Send an email to student@example.com about the homework assignment"
- "Zip the project folder at C:\Projects\StudentAssignments and email it to professor@university.edu"

## Troubleshooting

### Common Issues

- **"Outlook client not initialized"**: Make sure Outlook is running and your account is properly configured
- **Access Denied Errors**: You may need to run Claude Desktop as the same user that has Outlook configured
- **First Run Security Prompt**: Windows may show a security prompt the first time Outlook is accessed via COM, allow the access

### Security Considerations

This server interacts directly with your Outlook application using Windows COM. It will have the same permissions as your Windows user account for accessing emails.

## Project Structure

- `outlook_email_server.py`: Main server file
- `src/`: Directory containing modular components
  - `outlook_client.py`: Outlook COM client for retrieving emails
  - `outlook_client_part2.py`: Methods for sending emails and searching
  - `tools_email_retrieval.py`: MCP tools for retrieving and searching emails
  - `tools_email_sending.py`: MCP tools for creating drafts and sending emails
  - `tools_attachments.py`: MCP tools for handling attachments and file operations
