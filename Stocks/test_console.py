#!/usr/bin/env python3
"""
Console-based testing interface for the AI Stock Tracking Agent.

This script provides a simple command-line interface to test all
functionality without requiring Twilio or external SMS services.

What this file does:
- Creates a simple text-based interface for testing
- Simulates SMS commands without needing a phone
- Tests all the AI and stock tracking features
- Provides a way to interact with the system locally

For beginners: This is like a "test drive" version of the app. Instead of
sending real SMS messages, you type commands in the terminal and see
how the system responds. It's perfect for learning how everything works!
"""

# Standard library imports
import asyncio  # For handling async operations (multiple things at once)
import sys      # For system-specific parameters and functions
import os       # For operating system interface
from datetime import datetime  # For working with dates and times

# Add the app directory to the Python path so we can import our modules
# This tells Python where to find our custom code
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import our custom services and models
from app.services.mock_sms_service import MockSMSService  # Fake SMS service
from app.services.chatbot_service import ChatbotService   # AI command interpreter
from app.services.stock_service import StockService       # Stock data fetcher
from app.services.agent_service import AgentService       # AI stock analyzer
from app.models.sms import SMSMessage                     # SMS data structure


class StockTrackerConsole:
    """
    Console interface for testing the AI Stock Tracking Agent.
    
    This class is like a "control panel" that lets you interact with all
    the different parts of the stock tracking system through simple text commands.
    
    Think of it as a simplified version of the full app that runs in your terminal
    instead of through SMS messages. You can test everything without needing
    a phone or spending money on SMS!
    """
    
    def __init__(self):
        """
        Initialize the console interface.
        
        This sets up all the services we need and prepares the interface
        for user interaction.
        """
        # Create our mock SMS service (fake SMS for testing)
        self.mock_sms = MockSMSService()
        
        # These will be initialized later when we start the app
        self.chatbot = None        # AI that understands your commands
        self.stock_service = None  # Service that gets stock prices
        self.agent_service = None  # AI that analyzes stock movements
        
        # Flag to control the main loop
        self.running = True
        
    async def initialize_services(self):
        """
        Initialize all required services.
        
        This method creates instances of all the services we need:
        - ChatbotService: AI that understands and processes commands
        - StockService: Fetches real stock data from the internet
        - AgentService: AI that analyzes stock movements and generates insights
        
        Returns:
            bool: True if all services initialized successfully, False otherwise
        """
        try:
            print("🔄 Initializing services...")
            
            # Create instances of all our services
            # These are like "hiring" all the workers for our system
            self.chatbot = ChatbotService()      # AI command interpreter
            self.stock_service = StockService()  # Stock data fetcher
            self.agent_service = AgentService()  # AI stock analyzer
            
            print("✅ All services initialized successfully!")
            return True
            
        except Exception as e:
            # If anything goes wrong, print the error and return False
            print(f"❌ Error initializing services: {str(e)}")
            return False
    
    async def process_command(self, command: str):
        """
        Process a user command through the entire system.
        
        This method simulates the complete flow of how an SMS command would be
        processed in the real system:
        1. Convert the command to an SMS message format
        2. Use AI to understand what the user wants
        3. Validate that the command makes sense
        4. Execute the requested action
        5. Generate and send a response
        
        Args:
            command: The text command the user typed (e.g., "Add AAPL")
        """
        try:
            # Step 1: Create a mock SMS message from the user's command
            # This simulates receiving an SMS from the user's phone
            sms_message = SMSMessage(
                from_number=self.mock_sms.user_phone,  # User's phone number
                to_number=self.mock_sms.from_number,   # Our system's number
                body=command,                          # The command text
                direction="inbound"                    # Coming into our system
            )
            
            print(f"\n🔄 Processing command: '{command}'")
            
            # Step 2: Use AI to understand what the user wants
            # The chatbot service uses OpenAI to interpret natural language
            parsed_command = await self.chatbot.parse_command(sms_message)
            print(f"📝 Parsed command: {parsed_command.command_type} for {parsed_command.symbol}")
            
            # Step 3: Validate that the command makes sense
            # Check if the stock symbol exists, command is valid, etc.
            validation = self.chatbot.validate_command(parsed_command)
            if not validation["is_valid"]:
                print(f"❌ Command validation failed: {validation['errors']}")
                # Send an error message back to the user
                await self.mock_sms.send_error_message(
                    self.mock_sms.user_phone, 
                    " ".join(validation["errors"])
                )
                return
            
            # Step 4: Execute the actual command (add stock, remove stock, etc.)
            execution_result = await self.execute_command(parsed_command)
            
            # Step 5: Generate a user-friendly response and send it
            response_message = await self.chatbot.generate_response(parsed_command, execution_result)
            await self.mock_sms.send_sms(
                to_number=self.mock_sms.user_phone,
                message=response_message,
                message_type="text"
            )
            
        except Exception as e:
            # If anything goes wrong, log the error and send an error message
            print(f"❌ Error processing command: {str(e)}")
            await self.mock_sms.send_error_message(
                self.mock_sms.user_phone,
                f"An error occurred: {str(e)}"
            )
    
    async def execute_command(self, command):
        """
        Execute a parsed command.
        
        Args:
            command: Parsed SMSCommand object
            
        Returns:
            Execution result dictionary
        """
        try:
            if command.command_type == "add":
                return await self.execute_add_stock(command)
            elif command.command_type == "remove":
                return await self.execute_remove_stock(command)
            elif command.command_type == "list":
                return await self.execute_list_stocks(command)
            elif command.command_type == "status":
                return await self.execute_status_check(command)
            elif command.command_type == "help":
                return {"success": True, "message": "Help command executed"}
            else:
                return {"success": False, "error": f"Unknown command: {command.command_type}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def execute_add_stock(self, command):
        """Execute add stock command."""
        try:
            symbol = command.symbol.upper()
            
            # Validate stock symbol
            is_valid = await self.stock_service.validate_stock_symbol(symbol)
            if not is_valid:
                return {"success": False, "error": f"Invalid stock symbol: {symbol}"}
            
            # Get stock info
            stock_info = await self.stock_service.get_stock_info(symbol)
            if not stock_info:
                return {"success": False, "error": f"Could not fetch information for {symbol}"}
            
            print(f"✅ Stock {symbol} added to watchlist")
            
            return {
                "success": True,
                "symbol": symbol,
                "name": stock_info.get("name", symbol),
                "message": f"{symbol} added successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def execute_remove_stock(self, command):
        """Execute remove stock command."""
        try:
            symbol = command.symbol.upper()
            print(f"✅ Stock {symbol} removed from watchlist")
            
            return {
                "success": True,
                "symbol": symbol,
                "message": f"{symbol} removed successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def execute_list_stocks(self, command):
        """Execute list stocks command."""
        try:
            # Mock stock list
            mock_stocks = ["AAPL", "TSLA", "GOOGL", "MSFT"]
            print(f"📋 Listed {len(mock_stocks)} tracked stocks")
            
            return {
                "success": True,
                "stocks": mock_stocks,
                "count": len(mock_stocks)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def execute_status_check(self, command):
        """Execute status check command."""
        try:
            status_info = {
                "system": "operational",
                "last_check": datetime.utcnow().isoformat(),
                "tracked_stocks": 4,
                "alerts_sent": 0
            }
            
            print("📊 System status checked")
            
            return {
                "success": True,
                "status": status_info
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_stock_analysis(self):
        """Test stock analysis functionality."""
        try:
            print("\n🧪 Testing stock analysis...")
            
            # Test with AAPL
            symbol = "AAPL"
            previous_price = 150.00
            current_price = 155.00
            
            print(f"📊 Analyzing {symbol}: ${previous_price} → ${current_price}")
            
            analysis = await self.agent_service.analyze_stock_movement(
                symbol, previous_price, current_price
            )
            
            print(f"🤖 AI Analysis: {analysis.analysis}")
            print(f"📈 Confidence: {analysis.confidence_score:.2f}")
            print(f"🔑 Key Factors: {', '.join(analysis.key_factors)}")
            
        except Exception as e:
            print(f"❌ Error testing stock analysis: {str(e)}")
    
    def show_help(self):
        """Show help information."""
        print("""
📈 AI Stock Tracking Agent - Console Interface
=============================================

Available Commands:
• Add AAPL     - Add a stock to your watchlist
• Remove TSLA  - Remove a stock from your watchlist
• List         - Show all tracked stocks
• Status       - Check system status
• Help         - Show this help message
• Test         - Run stock analysis test
• History      - Show SMS message history
• Clear        - Clear message history
• Quit         - Exit the application

Examples:
  Add AAPL
  Remove TSLA
  List
  Status
  Test
        """)
    
    def show_message_history(self):
        """Show SMS message history."""
        history = self.mock_sms.get_message_history()
        
        if not history:
            print("📱 No messages in history")
            return
        
        print(f"\n📱 Message History ({len(history)} messages):")
        print("=" * 60)
        
        for i, msg in enumerate(history, 1):
            timestamp = msg["timestamp"].strftime("%H:%M:%S")
            print(f"{i}. [{timestamp}] {msg['type'].upper()}")
            print(f"   To: {msg['to']}")
            print(f"   Message: {msg['message'][:100]}{'...' if len(msg['message']) > 100 else ''}")
            print()
    
    async def run(self):
        """Run the console interface."""
        print("🚀 AI Stock Tracking Agent - Console Interface")
        print("=" * 50)
        
        # Initialize services
        if not await self.initialize_services():
            return
        
        print("\n✅ System ready! Type 'help' for available commands.")
        print("💡 Tip: Try 'Add AAPL' to test the system!")
        
        while self.running:
            try:
                # Get user input
                command = input("\n📱 Enter command: ").strip()
                
                if not command:
                    continue
                
                # Handle special commands
                if command.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    self.running = False
                    break
                elif command.lower() == 'help':
                    self.show_help()
                elif command.lower() == 'history':
                    self.show_message_history()
                elif command.lower() == 'clear':
                    self.mock_sms.clear_message_history()
                    print("🗑️ Message history cleared")
                elif command.lower() == 'test':
                    await self.test_stock_analysis()
                else:
                    # Process as SMS command
                    await self.process_command(command)
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")


async def main():
    """Main entry point."""
    console = StockTrackerConsole()
    await console.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)
