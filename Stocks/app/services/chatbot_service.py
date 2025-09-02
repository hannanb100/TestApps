"""
Chatbot service for interpreting SMS commands using LangChain.

This service is like a "smart translator" that understands what users want
when they send SMS messages. It uses AI (OpenAI) to interpret natural language
and convert it into specific actions the system can perform.

What this service does:
- Takes SMS messages like "Add AAPL" or "Remove Tesla"
- Uses AI to understand the user's intent
- Converts the message into structured commands
- Validates that the commands make sense
- Generates user-friendly responses

For beginners: This is the "brain" that makes the system understand human language.
Instead of requiring users to type exact commands, they can write naturally
and the AI figures out what they want to do.
"""

# Standard library imports
import logging  # For recording what happens
from typing import Dict, Any, Optional, List  # For type hints
from datetime import datetime  # For timestamps
import json  # For working with JSON data
import re  # For text pattern matching

# Third-party imports
from langchain.llms import OpenAI  # OpenAI language model
from langchain.prompts import PromptTemplate  # For creating AI prompts
from langchain.chains import LLMChain  # For chaining AI operations
from langchain.schema import BaseOutputParser  # For parsing AI responses
from pydantic import BaseModel, Field  # For data validation

# Our custom imports
from ..models.sms import SMSCommand, SMSMessage  # SMS data models
from ..models.config import settings  # App configuration

# Set up logging for this file
logger = logging.getLogger(__name__)


class CommandOutput(BaseModel):
    """
    Pydantic model for parsed command output.
    
    This is like a "form" that holds the structured information
    that the AI extracts from a user's SMS message.
    
    Attributes:
        command_type: What the user wants to do (add, remove, list, etc.)
        symbol: The stock symbol (like "AAPL" for Apple)
        confidence: How sure the AI is about its interpretation (0.0 to 1.0)
        parameters: Any extra information the AI found
    """
    command_type: str = Field(..., description="Type of command (add, remove, list, etc.)")
    symbol: Optional[str] = Field(None, description="Stock symbol (AAPL, TSLA, etc.)")
    confidence: float = Field(..., description="How confident the AI is (0.0 to 1.0)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional information found")


class CommandOutputParser(BaseOutputParser):
    """
    Custom output parser for command parsing.
    
    This class takes the raw text response from the AI and converts it
    into a structured CommandOutput object that our system can work with.
    
    Think of it as a "translator" that converts AI text into organized data.
    """
    
    def parse(self, text: str) -> CommandOutput:
        """
        Parse LLM output into CommandOutput.
        
        Args:
            text: Raw LLM output
            
        Returns:
            CommandOutput object
        """
        try:
            # Try to parse as JSON first
            if text.strip().startswith('{'):
                data = json.loads(text.strip())
            else:
                # Fallback to regex parsing
                data = self._parse_with_regex(text)
            
            return CommandOutput(**data)
            
        except Exception as e:
            logger.error(f"Error parsing command output: {str(e)}")
            # Return default help command
            return CommandOutput(
                command_type="help",
                confidence=0.0,
                parameters={"error": str(e)}
            )
    
    def _parse_with_regex(self, text: str) -> Dict[str, Any]:
        """
        Parse command using regex patterns.
        
        Args:
            text: Raw text to parse
            
        Returns:
            Dictionary with parsed command data
        """
        # Extract command type
        command_type = "help"
        if re.search(r'\b(add|track|watch)\b', text.lower()):
            command_type = "add"
        elif re.search(r'\b(remove|delete|stop)\b', text.lower()):
            command_type = "remove"
        elif re.search(r'\b(list|show|display)\b', text.lower()):
            command_type = "list"
        elif re.search(r'\b(status|health)\b', text.lower()):
            command_type = "status"
        elif re.search(r'\b(help|commands)\b', text.lower()):
            command_type = "help"
        
        # Extract symbol
        symbol = None
        symbol_match = re.search(r'\b([A-Z]{1,5})\b', text.upper())
        if symbol_match:
            symbol = symbol_match.group(1)
        
        # Calculate confidence based on clarity
        confidence = 0.8
        if not symbol and command_type in ["add", "remove"]:
            confidence = 0.3
        elif command_type == "help":
            confidence = 1.0
        
        return {
            "command_type": command_type,
            "symbol": symbol,
            "confidence": confidence,
            "parameters": {}
        }


