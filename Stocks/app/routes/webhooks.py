"""
Webhook routes for handling Twilio SMS messages.

This module contains FastAPI routes for receiving and processing
SMS messages from Twilio webhooks.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import Response
import asyncio

from ..models.sms import TwilioWebhook, SMSMessage
from ..services.sms_service import SMSService
from ..services.chatbot_service import ChatbotService
from ..services.stock_service import StockService

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Service instances (in production, use dependency injection)
sms_service = SMSService()
chatbot_service = ChatbotService()
stock_service = StockService()


@router.post("/twilio/sms")
async def handle_twilio_sms(request: Request) -> Response:
    """
    Handle incoming SMS messages from Twilio.
    
    This endpoint receives webhook calls from Twilio when SMS messages
    are sent to the configured phone number.
    
    Args:
        request: FastAPI request object containing webhook data
        
    Returns:
        TwiML response for Twilio
    """
    try:
        # Parse form data from Twilio
        form_data = await request.form()
        webhook_data = dict(form_data)
        
        logger.info(f"Received Twilio webhook: {webhook_data.get('MessageSid', 'unknown')}")
        
        # Parse webhook data
        webhook = sms_service.parse_webhook(webhook_data)
        
        # Handle incoming SMS
        sms_message = await sms_service.handle_incoming_sms(webhook)
        
        # Process the message asynchronously
        asyncio.create_task(process_sms_message(sms_message))
        
        # Return empty TwiML response (no immediate reply)
        return Response(content="", media_type="text/xml")
        
    except Exception as e:
        logger.error(f"Error handling Twilio webhook: {str(e)}")
        # Return empty response to avoid webhook retries
        return Response(content="", media_type="text/xml")


@router.post("/twilio/status")
async def handle_twilio_status(request: Request) -> Response:
    """
    Handle SMS status updates from Twilio.
    
    This endpoint receives webhook calls from Twilio when SMS
    message status changes (sent, delivered, failed, etc.).
    
    Args:
        request: FastAPI request object containing status data
        
    Returns:
        Empty response
    """
    try:
        # Parse form data from Twilio
        form_data = await request.form()
        status_data = dict(form_data)
        
        message_sid = status_data.get('MessageSid')
        message_status = status_data.get('MessageStatus')
        
        logger.info(f"Received status update for {message_sid}: {message_status}")
        
        # Update message status in our records
        await sms_service.update_message_status(message_sid, message_status)
        
        return Response(content="", media_type="text/xml")
        
    except Exception as e:
        logger.error(f"Error handling status webhook: {str(e)}")
        return Response(content="", media_type="text/xml")


async def process_sms_message(sms_message: SMSMessage):
    """
    Process an incoming SMS message asynchronously.
    
    This function handles the complete flow of processing an SMS:
    1. Parse the command using the chatbot service
    2. Execute the command (add/remove/list stocks)
    3. Send a response back to the user
    
    Args:
        sms_message: SMSMessage object containing the user's message
    """
    try:
        logger.info(f"Processing SMS from {sms_message.from_number}: {sms_message.body[:50]}...")
        
        # Parse the command using LangChain
        command = await chatbot_service.parse_command(sms_message)
        
        # Validate the command
        validation = chatbot_service.validate_command(command)
        
        if not validation["is_valid"]:
            # Send error message
            error_msg = " ".join(validation["errors"])
            await sms_service.send_error_message(sms_message.from_number, error_msg)
            return
        
        # Execute the command
        execution_result = await execute_command(command)
        
        # Generate response
        response_message = await chatbot_service.generate_response(command, execution_result)
        
        # Send response back to user
        await sms_service.send_sms(
            to_number=sms_message.from_number,
            message=response_message,
            message_type="text"
        )
        
        logger.info(f"Successfully processed SMS command: {command.command_type}")
        
    except Exception as e:
        logger.error(f"Error processing SMS message: {str(e)}")
        # Send error message to user
        try:
            await sms_service.send_error_message(
                sms_message.from_number, 
                "An error occurred while processing your request."
            )
        except Exception as send_error:
            logger.error(f"Failed to send error message: {str(send_error)}")


async def execute_command(command) -> Dict[str, Any]:
    """
    Execute a parsed command.
    
    This function handles the execution of different command types
    like adding/removing stocks, listing stocks, etc.
    
    Args:
        command: SMSCommand object with parsed command information
        
    Returns:
        Dictionary with execution results
    """
    try:
        if command.command_type == "add":
            return await execute_add_stock(command)
        elif command.command_type == "remove":
            return await execute_remove_stock(command)
        elif command.command_type == "list":
            return await execute_list_stocks(command)
        elif command.command_type == "status":
            return await execute_status_check(command)
        elif command.command_type == "help":
            return {"success": True, "message": "Help command executed"}
        else:
            return {"success": False, "error": f"Unknown command: {command.command_type}"}
            
    except Exception as e:
        logger.error(f"Error executing command {command.command_type}: {str(e)}")
        return {"success": False, "error": str(e)}


async def execute_add_stock(command) -> Dict[str, Any]:
    """
    Execute add stock command.
    
    Args:
        command: SMSCommand object
        
    Returns:
        Dictionary with execution results
    """
    try:
        symbol = command.symbol.upper()
        
        # Validate stock symbol
        is_valid = await stock_service.validate_stock_symbol(symbol)
        if not is_valid:
            return {"success": False, "error": f"Invalid stock symbol: {symbol}"}
        
        # Get stock info
        stock_info = await stock_service.get_stock_info(symbol)
        if not stock_info:
            return {"success": False, "error": f"Could not fetch information for {symbol}"}
        
        # In a real implementation, you would save to database here
        # For now, we'll just return success
        logger.info(f"Stock {symbol} added to watchlist")
        
        return {
            "success": True,
            "symbol": symbol,
            "name": stock_info.get("name", symbol),
            "message": f"{symbol} added successfully"
        }
        
    except Exception as e:
        logger.error(f"Error adding stock {command.symbol}: {str(e)}")
        return {"success": False, "error": str(e)}


async def execute_remove_stock(command) -> Dict[str, Any]:
    """
    Execute remove stock command.
    
    Args:
        command: SMSCommand object
        
    Returns:
        Dictionary with execution results
    """
    try:
        symbol = command.symbol.upper()
        
        # In a real implementation, you would remove from database here
        # For now, we'll just return success
        logger.info(f"Stock {symbol} removed from watchlist")
        
        return {
            "success": True,
            "symbol": symbol,
            "message": f"{symbol} removed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error removing stock {command.symbol}: {str(e)}")
        return {"success": False, "error": str(e)}


async def execute_list_stocks(command) -> Dict[str, Any]:
    """
    Execute list stocks command.
    
    Args:
        command: SMSCommand object
        
    Returns:
        Dictionary with execution results
    """
    try:
        # In a real implementation, you would fetch from database here
        # For now, we'll return mock data
        mock_stocks = ["AAPL", "TSLA", "GOOGL", "MSFT"]
        
        logger.info("Listed tracked stocks")
        
        return {
            "success": True,
            "stocks": mock_stocks,
            "count": len(mock_stocks)
        }
        
    except Exception as e:
        logger.error(f"Error listing stocks: {str(e)}")
        return {"success": False, "error": str(e)}


async def execute_status_check(command) -> Dict[str, Any]:
    """
    Execute status check command.
    
    Args:
        command: SMSCommand object
        
    Returns:
        Dictionary with execution results
    """
    try:
        # Get system status
        status_info = {
            "system": "operational",
            "last_check": "2024-01-01T00:00:00Z",
            "tracked_stocks": 4,
            "alerts_sent": 0
        }
        
        logger.info("System status checked")
        
        return {
            "success": True,
            "status": status_info
        }
        
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")
        return {"success": False, "error": str(e)}


@router.get("/test")
async def test_webhook():
    """
    Test endpoint for webhook functionality.
    
    Returns:
        Simple test response
    """
    return {
        "message": "Webhook endpoint is working",
        "timestamp": "2024-01-01T00:00:00Z",
        "status": "ok"
    }
