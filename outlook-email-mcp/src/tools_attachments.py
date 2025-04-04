"""
MCP tools for handling attachments
"""
import logging
import os
import zipfile
import tempfile
import shutil
import time

logger = logging.getLogger("outlook-email-mcp.tools")

def register_attachment_tools(mcp, outlook_client):
    """Register tools for handling attachments"""
    
    @mcp.tool()
    async def zip_and_attach_folder(
        folder_path: str,
        to_recipient: str,
        subject: str,
        body: str,
        include_hidden_files: bool = False
    ) -> str:
        """
        Zip a folder and attach it to a new email draft
        
        Args:
            folder_path: Path to the folder to zip
            to_recipient: Email address of the recipient
            subject: Email subject
            body: Email body content
            include_hidden_files: Whether to include hidden files in the zip
        """
        try:
            if not outlook_client:
                return "Outlook client not initialized"
            
            # Validate folder path
            folder_path = os.path.abspath(folder_path)
            if not os.path.exists(folder_path):
                return f"Folder not found: {folder_path}"
            if not os.path.isdir(folder_path):
                return f"Not a folder: {folder_path}"
            
            # Create a unique filename for the zip
            folder_name = os.path.basename(folder_path)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            zip_filename = f"{folder_name}_{timestamp}.zip"
            
            # Create temporary directory for the zip file
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, zip_filename)
                
                # Create the zip file
                file_count = 0
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(folder_path):
                        # Skip hidden directories if not explicitly included
                        if not include_hidden_files and os.path.basename(root).startswith('.'):
                            continue
                        
                        for file in files:
                            # Skip hidden files if not explicitly included
                            if not include_hidden_files and file.startswith('.'):
                                continue
                            
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
                            zipf.write(file_path, arcname)
                            file_count += 1
                
                # Create email with attachment
                outlook = outlook_client.outlook
                mail_item = outlook.CreateItem(0)  # 0 = olMailItem
                
                # Set properties
                mail_item.To = to_recipient
                mail_item.Subject = subject
                mail_item.Body = body
                
                # Add attachment
                mail_item.Attachments.Add(zip_path)
                
                # Save as draft
                mail_item.Save()
                
                return f"Zip file created with {file_count} files and attached to a new email draft.\n\n" \
                       f"**Draft Email:**\n" \
                       f"**To:** {to_recipient}\n" \
                       f"**Subject:** {subject}\n" \
                       f"**Attachment:** {zip_filename} ({os.path.getsize(zip_path) / (1024*1024):.2f} MB)\n\n" \
                       f"The email has been saved as a draft. You can review and send it from Outlook."
        except Exception as e:
            logger.error(f"Error zipping and attaching folder: {e}")
            return f"Error zipping and attaching folder: {str(e)}"