class ChatbotService:
    """
    Service for interpreting SMS commands using LangChain.
    
    This service uses OpenAI's LLM to understand natural language
    commands and convert them into structured actions.
    """
    
    def __init__(self):
        """Initialize the chatbot service."""
        try:
            # Initialize OpenAI LLM
            self.llm = OpenAI(
                openai_api_key=settings.openai_api_key,
                temperature=0.1,  # Low temperature for consistent parsing
                max_tokens=150
            )
            
            # Create command parsing prompt
            self.command_prompt = PromptTemplate(
                input_variables=["message"],
                template="""
You are a stock tracking assistant. Parse the following SMS message into a JSON command.

Available commands:
- add: Add a stock to watchlist (requires stock symbol)
- remove: Remove a stock from watchlist (requires stock symbol)  
- list: Show all tracked stocks
- status: Check system status
- help: Show available commands

Message: "{message}"

Respond with JSON only in this format:
{{
    "command_type": "add|remove|list|status|help",
    "symbol": "STOCK_SYMBOL_OR_NULL",
    "confidence": 0.0-1.0,
    "parameters": {{}}
}}

Examples:
- "Add AAPL" -> {{"command_type": "add", "symbol": "AAPL", "confidence": 0.9, "parameters": {{}}}}
- "Remove TSLA" -> {{"command_type": "remove", "symbol": "TSLA", "confidence": 0.9, "parameters": {{}}}}
- "List my stocks" -> {{"command_type": "list", "symbol": null, "confidence": 0.9, "parameters": {{}}}}
- "Help" -> {{"command_type": "help", "symbol": null, "confidence": 1.0, "parameters": {{}}}}
                """.strip()
            )
            
            # Create LLM chain
            self.command_chain = LLMChain(
                llm=self.llm,
                prompt=self.command_prompt,
                output_parser=CommandOutputParser()
            )
            
            logger.info("Chatbot service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize chatbot service: {str(e)}")
            raise
    
    async def parse_command(self, sms_message: SMSMessage) -> SMSCommand:
        """
        Parse an SMS message into a structured command.
        
        Args:
            sms_message: SMSMessage object containing the user's message
            
        Returns:
            SMSCommand object with parsed command information
        """
        try:
            logger.info(f"Parsing command from SMS: {sms_message.body[:50]}...")
            
            # Use LangChain to parse the command
            result = await self._parse_with_llm(sms_message.body)
            
            # Create SMSCommand object
            command = SMSCommand(
                command_type=result.command_type,
                symbol=result.symbol,
                original_message=sms_message.body,
                confidence=result.confidence,
                parameters=result.parameters,
                created_at=datetime.utcnow()
            )
            
            logger.info(f"Parsed command: {command.command_type} for {command.symbol}")
            return command
            
        except Exception as e:
            logger.error(f"Error parsing command: {str(e)}")
            # Return help command as fallback
            return SMSCommand(
                command_type="help",
                original_message=sms_message.body,
                confidence=0.0,
                parameters={"error": str(e)}
            )
    
    async def _parse_with_llm(self, message: str) -> CommandOutput:
        """
        Parse message using LangChain LLM.
        
        Args:
            message: User's SMS message
            
        Returns:
            CommandOutput object
        """
        try:
            # Run the LLM chain
            result = self.command_chain.run(message=message)
            return result
            
        except Exception as e:
            logger.error(f"LLM parsing failed: {str(e)}")
            # Fallback to regex parsing
            parser = CommandOutputParser()
            return parser._parse_with_regex(message)
    
    def validate_command(self, command: SMSCommand) -> Dict[str, Any]:
        """
        Validate a parsed command.
        
        Args:
            command: SMSCommand object to validate
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check command type
        valid_commands = ["add", "remove", "list", "status", "help"]
        if command.command_type not in valid_commands:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Invalid command type: {command.command_type}")
        
        # Check symbol requirement
        if command.command_type in ["add", "remove"] and not command.symbol:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Command '{command.command_type}' requires a stock symbol")
        
        # Check confidence level
        if command.confidence < 0.5:
            validation_result["warnings"].append("Low confidence in command parsing")
        
        # Validate symbol format
        if command.symbol:
            if not re.match(r'^[A-Z]{1,5}$', command.symbol):
                validation_result["is_valid"] = False
                validation_result["errors"].append(f"Invalid stock symbol format: {command.symbol}")
        
        return validation_result
    
    async def generate_response(self, command: SMSCommand, 
                              execution_result: Dict[str, Any]) -> str:
        """
        Generate a response message for a command execution.
        
        Args:
            command: Original SMSCommand
            execution_result: Result from command execution
            
        Returns:
            Response message string
        """
        try:
            if command.command_type == "add":
                if execution_result.get("success"):
                    return f"✅ {command.symbol} added to your watchlist!"
                else:
                    return f"❌ Failed to add {command.symbol}: {execution_result.get('error', 'Unknown error')}"
            
            elif command.command_type == "remove":
                if execution_result.get("success"):
                    return f"✅ {command.symbol} removed from your watchlist!"
                else:
                    return f"❌ Failed to remove {command.symbol}: {execution_result.get('error', 'Unknown error')}"
            
            elif command.command_type == "list":
                stocks = execution_result.get("stocks", [])
                if stocks:
                    stock_list = "\n".join([f"• {stock}" for stock in stocks])
                    return f"📋 Your tracked stocks:\n{stock_list}"
                else:
                    return "📋 No stocks in your watchlist. Send 'Add SYMBOL' to start tracking!"
            
            elif command.command_type == "status":
                return "📊 System status: All systems operational ✅"
            
            elif command.command_type == "help":
                return """
📈 Stock Tracker Commands:

• Add AAPL - Add stock to watchlist
• Remove TSLA - Remove stock from watchlist  
• List - Show all tracked stocks
• Status - Check system status
• Help - Show this message

Example: "Add AAPL" or "Remove TSLA"
                """.strip()
            
            else:
                return "❓ I didn't understand that command. Send 'help' for available commands."
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "❌ An error occurred. Please try again or send 'help' for assistance."
    
    def get_supported_commands(self) -> List[Dict[str, Any]]:
        """
        Get list of supported commands.
        
        Returns:
            List of command information dictionaries
        """
        return [
            {
                "command": "add",
                "description": "Add a stock to your watchlist",
                "example": "Add AAPL",
                "requires_symbol": True
            },
            {
                "command": "remove", 
                "description": "Remove a stock from your watchlist",
                "example": "Remove TSLA",
                "requires_symbol": True
            },
            {
                "command": "list",
                "description": "Show all tracked stocks",
                "example": "List my stocks",
                "requires_symbol": False
            },
            {
                "command": "status",
                "description": "Check system status",
                "example": "Status",
                "requires_symbol": False
            },
            {
                "command": "help",
                "description": "Show available commands",
                "example": "Help",
                "requires_symbol": False
            }
        ]
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get chatbot service status.
        
        Returns:
            Dictionary with service status information
        """
        return {
            "service": "Chatbot Service",
            "llm_provider": "OpenAI",
            "supported_commands": len(self.get_supported_commands()),
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }
