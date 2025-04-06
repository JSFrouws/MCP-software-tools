"""
Outlook COM client for interacting with local Outlook installation
"""
import re
import logging
from datetime import datetime
import win32com.client

logger = logging.getLogger("outlook-email-mcp.client")

class OutlookClient:
    """Client for Outlook using COM interface"""
    
    def __init__(self):
        self.outlook = None
        self.namespace = None
        
    async def initialize(self):
        """Initialize the Outlook COM connection"""
        try:
            # Create Outlook application object
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            # Get MAPI namespace
            self.namespace = self.outlook.GetNamespace("MAPI")
            logger.info("Successfully connected to Outlook")
            return True
        except Exception as e:
            logger.error(f"Error connecting to Outlook: {e}")
            return False
    
    async def get_inbox_messages(self, limit=50, filter_text=None):
        """Get inbox messages with optional filtering"""
        try:
            # Get the inbox folder
            inbox = self.namespace.GetDefaultFolder(6)  # 6 is the index for Inbox
            
            # Get all items
            messages = inbox.Items
            
            # Sort by received time (newest first)
            messages.Sort("[ReceivedTime]", True)
            
            # Apply filter if provided
            if filter_text:
                messages = messages.Restrict(f"@SQL=(urn:schemas:httpmail:subject LIKE '%{filter_text}%') OR (urn:schemas:httpmail:textdescription LIKE '%{filter_text}%')")
            
            # Convert to list (limiting to the specified number)
            result = []
            count = 0
            
            for message in messages:
                if count >= limit:
                    break
                
                # Extract relevant information
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
            logger.error(f"Error getting inbox messages: {e}")
            return []
    
    async def get_message_by_id(self, entry_id):
        """Get a specific message by its Entry ID"""
        try:
            message = self.namespace.GetItemFromID(entry_id)
            return message
        except Exception as e:
            logger.error(f"Error getting message by ID: {e}")
            return None
    
    async def get_conversation_history(self, email_address, limit=20):
        """Get conversation history with a specific email address"""
        try:
            # Get all folders
            inbox = self.namespace.GetDefaultFolder(6)  # Inbox
            sent_items = self.namespace.GetDefaultFolder(5)  # Sent Items
            
            # Create filters for this email address
            inbox_filter = f"@SQL=\"urn:schemas:httpmail:fromemail\" = '{email_address}'"
            sent_filter = f"@SQL=\"urn:schemas:httpmail:toemail\" LIKE '%{email_address}%'"
            
            # Get messages from both folders
            inbox_messages = inbox.Items.Restrict(inbox_filter)
            sent_messages = sent_items.Items.Restrict(sent_filter)
            
            # Convert to lists
            received = []
            for message in inbox_messages:
                received.append({
                    "id": message.EntryID,
                    "subject": message.Subject,
                    "from": {
                        "emailAddress": {
                            "address": message.SenderEmailAddress,
                            "name": message.SenderName
                        }
                    },
                    "receivedDateTime": message.ReceivedTime.strftime("%Y-%m-%d %H:%M:%S"),
                    "bodyPreview": message.Body[:200].replace("\r\n", " "),
                    "direction": "FROM"
                })
            
            sent = []
            for message in sent_messages:
                # Check if the email is actually in the recipients (for more accuracy)
                is_recipient = False
                for recipient in message.Recipients:
                    if email_address.lower() in recipient.Address.lower():
                        is_recipient = True
                        break
                
                if is_recipient:
                    sent.append({
                        "id": message.EntryID,
                        "subject": message.Subject,
                        "from": {
                            "emailAddress": {
                                "address": message.SenderEmailAddress,
                                "name": message.SenderName
                            }
                        },
                        "receivedDateTime": message.SentOn.strftime("%Y-%m-%d %H:%M:%S"),
                        "bodyPreview": message.Body[:200].replace("\r\n", " "),
                        "direction": "TO"
                    })
            
            # Combine and sort by date (newest first)
            all_messages = received + sent
            all_messages.sort(key=lambda x: x["receivedDateTime"], reverse=True)
            
            # Limit to requested number
            return all_messages[:limit]
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
