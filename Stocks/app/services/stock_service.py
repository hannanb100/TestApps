"""
Stock service for fetching and managing stock data.

This service is like a "stock data specialist" that knows how to:
- Get real-time stock prices from the internet
- Calculate how much stocks have changed in price
- Validate that stock symbols are real
- Store and retrieve stock information
- Handle errors when stock data isn't available

For beginners: This service talks to Yahoo Finance (through the yfinance library)
to get real stock prices. It's like having a financial assistant that can
look up any stock price instantly and tell you how it's performing.
"""

# Standard library imports
import logging  # For recording what happens
from typing import List, Optional, Dict, Any  # For type hints
from datetime import datetime, timedelta  # For working with dates and times
from decimal import Decimal  # For precise financial calculations
import asyncio  # For handling multiple operations at once
from dataclasses import dataclass  # For creating simple data containers

# Third-party imports
import yfinance as yf  # Yahoo Finance library for stock data
import aiohttp  # For making HTTP requests asynchronously

# Our custom imports
from ..models.stock import Stock, StockPrice, StockAlert  # Our stock data models
from ..models.config import settings  # App configuration

# Set up logging for this file
logger = logging.getLogger(__name__)


@dataclass
class StockQuote:
    """
    Data class for stock quote information.
    
    This is like a "container" that holds all the important information
    about a stock at a specific moment in time. Think of it as a snapshot
    of a stock's current status.
    
    Attributes:
        symbol: Stock symbol (like "AAPL" for Apple)
        price: Current price per share
        change: How much the price changed (in dollars)
        change_percent: How much the price changed (as a percentage)
        volume: How many shares were traded today
        high: Highest price today
        low: Lowest price today
        open_price: Price when the market opened
        previous_close: Price when the market closed yesterday
        timestamp: When this data was fetched
    """
    symbol: str
    price: Decimal
    change: Decimal
    change_percent: Decimal
    volume: int
    high: Decimal
    low: Decimal
    open_price: Decimal
    previous_close: Decimal
    timestamp: datetime


