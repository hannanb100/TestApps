"""
SMS service for handling Twilio integration.

This service manages all SMS operations including sending messages,
receiving webhooks, and handling message status updates.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

from ..models.sms import SMSMessage, SMSResponse, SMSAlert, TwilioWebhook
from ..models.config import TwilioConfig

# Configure logging
logger = logging.getLogger(__name__)


class SMSService:
    """
    Service for managing SMS operations with Twilio.
    
    This service provides methods for sending SMS messages,
    handling incoming webhooks, and managing message status.
    """
    
    def __init__(self):
        """Initialize the SMS service with Twilio client."""
        try:
            self.client = Client(
                TwilioConfig.get_account_sid(),
                TwilioConfig.get_auth_token()
            )
            self.from_number = TwilioConfig.get_phone_number()
            self.user_phone = TwilioConfig.get_user_phone()
            logger.info("SMS service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SMS service: {str(e)}")
            raise
    
    async def send_sms(self, to_number: str, message: str, 
                      message_type: str = "text") -> Optional[SMSMessage]:
        """
        Send an SMS message via Twilio.
        
        Args:
            to_number: Recipient phone number
            message: Message content
            message_type: Type of message (text, alert, error)
            
        Returns:
            SMSMessage object if successful, None if failed
            
        Raises:
            TwilioException: If SMS sending fails
        """
        try:
            logger.info(f"Sending SMS to {to_number}: {message[:50]}...")
            
            # Send message via Twilio
            twilio_message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            # Create SMSMessage record
            sms_record = SMSMessage(
                from_number=self.from_number,
                to_number=to_number,
                body=message,
                status="sent",
                direction="outbound",
                twilio_sid=twilio_message.sid,
                sent_at=datetime.utcnow()
            )
            
            logger.info(f"SMS sent successfully. SID: {twilio_message.sid}")
            return sms_record
            
        except TwilioException as e:
            logger.error(f"Twilio error sending SMS: {str(e)}")
            # Create failed SMS record
            failed_sms = SMSMessage(
                from_number=self.from_number,
                to_number=to_number,
                body=message,
                status="failed",
                direction="outbound",
                error_code=str(e.code) if hasattr(e, 'code') else None,
                error_message=str(e)
            )
            return failed_sms
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {str(e)}")
            return None
    
    async def send_stock_alert(self, alert: SMSAlert) -> Optional[SMSMessage]:
        """
        Send a stock price alert via SMS.
        
        Args:
            alert: SMSAlert object with alert information
            
        Returns:
            SMSMessage object if successful, None if failed
        """
        try:
            # Format alert message
            message = self._format_alert_message(alert)
            
            # Send SMS
            sms_record = await self.send_sms(
                to_number=self.user_phone,
                message=message,
                message_type="alert"
            )
            
            if sms_record and sms_record.status == "sent":
                logger.info(f"Stock alert sent for {alert.symbol}")
            else:
                logger.error(f"Failed to send stock alert for {alert.symbol}")
            
            return sms_record
            
        except Exception as e:
            logger.error(f"Error sending stock alert: {str(e)}")
            return None
    
    async def send_confirmation(self, to_number: str, action: str, 
                               symbol: Optional[str] = None) -> Optional[SMSMessage]:
        """
        Send a confirmation message for user actions.
        
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
            
            logger.info(f"Confirmation sent for {action} action")
            return sms_record
            
        except Exception as e:
            logger.error(f"Error sending confirmation: {str(e)}")
            return None
    
    async def send_error_message(self, to_number: str, error_message: str) -> Optional[SMSMessage]:
        """
        Send an error message to the user.
        
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
            
            logger.info("Error message sent to user")
            return sms_record
            
        except Exception as e:
            logger.error(f"Error sending error message: {str(e)}")
            return None
    
    async def send_help_message(self, to_number: str) -> Optional[SMSMessage]:
        """
        Send a help message with available commands.
        
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
            
            logger.info("Help message sent to user")
            return sms_record
            
        except Exception as e:
            logger.error(f"Error sending help message: {str(e)}")
            return None
    
    def parse_webhook(self, webhook_data: Dict[str, Any]) -> TwilioWebhook:
        """
        Parse Twilio webhook data.
        
        Args:
            webhook_data: Raw webhook data from Twilio
            
        Returns:
            TwilioWebhook object
        """
        try:
            webhook = TwilioWebhook(**webhook_data)
            logger.info(f"Parsed webhook for message {webhook.MessageSid}")
            return webhook
        except Exception as e:
            logger.error(f"Error parsing webhook: {str(e)}")
            raise
    
    async def handle_incoming_sms(self, webhook: TwilioWebhook) -> SMSMessage:
        """
        Handle incoming SMS message from webhook.
        
        Args:
            webhook: TwilioWebhook object
            
        Returns:
            SMSMessage object representing the incoming message
        """
        try:
            sms_record = SMSMessage(
                from_number=webhook.From,
                to_number=webhook.To,
                body=webhook.Body,
                status=webhook.MessageStatus,
                direction="inbound",
                twilio_sid=webhook.MessageSid,
                created_at=datetime.utcnow()
            )
            
            logger.info(f"Received SMS from {webhook.From}: {webhook.Body[:50]}...")
            return sms_record
            
        except Exception as e:
            logger.error(f"Error handling incoming SMS: {str(e)}")
            raise
    
    async def update_message_status(self, message_sid: str, status: str) -> bool:
        """
        Update message status in our records.
        
        Args:
            message_sid: Twilio message SID
            status: New message status
            
        Returns:
            True if update was successful
        """
        try:
            # In a real implementation, you would update the database here
            logger.info(f"Message {message_sid} status updated to {status}")
            return True
        except Exception as e:
            logger.error(f"Error updating message status: {str(e)}")
            return False
    
    def _format_alert_message(self, alert: SMSAlert) -> str:
        """
        Format stock alert message for SMS.
        
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
    
    async def get_message_status(self, message_sid: str) -> Optional[Dict[str, Any]]:
        """
        Get message status from Twilio.
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            Dictionary with message status information
        """
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                'sid': message.sid,
                'status': message.status,
                'direction': message.direction,
                'from': message.from_,
                'to': message.to,
                'body': message.body,
                'date_created': message.date_created,
                'date_sent': message.date_sent,
                'date_updated': message.date_updated,
                'error_code': message.error_code,
                'error_message': message.error_message
            }
        except TwilioException as e:
            logger.error(f"Error fetching message status: {str(e)}")
            return None
    
    async def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            True if phone number is valid
        """
        try:
            # Basic validation - in production, use Twilio's Lookup API
            cleaned = ''.join(filter(str.isdigit, phone_number))
            return len(cleaned) >= 10
        except Exception:
            return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get SMS service status information.
        
        Returns:
            Dictionary with service status
        """
        return {
            'service': 'SMS Service',
            'provider': 'Twilio',
            'from_number': self.from_number,
            'user_phone': self.user_phone,
            'status': 'operational',
            'timestamp': datetime.utcnow().isoformat()
        }
