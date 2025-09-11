"""
Main FastAPI application for the AI Stock Tracking Agent.

This is the main entry point for our web application. Think of it as the "brain" 
that coordinates all the different parts of our stock tracking system.

What this file does:
- Sets up the web server (FastAPI)
- Connects all our services together (SMS, stock data, AI analysis)
- Handles incoming web requests
- Manages background tasks (like checking stock prices)
- Provides error handling and logging

For beginners: FastAPI is a modern Python web framework that makes it easy to 
build APIs (Application Programming Interfaces) - basically, it lets other 
programs talk to our application over the internet.
"""

# Standard library imports - these come with Python
from calendar import weekday
import logging  # For recording what happens in our app
import asyncio  # For handling multiple tasks at the same time
from contextlib import asynccontextmanager  # For managing app startup/shutdown
from typing import Dict, Any  # For type hints (helps catch errors)

# Third-party imports - these are external packages we installed
from fastapi import FastAPI, Request, HTTPException  # Web framework
from fastapi.middleware.cors import CORSMiddleware  # Allows web browsers to access our API
from fastapi.middleware.trustedhost import TrustedHostMiddleware  # Security middleware
from fastapi.responses import JSONResponse  # For sending JSON data back to clients
from fastapi.openapi.docs import get_swagger_ui_html  # For API documentation
from fastapi.openapi.utils import get_openapi  # For API schema generation

# Our custom imports - these are files we created in this project
from .routes import webhooks_router, api_router, health_router  # URL routing
from .services.scheduler_service import SchedulerService  # Background task scheduler
from .services.stock_service import StockService  # Stock data fetching
from .services.sms_service import SMSService  # SMS messaging (legacy)
from .services.email_service import EmailService  # Email messaging
from .services.agent_service import AgentService  # AI analysis
from .models.config import settings  # App configuration

# Configure logging - this sets up how we record what happens in our app
# Logging is like keeping a diary of what your app does - very useful for debugging!
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),  # How detailed the logs should be
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Format of log messages
)
logger = logging.getLogger(__name__)  # Create a logger for this specific file

# Global service instances - these will hold our main services
# Think of these as the "workers" that do the actual work
scheduler_service = None  # Handles scheduled tasks (like checking stock prices every hour)
stock_service = None      # Fetches stock data from the internet
sms_service = None        # Sends and receives SMS messages (legacy)
email_service = None      # Sends email alerts
agent_service = None      # Uses AI to analyze stock movements


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    This function is like a "lifecycle manager" for our app. It handles:
    - Starting up all our services when the app starts
    - Shutting down everything cleanly when the app stops
    
    Think of it like turning on/off a complex machine - you need to start
    all the parts in the right order, and shut them down safely too.
    
    The @asynccontextmanager decorator tells FastAPI to call this function
    when the app starts and stops.
    """
    # Make these variables available throughout the function
    global scheduler_service, stock_service, sms_service, email_service, agent_service
    
    # ===== STARTUP PHASE =====
    logger.info("Starting AI Stock Tracking Agent...")
    
    try:
        # Initialize all our services - this is like hiring all the workers
        logger.info("Creating service instances...")
        stock_service = StockService()      # Worker that gets stock prices
        sms_service = SMSService()          # Worker that sends SMS messages (legacy)
        email_service = EmailService()      # Worker that sends email alerts
        agent_service = AgentService()      # Worker that does AI analysis
        scheduler_service = SchedulerService()  # Worker that schedules tasks
        
        # Tell the scheduler what tasks to run and when
        # This is like setting up a schedule for our workers
        logger.info("Registering scheduled tasks...")
        scheduler_service.register_task_callback('stock_check', stock_price_check_task)
        scheduler_service.register_task_callback('cache_cleanup', cache_cleanup_task)
        scheduler_service.register_task_callback('health_check', health_check_task)
        
        # Start the scheduler - this begins running our scheduled tasks
        logger.info("Starting background scheduler...")
        await scheduler_service.start()
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        # If anything goes wrong during startup, log the error and stop
        logger.error(f"Failed to initialize services: {str(e)}")
        raise  # This stops the app from starting
    
    # The 'yield' keyword is where the app actually runs
    # Everything before yield = startup, everything after = shutdown
    yield
    
    # ===== SHUTDOWN PHASE =====
    logger.info("Shutting down AI Stock Tracking Agent...")
    
    try:
        # Stop the scheduler first - this stops all background tasks
        if scheduler_service:
            logger.info("Stopping background scheduler...")
            await scheduler_service.stop()
        
        # Clean up any cached data
        if stock_service:
            logger.info("Clearing cached data...")
            stock_service.clear_cache()
        
        logger.info("Shutdown completed successfully")
        
    except Exception as e:
        # Log any errors during shutdown, but don't crash
        logger.error(f"Error during shutdown: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title="AI Stock Tracking Agent",
    description="""
    An AI-powered stock tracking system that monitors stock prices and sends SMS alerts.
    
    ## Features
    
    * **Stock Tracking**: Add/remove stocks from your watchlist via SMS
    * **Price Monitoring**: Automatic price checks with configurable intervals
    * **AI Analysis**: AI-powered analysis of stock movements with news integration
    * **SMS Alerts**: Receive alerts when stocks move beyond your threshold
    * **Natural Language**: Interact with the system using natural language SMS commands
    
    ## SMS Commands
    
    * `Add AAPL` - Add a stock to your watchlist
    * `Remove TSLA` - Remove a stock from your watchlist
    * `List` - Show all tracked stocks
    * `Status` - Check system status
    * `Help` - Show available commands
    
    ## API Endpoints
    
    The API provides REST endpoints for managing stocks, viewing alerts, and monitoring system health.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)


# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with custom error responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with custom error responses."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    )


# Include routers
app.include_router(webhooks_router)
app.include_router(api_router)
app.include_router(health_router)

# Import and include alert history router
from .routes.alert_history import router as alert_history_router
app.include_router(alert_history_router)

# Import and include dashboard router
from .routes.dashboard import router as dashboard_router
app.include_router(dashboard_router)

# Import and include stock list router
from .routes.stock_list import router as stock_list_router
app.include_router(stock_list_router)

# Import and include alert preferences router
from .routes.alert_preferences import router as alert_preferences_router
app.include_router(alert_preferences_router)


# Simple health check endpoint for Railway
@app.get("/health")
async def simple_health():
    """
    Simple health check endpoint for Railway deployment.
    
    Returns:
        Basic health status with HTTP 200
    """
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "AI Stock Tracking Agent",
            "version": "1.0.0",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with basic API information.
    
    Returns:
        Basic API information and links
    """
    return {
        "message": "AI Stock Tracking Agent API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1",
        "webhooks": "/webhooks"
    }


# Custom OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema with additional metadata."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="AI Stock Tracking Agent API",
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom metadata
    openapi_schema["info"]["contact"] = {
        "name": "AI Stock Tracking Agent",
        "email": "support@example.com"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    # Add server information
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Scheduler task functions
async def stock_price_check_task():
    """
    Scheduled task for checking stock prices and triggering alerts.
    
    This function is called by the scheduler at regular intervals
    to check stock prices and send alerts when thresholds are exceeded.
    """
    try:
        logger.info("Executing scheduled stock price check")
        
        # In a real implementation, you would:
        # 1. Get list of tracked stocks from database
        # 2. Fetch current prices for all stocks
        # 3. Compare with previous prices
        # 4. Generate alerts for significant changes
        # 5. Send SMS alerts with AI analysis
        
        # Get dynamic list of tracked stocks from the stock list service
        from .services.stock_list_service import StockListService
        from .services.alert_preferences_service import AlertPreferencesService
        
        stock_list_service = StockListService()
        preferences_service = AlertPreferencesService()
        
        tracked_stocks = stock_list_service.get_active_stocks()
        
        if not tracked_stocks:
            logger.warning("No active stocks found in tracking list")
            return
        
        # Get alert preferences
        preferences = preferences_service.get_preferences()
        if not preferences or not preferences.is_active:
            logger.warning("Alert preferences not active, skipping price checks")
            return
        
        for symbol in tracked_stocks:
            try:
                # Get current quote
                quote = await stock_service.get_stock_quote(symbol)
                if not quote:
                    continue
                
                # Check if alert should be triggered using simple threshold comparison
                threshold = preferences_service.get_effective_threshold(symbol)
                current_price = float(quote.price)
                previous_close = float(quote.previous_close)
                
                # Calculate percentage change from previous close
                price_change_percent = abs((current_price - previous_close) / previous_close * 100)
                
                if price_change_percent >= threshold:
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
                    
            except Exception as e:
                logger.error(f"Error processing stock {symbol}: {str(e)}")
        
        logger.info("Stock price check completed")
        
    except Exception as e:
        logger.error(f"Error in stock price check task: {str(e)}")


async def cache_cleanup_task():
    """
    Scheduled task for cleaning up cached data.
    
    This function is called daily to clean up old cached data
    and temporary files.
    """
    try:
        logger.info("Executing cache cleanup task")
        
        if stock_service:
            stock_service.clear_cache()
        
        logger.info("Cache cleanup completed")
        
    except Exception as e:
        logger.error(f"Error in cache cleanup task: {str(e)}")


async def health_check_task():
    """
    Scheduled task for system health monitoring.
    
    This function is called periodically to check system health
    and log status information.
    """
    try:
        logger.info("Executing health check task")
        
        # Check service status
        services_status = {
            "stock_service": stock_service.get_cache_stats() if stock_service else "unavailable",
            "sms_service": sms_service.get_service_status() if sms_service else "unavailable",
            "agent_service": agent_service.get_service_status() if agent_service else "unavailable",
            "scheduler_service": scheduler_service.get_scheduler_status() if scheduler_service else "unavailable"
        }
        
        logger.info(f"System health check completed: {services_status}")
        
    except Exception as e:
        logger.error(f"Error in health check task: {str(e)}")


# Development server runner
if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting development server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
