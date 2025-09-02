"""
SMS-related Pydantic models.

This file defines the "data structures" for all SMS and communication-related
information in our system. These models help us organize and validate
all the different types of messages and data we work with.

What this file contains:
- SMSMessage: Information about individual SMS messages
- TwilioWebhook: Data sent by Twilio when messages are received
- SMSCommand: Commands parsed from user messages
- SMSResponse: Responses we send back to users
- SMSAlert: Stock price alerts sent via SMS

For beginners: These models are like "forms" that ensure all our SMS data
is in the right format and contains the right information. They help prevent
errors and make our code more reliable.
"""

# Standard library imports
from typing import Optional, Dict, Any  # For optional values and dictionaries
from datetime import datetime  # For dates and times

# Third-party imports
from pydantic import BaseModel, Field, validator  # For data models and validation


class SMSMessage(BaseModel):
    """
    Model representing an SMS message.
    
    This is like a "record" of every SMS message that goes through our system.
    It stores all the important information about who sent it, when, what it said,
    and what happened to it.
    
    Attributes:
        id: Unique identifier for this message in our database
        from_number: Phone number of the person who sent the message
        to_number: Phone number of the person who received the message
        body: The actual text content of the message
        status: Current status (pending, sent, delivered, failed, etc.)
        direction: Whether this message is coming in (inbound) or going out (outbound)
        twilio_sid: Twilio's unique identifier for this message
        created_at: When we first received/created this message
        sent_at: When we actually sent the message (for outbound messages)
        delivered_at: When the message was delivered to the recipient
        error_code: If something went wrong, what error occurred
        error_message: Human-readable description of any error
    """
    
    id: Optional[int] = Field(None, description="Message ID")
    from_number: str = Field(..., description="Sender phone number")
    to_number: str = Field(..., description="Recipient phone number")
    body: str = Field(..., description="Message content")
    status: str = Field(default="pending", description="Message status")
    direction: str = Field(..., description="Message direction: inbound or outbound")
    twilio_sid: Optional[str] = Field(None, description="Twilio message SID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Message creation time")
    sent_at: Optional[datetime] = Field(None, description="When message was sent")
    delivered_at: Optional[datetime] = Field(None, description="When message was delivered")
    error_code: Optional[str] = Field(None, description="Error code if message failed")
    error_message: Optional[str] = Field(None, description="Error message if message failed")
    
    @validator('direction')
    def validate_direction(cls, v):
        """
        Validate message direction.
        
        This makes sure the direction is either 'inbound' (coming in) or 'outbound' (going out).
        """
        if v not in ['inbound', 'outbound']:
            raise ValueError("Direction must be 'inbound' or 'outbound'")
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """
        Validate message status.
        
        This makes sure the status is one of the valid states a message can be in.
        """
        valid_statuses = ['pending', 'sent', 'delivered', 'failed', 'undelivered']
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return v


class TwilioWebhook(BaseModel):
    """
    Model for Twilio webhook data.
    
    This model represents the data structure sent by Twilio
    when an SMS is received or status is updated.
    """
    
    # Message identification
    MessageSid: str = Field(..., description="Twilio message SID")
    AccountSid: str = Field(..., description="Twilio account SID")
    
    # Message details
    From: str = Field(..., description="Sender phone number")
    To: str = Field(..., description="Recipient phone number")
    Body: str = Field(..., description="Message content")
    
    # Status information
    MessageStatus: str = Field(..., description="Message status")
    SmsStatus: Optional[str] = Field(None, description="SMS status")
    
    # Additional metadata
    NumMedia: Optional[str] = Field("0", description="Number of media attachments")
    ApiVersion: Optional[str] = Field("2010-04-01", description="Twilio API version")
    
    # Error information (if applicable)
    ErrorCode: Optional[str] = Field(None, description="Error code")
    ErrorMessage: Optional[str] = Field(None, description="Error message")
    
    @validator('From', 'To')
    def validate_phone_numbers(cls, v):
        """Validate phone number format."""
        if not v or not isinstance(v, str):
            raise ValueError("Phone number must be a non-empty string")
        return v
    
    @validator('Body')
    def validate_message_body(cls, v):
        """Validate message body."""
        if not isinstance(v, str):
            raise ValueError("Message body must be a string")
        if len(v) > 1600:  # SMS character limit
            raise ValueError("Message body too long")
        return v


class SMSCommand(BaseModel):
    """
    Model for parsed SMS commands.
    
    This model represents a parsed and validated command
    extracted from an SMS message.
    """
    
    command_type: str = Field(..., description="Type of command (add, remove, list, help)")
    symbol: Optional[str] = Field(None, description="Stock symbol (for add/remove commands)")
    original_message: str = Field(..., description="Original SMS message")
    confidence: float = Field(default=1.0, description="Command parsing confidence (0-1)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional command parameters")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Command parsing time")
    
    @validator('command_type')
    def validate_command_type(cls, v):
        """Validate command type."""
        valid_commands = ['add', 'remove', 'list', 'help', 'status', 'settings']
        if v not in valid_commands:
            raise ValueError(f"Command type must be one of: {valid_commands}")
        return v
    
    @validator('confidence')
    def validate_confidence(cls, v):
        """Validate confidence score."""
        if not 0 <= v <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        return v


class SMSResponse(BaseModel):
    """
    Model for SMS response messages.
    
    This model represents the structure of responses
    sent back to users via SMS.
    """
    
    to_number: str = Field(..., description="Recipient phone number")
    message: str = Field(..., description="Response message content")
    message_type: str = Field(default="text", description="Type of message (text, alert, error)")
    priority: str = Field(default="normal", description="Message priority (low, normal, high)")
    scheduled_at: Optional[datetime] = Field(None, description="When to send message (for scheduling)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Response creation time")
    
    @validator('message_type')
    def validate_message_type(cls, v):
        """Validate message type."""
        valid_types = ['text', 'alert', 'error', 'confirmation']
        if v not in valid_types:
            raise ValueError(f"Message type must be one of: {valid_types}")
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        """Validate message priority."""
        valid_priorities = ['low', 'normal', 'high', 'urgent']
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")
        return v


class SMSAlert(BaseModel):
    """
    Model for SMS alert messages.
    
    This model represents stock price alerts sent via SMS
    with AI-generated analysis.
    """
    
    symbol: str = Field(..., description="Stock symbol")
    current_price: float = Field(..., description="Current stock price")
    previous_price: float = Field(..., description="Previous stock price")
    change_percent: float = Field(..., description="Percentage change")
    alert_message: str = Field(..., description="AI-generated alert message")
    news_summary: Optional[str] = Field(None, description="News summary")
    analysis: Optional[str] = Field(None, description="AI analysis")
    urgency_level: str = Field(default="normal", description="Alert urgency level")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Alert creation time")
    
    @validator('urgency_level')
    def validate_urgency(cls, v):
        """Validate urgency level."""
        valid_levels = ['low', 'normal', 'high', 'critical']
        if v not in valid_levels:
            raise ValueError(f"Urgency level must be one of: {valid_levels}")
        return v
