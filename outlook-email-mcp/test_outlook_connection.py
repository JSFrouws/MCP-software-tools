"""
Test script to verify connection to Outlook via COM
"""
import win32com.client
import sys

def test_outlook_connection():
    """Test if we can connect to Outlook via COM"""
    print("Testing connection to Outlook...")
    
    try:
        # Try to create the Outlook application object
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        
        # Get the inbox folder
        inbox = namespace.GetDefaultFolder(6)  # 6 is the index for Inbox
        
        # Print the number of items in inbox
        print(f"Successfully connected to Outlook!")
        print(f"Your inbox contains {inbox.Items.Count} emails")
        
        return True
    except Exception as e:
        print(f"Error connecting to Outlook: {e}")
        return False

if __name__ == "__main__":
    success = test_outlook_connection()
    sys.exit(0 if success else 1)
