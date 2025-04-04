"""
Outlook client methods for sending and drafting emails
"""
import logging
import re

logger = logging.getLogger("outlook-email-mcp.client")

# Extend the OutlookClient class
class OutlookClientPart2:
    async def create_draft(self, to_recipient, subject, body, is_html=False):
        """Create a draft email message"""
        try:
            # Create a new mail item
            mail_item = self.outlook.CreateItem(0)  # 0 = olMailItem
            
            # Set the properties
            mail_item.To = to_recipient
            mail_item.Subject = subject
            
            if is_html:
                mail_item.HTMLBody = body
            else:
                mail_item.Body = body
            
            # Save as draft
            mail_item.Save()
            
            return {
                "id": mail_item.EntryID,
                "subject": mail_item.Subject,
                "to": mail_item.To
            }
        except Exception as e:
            logger.error(f"Error creating draft: {e}")
            return None
    
    async def send_email(self, message_id=None, to_recipient=None, subject=None, body=None, is_html=False):
        """Send an email, either an existing draft or a new message"""
        try:
            if message_id:
                # Send an existing draft
                mail_item = self.namespace.GetItemFromID(message_id)
                mail_item.Send()
                return {"status": "sent", "id": message_id}
            
            elif to_recipient and subject and body:
                # Create and send a new email
                mail_item = self.outlook.CreateItem(0)  # 0 = olMailItem
                
                # Set properties
                mail_item.To = to_recipient
                mail_item.Subject = subject
                
                if is_html:
                    mail_item.HTMLBody = body
                else:
                    mail_item.Body = body
                
                # Send the email
                mail_item.Send()
                
                return {"status": "sent", "to": to_recipient, "subject": subject}
            
            else:
                raise ValueError("Either message_id or (to_recipient, subject, body) must be provided")
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {"status": "error", "message": str(e)}
    
    async def search_emails(self, query, limit=10):
        """Search emails using a text query"""
        try:
            # Check if query is an email address
            email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if re.match(email_pattern, query):
                # Search by sender email
                inbox = self.namespace.GetDefaultFolder(6)  # Inbox
                filter_string = f"@SQL=\"urn:schemas:httpmail:fromemail\" = '{query}'"
                messages = inbox.Items.Restrict(filter_string)
            else:
                # Search by subject or body text
                inbox = self.namespace.GetDefaultFolder(6)  # Inbox
                filter_string = f"@SQL=(urn:schemas:httpmail:subject LIKE '%{query}%') OR (urn:schemas:httpmail:textdescription LIKE '%{query}%')"
                messages = inbox.Items.Restrict(filter_string)
            
            # Sort by received time (newest first)
            messages.Sort("[ReceivedTime]", True)
            
            # Convert to list
            result = []
            count = 0
            
            for message in messages:
                if count >= limit:
                    break
                
                msg_data = {
                    "id": message.EntryID,
                    "subject": message.Subject,
                    "from": {
                        "emailAddress": {
                            "address": message.SenderEmailAddress,
                            "name": message.SenderName
                        }
                    },
                    "receivedDateTime": message.ReceivedTime.strftime("%Y-%m-%d %H:%M:%S"),
                    "bodyPreview": message.Body[:200].replace("\r\n", " ")
                }
                
                result.append(msg_data)
                count += 1
            
            return result
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []
