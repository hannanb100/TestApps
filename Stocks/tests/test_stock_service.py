"""
Unit tests for the stock service.

This module contains tests for stock data fetching, price calculations,
and validation functionality.
"""

import pytest
import asyncio
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from app.services.stock_service import StockService, StockQuote
from app.models.stock import StockPrice, StockAlert


class TestStockService:
    """Test cases for StockService class."""
    
    @pytest.fixture
    def stock_service(self):
        """Create a StockService instance for testing."""
        return StockService()
    
    @pytest.fixture
    def mock_quote(self):
        """Create a mock StockQuote for testing."""
        return StockQuote(
            symbol="AAPL",
            price=Decimal("150.00"),
            change=Decimal("2.50"),
            change_percent=Decimal("1.69"),
            volume=1000000,
            high=Decimal("152.00"),
            low=Decimal("148.00"),
            open_price=Decimal("149.50"),
            previous_close=Decimal("147.50"),
            timestamp=datetime.utcnow()
        )
    
    def test_calculate_price_change(self, stock_service):
        """Test price change calculation."""
        current_price = Decimal("150.00")
        previous_price = Decimal("147.50")
        
        result = stock_service.calculate_price_change(current_price, previous_price)
        
        assert result["change"] == Decimal("2.50")
        assert result["change_percent"] == Decimal("1.6949152542372881")
    
    def test_calculate_price_change_zero_previous(self, stock_service):
        """Test price change calculation with zero previous price."""
        current_price = Decimal("150.00")
        previous_price = Decimal("0")
        
        result = stock_service.calculate_price_change(current_price, previous_price)
        
        assert result["change"] == Decimal("0")
        assert result["change_percent"] == Decimal("0")
    
    def test_should_trigger_alert_positive(self, stock_service):
        """Test alert triggering for positive price change."""
        change_percent = Decimal("6.0")
        threshold_percent = 5.0
        
        result = stock_service.should_trigger_alert(change_percent, threshold_percent)
        
        assert result is True
    
    def test_should_trigger_alert_negative(self, stock_service):
        """Test alert triggering for negative price change."""
        change_percent = Decimal("-6.0")
        threshold_percent = 5.0
        
        result = stock_service.should_trigger_alert(change_percent, threshold_percent)
        
        assert result is True
    
    def test_should_trigger_alert_below_threshold(self, stock_service):
        """Test alert not triggering when below threshold."""
        change_percent = Decimal("3.0")
        threshold_percent = 5.0
        
        result = stock_service.should_trigger_alert(change_percent, threshold_percent)
        
        assert result is False
    
    def test_create_stock_price_record(self, stock_service, mock_quote):
        """Test creating StockPrice record from StockQuote."""
        price_record = stock_service.create_stock_price_record(mock_quote)
        
        assert isinstance(price_record, StockPrice)
        assert price_record.symbol == "AAPL"
        assert price_record.price == Decimal("150.00")
        assert price_record.volume == 1000000
        assert price_record.change == Decimal("2.50")
        assert price_record.change_percent == Decimal("1.69")
    
    def test_create_stock_alert(self, stock_service):
        """Test creating StockAlert record."""
        symbol = "AAPL"
        previous_price = Decimal("147.50")
        current_price = Decimal("150.00")
        threshold_percent = 5.0
        alert_message = "AAPL showed strong performance"
        news_summary = "Apple reported strong earnings"
        
        alert = stock_service.create_stock_alert(
            symbol, previous_price, current_price, 
            threshold_percent, alert_message, news_summary
        )
        
        assert isinstance(alert, StockAlert)
        assert alert.symbol == "AAPL"
        assert alert.previous_price == Decimal("147.50")
        assert alert.current_price == Decimal("150.00")
        assert alert.threshold_percent == Decimal("5.0")
        assert alert.alert_message == "AAPL showed strong performance"
        assert alert.news_summary == "Apple reported strong earnings"
    
    @pytest.mark.asyncio
    async def test_validate_stock_symbol_valid(self, stock_service):
        """Test validating a valid stock symbol."""
        with patch.object(stock_service, 'get_stock_quote', return_value=Mock()):
            result = await stock_service.validate_stock_symbol("AAPL")
            assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_stock_symbol_invalid(self, stock_service):
        """Test validating an invalid stock symbol."""
        with patch.object(stock_service, 'get_stock_quote', return_value=None):
            result = await stock_service.validate_stock_symbol("INVALID")
            assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_stock_symbol_exception(self, stock_service):
        """Test validating stock symbol with exception."""
        with patch.object(stock_service, 'get_stock_quote', side_effect=Exception("API Error")):
            result = await stock_service.validate_stock_symbol("AAPL")
            assert result is False
    
    def test_clear_cache(self, stock_service):
        """Test clearing the price cache."""
        # Add some mock data to cache
        stock_service._cache["test_key"] = (Mock(), datetime.utcnow())
        
        stock_service.clear_cache()
        
        assert len(stock_service._cache) == 0
    
    def test_get_cache_stats(self, stock_service):
        """Test getting cache statistics."""
        # Add some mock data to cache
        now = datetime.utcnow()
        stock_service._cache["valid_key"] = (Mock(), now)
        stock_service._cache["expired_key"] = (Mock(), now.replace(year=2020))
        
        stats = stock_service.get_cache_stats()
        
        assert "total_entries" in stats
        assert "valid_entries" in stats
        assert "expired_entries" in stats
        assert "cache_ttl_seconds" in stats
        assert stats["total_entries"] == 2


