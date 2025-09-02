"""
Unit tests for the chatbot service.

This module contains tests for SMS command parsing, validation,
and response generation functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from app.services.chatbot_service import ChatbotService, CommandOutputParser
from app.models.sms import SMSMessage, SMSCommand


class TestCommandOutputParser:
    """Test cases for CommandOutputParser class."""
    
    def test_parse_json_output(self):
        """Test parsing JSON output from LLM."""
        parser = CommandOutputParser()
        
        json_output = '{"command_type": "add", "symbol": "AAPL", "confidence": 0.9, "parameters": {}}'
        
        result = parser.parse(json_output)
        
        assert result.command_type == "add"
        assert result.symbol == "AAPL"
        assert result.confidence == 0.9
        assert result.parameters == {}
    
    def test_parse_regex_fallback(self):
        """Test regex parsing fallback."""
        parser = CommandOutputParser()
        
        text_output = "Add AAPL to my watchlist"
        
        result = parser._parse_with_regex(text_output)
        
        assert result["command_type"] == "add"
        assert result["symbol"] == "AAPL"
        assert result["confidence"] == 0.8
    
    def test_parse_remove_command(self):
        """Test parsing remove command."""
        parser = CommandOutputParser()
        
        text_output = "Remove TSLA from my portfolio"
        
        result = parser._parse_with_regex(text_output)
        
        assert result["command_type"] == "remove"
        assert result["symbol"] == "TSLA"
        assert result["confidence"] == 0.8
    
    def test_parse_list_command(self):
        """Test parsing list command."""
        parser = CommandOutputParser()
        
        text_output = "Show me all my stocks"
        
        result = parser._parse_with_regex(text_output)
        
        assert result["command_type"] == "list"
        assert result["symbol"] is None
        assert result["confidence"] == 0.8
    
    def test_parse_help_command(self):
        """Test parsing help command."""
        parser = CommandOutputParser()
        
        text_output = "Help me with commands"
        
        result = parser._parse_with_regex(text_output)
        
        assert result["command_type"] == "help"
        assert result["symbol"] is None
        assert result["confidence"] == 1.0
    
    def test_parse_invalid_json(self):
        """Test parsing invalid JSON with regex fallback."""
        parser = CommandOutputParser()
        
        invalid_json = "This is not valid JSON but contains Add AAPL"
        
        result = parser.parse(invalid_json)
        
        assert result.command_type == "add"
        assert result.symbol == "AAPL"
        assert result.confidence == 0.8
    
    def test_parse_exception_handling(self):
        """Test exception handling in parsing."""
        parser = CommandOutputParser()
        
        # This should trigger an exception and return help command
        result = parser.parse("")
        
        assert result.command_type == "help"
        assert result.confidence == 0.0


class TestChatbotService:
    """Test cases for ChatbotService class."""
    
    @pytest.fixture
    def chatbot_service(self):
        """Create a ChatbotService instance for testing."""
        with patch('app.services.chatbot_service.OpenAI'):
            return ChatbotService()
    
    @pytest.fixture
    def mock_sms_message(self):
        """Create a mock SMSMessage for testing."""
        return SMSMessage(
            from_number="+1234567890",
            to_number="+0987654321",
            body="Add AAPL",
            direction="inbound"
        )
    
    def test_validate_command_valid_add(self, chatbot_service):
        """Test validating a valid add command."""
        command = SMSCommand(
            command_type="add",
            symbol="AAPL",
            original_message="Add AAPL",
            confidence=0.9
        )
        
        result = chatbot_service.validate_command(command)
        
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_command_invalid_type(self, chatbot_service):
        """Test validating command with invalid type."""
        command = SMSCommand(
            command_type="invalid",
            symbol="AAPL",
            original_message="Invalid command",
            confidence=0.9
        )
        
        result = chatbot_service.validate_command(command)
        
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
        assert "Invalid command type" in result["errors"][0]
    
    def test_validate_command_missing_symbol(self, chatbot_service):
        """Test validating add command without symbol."""
        command = SMSCommand(
            command_type="add",
            symbol=None,
            original_message="Add",
            confidence=0.9
        )
        
        result = chatbot_service.validate_command(command)
        
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
        assert "requires a stock symbol" in result["errors"][0]
    
    def test_validate_command_low_confidence(self, chatbot_service):
        """Test validating command with low confidence."""
        command = SMSCommand(
            command_type="add",
            symbol="AAPL",
            original_message="Add AAPL",
            confidence=0.3
        )
        
        result = chatbot_service.validate_command(command)
        
        assert result["is_valid"] is True
        assert len(result["warnings"]) > 0
        assert "Low confidence" in result["warnings"][0]
    
    def test_validate_command_invalid_symbol_format(self, chatbot_service):
        """Test validating command with invalid symbol format."""
        command = SMSCommand(
            command_type="add",
            symbol="INVALID_SYMBOL_TOO_LONG",
            original_message="Add INVALID_SYMBOL_TOO_LONG",
            confidence=0.9
        )
        
        result = chatbot_service.validate_command(command)
        
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
        assert "Invalid stock symbol format" in result["errors"][0]
    
    @pytest.mark.asyncio
    async def test_generate_response_add_success(self, chatbot_service):
        """Test generating response for successful add command."""
        command = SMSCommand(
            command_type="add",
            symbol="AAPL",
            original_message="Add AAPL",
            confidence=0.9
        )
        
        execution_result = {
            "success": True,
            "symbol": "AAPL",
            "name": "Apple Inc."
        }
        
        response = await chatbot_service.generate_response(command, execution_result)
        
        assert "AAPL added to your watchlist" in response
        assert "✅" in response
    
    @pytest.mark.asyncio
    async def test_generate_response_add_failure(self, chatbot_service):
        """Test generating response for failed add command."""
        command = SMSCommand(
            command_type="add",
            symbol="INVALID",
            original_message="Add INVALID",
            confidence=0.9
        )
        
        execution_result = {
            "success": False,
            "error": "Invalid stock symbol"
        }
        
        response = await chatbot_service.generate_response(command, execution_result)
        
        assert "Failed to add INVALID" in response
        assert "❌" in response
        assert "Invalid stock symbol" in response
    
    @pytest.mark.asyncio
    async def test_generate_response_remove_success(self, chatbot_service):
        """Test generating response for successful remove command."""
        command = SMSCommand(
            command_type="remove",
            symbol="TSLA",
            original_message="Remove TSLA",
            confidence=0.9
        )
        
        execution_result = {
            "success": True,
            "symbol": "TSLA"
        }
        
        response = await chatbot_service.generate_response(command, execution_result)
        
        assert "TSLA removed from your watchlist" in response
        assert "✅" in response
    
    @pytest.mark.asyncio
    async def test_generate_response_list_with_stocks(self, chatbot_service):
        """Test generating response for list command with stocks."""
        command = SMSCommand(
            command_type="list",
            original_message="List my stocks",
            confidence=0.9
        )
        
        execution_result = {
            "success": True,
            "stocks": ["AAPL", "TSLA", "GOOGL"]
        }
        
        response = await chatbot_service.generate_response(command, execution_result)
        
        assert "Your tracked stocks" in response
        assert "AAPL" in response
        assert "TSLA" in response
        assert "GOOGL" in response
    
    @pytest.mark.asyncio
    async def test_generate_response_list_empty(self, chatbot_service):
        """Test generating response for list command with no stocks."""
        command = SMSCommand(
            command_type="list",
            original_message="List my stocks",
            confidence=0.9
        )
        
        execution_result = {
            "success": True,
            "stocks": []
        }
        
        response = await chatbot_service.generate_response(command, execution_result)
        
        assert "No stocks in your watchlist" in response
        assert "Add SYMBOL" in response
    
    @pytest.mark.asyncio
    async def test_generate_response_status(self, chatbot_service):
        """Test generating response for status command."""
        command = SMSCommand(
            command_type="status",
            original_message="Status",
            confidence=0.9
        )
        
        execution_result = {
            "success": True,
            "status": {"system": "operational"}
        }
        
        response = await chatbot_service.generate_response(command, execution_result)
        
        assert "System status" in response
        assert "operational" in response
    
    @pytest.mark.asyncio
    async def test_generate_response_help(self, chatbot_service):
        """Test generating response for help command."""
        command = SMSCommand(
            command_type="help",
            original_message="Help",
            confidence=1.0
        )
        
        execution_result = {
            "success": True,
            "message": "Help command executed"
        }
        
        response = await chatbot_service.generate_response(command, execution_result)
        
        assert "Stock Tracker Commands" in response
        assert "Add AAPL" in response
        assert "Remove TSLA" in response
        assert "List" in response
    
    @pytest.mark.asyncio
    async def test_generate_response_unknown_command(self, chatbot_service):
        """Test generating response for unknown command."""
        command = SMSCommand(
            command_type="unknown",
            original_message="Unknown command",
            confidence=0.5
        )
        
        execution_result = {
            "success": False,
            "error": "Unknown command"
        }
        
        response = await chatbot_service.generate_response(command, execution_result)
        
        assert "didn't understand" in response
        assert "help" in response
    
    @pytest.mark.asyncio
    async def test_generate_response_exception(self, chatbot_service):
        """Test generating response with exception."""
        command = SMSCommand(
            command_type="add",
            symbol="AAPL",
            original_message="Add AAPL",
            confidence=0.9
        )
        
        execution_result = {
            "success": True,
            "symbol": "AAPL"
        }
        
        # Mock an exception in the response generation
        with patch.object(chatbot_service, '_format_confirmation_message', side_effect=Exception("Test error")):
            response = await chatbot_service.generate_response(command, execution_result)
            
            assert "An error occurred" in response
            assert "try again" in response
    
    def test_get_supported_commands(self, chatbot_service):
        """Test getting list of supported commands."""
        commands = chatbot_service.get_supported_commands()
        
        assert len(commands) == 5
        assert any(cmd["command"] == "add" for cmd in commands)
        assert any(cmd["command"] == "remove" for cmd in commands)
        assert any(cmd["command"] == "list" for cmd in commands)
        assert any(cmd["command"] == "status" for cmd in commands)
        assert any(cmd["command"] == "help" for cmd in commands)
        
        # Check that add and remove require symbols
        add_cmd = next(cmd for cmd in commands if cmd["command"] == "add")
        remove_cmd = next(cmd for cmd in commands if cmd["command"] == "remove")
        
        assert add_cmd["requires_symbol"] is True
        assert remove_cmd["requires_symbol"] is True
    
    def test_get_service_status(self, chatbot_service):
        """Test getting service status."""
        status = chatbot_service.get_service_status()
        
        assert "service" in status
        assert "llm_provider" in status
        assert "supported_commands" in status
        assert "status" in status
        assert "timestamp" in status
        
        assert status["service"] == "Chatbot Service"
        assert status["llm_provider"] == "OpenAI"
        assert status["supported_commands"] == 5
        assert status["status"] == "operational"


class TestSMSCommand:
    """Test cases for SMSCommand model."""
    
    def test_sms_command_creation(self):
        """Test creating an SMSCommand instance."""
        command = SMSCommand(
            command_type="add",
            symbol="AAPL",
            original_message="Add AAPL",
            confidence=0.9
        )
        
        assert command.command_type == "add"
        assert command.symbol == "AAPL"
        assert command.original_message == "Add AAPL"
        assert command.confidence == 0.9
        assert command.parameters == {}
        assert isinstance(command.created_at, datetime)
    
    def test_sms_command_validation(self):
        """Test SMSCommand validation."""
        # Test valid command
        command = SMSCommand(
            command_type="add",
            symbol="AAPL",
            original_message="Add AAPL",
            confidence=0.9
        )
        assert command.command_type == "add"
        
        # Test invalid command type (should raise validation error)
        with pytest.raises(ValueError):
            SMSCommand(
                command_type="invalid",
                symbol="AAPL",
                original_message="Invalid command",
                confidence=0.9
            )
        
        # Test invalid confidence (should raise validation error)
        with pytest.raises(ValueError):
            SMSCommand(
                command_type="add",
                symbol="AAPL",
                original_message="Add AAPL",
                confidence=1.5  # Invalid confidence > 1
            )
