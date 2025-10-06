#!/usr/bin/env python3
"""
Lambda Handler for AI Stock Tracking Agent

This handler wraps the existing stock checking logic to run on AWS Lambda.
It preserves all the sophisticated scheduling and market hours logic.
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any

# Import your existing services
from app.services.stock_list_service import StockListService
from app.services.alert_preferences_service import AlertPreferencesService
from app.services.stock_service import StockService
from app.services.email_service import EmailService
from app.services.agent_service import AgentService

# Configure logging for Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize services (these will be reused across Lambda invocations)
stock_list_service = None
preferences_service = None
stock_service = None
email_service = None
agent_service = None

def initialize_services():
    """Initialize services on first Lambda invocation."""
    global stock_list_service, preferences_service, stock_service, email_service, agent_service
    
    if stock_list_service is None:
        logger.info("Initializing services for first Lambda invocation")
        stock_list_service = StockListService()
        preferences_service = AlertPreferencesService()
        stock_service = StockService()
        email_service = EmailService()
        agent_service = AgentService()
        logger.info("Services initialized successfully")

async def stock_price_check_task():
    """
    Main stock checking function - this is your existing logic from main.py
    """
    try:
        logger.info("Executing scheduled stock price check")
        
        # Get the list of all stocks we're currently tracking
        tracked_stocks = stock_list_service.get_active_stocks()
        
        # If no stocks are being tracked, we don't need to do anything
        if not tracked_stocks:
            logger.warning("No active stocks found in tracking list")
            return
        
        # Check if email alerts are enabled
        preferences = preferences_service.get_preferences()
        if not preferences or not preferences.email_alerts_enabled:
            logger.warning("Email alerts not enabled, skipping price checks")
            return
        
        # Process each tracked stock one by one
        for symbol in tracked_stocks:
            try:
                # Fetch current stock data from Yahoo Finance
                quote = await stock_service.get_stock_quote(symbol)
                if not quote:
                    logger.warning(f"No quote data available for {symbol}")
                    continue
                
                # Extract the current price from the quote data
                current_price = float(quote.price)
                
                # Get the alert threshold for this specific stock
                threshold = preferences_service.get_effective_threshold(symbol)
                previous_close = float(quote.previous_close)
                
                # Calculate how much the price has changed
                price_change_percent = ((current_price - previous_close) / previous_close * 100)
                
                if abs(price_change_percent) >= threshold:
                    # Check if alert should be sent based on preferences
                    if not preferences_service.should_send_alert(symbol):
                        logger.info(f"Alert triggered for {symbol}: {price_change_percent:+.2f}% but alerts disabled")
                        continue
                    
                    logger.info(f"Alert triggered for {symbol}: {price_change_percent:+.2f}% (threshold: {threshold}%)")
                    
                    # Generate AI analysis (if enabled in preferences)
                    analysis = None
                    if preferences.include_analysis:
                        analysis = await agent_service.analyze_stock_movement(
                            symbol, float(quote.previous_close), float(quote.price), 
                            int(quote.volume) if hasattr(quote, 'volume') else 0
                        )
                    else:
                        # Create minimal analysis if disabled
                        analysis = type('Analysis', (), {
                            'analysis': f"Stock {symbol} moved {quote.change_percent:+.2f}%",
                            'key_factors': ["Price movement"]
                        })()
                    
                    # Send email alert
                    await email_service.send_stock_alert(
                        symbol=symbol,
                        current_price=current_price,
                        previous_price=previous_close,
                        change_percent=price_change_percent,
                        analysis=analysis.analysis,
                        key_factors=analysis.key_factors if preferences.include_key_factors else [],
                        threshold_used=threshold
                    )
                    
                    logger.info(f"Email alert sent for {symbol}")
                    
            except Exception as e:
                logger.error(f"Error processing stock {symbol}: {str(e)}")
        
        logger.info("Stock price check completed successfully")
        
    except Exception as e:
        logger.error(f"Error in stock price check task: {str(e)}")
        raise

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function.
    
    Args:
        event: Lambda event data
        context: Lambda context object
        
    Returns:
        Response dictionary
    """
    try:
        logger.info(f"Lambda invoked with event: {json.dumps(event)}")
        
        # Initialize services on first invocation
        initialize_services()
        
        # Run the stock checking task
        asyncio.run(stock_price_check_task())
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Stock price check completed successfully',
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': context.aws_request_id
            })
        }
        
    except Exception as e:
        logger.error(f"Lambda execution failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Stock price check failed',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': context.aws_request_id
            })
        }
