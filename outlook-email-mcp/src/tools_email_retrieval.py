"""
MCP tools for retrieving emails and conversation history
"""
import logging
import re

logger = logging.getLogger("outlook-email-mcp.tools")

def register_retrieval_tools(mcp, outlook_client):
    """Register tools for retrieving and searching emails"""
    
    @mcp.resource("emails://inbox")
    async def get_inbox_emails() -> str:
        """Retrieve recent emails from the inbox"""
        try:
            if not outlook_client:
                return "Outlook client not initialized"
            
            # Use a fixed limit
            limit = 20
            
            messages = await outlook_client.get_inbox_messages(limit=limit)
            
            # Format as a readable text list
            result = f"# Recent Inbox Emails ({len(messages)} messages)\n\n"
            
            for msg in messages:
                sent_time = msg.get("receivedDateTime", "")
                from_email = msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown")
                from_name = msg.get("from", {}).get("emailAddress", {}).get("name", from_email)
                
                result += f"## {msg.get('subject', 'No Subject')}\n"
                result += f"**From:** {from_name} <{from_email}>\n"
                result += f"**Time:** {sent_time}\n"
                result += f"**ID:** {msg.get('id')}\n\n"
                result += f"{msg.get('bodyPreview', 'No preview available')}...\n\n"
                result += "---\n\n"
            
            return result
        except Exception as e:
            logger.error(f"Error getting inbox emails: {e}")
            return f"Error retrieving emails: {str(e)}"

    @mcp.tool()
    async def get_email_details(email_id: str) -> str:
        """
        Get the full content of a specific email
        
        Args:
            email_id: The ID of the email to retrieve
        """
        try:
            if not outlook_client:
                return "Outlook client not initialized"
            
            message = await outlook_client.get_message_by_id(email_id)
            
            if not message:
                return f"Email with ID {email_id} not found"
            
            # Format the email details
            result = f"# Email: {message.Subject}\n\n"
            result += f"**From:** {message.SenderName} <{message.SenderEmailAddress}>\n"
            
            # Get recipients
            recipients = []
            for recipient in message.Recipients:
                recipients.append(f"{recipient.Name} <{recipient.Address}>")
            
            result += f"**To:** {', '.join(recipients)}\n"
            result += f"**Time:** {message.ReceivedTime.strftime('%Y-%m-%d %H:%M:%S')}\n"
            result += f"**ID:** {message.EntryID}\n\n"
            
            # Handle body content
            if message.BodyFormat == 2:  # 2 = HTML
                # Simple HTML tag removal for better readability
                body_text = re.sub(r'<[^>]*>', ' ', message.HTMLBody)
                body_text = re.sub(r'\s+', ' ', body_text).strip()
                result += f"## Content\n\n{body_text}\n\n"
                result += "## Original HTML Content\n\n```html\n" + message.HTMLBody + "\n```\n"
            else:
                result += f"## Content\n\n{message.Body}\n\n"
            
            # Check for attachments
            if message.Attachments.Count > 0:
                result += f"## Attachments ({message.Attachments.Count})\n\n"
                for i in range(1, message.Attachments.Count + 1):
                    attachment = message.Attachments.Item(i)
                    result += f"- {attachment.DisplayName} ({attachment.Size} bytes)\n"
            
            return result
        except Exception as e:
            logger.error(f"Error getting email details: {e}")
            return f"Error retrieving email details: {str(e)}"

    @mcp.tool()
    async def get_conversation_history(email_address: str, limit: int = 10) -> str:
        """
        Get conversation history with a specific student/person
        
        Args:
            email_address: The email address of the student/person
            limit: Maximum number of emails to retrieve
        """
        try:
            if not outlook_client:
                return "Outlook client not initialized"
            
            # Sanitize input
            email_address = email_address.strip().lower()
            limit = min(int(limit), 20) if limit else 10
            
            # Get conversation history
            messages = await outlook_client.get_conversation_history(email_address, limit=limit)
            
            # Format as a readable conversation history
            result = f"# Conversation History with {email_address} ({len(messages)} messages)\n\n"
            
            if not messages:
                result += "No previous messages found with this email address.\n"
                return result
            
            for msg in messages:
                # Determine if this is an incoming or outgoing message
                direction = msg.get("direction", "FROM")
                from_email = msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown")
                from_name = msg.get("from", {}).get("emailAddress", {}).get("name", from_email)
                
                sent_time = msg.get("receivedDateTime", "")
                
                result += f"## [{direction} STUDENT] {msg.get('subject', 'No Subject')}\n"
                result += f"**From:** {from_name} <{from_email}>\n"
                result += f"**Time:** {sent_time}\n"
                result += f"**ID:** {msg.get('id')}\n\n"
                
                # Extract the body preview
                result += f"{msg.get('bodyPreview', 'No preview available')}...\n\n"
                result += "---\n\n"
            
            return result
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return f"Error retrieving conversation history: {str(e)}"

    @mcp.tool()
    async def search_emails(query: str, limit: int = 10) -> str:
        """
        Search emails using keywords or filters
        
        Args:
            query: Search query text or email address
            limit: Maximum number of results to return
        """
        try:
            if not outlook_client:
                return "Outlook client not initialized"
            
            # Search for emails
            messages = await outlook_client.search_emails(query, limit=limit)
            
            # Format as a readable text list
            result = f"# Search Results for '{query}' ({len(messages)} messages)\n\n"
            
            if not messages:
                result += "No messages found matching your search query.\n"
                return result
            
            for msg in messages:
                sent_time = msg.get("receivedDateTime", "")
                from_email = msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown")
                from_name = msg.get("from", {}).get("emailAddress", {}).get("name", from_email)
                
                result += f"## {msg.get('subject', 'No Subject')}\n"
                result += f"**From:** {from_name} <{from_email}>\n"
                result += f"**Time:** {sent_time}\n"
                result += f"**ID:** {msg.get('id')}\n\n"
                result += f"{msg.get('bodyPreview', 'No preview available')}...\n\n"
                result += "---\n\n"
            
            return result
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return f"Error searching emails: {str(e)}"
