#!/usr/bin/env python3
"""
Demo script for Financial Advisor Assistant
This allows testing the application without an OpenAI API key
"""

import json

def demo_financial_advisor():
    """Demo the financial advisor with sample data."""
    
    print("=" * 60)
    print("🤖 FINANCIAL ADVISOR ASSISTANT - DEMO MODE")
    print("=" * 60)
    print()
    
    # Sample user data
    sample_data = {
        "financial_goal": "Save for a house down payment",
        "timeframe": "5",
        "current_savings": "15000",
        "monthly_income": "5000",
        "monthly_expenses": "3000",
        "risk_tolerance": "Medium"
    }
    
    print("📊 Sample Financial Profile:")
    print(f"• Financial Goal: {sample_data['financial_goal']}")
    print(f"• Timeframe: {sample_data['timeframe']} years")
    print(f"• Current Savings: ${sample_data['current_savings']}")
    print(f"• Monthly Income: ${sample_data['monthly_income']}")
    print(f"• Monthly Expenses: ${sample_data['monthly_expenses']}")
    print(f"• Risk Tolerance: {sample_data['risk_tolerance']}")
    print()
    
    print("🔄 Generating financial advice...")
    print("📋 Using built-in financial advice (no API key required)")
    print()
    
    # Generate fallback advice directly in demo
    advice_list = get_fallback_advice(sample_data)
    
    print("=" * 60)
    print("💡 FINANCIAL ADVICE")
    print("=" * 60)
    print()
    
    for i, advice in enumerate(advice_list, 1):
        print(f"📋 ADVICE #{i}: {advice['recommendation']}")
        print("-" * 40)
        print(f"💭 Explanation: {advice['explanation']}")
        print(f"📈 Growth Projection: {advice['growth_projection']}")
        print(f"⚠️  Risks & Considerations: {advice['risks']}")
        print()
    
    # Calculate growth projections
    print("📈 GROWTH PROJECTIONS")
    print("-" * 40)
    
    timeframe = int(sample_data['timeframe'])
    current_savings = float(sample_data['current_savings'])
    monthly_savings = float(sample_data['monthly_income']) - float(sample_data['monthly_expenses'])
    
    print(f"Monthly Savings: ${monthly_savings}")
    print(f"Current Savings: ${current_savings}")
    print()
    
    scenarios = {
        "Conservative (4% annual)": 0.04,
        "Moderate (7% annual)": 0.07,
        "Aggressive (10% annual)": 0.10
    }
    
    for scenario_name, rate in scenarios.items():
        final_value = calculate_compound_growth(current_savings, monthly_savings, rate, timeframe)
        print(f"{scenario_name}: ${final_value:,.0f}")
    
    print("\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("1. Set up your OpenAI API key in the .env file")
    print("2. Run the web app: python app.py")
    print("3. Run the CLI: python main.py")
    print("4. Open http://localhost:8000 in your browser")
    print("=" * 60)

def get_fallback_advice(user_data):
    """Provide fallback advice without requiring OpenAI."""
    
    timeframe = user_data.get('timeframe', 'specified')
    risk_tolerance = user_data.get('risk_tolerance', 'medium')
    
    fallback_advice = [
        {
            "recommendation": "Build an Emergency Fund",
            "explanation": "Start by saving 3-6 months of expenses in a high-yield savings account.",
            "growth_projection": f"With consistent monthly contributions, you could build a substantial emergency fund over {timeframe} years.",
            "risks": "Low risk, but inflation may reduce purchasing power over time."
        },
        {
            "recommendation": "Diversified Investment Portfolio",
            "explanation": f"Based on your {risk_tolerance} risk tolerance, consider a mix of stocks, bonds, and other assets.",
            "growth_projection": f"Historical market returns suggest potential growth of 6-8% annually over {timeframe} years.",
            "risks": "Market volatility and potential for loss of principal."
        },
        {
            "recommendation": "Retirement Planning",
            "explanation": "Maximize contributions to retirement accounts like 401(k) or IRA for tax advantages.",
            "growth_projection": f"Compound growth could significantly increase your retirement savings over {timeframe} years.",
            "risks": "Early withdrawal penalties and market dependency."
        },
        {
            "recommendation": "Debt Management",
            "explanation": "Prioritize paying off high-interest debt before aggressive investing.",
            "growth_projection": f"Eliminating debt can free up ${user_data.get('monthly_income', '0')} monthly for investment over {timeframe} years.",
            "risks": "Opportunity cost of not investing, but debt reduction provides guaranteed returns."
        }
    ]
    
    return fallback_advice

def calculate_compound_growth(initial, monthly_contribution, annual_rate, years):
    """Calculate compound growth over time."""
    monthly_rate = annual_rate / 12
    months = years * 12
    
    # Future value of initial investment
    future_value_initial = initial * (1 + monthly_rate) ** months
    
    # Future value of monthly contributions
    if monthly_rate > 0:
        future_value_contributions = monthly_contribution * ((1 + monthly_rate) ** months - 1) / monthly_rate
    else:
        future_value_contributions = monthly_contribution * months
    
    return future_value_initial + future_value_contributions

if __name__ == "__main__":
    demo_financial_advisor()