class StockService:
    """
    Service for managing stock data and price tracking.
    
    This class is like a "stock market expert" that can:
    - Look up any stock price instantly
    - Tell you how much a stock has changed
    - Check if a stock symbol is valid
    - Remember stock prices for comparison
    - Handle errors gracefully when data isn't available
    
    It uses Yahoo Finance to get real, live stock data from the internet.
    """
    
    def __init__(self):
        """Initialize the stock service."""
        self.session = None
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes cache TTL
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_stock_quote(self, symbol: str) -> Optional[StockQuote]:
        """
        Get current stock quote for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA')
            
        Returns:
            StockQuote object with current price data, or None if not found
            
        Raises:
            ValueError: If symbol is invalid
            Exception: If API request fails
        """
        try:
            # Validate symbol
            symbol = symbol.upper().strip()
            if not symbol or len(symbol) > 10:
                raise ValueError(f"Invalid stock symbol: {symbol}")
            
            # Check cache first
            cache_key = f"quote_{symbol}"
            if cache_key in self._cache:
                cached_data, timestamp = self._cache[cache_key]
                if datetime.utcnow() - timestamp < timedelta(seconds=self._cache_ttl):
                    logger.debug(f"Returning cached quote for {symbol}")
                    return cached_data
            
            # Fetch from yfinance
            logger.info(f"Fetching quote for {symbol}")
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Validate that we got valid data
            if not info or 'regularMarketPrice' not in info:
                logger.warning(f"No price data available for {symbol}")
                return None
            
            # Extract price data
            current_price = Decimal(str(info.get('regularMarketPrice', 0)))
            previous_close = Decimal(str(info.get('previousClose', current_price)))
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close > 0 else Decimal('0')
            
            quote = StockQuote(
                symbol=symbol,
                price=current_price,
                change=change,
                change_percent=change_percent,
                volume=info.get('volume', 0),
                high=Decimal(str(info.get('dayHigh', current_price))),
                low=Decimal(str(info.get('dayLow', current_price))),
                open_price=Decimal(str(info.get('open', current_price))),
                previous_close=previous_close,
                timestamp=datetime.utcnow()
            )
            
            # Cache the result
            self._cache[cache_key] = (quote, datetime.utcnow())
            
            logger.info(f"Successfully fetched quote for {symbol}: ${current_price}")
            return quote
            
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {str(e)}")
            raise
    
    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Optional[StockQuote]]:
        """
        Get quotes for multiple stocks concurrently.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary mapping symbols to StockQuote objects
        """
        logger.info(f"Fetching quotes for {len(symbols)} symbols")
        
        # Create tasks for concurrent fetching
        tasks = []
        for symbol in symbols:
            task = asyncio.create_task(self.get_stock_quote(symbol))
            tasks.append((symbol, task))
        
        # Wait for all tasks to complete
        results = {}
        for symbol, task in tasks:
            try:
                quote = await task
                results[symbol] = quote
            except Exception as e:
                logger.error(f"Failed to fetch quote for {symbol}: {str(e)}")
                results[symbol] = None
        
        logger.info(f"Successfully fetched {len([q for q in results.values() if q])} quotes")
        return results
    
    def calculate_price_change(self, current_price: Decimal, previous_price: Decimal) -> Dict[str, Decimal]:
        """
        Calculate price change metrics.
        
        Args:
            current_price: Current stock price
            previous_price: Previous stock price
            
        Returns:
            Dictionary with change amount and percentage
        """
        if previous_price == 0:
            return {
                'change': Decimal('0'),
                'change_percent': Decimal('0')
            }
        
        change = current_price - previous_price
        change_percent = (change / previous_price) * 100
        
        return {
            'change': change,
            'change_percent': change_percent
        }
    
    def should_trigger_alert(self, change_percent: Decimal, threshold_percent: float) -> bool:
        """
        Check if price change should trigger an alert.
        
        Args:
            change_percent: Percentage change in price
            threshold_percent: Alert threshold percentage
            
        Returns:
            True if alert should be triggered
        """
        abs_change = abs(change_percent)
        return abs_change >= Decimal(str(threshold_percent))
    
    async def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed stock information.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with stock information, or None if not found
        """
        try:
            symbol = symbol.upper().strip()
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return None
            
            # Extract relevant information
            stock_info = {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'previous_close': info.get('previousClose') or info.get('regularMarketPreviousClose'),
                'open_price': info.get('open') or info.get('regularMarketOpen'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'description': info.get('longBusinessSummary', ''),
                'website': info.get('website'),
                'employees': info.get('fullTimeEmployees'),
                'city': info.get('city'),
                'state': info.get('state'),
                'country': info.get('country')
            }
            
            logger.info(f"Retrieved stock info for {symbol}")
            return stock_info
            
        except Exception as e:
            logger.error(f"Error fetching stock info for {symbol}: {str(e)}")
            return None
    
    async def validate_stock_symbol(self, symbol: str) -> bool:
        """
        Validate if a stock symbol exists and is tradeable.
        
        Args:
            symbol: Stock symbol to validate
            
        Returns:
            True if symbol is valid and tradeable
        """
        try:
            symbol = symbol.upper().strip()
            quote = await self.get_stock_quote(symbol)
            return quote is not None
        except Exception as e:
            logger.error(f"Error validating symbol {symbol}: {str(e)}")
            return False
    
    def create_stock_price_record(self, quote: StockQuote) -> StockPrice:
        """
        Create a StockPrice record from a StockQuote.
        
        Args:
            quote: StockQuote object
            
        Returns:
            StockPrice model instance
        """
        return StockPrice(
            symbol=quote.symbol,
            price=quote.price,
            timestamp=quote.timestamp,
            volume=quote.volume,
            change=quote.change,
            change_percent=quote.change_percent
        )
    
    def create_stock_alert(self, symbol: str, previous_price: Decimal, 
                          current_price: Decimal, threshold_percent: float,
                          alert_message: str, news_summary: Optional[str] = None) -> StockAlert:
        """
        Create a StockAlert record.
        
        Args:
            symbol: Stock symbol
            previous_price: Previous price
            current_price: Current price
            threshold_percent: Alert threshold percentage
            alert_message: AI-generated alert message
            news_summary: Optional news summary
            
        Returns:
            StockAlert model instance
        """
        change_percent = self.calculate_price_change(current_price, previous_price)['change_percent']
        
        return StockAlert(
            symbol=symbol,
            previous_price=previous_price,
            current_price=current_price,
            change_percent=change_percent,
            threshold_percent=Decimal(str(threshold_percent)),
            alert_message=alert_message,
            news_summary=news_summary
        )
    
    async def get_historical_prices(self, symbol: str, days: int = 30) -> List[StockPrice]:
        """
        Get historical price data for a stock.
        
        Args:
            symbol: Stock symbol
            days: Number of days of historical data
            
        Returns:
            List of StockPrice records
        """
        try:
            symbol = symbol.upper().strip()
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                logger.warning(f"No historical data available for {symbol}")
                return []
            
            # Convert to StockPrice records
            prices = []
            for date, row in hist.iterrows():
                price = StockPrice(
                    symbol=symbol,
                    price=Decimal(str(row['Close'])),
                    timestamp=date.to_pydatetime(),
                    volume=int(row['Volume']),
                    change=Decimal(str(row['Close'] - row['Open'])),
                    change_percent=Decimal(str((row['Close'] - row['Open']) / row['Open'] * 100))
                )
                prices.append(price)
            
            logger.info(f"Retrieved {len(prices)} historical prices for {symbol}")
            return prices
            
        except Exception as e:
            logger.error(f"Error fetching historical prices for {symbol}: {str(e)}")
            return []
    
    def clear_cache(self):
        """Clear the price cache."""
        self._cache.clear()
        logger.info("Stock price cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        now = datetime.utcnow()
        valid_entries = 0
        expired_entries = 0
        
        for key, (_, timestamp) in self._cache.items():
            if now - timestamp < timedelta(seconds=self._cache_ttl):
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            'total_entries': len(self._cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_ttl_seconds': self._cache_ttl
        }
