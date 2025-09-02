"""
Stock-related Pydantic models.

This file defines the "data structures" for all stock-related information
in our system. Think of these as "forms" or "templates" that describe
what information we need to store about stocks, prices, and alerts.

What this file contains:
- Stock: Information about a stock we're tracking
- StockPrice: A single price reading at a specific time
- StockAlert: An alert that was triggered by price changes
- StockNews: News articles related to stock movements
- MarketData: General market information
- StockAnalysis: AI analysis of stock movements

For beginners: Pydantic models are like "blueprints" that define what
data looks like and how it should be validated. They help catch errors
and make sure our data is always in the right format.
"""

# Standard library imports
from typing import Optional, List  # For optional values and lists
from datetime import datetime  # For dates and times
from decimal import Decimal  # For precise financial calculations

# Third-party imports
from pydantic import BaseModel, Field, validator  # For data models and validation


class Stock(BaseModel):
    """
    Model representing a tracked stock.
    
    This is like a "profile" for each stock that the user wants to track.
    It stores all the important information about a stock and keeps track
    of its current status.
    
    Attributes:
        symbol: Stock symbol (like "AAPL" for Apple, "TSLA" for Tesla)
        name: Full company name (like "Apple Inc.")
        current_price: The most recent price we fetched
        previous_price: The price from the last time we checked
        added_date: When the user first added this stock to their watchlist
        last_checked: When we last fetched the price for this stock
        is_active: Whether we're still tracking this stock (user can pause tracking)
    """
    
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, TSLA)")
    name: Optional[str] = Field(None, description="Company name")
    current_price: Optional[Decimal] = Field(None, description="Current stock price")
    previous_price: Optional[Decimal] = Field(None, description="Previous recorded price")
    added_date: datetime = Field(default_factory=datetime.utcnow, description="When stock was added")
    last_checked: Optional[datetime] = Field(None, description="Last time price was checked")
    is_active: bool = Field(default=True, description="Whether stock is actively tracked")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """
        Validate stock symbol format.
        
        This makes sure the stock symbol is:
        - Not empty
        - A string (not a number or other type)
        - Converted to uppercase (AAPL not aapl)
        - Trimmed of extra spaces
        """
        if not v or not isinstance(v, str):
            raise ValueError("Stock symbol must be a non-empty string")
        return v.upper().strip()
    
    @validator('current_price', 'previous_price')
    def validate_price(cls, v):
        """
        Validate price values.
        
        This makes sure prices are not negative (stocks can't have negative prices).
        """
        if v is not None and v < 0:
            raise ValueError("Price cannot be negative")
        return v


class StockPrice(BaseModel):
    """
    Model for stock price data points.
    
    This model represents a single price reading for a stock
    at a specific point in time.
    """
    
    symbol: str = Field(..., description="Stock symbol")
    price: Decimal = Field(..., description="Stock price")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Price timestamp")
    volume: Optional[int] = Field(None, description="Trading volume")
    change: Optional[Decimal] = Field(None, description="Price change from previous close")
    change_percent: Optional[Decimal] = Field(None, description="Percentage change")
    
    @validator('price', 'change', 'change_percent')
    def validate_decimal_fields(cls, v):
        """Validate decimal fields."""
        if v is not None and v < 0 and v != 0:
            # Allow negative values for change and change_percent
            pass
        return v


class StockAlert(BaseModel):
    """
    Model for stock price alerts.
    
    This model represents an alert that was triggered when
    a stock price changed beyond the threshold.
    """
    
    id: Optional[int] = Field(None, description="Alert ID")
    symbol: str = Field(..., description="Stock symbol")
    previous_price: Decimal = Field(..., description="Previous price")
    current_price: Decimal = Field(..., description="Current price")
    change_percent: Decimal = Field(..., description="Percentage change")
    threshold_percent: Decimal = Field(..., description="Alert threshold percentage")
    alert_message: str = Field(..., description="AI-generated alert message")
    news_summary: Optional[str] = Field(None, description="News summary for the price change")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Alert creation time")
    sent_at: Optional[datetime] = Field(None, description="When alert was sent via SMS")
    is_sent: bool = Field(default=False, description="Whether alert was sent")
    
    @validator('change_percent', 'threshold_percent')
    def validate_percentages(cls, v):
        """Validate percentage values."""
        if v is None:
            return v
        # Allow both positive and negative percentages
        return v


class StockNews(BaseModel):
    """
    Model for stock-related news articles.
    
    This model represents news articles that might explain
    stock price movements.
    """
    
    title: str = Field(..., description="News article title")
    summary: str = Field(..., description="Article summary")
    url: Optional[str] = Field(None, description="Article URL")
    published_at: Optional[datetime] = Field(None, description="Publication date")
    source: Optional[str] = Field(None, description="News source")
    relevance_score: Optional[float] = Field(None, description="Relevance to stock movement")


class MarketData(BaseModel):
    """
    Model for general market data.
    
    This model represents broader market information that
    might be relevant to stock movements.
    """
    
    market_index: str = Field(..., description="Market index (e.g., SPY, QQQ)")
    current_value: Decimal = Field(..., description="Current index value")
    change_percent: Decimal = Field(..., description="Index change percentage")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data timestamp")


class StockAnalysis(BaseModel):
    """
    Model for AI-generated stock analysis.
    
    This model represents the AI's analysis of why a stock
    price moved and what it means.
    """
    
    symbol: str = Field(..., description="Stock symbol")
    analysis: str = Field(..., description="AI-generated analysis")
    confidence_score: Optional[float] = Field(None, description="Analysis confidence (0-1)")
    key_factors: List[str] = Field(default_factory=list, description="Key factors identified")
    recommendation: Optional[str] = Field(None, description="AI recommendation")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
