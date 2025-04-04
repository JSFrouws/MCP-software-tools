"""
MCP tools for creating drafts and sending emails
"""
import logging
from typing import Optional

logger = logging.getLogger("outlook-email-mcp.tools")

def register_sending_tools(mcp, outlook_client):
    """Register tools for creating and sending emails"""
    
    @mcp.tool()
    async def create_email_draft(
        to_recipient: str,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> str:
        """
        Create a draft email that can be reviewed before sending
        
        Args:
            to_recipient: Email address of the recipient
            subject: Email subject
            body: Email body content
            is_html: Whether the body is HTML formatted (default: False)
        """
        try:
            if not outlook_client:
                return "Outlook client not initialized"
            
            # Sanitize input
            to_recipient = to_recipient.strip()
            
            # Create the draft email
            draft = await outlook_client.create_draft(
                to_recipient=to_recipient,
                subject=subject,
                body=body,
                is_html=is_html
            )
            
            if not draft:
                return "Failed to create draft email"
            
            draft_id = draft.get("id")
            
            return f"Draft email created successfully!\n\n**Draft ID:** {draft_id}\n\n**To:** {to_recipient}\n**Subject:** {subject}\n\nUse the send_email tool with this Draft ID to send the email."
        except Exception as e:
            logger.error(f"Error creating email draft: {e}")
            return f"Error creating email draft: {str(e)}"

    @mcp.tool()
    async def send_email(
        message_id: Optional[str] = None,
        to_recipient: Optional[str] = None,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        is_html: bool = False
    ) -> str:
        """
        Send an email, either an existing draft or a new message
        
        Args:
            message_id: ID of a draft message to send (optional)
            to_recipient: Email address of the recipient (required if message_id not provided)
            subject: Email subject (required if message_id not provided)
            body: Email body content (required if message_id not provided)
            is_html: Whether the body is HTML formatted (default: False)
        """
        try:
            if not outlook_client:
                return "Outlook client not initialized"
            
            # Determine if we're sending a draft or creating a new email
            if message_id:
                # Send existing draft
                result = await outlook_client.send_email(message_id=message_id)
                
                if result.get("status") == "error":
                    return f"Error sending email: {result.get('message')}"
                
                return f"Email draft has been sent successfully!\n\n**Message ID:** {message_id}"
            
            elif to_recipient and subject and body:
                # Sanitize input
                to_recipient = to_recipient.strip()
                
                # Send new email
                result = await outlook_client.send_email(
                    to_recipient=to_recipient,
                    subject=subject,
                    body=body,
                    is_html=is_html
                )
                
                if result.get("status") == "error":
                    return f"Error sending email: {result.get('message')}"
                
                return f"Email has been sent successfully!\n\n**To:** {to_recipient}\n**Subject:** {subject}"
            
            else:
                return "Error: Either provide a message_id to send an existing draft, or provide to_recipient, subject, and body to send a new email."
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return f"Error sending email: {str(e)}"

    # Email response template prompt
    @mcp.prompt()
    def prepare_email_response(student_email: str, subject: str) -> str:
        """Create a response to a student email"""
        return f"""I need to respond to an email from a student with email address {student_email} regarding "{subject}".

First, retrieve any previous conversation history with this student to understand the context.

Then, help me craft a professional and helpful response that addresses their concerns while maintaining an appropriate tone for an educator.

The response should include:
- A proper greeting
- Clear answers to their questions
- Any necessary follow-up questions
- A professional closing

I'll review your suggested response before sending it.
"""
