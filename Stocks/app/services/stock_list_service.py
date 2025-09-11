"""
Stock List Service - Manages the dynamic list of tracked stocks.

This service handles adding, removing, and updating the list of stocks
that are being monitored for price changes and alerts.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import os

from ..models.stock_list import (
    TrackedStock, 
    StockListResponse, 
    StockListSummary,
    AddStockRequest,
    UpdateStockRequest
)
from ..services.stock_service import StockService

# Configure logging
logger = logging.getLogger(__name__)


class StockListService:
    """
    Service for managing the dynamic list of tracked stocks.
    
    This service stores stock information in a simple JSON file
    for now, but could be easily upgraded to use a database later.
    """
    
    def __init__(self, storage_file: str = "tracked_stocks.json"):
        """
        Initialize the stock list service.
        
        Args:
            storage_file: Path to the JSON file for storing tracked stocks
        """
        self.storage_file = storage_file
        self.tracked_stocks: List[TrackedStock] = []
        self.stock_service = StockService()
        self._load_stocks()
        logger.info(f"StockListService initialized with {len(self.tracked_stocks)} tracked stocks")
    
    def _load_stocks(self):
        """Load existing tracked stocks from the storage file."""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.tracked_stocks = [TrackedStock(**stock) for stock in data]
                logger.info(f"Loaded {len(self.tracked_stocks)} tracked stocks from {self.storage_file}")
            else:
                # Initialize with default stocks if no file exists
                self._initialize_default_stocks()
                logger.info(f"No existing stock list file found, initialized with default stocks")
        except Exception as e:
            logger.error(f"Error loading tracked stocks: {str(e)}")
            self._initialize_default_stocks()
    
    def _initialize_default_stocks(self):
        """Initialize with default tracked stocks."""
        default_stocks = [
            TrackedStock(symbol="VOO", name="Vanguard S&P 500 ETF", alert_threshold=1.0),
            TrackedStock(symbol="QQQM", name="Invesco NASDAQ 100 ETF", alert_threshold=1.0),
            TrackedStock(symbol="SCHD", name="Schwab U.S. Dividend Equity ETF", alert_threshold=1.0),
            TrackedStock(symbol="VT", name="Vanguard Total World Stock ETF", alert_threshold=1.0),
            TrackedStock(symbol="SPLG", name="SPDR Portfolio S&P 500 ETF", alert_threshold=1.0),
            TrackedStock(symbol="SPY", name="SPDR S&P 500 ETF Trust", alert_threshold=1.0),
            TrackedStock(symbol="JEPI", name="JPMorgan Equity Premium Income ETF", alert_threshold=1.0),
            TrackedStock(symbol="MSTY", name="YieldMax MSTR Option Income Strategy ETF", alert_threshold=1.0),
            TrackedStock(symbol="ARKK", name="ARK Innovation ETF", alert_threshold=1.0),
            TrackedStock(symbol="WDAY", name="Workday Inc.", alert_threshold=0.5)
        ]
        
        # Assign IDs to default stocks
        for i, stock in enumerate(default_stocks, 1):
            stock.id = i
        
        self.tracked_stocks = default_stocks
        self._save_stocks()
    
    def _save_stocks(self):
        """Save tracked stocks to the storage file."""
        try:
            # Convert stocks to dictionaries for JSON serialization
            stocks_data = [stock.model_dump() for stock in self.tracked_stocks]
            
            with open(self.storage_file, 'w') as f:
                json.dump(stocks_data, f, indent=2, default=str)
            
            logger.info(f"Saved {len(self.tracked_stocks)} tracked stocks to {self.storage_file}")
        except Exception as e:
            logger.error(f"Error saving tracked stocks: {str(e)}")
    
    def get_all_stocks(self) -> List[StockListResponse]:
        """
        Get all tracked stocks with computed fields.
        
        Returns:
            List of all tracked stocks with additional computed information
        """
        try:
            response_stocks = []
            
            for stock in self.tracked_stocks:
                # Calculate days tracked
                # Handle both datetime and string formats for added_date
                if isinstance(stock.added_date, str):
                    try:
                        added_date = datetime.fromisoformat(stock.added_date.replace('Z', '+00:00'))
                    except ValueError:
                        added_date = datetime.utcnow()
                else:
                    added_date = stock.added_date
                
                days_tracked = (datetime.utcnow() - added_date).days
                
                # Get current price (optional, might fail)
                current_price = None
                try:
                    # Note: get_stock_info is async, but we're in a sync method
                    # For now, we'll skip current price fetching in this method
                    # TODO: Make this method async or use a different approach
                    pass
                except Exception as e:
                    logger.debug(f"Could not get current price for {stock.symbol}: {str(e)}")
                
                # Create response object
                response_stock = StockListResponse(
                    id=stock.id,
                    symbol=stock.symbol,
                    name=stock.name,
                    added_date=stock.added_date.isoformat() if isinstance(stock.added_date, datetime) else stock.added_date,
                    is_active=stock.is_active,
                    alert_threshold=stock.alert_threshold,
                    notes=stock.notes,
                    days_tracked=days_tracked,
                    current_price=current_price,
                    last_alert=None  # TODO: Get from alert history
                )
                
                response_stocks.append(response_stock)
            
            logger.info(f"Retrieved {len(response_stocks)} tracked stocks")
            return response_stocks
            
        except Exception as e:
            logger.error(f"Error getting all stocks: {str(e)}")
            return []
    
    def get_active_stocks(self) -> List[str]:
        """
        Get list of active stock symbols for monitoring.
        
        Returns:
            List of stock symbols that are actively being monitored
        """
        try:
            active_symbols = [
                stock.symbol for stock in self.tracked_stocks 
                if stock.is_active
            ]
            logger.info(f"Retrieved {len(active_symbols)} active stock symbols")
            return active_symbols
            
        except Exception as e:
            logger.error(f"Error getting active stocks: {str(e)}")
            return []
    
    def get_stock_by_id(self, stock_id: int) -> Optional[StockListResponse]:
        """
        Get a specific tracked stock by ID.
        
        Args:
            stock_id: The ID of the stock to retrieve
            
        Returns:
            StockListResponse if found, None otherwise
        """
        try:
            stock = next((s for s in self.tracked_stocks if s.id == stock_id), None)
            
            if not stock:
                logger.warning(f"Stock with ID {stock_id} not found")
                return None
            
            # Calculate days tracked
            days_tracked = (datetime.utcnow() - stock.added_date).days
            
            # Get current price (optional)
            current_price = None
            try:
                # Note: get_stock_info is async, but we're in a sync method
                # For now, we'll skip current price fetching in this method
                # TODO: Make this method async or use a different approach
                pass
            except Exception as e:
                logger.debug(f"Could not get current price for {stock.symbol}: {str(e)}")
            
            response_stock = StockListResponse(
                id=stock.id,
                symbol=stock.symbol,
                name=stock.name,
                added_date=stock.added_date,
                is_active=stock.is_active,
                alert_threshold=stock.alert_threshold,
                notes=stock.notes,
                days_tracked=days_tracked,
                current_price=current_price,
                last_alert=None  # TODO: Get from alert history
            )
            
            logger.info(f"Retrieved stock {stock.symbol} (ID: {stock_id})")
            return response_stock
            
        except Exception as e:
            logger.error(f"Error getting stock by ID {stock_id}: {str(e)}")
            return None
    
    async def add_stock(self, request: AddStockRequest) -> Optional[StockListResponse]:
        """
        Add a new stock to the tracking list.
        
        Args:
            request: AddStockRequest with stock information
            
        Returns:
            StockListResponse if successful, None if failed
        """
        try:
            # Validate stock symbol
            symbol = request.symbol.upper().strip()
            if not symbol or len(symbol) > 10:
                logger.error(f"Invalid stock symbol: {symbol}")
                return None
            
            # Check if stock already exists
            existing_stock = next((s for s in self.tracked_stocks if s.symbol.upper() == symbol), None)
            if existing_stock:
                logger.warning(f"Stock {symbol} is already being tracked")
                return None
            
            # Validate stock exists by fetching basic info
            try:
                # Import here to avoid circular imports
                from .stock_service import StockService
                stock_service = StockService()
                
                # Fetch stock information to validate the symbol and get company name
                stock_info = await stock_service.get_stock_info(symbol)
                
                if not stock_info:
                    logger.error(f"Stock symbol {symbol} not found or invalid")
                    return None
                
                logger.info(f"Found stock {symbol}: {stock_info.get('name', 'Unknown')}")
                
            except Exception as e:
                logger.error(f"Error validating stock {symbol}: {str(e)}")
                return None
            
            # Create new tracked stock
            new_stock = TrackedStock(
                symbol=symbol,
                name=request.name or stock_info.get('name', symbol),
                alert_threshold=request.alert_threshold,
                notes=request.notes,
                added_date=datetime.utcnow(),
                is_active=True
            )
            
            # Assign ID
            if self.tracked_stocks:
                new_stock.id = max(stock.id for stock in self.tracked_stocks if stock.id) + 1
            else:
                new_stock.id = 1
            
            # Add to list
            self.tracked_stocks.append(new_stock)
            
            # Save to file
            self._save_stocks()
            
            logger.info(f"Added stock {symbol} to tracking list (ID: {new_stock.id})")
            
            # Return response object
            return StockListResponse(
                id=new_stock.id,
                symbol=new_stock.symbol,
                name=new_stock.name,
                added_date=new_stock.added_date,
                is_active=new_stock.is_active,
                alert_threshold=new_stock.alert_threshold,
                alert_type=new_stock.alert_type,
                notes=new_stock.notes,
                days_tracked=0,
                current_price=None,  # TODO: Get current price
                last_alert=None
            )
            
        except Exception as e:
            logger.error(f"Error adding stock {request.symbol}: {str(e)}")
            return None
    
    def update_stock(self, stock_id: int, request: UpdateStockRequest) -> Optional[StockListResponse]:
        """
        Update an existing tracked stock.
        
        Args:
            stock_id: The ID of the stock to update
            request: UpdateStockRequest with updated information
            
        Returns:
            StockListResponse if successful, None if failed
        """
        try:
            # Find the stock
            stock = next((s for s in self.tracked_stocks if s.id == stock_id), None)
            if not stock:
                logger.warning(f"Stock with ID {stock_id} not found")
                return None
            
            # Update fields if provided
            if request.name is not None:
                stock.name = request.name
            if request.is_active is not None:
                stock.is_active = request.is_active
            if request.alert_threshold is not None:
                stock.alert_threshold = request.alert_threshold
            if request.notes is not None:
                stock.notes = request.notes
            
            # Save to file
            self._save_stocks()
            
            logger.info(f"Updated stock {stock.symbol} (ID: {stock_id})")
            
            # Return updated response object
            days_tracked = (datetime.utcnow() - stock.added_date).days
            
            return StockListResponse(
                id=stock.id,
                symbol=stock.symbol,
                name=stock.name,
                added_date=stock.added_date,
                is_active=stock.is_active,
                alert_threshold=stock.alert_threshold,
                notes=stock.notes,
                days_tracked=days_tracked,
                current_price=None,  # TODO: Get current price
                last_alert=None
            )
            
        except Exception as e:
            logger.error(f"Error updating stock {stock_id}: {str(e)}")
            return None
    
    def remove_stock(self, stock_id: int) -> bool:
        """
        Remove a stock from the tracking list.
        
        Args:
            stock_id: The ID of the stock to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the stock
            stock = next((s for s in self.tracked_stocks if s.id == stock_id), None)
            if not stock:
                logger.warning(f"Stock with ID {stock_id} not found")
                return False
            
            # Remove from list
            self.tracked_stocks = [s for s in self.tracked_stocks if s.id != stock_id]
            
            # Save to file
            self._save_stocks()
            
            logger.info(f"Removed stock {stock.symbol} (ID: {stock_id}) from tracking list")
            return True
            
        except Exception as e:
            logger.error(f"Error removing stock {stock_id}: {str(e)}")
            return False
    
    def get_stock_list_summary(self) -> StockListSummary:
        """
        Get a summary of the tracked stocks.
        
        Returns:
            Summary statistics about the tracked stocks
        """
        try:
            total_stocks = len(self.tracked_stocks)
            active_stocks = len([s for s in self.tracked_stocks if s.is_active])
            inactive_stocks = total_stocks - active_stocks
            
            # Find most recent addition
            most_recent_addition = None
            if self.tracked_stocks:
                most_recent_addition = max(stock.added_date for stock in self.tracked_stocks)
            
            # Calculate average threshold
            average_threshold = 0.0
            if self.tracked_stocks:
                total_threshold = sum(stock.alert_threshold for stock in self.tracked_stocks)
                average_threshold = total_threshold / len(self.tracked_stocks)
            
            summary = StockListSummary(
                total_stocks=total_stocks,
                active_stocks=active_stocks,
                inactive_stocks=inactive_stocks,
                most_recent_addition=most_recent_addition,
                average_threshold=average_threshold
            )
            
            logger.info(f"Generated stock list summary: {total_stocks} total, {active_stocks} active")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating stock list summary: {str(e)}")
            return StockListSummary(
                total_stocks=0,
                active_stocks=0,
                inactive_stocks=0,
                most_recent_addition=None,
                average_threshold=0.0
            )
