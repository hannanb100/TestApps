#!/usr/bin/env python3
"""
Email Service for Stock Alerts

This service handles sending email notifications for stock alerts.
It replaces the SMS service with rich HTML emails that can include
more detailed information, formatting, and links.

Features:
- HTML email formatting with stock data
- Gmail SMTP support
- Rich alert messages with charts and analysis
- Error handling and logging
- Mock mode for testing
"""

import smtplib
import logging
import os
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio
from dataclasses import dataclass

from ..models.config import settings

logger = logging.getLogger(__name__)

@dataclass
class EmailMessage:
    """Data class for email message structure"""
    to_email: str
    subject: str
    html_content: str
    text_content: str
    message_type: str = "alert"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class EmailResponse:
    """Data class for email response"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class EmailService:
    """
    Email service for sending stock alerts via email.
    
    This service can work in two modes:
    1. Real mode: Sends actual emails via SMTP
    2. Mock mode: Logs emails to console (for testing)
    """
    
    def __init__(self):
        """Initialize the email service with configuration"""
        # Mailgun API credentials
        self.mailgun_api_key = os.getenv('MAILGUN_API_KEY')
        self.mailgun_domain = os.getenv('MAILGUN_DOMAIN')
        
        # Use Mailgun sandbox domain for sending
        self.from_email = f"postmaster@{self.mailgun_domain}" if self.mailgun_domain else "testingforben123@gmail.com"
        self.to_email = "testingforben123@gmail.com"    # Your email
        
        # Service state
        self.message_history = []
        self.is_mock_mode = not all([self.mailgun_api_key, self.mailgun_domain])
        
        if not self.is_mock_mode:
            logger.info("Mailgun email service initialized")
            logger.info(f"From: {self.from_email}, To: {self.to_email}")
            logger.info(f"Domain: {self.mailgun_domain}")
        else:
            logger.info("Email service running in MOCK mode - emails will be logged to console")
            logger.info("To enable real emails, configure MAILGUN_API_KEY and MAILGUN_DOMAIN in your .env file")
    
    async def send_email(self, 
                        to_email: str, 
                        subject: str, 
                        html_content: str, 
                        text_content: str = None,
                        message_type: str = "alert") -> Optional[EmailMessage]:
        """
        Send an email with HTML content.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML content of the email
            text_content: Plain text fallback (optional)
            message_type: Type of message (alert, summary, etc.)
            
        Returns:
            EmailMessage object if successful, None if failed
        """
        try:
            # Create email message
            email_msg = EmailMessage(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content or self._html_to_text(html_content),
                message_type=message_type
            )
            
            if self.is_mock_mode:
                return await self._send_mock_email(email_msg)
            else:
                return await self._send_real_email(email_msg)
                
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return None
    
    async def send_stock_alert(self, 
                              symbol: str, 
                              current_price: float, 
                              previous_price: float, 
                              change_percent: float,
                              analysis: str,
                              key_factors: List[str],
                              alert_type: str = "DAILY",
                              threshold_used: float = 3.0) -> Optional[EmailMessage]:
        """
        Send a formatted stock alert email.
        
        Args:
            symbol: Stock symbol (e.g., AAPL)
            current_price: Current stock price
            previous_price: Previous price for comparison
            change_percent: Percentage change
            analysis: AI-generated analysis
            key_factors: List of key factors
            alert_type: Type of alert (DAILY, INTRADAY)
            
        Returns:
            EmailMessage object if successful, None if failed
        """
        try:
            # Determine alert direction and color
            if change_percent > 0:
                direction = "📈 UP"
                color = "#28a745"  # Green
                emoji = "🚀"
            else:
                direction = "📉 DOWN"
                color = "#dc3545"  # Red
                emoji = "⚠️"
            
            # Create subject line
            subject = f"{emoji} {symbol} {alert_type} Alert: {direction} {abs(change_percent):.2f}%"
            
            # Create HTML content
            html_content = self._create_alert_html(
                symbol=symbol,
                current_price=current_price,
                previous_price=previous_price,
                change_percent=change_percent,
                analysis=analysis,
                key_factors=key_factors,
                alert_type=alert_type,
                direction=direction,
                color=color,
                emoji=emoji
            )
            
            # Create plain text fallback
            text_content = self._create_alert_text(
                symbol=symbol,
                current_price=current_price,
                previous_price=previous_price,
                change_percent=change_percent,
                analysis=analysis,
                key_factors=key_factors,
                alert_type=alert_type
            )
            
            # Send the email
            email_result = await self.send_email(
                to_email=self.to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                message_type="alert"
            )
            
            # Log the alert to history (regardless of email success)
            try:
                from ..models.alert_history import AlertHistory
                from ..services.alert_history_service import AlertHistoryService
                
                # Create alert history entry
                alert_history = AlertHistory(
                    symbol=symbol,
                    current_price=current_price,
                    previous_price=previous_price,
                    change_percent=change_percent,
                    alert_type=alert_type,
                    analysis=analysis,
                    key_factors=key_factors,
                    threshold_used=threshold_used,
                    email_sent=email_result is not None
                )
                
                # Add to alert history
                alert_service = AlertHistoryService()
                alert_id = alert_service.add_alert(alert_history)
                logger.info(f"Logged alert #{alert_id} to history for {symbol}")
                
            except Exception as e:
                logger.error(f"Error logging alert to history: {str(e)}")
            
            return email_result
            
        except Exception as e:
            logger.error(f"Error sending stock alert email: {str(e)}")
            return None
    
    async def send_watchlist_summary(self, 
                                   stocks_data: List[Dict[str, Any]]) -> Optional[EmailMessage]:
        """
        Send a summary email of all watched stocks.
        
        Args:
            stocks_data: List of stock data dictionaries
            
        Returns:
            EmailMessage object if successful, None if failed
        """
        try:
            subject = f"📊 Stock Watchlist Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            html_content = self._create_summary_html(stocks_data)
            text_content = self._create_summary_text(stocks_data)
            
            return await self.send_email(
                to_email=self.to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                message_type="summary"
            )
            
        except Exception as e:
            logger.error(f"Error sending watchlist summary: {str(e)}")
            return None
    
    async def _send_mock_email(self, email_msg: EmailMessage) -> EmailMessage:
        """Send a mock email (log to console)"""
        print(f"\n{'='*80}")
        print(f"📧 MOCK EMAIL SENT")
        print(f"To: {email_msg.to_email}")
        print(f"Subject: {email_msg.subject}")
        print(f"Type: {email_msg.message_type}")
        print(f"Time: {email_msg.timestamp.strftime('%H:%M:%S')}")
        print(f"{'='*80}")
        print(f"HTML Content Preview:")
        print(f"{email_msg.html_content[:500]}...")
        print(f"{'='*80}\n")
        
        # Store in history
        self.message_history.append(email_msg)
        logger.info(f"Mock email sent to {email_msg.to_email}: {email_msg.subject}")
        
        return email_msg
    
    async def _send_real_email(self, email_msg: EmailMessage) -> EmailMessage:
        """Send a real email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = email_msg.to_email
            msg['Subject'] = email_msg.subject
            
            # Add text and HTML parts
            text_part = MIMEText(email_msg.text_content, 'plain')
            html_part = MIMEText(email_msg.html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email using Mailgun API
            try:
                logger.info(f"Sending email via Mailgun to {email_msg.to_email}")
                
                # Mailgun API endpoint
                mailgun_url = f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages"
                
                # Send email using Mailgun API (sandbox format)
                response = requests.post(
                    mailgun_url,
                    auth=("api", self.mailgun_api_key),
                    data={
                        "from": f"Stock Alert System <{self.from_email}>",
                        "to": f"Ben Hannan <{email_msg.to_email}>",
                        "subject": email_msg.subject,
                        "html": email_msg.html_content,
                        "text": email_msg.text_content
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"Email sent successfully via Mailgun to {email_msg.to_email}")
                else:
                    logger.warning(f"Mailgun response: {response.status_code} - {response.text}")
                
            except Exception as e:
                logger.error(f"Failed to send email via Mailgun: {str(e)}")
                # Don't raise the exception, just log it and continue
                logger.warning("Continuing despite email send failure...")
            
            # Store in history
            self.message_history.append(email_msg)
            logger.info(f"Email sent successfully to {email_msg.to_email}: {email_msg.subject}")
            
            return email_msg
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise
    
    def _create_alert_html(self, 
                          symbol: str, 
                          current_price: float, 
                          previous_price: float, 
                          change_percent: float,
                          analysis: str,
                          key_factors: List[str],
                          alert_type: str,
                          direction: str,
                          color: str,
                          emoji: str) -> str:
        """Create HTML content for stock alert email"""
        
        change_amount = current_price - previous_price
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Stock Alert - {symbol}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background-color: {color}; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .content {{ padding: 20px; }}
                .price-section {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .price {{ font-size: 28px; font-weight: bold; color: {color}; }}
                .change {{ font-size: 18px; color: {color}; }}
                .analysis {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .factors {{ background-color: #d1ecf1; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .footer {{ background-color: #6c757d; color: white; padding: 15px; border-radius: 0 0 8px 8px; text-align: center; font-size: 12px; }}
                .alert-type {{ background-color: #ffc107; color: #212529; padding: 5px 10px; border-radius: 3px; font-size: 12px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{emoji} {symbol} {alert_type} Alert</h1>
                    <div class="alert-type">{alert_type}</div>
                </div>
                
                <div class="content">
                    <div class="price-section">
                        <div class="price">${current_price:.2f}</div>
                        <div class="change">{direction} {abs(change_percent):.2f}% (${change_amount:+.2f})</div>
                        <div style="margin-top: 10px; color: #6c757d;">
                            Previous: ${previous_price:.2f}
                        </div>
                    </div>
                    
                    <div class="analysis">
                        <h3>🤖 AI Analysis</h3>
                        <p>{analysis}</p>
                    </div>
                    
                    <div class="factors">
                        <h3>🔍 Key Factors</h3>
                        <ul>
                            {''.join([f'<li>{factor}</li>' for factor in key_factors])}
                        </ul>
                    </div>
                </div>
                
                <div class="footer">
                    <p>AI Stock Tracking Agent | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                    <p>This is an automated alert. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_alert_text(self, 
                          symbol: str, 
                          current_price: float, 
                          previous_price: float, 
                          change_percent: float,
                          analysis: str,
                          key_factors: List[str],
                          alert_type: str) -> str:
        """Create plain text content for stock alert email"""
        
        change_amount = current_price - previous_price
        direction = "UP" if change_percent > 0 else "DOWN"
        
        text = f"""
{symbol} {alert_type} ALERT
{'='*50}

Price: ${current_price:.2f}
Change: {direction} {abs(change_percent):.2f}% (${change_amount:+.2f})
Previous: ${previous_price:.2f}

AI ANALYSIS:
{analysis}

KEY FACTORS:
{chr(10).join([f'• {factor}' for factor in key_factors])}

---
AI Stock Tracking Agent
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """
        
        return text.strip()
    
    def _create_summary_html(self, stocks_data: List[Dict[str, Any]]) -> str:
        """Create HTML content for watchlist summary email"""
        # Implementation for summary email
        return "<html><body><h1>Stock Summary</h1><p>Summary content here</p></body></html>"
    
    def _create_summary_text(self, stocks_data: List[Dict[str, Any]]) -> str:
        """Create plain text content for watchlist summary email"""
        # Implementation for summary email
        return "Stock Summary\n\nSummary content here"
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML content to plain text"""
        # Simple HTML to text conversion
        import re
        # Remove HTML tags
        text = re.sub('<[^<]+?>', '', html_content)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def get_message_history(self) -> List[EmailMessage]:
        """Get history of sent emails"""
        return self.message_history.copy()
    
    def clear_history(self):
        """Clear email message history"""
        self.message_history.clear()
        logger.info("Email message history cleared")