class TestStockQuote:
    """Test cases for StockQuote dataclass."""
    
    def test_stock_quote_creation(self):
        """Test creating a StockQuote instance."""
        quote = StockQuote(
            symbol="AAPL",
            price=Decimal("150.00"),
            change=Decimal("2.50"),
            change_percent=Decimal("1.69"),
            volume=1000000,
            high=Decimal("152.00"),
            low=Decimal("148.00"),
            open_price=Decimal("149.50"),
            previous_close=Decimal("147.50"),
            timestamp=datetime.utcnow()
        )
        
        assert quote.symbol == "AAPL"
        assert quote.price == Decimal("150.00")
        assert quote.change == Decimal("2.50")
        assert quote.change_percent == Decimal("1.69")
        assert quote.volume == 1000000
        assert quote.high == Decimal("152.00")
        assert quote.low == Decimal("148.00")
        assert quote.open_price == Decimal("149.50")
        assert quote.previous_close == Decimal("147.50")
        assert isinstance(quote.timestamp, datetime)


class TestStockPrice:
    """Test cases for StockPrice model."""
    
    def test_stock_price_creation(self):
        """Test creating a StockPrice instance."""
        price = StockPrice(
            symbol="AAPL",
            price=Decimal("150.00"),
            timestamp=datetime.utcnow(),
            volume=1000000,
            change=Decimal("2.50"),
            change_percent=Decimal("1.69")
        )
        
        assert price.symbol == "AAPL"
        assert price.price == Decimal("150.00")
        assert price.volume == 1000000
        assert price.change == Decimal("2.50")
        assert price.change_percent == Decimal("1.69")
        assert isinstance(price.timestamp, datetime)
    
    def test_stock_price_validation(self):
        """Test StockPrice validation."""
        # Test valid price
        price = StockPrice(
            symbol="AAPL",
            price=Decimal("150.00"),
            timestamp=datetime.utcnow()
        )
        assert price.price == Decimal("150.00")
        
        # Test negative price (should raise validation error)
        with pytest.raises(ValueError):
            StockPrice(
                symbol="AAPL",
                price=Decimal("-150.00"),
                timestamp=datetime.utcnow()
            )


class TestStockAlert:
    """Test cases for StockAlert model."""
    
    def test_stock_alert_creation(self):
        """Test creating a StockAlert instance."""
        alert = StockAlert(
            symbol="AAPL",
            previous_price=Decimal("147.50"),
            current_price=Decimal("150.00"),
            change_percent=Decimal("1.69"),
            threshold_percent=Decimal("5.0"),
            alert_message="AAPL showed strong performance"
        )
        
        assert alert.symbol == "AAPL"
        assert alert.previous_price == Decimal("147.50")
        assert alert.current_price == Decimal("150.00")
        assert alert.change_percent == Decimal("1.69")
        assert alert.threshold_percent == Decimal("5.0")
        assert alert.alert_message == "AAPL showed strong performance"
        assert alert.is_sent is False
        assert isinstance(alert.created_at, datetime)
    
    def test_stock_alert_validation(self):
        """Test StockAlert validation."""
        # Test valid alert
        alert = StockAlert(
            symbol="AAPL",
            previous_price=Decimal("147.50"),
            current_price=Decimal("150.00"),
            change_percent=Decimal("1.69"),
            threshold_percent=Decimal("5.0"),
            alert_message="Test alert"
        )
        assert alert.threshold_percent == Decimal("5.0")
        
        # Test invalid threshold (should raise validation error)
        with pytest.raises(ValueError):
            StockAlert(
                symbol="AAPL",
                previous_price=Decimal("147.50"),
                current_price=Decimal("150.00"),
                change_percent=Decimal("1.69"),
                threshold_percent=Decimal("-5.0"),  # Negative threshold
                alert_message="Test alert"
            )
