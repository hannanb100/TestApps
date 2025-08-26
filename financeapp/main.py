#!/usr/bin/env python3
"""
Financial Advisor Assistant - Command Line Interface

This application provides personalized financial advice using AI analysis.
"""

import sys
from typing import Dict, Optional
from finance_advisor import FinanceAdvisor


def get_user_input() -> Dict[str, str]:
    """Collect financial information from the user via command line."""
    
    print("=" * 60)
    print("🤖 FINANCIAL ADVISOR ASSISTANT")
    print("=" * 60)
    print()
    
    user_data = {}
    
    # Financial Goal
    print("What is your primary financial goal?")
    print("Examples: buy a house, retire early, build emergency fund, save for education")
    user_data['financial_goal'] = input("Financial Goal: ").strip()
    
    # Timeframe
    while True:
        try:
            timeframe = input("How many years do you want to achieve this goal? (e.g., 5, 10, 20): ").strip()
            timeframe_int = int(timeframe)
            if timeframe_int > 0:
                user_data['timeframe'] = timeframe
                break
            else:
                print("Please enter a positive number of years.")
        except ValueError:
            print("Please enter a valid number of years.")
    
    # Current Income
    while True:
        try:
            income = input("What is your monthly income? $").strip()
            income_float = float(income)
            if income_float >= 0:
                user_data['monthly_income'] = income
                break
            else:
                print("Please enter a non-negative amount.")
        except ValueError:
            print("Please enter a valid amount.")
    
    # Current Savings
    while True:
        try:
            savings = input("What is your current total savings? $").strip()
            savings_float = float(savings)
            if savings_float >= 0:
                user_data['current_savings'] = savings
                break
            else:
                print("Please enter a non-negative amount.")
        except ValueError:
            print("Please enter a valid amount.")
    
    # Monthly Expenses
    while True:
        try:
            expenses = input("What are your monthly expenses? $").strip()
            expenses_float = float(expenses)
            if expenses_float >= 0:
                user_data['monthly_expenses'] = expenses
                break
            else:
                print("Please enter a non-negative amount.")
        except ValueError:
            print("Please enter a valid amount.")
    
    # Risk Tolerance
    print("\nWhat is your risk tolerance?")
    print("1. Low - Prefer stable, low-risk investments")
    print("2. Medium - Balanced approach with moderate risk")
    print("3. High - Comfortable with higher risk for higher potential returns")
    
    while True:
        risk_choice = input("Enter your choice (1-3): ").strip()
        if risk_choice in ['1', '2', '3']:
            risk_map = {'1': 'low', '2': 'medium', '3': 'high'}
            user_data['risk_tolerance'] = risk_map[risk_choice]
            break
        else:
            print("Please enter 1, 2, or 3.")
    
    return user_data


def display_advice(advice_list: list, user_data: Dict[str, str]) -> None:
    """Display the financial advice in a clear, formatted way."""
    
    print("\n" + "=" * 60)
    print("💡 PERSONALIZED FINANCIAL ADVICE")
    print("=" * 60)
    print()
    
    print(f"Based on your goal to {user_data['financial_goal']} in {user_data['timeframe']} years:")
    print(f"• Monthly Income: ${user_data['monthly_income']}")
    print(f"• Current Savings: ${user_data['current_savings']}")
    print(f"• Monthly Expenses: ${user_data['monthly_expenses']}")
    print(f"• Risk Tolerance: {user_data['risk_tolerance'].title()}")
    print()
    
    for i, advice in enumerate(advice_list, 1):
        print(f"📋 ADVICE #{i}: {advice['recommendation']}")
        print("-" * 40)
        print(f"💭 Explanation: {advice['explanation']}")
        print(f"📈 Growth Projection: {advice['growth_projection']}")
        print(f"⚠️  Risks & Considerations: {advice['risks']}")
        print()
    
    print("=" * 60)
    print("💡 Remember: This advice is for educational purposes.")
    print("   Consider consulting with a licensed financial advisor for personalized guidance.")
    print("=" * 60)


def main() -> None:
    """Main function to run the financial advisor application."""
    
    try:
        # Get user input
        user_data = get_user_input()
        
        print("\n🔄 Generating personalized financial advice...")
        print("This may take a few moments...")
        
        # Initialize the finance advisor
        advisor = FinanceAdvisor()
        
        # Generate advice
        advice_list = advisor.generate_financial_advice(user_data)
        
        # Display the advice
        display_advice(advice_list, user_data)
        
        # Ask if user wants to save advice
        save_choice = input("\nWould you like to save this advice to a file? (y/n): ").strip().lower()
        if save_choice in ['y', 'yes']:
            save_advice_to_file(advice_list, user_data)
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using the Financial Advisor Assistant.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please check your .env file and ensure your OpenAI API key is set correctly.")
        sys.exit(1)


def save_advice_to_file(advice_list: list, user_data: Dict[str, str]) -> None:
    """Save the financial advice to a text file."""
    
    try:
        filename = f"financial_advice_{user_data['financial_goal'].replace(' ', '_').lower()}.txt"
        
        with open(filename, 'w') as f:
            f.write("FINANCIAL ADVISOR ASSISTANT - PERSONALIZED ADVICE\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Financial Goal: {user_data['financial_goal']}\n")
            f.write(f"Timeframe: {user_data['timeframe']} years\n")
            f.write(f"Monthly Income: ${user_data['monthly_income']}\n")
            f.write(f"Current Savings: ${user_data['current_savings']}\n")
            f.write(f"Monthly Expenses: ${user_data['monthly_expenses']}\n")
            f.write(f"Risk Tolerance: {user_data['risk_tolerance'].title()}\n\n")
            
            for i, advice in enumerate(advice_list, 1):
                f.write(f"ADVICE #{i}: {advice['recommendation']}\n")
                f.write("-" * 30 + "\n")
                f.write(f"Explanation: {advice['explanation']}\n")
                f.write(f"Growth Projection: {advice['growth_projection']}\n")
                f.write(f"Risks & Considerations: {advice['risks']}\n\n")
        
        print(f"✅ Advice saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Error saving file: {e}")


if __name__ == "__main__":
    main()
