"""
Mock SMS service for local testing without Twilio.

This service is like a "fake SMS service" that simulates sending and receiving
SMS messages without actually using Twilio (which costs money). It's perfect
for testing and development.

What this service does:
- Simulates sending SMS messages (displays them in the console)
- Keeps a history of all "sent" messages
- Handles incoming SMS simulation
- Provides all the same methods as the real SMS service

For beginners: A "mock" service is a fake version of a real service that
behaves the same way but doesn't actually do the expensive operations.
It's like having a fake credit card for testing - it looks and works the same,
but doesn't charge real money.
"""

# Standard library imports
import logging  # For recording what happens
from typing import Optional, Dict, Any  # For type hints
from datetime import datetime  # For timestamps
import asyncio  # For async operations

# Our custom imports
from ..models.sms import SMSMessage, SMSResponse, SMSAlert  # SMS data models
from ..models.config import settings  # App configuration

# Set up logging for this file
logger = logging.getLogger(__name__)


class MockSMSService:
    """
    Mock SMS service for local testing.
    
    This class simulates all SMS operations without requiring Twilio.
    Instead of sending real SMS messages, it:
    - Prints messages to the console
    - Stores them in a history list
    - Returns success/failure responses
    
    This lets you test the entire system without spending money on SMS!
    """
    
    def __init__(self):
        """
        Initialize the mock SMS service.
        
        This sets up the fake phone numbers and message history.
        """
        # Set up fake phone numbers for testing
        self.from_number = "+1555MOCK123"  # Fake Twilio number
        self.user_phone = "+1555USER123"   # Fake user number
        
        # Keep track of all "sent" messages
        self.message_history = []
        
        logger.info("Mock SMS service initialized - no external dependencies required")
    
    async def send_sms(self, to_number: str, message: str, 
                      message_type: str = "text") -> Optional[SMSMessage]:
        """
        Simulate sending an SMS message.
        
        Args:
            to_number: Recipient phone number
            message: Message content
            message_type: Type of message (text, alert, error)
            
        Returns:
            SMSMessage object if successful, None if failed
        """
        try:
            logger.info(f"📱 MOCK SMS SENT to {to_number}: {message[:50]}...")
            
            # Create mock SMS record
            sms_record = SMSMessage(
                from_number=self.from_number,
                to_number=to_number,
                body=message,
                status="sent",
                direction="outbound",
                twilio_sid=f"MOCK_{datetime.utcnow().timestamp()}",
                sent_at=datetime.utcnow()
            )
            
            # Store in message history
            self.message_history.append({
                "timestamp": datetime.utcnow(),
                "to": to_number,
                "message": message,
                "type": message_type
            })
            
            # Print to console for visibility
            print(f"\n{'='*60}")
            print(f"📱 MOCK SMS SENT")
            print(f"To: {to_number}")
            print(f"Message: {message}")
            print(f"Type: {message_type}")
            print(f"Time: {datetime.utcnow().strftime('%H:%M:%S')}")
            print(f"{'='*60}\n")
            
            return sms_record
            
        except Exception as e:
            logger.error(f"Error in mock SMS: {str(e)}")
            return None
    
    async def send_stock_alert(self, alert: SMSAlert) -> Optional[SMSMessage]:
        """
        Simulate sending a stock price alert.
        
        Args:
            alert: SMSAlert object with alert information
            
        Returns:
            SMSMessage object if successful, None if failed
        """
        try:
            # Format alert message
            message = self._format_alert_message(alert)
            
            # Send mock SMS
            sms_record = await self.send_sms(
                to_number=self.user_phone,
                message=message,
                message_type="alert"
            )
            
            if sms_record:
                logger.info(f"Mock stock alert sent for {alert.symbol}")
            
            return sms_record
            
        except Exception as e:
            logger.error(f"Error sending mock stock alert: {str(e)}")
            return None
    
    async def send_confirmation(self, to_number: str, action: str, 
                               symbol: Optional[str] = None) -> Optional[SMSMessage]:
        """
        Simulate sending a confirmation message.
        
        Args:
            to_number: Recipient phone number
            action: Action performed (add, remove, list)
            symbol: Stock symbol (if applicable)
            
        Returns:
            SMSMessage object if successful, None if failed
        """
        try:
            message = self._format_confirmation_message(action, symbol)
            
            sms_record = await self.send_sms(
                to_number=to_number,
                message=message,
                message_type="confirmation"
            )
            
            logger.info(f"Mock confirmation sent for {action} action")
            return sms_record
            
        except Exception as e:
            logger.error(f"Error sending mock confirmation: {str(e)}")
            return None
    
    async def send_error_message(self, to_number: str, error_message: str) -> Optional[SMSMessage]:
        """
        Simulate sending an error message.
        
        Args:
            to_number: Recipient phone number
            error_message: Error description
            
        Returns:
            SMSMessage object if successful, None if failed
        """
        try:
            message = f"❌ Error: {error_message}\n\nType 'help' for available commands."
            
            sms_record = await self.send_sms(
                to_number=to_number,
                message=message,
                message_type="error"
            )
            
            logger.info("Mock error message sent to user")
            return sms_record
            
        except Exception as e:
            logger.error(f"Error sending mock error message: {str(e)}")
            return None
    
    async def send_help_message(self, to_number: str) -> Optional[SMSMessage]:
        """
        Simulate sending a help message.
        
        Args:
            to_number: Recipient phone number
            
        Returns:
            SMSMessage object if successful, None if failed
        """
        try:
            help_text = """
📈 Stock Tracker Commands:

• Add AAPL - Add stock to watchlist
• Remove TSLA - Remove stock from watchlist  
• List - Show all tracked stocks
• Status - Check system status
• Help - Show this message

Example: "Add AAPL" or "Remove TSLA"
            """.strip()
            
            sms_record = await self.send_sms(
                to_number=to_number,
                message=help_text,
                message_type="text"
            )
            
            logger.info("Mock help message sent to user")
            return sms_record
            
        except Exception as e:
            logger.error(f"Error sending mock help message: {str(e)}")
            return None
    
    def parse_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse mock webhook data.
        
        Args:
            webhook_data: Mock webhook data
            
        Returns:
            Parsed webhook data
        """
        try:
            # Simulate webhook parsing
            mock_webhook = {
                "MessageSid": f"MOCK_{datetime.utcnow().timestamp()}",
                "AccountSid": "MOCK_ACCOUNT_SID",
                "From": webhook_data.get("From", self.user_phone),
                "To": webhook_data.get("To", self.from_number),
                "Body": webhook_data.get("Body", ""),
                "MessageStatus": "received",
                "SmsStatus": "received"
            }
            
            logger.info(f"Mock webhook parsed for message {mock_webhook['MessageSid']}")
            return mock_webhook
            
        except Exception as e:
            logger.error(f"Error parsing mock webhook: {str(e)}")
            raise
    
    async def handle_incoming_sms(self, webhook_data: Dict[str, Any]) -> SMSMessage:
        """
        Handle incoming SMS message from mock webhook.
        
        Args:
            webhook_data: Mock webhook data
            
        Returns:
            SMSMessage object representing the incoming message
        """
        try:
            sms_record = SMSMessage(
                from_number=webhook_data.get("From", self.user_phone),
                to_number=webhook_data.get("To", self.from_number),
                body=webhook_data.get("Body", ""),
                status=webhook_data.get("MessageStatus", "received"),
                direction="inbound",
                twilio_sid=webhook_data.get("MessageSid", f"MOCK_{datetime.utcnow().timestamp()}"),
                created_at=datetime.utcnow()
            )
            
            logger.info(f"Mock SMS received from {sms_record.from_number}: {sms_record.body[:50]}...")
            return sms_record
            
        except Exception as e:
            logger.error(f"Error handling mock incoming SMS: {str(e)}")
            raise
    
    async def update_message_status(self, message_sid: str, status: str) -> bool:
        """
        Update message status in mock records.
        
        Args:
            message_sid: Mock message SID
            status: New message status
            
        Returns:
            True if update was successful
        """
        try:
            logger.info(f"Mock message {message_sid} status updated to {status}")
            return True
        except Exception as e:
            logger.error(f"Error updating mock message status: {str(e)}")
            return False
    
    def _format_alert_message(self, alert) -> str:
        """
        Format stock alert message for mock SMS.
        
        Args:
            alert: SMSAlert object
            
        Returns:
            Formatted message string
        """
        # Determine emoji based on price change
        if alert.change_percent > 0:
            emoji = "📈"
            direction = "up"
        else:
            emoji = "📉"
            direction = "down"
        
        # Format price change
        change_str = f"{alert.change_percent:+.2f}%"
        
        # Build message
        message = f"{emoji} {alert.symbol} Alert\n\n"
        message += f"Price: ${alert.current_price:.2f} ({change_str})\n"
        message += f"Previous: ${alert.previous_price:.2f}\n\n"
        message += f"{alert.alert_message}\n"
        
        # Add news summary if available
        if alert.news_summary:
            message += f"\n📰 {alert.news_summary}"
        
        return message
    
    def _format_confirmation_message(self, action: str, symbol: Optional[str] = None) -> str:
        """
        Format confirmation message for user actions.
        
        Args:
            action: Action performed
            symbol: Stock symbol (if applicable)
            
        Returns:
            Formatted confirmation message
        """
        if action == "add" and symbol:
            return f"✅ {symbol} added to your watchlist!"
        elif action == "remove" and symbol:
            return f"✅ {symbol} removed from your watchlist!"
        elif action == "list":
            return "📋 Here are your tracked stocks:"
        elif action == "status":
            return "📊 System status: All systems operational"
        else:
            return f"✅ {action} completed successfully!"
    
    def get_message_history(self) -> list:
        """
        Get history of mock SMS messages.
        
        Returns:
            List of message history
        """
        return self.message_history
    
    def clear_message_history(self):
        """Clear the message history."""
        self.message_history.clear()
        logger.info("Mock SMS message history cleared")
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get mock SMS service status information.
        
        Returns:
            Dictionary with service status
        """
        return {
            'service': 'Mock SMS Service',
            'provider': 'Local Testing',
            'from_number': self.from_number,
            'user_phone': self.user_phone,
            'status': 'operational',
            'message_count': len(self.message_history),
            'timestamp': datetime.utcnow().isoformat()
        }
