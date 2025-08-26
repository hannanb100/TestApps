import os
import openai
import logging
from typing import Dict, List, Tuple
from dotenv import load_dotenv

# Set up logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('finance_advisor.log'),
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class FinanceAdvisor:
    """Handles LLM interactions to generate personalized financial advice."""
    
    def __init__(self):
        """Initialize the FinanceAdvisor with OpenAI API configuration."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        logger.info(f"API Key loaded: {bool(self.api_key)}")
        self.model = os.getenv("DEFAULT_MODEL", "gpt-4")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1000"))
        
        if not self.api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    def generate_financial_advice(self, user_data: Dict[str, str]) -> List[Dict[str, str]]:
        """
        Generate personalized financial advice using OpenAI API.
        
        Args:
            user_data: Dictionary containing user's financial information
            
        Returns:
            List of dictionaries containing advice with explanation and growth projection
        """
        
        # Construct the prompt for the LLM
        prompt = self._build_prompt(user_data)
        
        try:
            logger.info("Starting OpenAI API call...")
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            logger.info(f"OpenAI client created, model: {self.model}")
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a professional financial advisor with expertise in personal finance, 
                        investment strategies, and retirement planning. Provide clear, actionable advice based on the user's financial situation and goals.
                        


                        """
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=self.max_tokens
            )
            
            logger.info("OpenAI API call successful")
            # Parse the response and structure it
            advice_text = response.choices[0].message.content
            return self._parse_advice_response(advice_text, user_data)
            
        except Exception as e:
            logger.error(f"Error generating financial advice: {e}", exc_info=True)
            return self._get_fallback_advice(user_data)
    
    def _build_prompt(self, user_data: Dict[str, str]) -> str:
        """Build a comprehensive prompt for the LLM based on user data."""
        
        # Calculate some basic financial metrics for the prompt
        monthly_income = int(user_data.get('monthly_income', 0))
        monthly_expenses = int(user_data.get('monthly_expenses', 0))
        current_savings = int(user_data.get('current_savings', 0))
        timeframe = int(user_data.get('timeframe', 10))
        monthly_savings = max(0, monthly_income - monthly_expenses)
        annual_savings = monthly_savings * 12
        
        prompt = f"""
        As a financial advisor, please provide exactly 3 specific pieces of financial advice for the following situation:

        Financial Goal: {user_data.get('financial_goal', 'Not specified')}
        Timeframe: {timeframe} years
        Current Income: ${monthly_income:,} per month
        Current Savings: ${current_savings:,}
        Monthly Expenses: ${monthly_expenses:,}
        Monthly Savings: ${monthly_savings:,}
        Annual Savings: ${annual_savings:,}
        Risk Tolerance: {user_data.get('risk_tolerance', 'Not specified')}

        For each piece of advice, provide SPECIFIC, ACTIONABLE recommendations with exact dollar amounts:

        1. A clear, actionable recommendation title (one line)
        2. A specific explanation of why this advice fits their situation (2-3 sentences, mention their specific goal, income, savings, or risk tolerance)
        3. SPECIFIC growth projections with exact dollar amounts and percentages (2-3 sentences, e.g., "Invest $X monthly in index funds, could grow to $Y in {timeframe} years with 7-9% annual returns" or "Allocate $X to emergency fund, then invest $Y monthly for growth")
        4. Specific risks related to this particular strategy (2-3 sentences, e.g., "Market volatility could reduce returns by 20-30% in bad years" or "Inflation may reduce purchasing power by 2-3% annually")

        CRITICAL REQUIREMENTS:
        - Include SPECIFIC DOLLAR AMOUNTS for monthly contributions, target amounts, and expected growth
        - Use their actual monthly savings (${monthly_savings:,}) to calculate realistic investment amounts
        - Provide concrete numbers like "Invest $X monthly" or "Allocate $Y to this strategy"
        - Show expected growth to specific dollar amounts over their {timeframe}-year timeframe
        - Each piece of advice must have THREE DISTINCT sections with specific numbers

        Format your response exactly like this:
        1. [Catchy Title Here]
        [Complete explanation paragraph - 2-3 sentences with specific dollar amounts]
        [Complete growth projection paragraph - 2-3 sentences with exact dollar amounts and percentages]
        [Complete risks paragraph - 2-3 sentences about potential downsides]

        2. [Catchy Title Here]
        [Complete explanation paragraph - 2-3 sentences with specific dollar amounts]
        [Complete growth projection paragraph - 2-3 sentences with exact dollar amounts and percentages]
        [Complete risks paragraph - 2-3 sentences about potential downsides]

        3. [Catchy Title Here]
        [Complete explanation paragraph - 2-3 sentences with specific dollar amounts]
        [Complete growth projection paragraph - 2-3 sentences with exact dollar amounts and percentages]
        [Complete risks paragraph - 2-3 sentences about potential downsides]

        Be SPECIFIC and ACTIONABLE. Include actual dollar amounts, percentages, and timeframes.
        Use their monthly savings of ${monthly_savings:,} to calculate realistic investment amounts.
        Show how much they could have in {timeframe} years with specific numbers.
        Ensure each section is complete, well-structured, and DISTINCT from the others.
        """
        
        return prompt
    
    def _parse_advice_response(self, advice_text: str, user_data: Dict[str, str]) -> List[Dict[str, str]]:
        """Parse the LLM response into structured advice format."""
        
        try:
            # Split the response into sections and look for structured advice
            sections = self._extract_advice_sections(advice_text)
            
            if sections:
                return sections[:3]  # Limit to 3 pieces of advice
            else:
                # Fallback: try to extract individual pieces of advice
                return self._extract_individual_advice(advice_text, user_data)
                
        except Exception as e:
            # Final fallback
            return [{
                "recommendation": "AI Financial Guidance",
                "explanation": advice_text[:200] + "..." if len(advice_text) > 200 else advice_text,
                "growth_projection": f"Personalized analysis for your {user_data.get('timeframe', 'timeframe')} year goal.",
                "risks": "This is AI-generated advice. Consider consulting with a licensed financial advisor."
            }]
    
    def _extract_advice_sections(self, advice_text: str) -> List[Dict[str, str]]:
        """Extract structured advice sections from the LLM response."""
        advice_list = []
        
        # Look for numbered sections (1., 2., 3., etc.)
        import re
        
        # Multiple patterns to try for better title extraction
        patterns = [
            # Pattern 1: Standard numbered format (1. Title: Content)
            r'(\d+\.\s*)([^:\n]+)(?:[:]?\s*)(.*?)(?=\d+\.|$)',
            # Pattern 2: Title on separate line after number
            r'(\d+\.\s*)([^:\n]+)\n(.*?)(?=\d+\.|$)',
            # Pattern 3: Title with dash or bullet
            r'(\d+\.\s*)([^:\-\n]+)(?:[\-\s]*)(.*?)(?=\d+\.|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, advice_text, re.DOTALL | re.IGNORECASE)
            if matches:
                for match in matches:
                    number, title, content = match
                    title = title.strip()
                    content = content.strip()
                    
                    # Format the title properly
                    formatted_title = self._format_title(title)
                    
                    if formatted_title and len(content) > 30:
                        # Parse the content for explanation, growth, and risks
                        explanation, growth, risks = self._parse_advice_content(content)
                        
                        advice_list.append({
                            "recommendation": formatted_title,
                            "explanation": explanation,
                            "growth_projection": growth,
                            "risks": risks
                        })
                
                # If we found advice with this pattern, break
                if advice_list:
                    break
        
        return advice_list
    
    def _extract_individual_advice(self, advice_text: str, user_data: Dict[str, str]) -> List[Dict[str, str]]:
        """Extract individual pieces of advice when structured format isn't available."""
        advice_list = []
        
        # Try to find numbered sections first (1., 2., 3.)
        import re
        numbered_pattern = r'(\d+\.\s*)([^:\n]+)(?:[:]?\s*)(.*?)(?=\d+\.|$)'
        numbered_matches = re.findall(numbered_pattern, advice_text, re.DOTALL | re.IGNORECASE)
        
        if numbered_matches:
            for match in numbered_matches:
                number, title, content = match
                title = title.strip()
                content = content.strip()
                
                # Format the title properly
                formatted_title = self._format_title(title)
                
                if formatted_title and len(content) > 30:
                    explanation, growth, risks = self._parse_advice_content(content)
                    
                    advice_list.append({
                        "recommendation": formatted_title,
                        "explanation": explanation,
                        "growth_projection": growth,
                        "risks": risks
                    })
        
        # If no numbered sections found, try other patterns
        if not advice_list:
            # Look for sections with common headers
            header_patterns = [
                r'(?:Recommendation|Advice|Strategy|Plan)\s*[:\-]?\s*([^:\n]+)',
                r'([A-Z][^:\n]{10,50})[:\-]?\s*',
                r'([^:\n]{15,60})[:\-]?\s*'
            ]
            
            for pattern in header_patterns:
                matches = re.findall(pattern, advice_text, re.DOTALL | re.IGNORECASE)
                if matches:
                    for match in matches[:3]:  # Limit to 3
                        title = match.strip()
                        if len(title) > 10 and len(title) < 80:
                            # Format the title properly
                            formatted_title = self._format_title(title)
                            
                            if formatted_title:
                                # Extract content after this title
                                content_start = advice_text.find(match) + len(match)
                                content = advice_text[content_start:content_start + 300].strip()
                                
                                if len(content) > 50:
                                    explanation, growth, risks = self._parse_advice_content(content)
                                    
                                    advice_list.append({
                                        "recommendation": formatted_title,
                                        "explanation": explanation,
                                        "growth_projection": growth,
                                        "risks": risks
                                    })
                                    break
            
            # If still no advice found, create generic but contextual advice
            if not advice_list:
                advice_list = self._create_contextual_advice(user_data)
        
        return advice_list[:3]
    
    def _format_title(self, title: str) -> str:
        """Format a title to be clean, capitalized, and professional."""
        import re
        
        # Clean up the title - remove extra whitespace, newlines, and common prefixes
        title = re.sub(r'\s+', ' ', title).strip()
        title = re.sub(r'^(recommendation|advice|strategy|plan)\s*', '', title, flags=re.IGNORECASE).strip()
        
        # Remove quotes if present
        title = re.sub(r'^["\']|["\']$', '', title).strip()
        
        # Ensure title is capitalized and meaningful
        if title and len(title) > 5 and len(title) < 100:
            # Capitalize first letter of each word for better presentation
            title = ' '.join(word.capitalize() for word in title.split())
            return title
        
        return title
    
    def _create_contextual_advice(self, user_data: Dict[str, str]) -> List[Dict[str, str]]:
        """Create contextual advice when LLM parsing fails completely."""
        timeframe = int(user_data.get('timeframe', 5))
        risk_tolerance = user_data.get('risk_tolerance', 'Balanced')
        
        return [
            {
                "recommendation": "Build Your Emergency Fund First",
                "explanation": f"Before investing, ensure you have 3-6 months of expenses saved. With your current monthly expenses, aim for a ${int(user_data.get('monthly_expenses', 0)) * 6} emergency fund to protect against unexpected setbacks.",
                "growth_projection": f"High-yield savings accounts can earn 4-5% annually, helping your emergency fund keep pace with inflation while remaining accessible.",
                "risks": "Low risk, but inflation may reduce purchasing power over time. Consider reviewing and adjusting your emergency fund amount annually."
            },
            {
                "recommendation": f"Start with {risk_tolerance} Investment Strategy",
                "explanation": f"Based on your {risk_tolerance} risk tolerance, focus on a diversified portfolio that balances growth potential with risk management.",
                "growth_projection": f"Historical data suggests {risk_tolerance.lower()} portfolios typically return 6-10% annually over {timeframe} years, though past performance doesn't guarantee future results.",
                "risks": "Market volatility can cause temporary losses. Your {timeframe}-year timeframe helps ride out market cycles, but be prepared for ups and downs."
            },
            {
                "recommendation": "Maximize Tax-Advantaged Accounts",
                "explanation": f"Take advantage of retirement accounts like 401(k)s and IRAs to reduce your tax burden while building long-term wealth.",
                "growth_projection": f"Contributing regularly over {timeframe} years can significantly impact your retirement savings through compound growth and tax benefits.",
                "risks": "Early withdrawal penalties apply before age 59½. Ensure you have adequate emergency savings before prioritizing retirement contributions."
            }
        ]
    
    def _parse_advice_content(self, content: str) -> tuple:
        """Parse advice content into explanation, growth projection, and risks."""
        content = content.strip()
        
        # Split content into sentences for better parsing
        import re
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        explanation = ""
        growth = ""
        risks = ""
        
        # Strategy: Divide content into three equal parts and assign intelligently
        total_length = len(content)
        section_length = total_length // 3
        
        if len(sentences) >= 3:
            # We have enough sentences to work with
            explanation = sentences[0]
            
            # Find a good growth sentence (look for numbers, percentages, timeframes)
            for sentence in sentences[1:]:
                if re.search(r'\d+%|\d+ percent|\$\d+|\d+ years?|growth|return|potential|could|expect', sentence, re.IGNORECASE):
                    growth = sentence
                    break
            
            # Find a good risk sentence (look for risk-related keywords)
            for sentence in sentences[1:]:
                if re.search(r'risk|volatility|market|downside|consider|however|although|while|though|but', sentence, re.IGNORECASE):
                    if sentence != growth:  # Don't duplicate
                        risks = sentence
                        break
        
        # If we don't have enough sentences or couldn't find good matches, create structured content
        if not explanation:
            explanation = sentences[0] if sentences else "This financial strategy is designed to help you achieve your goals based on your current situation and risk tolerance."
        
        if not growth:
            # Look for any sentence with numbers, percentages, or timeframes
            for sentence in sentences:
                if re.search(r'\d+%|\d+ percent|\$\d+|\d+ years?|growth|return|potential', sentence, re.IGNORECASE):
                    if sentence != explanation:
                        growth = sentence
                        break
            
            if not growth:
                # Create a contextual growth statement
                growth = "This strategy could provide steady growth over time, though actual returns depend on market conditions and your specific implementation."
        
        if not risks:
            # Look for any sentence that mentions potential downsides or considerations
            for sentence in sentences:
                if re.search(r'risk|volatility|market|downside|consider|however|although|while|though|but', sentence, re.IGNORECASE):
                    if sentence != explanation and sentence != growth:
                        risks = sentence
                        break
            
            if not risks:
                # Create a contextual risk statement
                risks = "Consider market volatility and ensure this strategy aligns with your overall financial plan and risk tolerance."
        
        # Ensure all content ends properly
        if explanation and not explanation.endswith(('.', '!', '?')):
            explanation += '.'
        if growth and not growth.endswith(('.', '!', '?')):
            growth += '.'
        if risks and not risks.endswith(('.', '!', '?')):
            risks += '.'
        
        # Final validation: ensure we have distinct content
        if explanation == growth:
            explanation = "This financial strategy is designed to help you achieve your goals based on your current situation and risk tolerance."
        if explanation == risks:
            explanation = "This approach aligns with your financial goals and current circumstances."
        if growth == risks:
            risks = "Consider market volatility and ensure this strategy aligns with your overall financial plan."
        
        return explanation, growth, risks
    
    def _get_fallback_advice(self, user_data: Dict[str, str]) -> List[Dict[str, str]]:
        """Provide fallback advice if LLM fails."""
        
        timeframe = int(user_data.get('timeframe', 10))
        risk_tolerance = user_data.get('risk_tolerance', 'medium')
        monthly_income = int(user_data.get('monthly_income', 0))
        monthly_expenses = int(user_data.get('monthly_expenses', 0))
        current_savings = int(user_data.get('current_savings', 0))
        monthly_savings = max(0, monthly_income - monthly_expenses)
        annual_savings = monthly_savings * 12
        
        # Calculate specific amounts for each strategy
        emergency_fund_target = monthly_expenses * 6
        emergency_fund_monthly = max(100, min(monthly_savings * 0.3, emergency_fund_target / 12))
        
        investment_monthly = max(100, monthly_savings * 0.5)
        investment_growth = investment_monthly * 12 * timeframe * (1.07 ** timeframe)
        
        retirement_monthly = max(100, monthly_savings * 0.2)
        retirement_growth = retirement_monthly * 12 * timeframe * (1.08 ** timeframe)
        
        fallback_advice = [
            {
                "recommendation": "Build an Emergency Fund",
                "explanation": f"With your current monthly expenses of ${monthly_expenses:,}, you need to build a 6-month emergency fund of ${emergency_fund_target:,} to protect against unexpected financial setbacks. This provides a safety net for job loss, medical emergencies, or major repairs.",
                "growth_projection": f"Allocate ${emergency_fund_monthly:,} monthly to high-yield savings accounts. You could build your ${emergency_fund_target:,} emergency fund within {max(1, int(emergency_fund_target / (emergency_fund_monthly * 12)))} years, then redirect those funds to investments.",
                "risks": "Low risk, but inflation may reduce purchasing power by 2-3% annually. Ensure your emergency fund keeps pace with rising costs by reviewing and adjusting the target amount yearly."
            },
            {
                "recommendation": "Diversified Investment Portfolio",
                "explanation": f"Your {risk_tolerance} risk tolerance suggests a balanced approach: {self._get_portfolio_mix(risk_tolerance)}. With your monthly savings of ${monthly_savings:,}, you can afford to take calculated risks for better long-term growth.",
                "growth_projection": f"Invest ${investment_monthly:,} monthly in a diversified portfolio. Historical returns suggest potential growth of {self._get_expected_returns(risk_tolerance)} annually, which could grow your investments to approximately ${int(investment_growth):,} in {timeframe} years.",
                "risks": f"{self._get_risk_description(risk_tolerance)} Consider dollar-cost averaging to reduce timing risk and emotional decision-making. Market downturns could temporarily reduce your portfolio value by 15-30%."
            },
            {
                "recommendation": "Retirement Planning",
                "explanation": f"With your {timeframe}-year timeframe and monthly savings of ${monthly_savings:,}, maximizing retirement contributions now can leverage compound growth effectively. Tax-advantaged accounts like 401(k)s and IRAs provide significant long-term benefits.",
                "growth_projection": f"Contribute ${retirement_monthly:,} monthly to retirement accounts. With compound interest at 8% annually, your retirement savings could grow to approximately ${int(retirement_growth):,} in {timeframe} years, giving you a solid foundation for your future.",
                "risks": "Early withdrawal penalties (10% + taxes) and dependency on market performance. Ensure you have adequate emergency savings before prioritizing retirement contributions. Consider diversifying across different retirement vehicles."
            }
        ]
        
        return fallback_advice
    
    def _get_portfolio_mix(self, risk_tolerance: str) -> str:
        """Get portfolio mix based on risk tolerance."""
        if risk_tolerance.lower() == 'low':
            return "60% bonds, 30% stocks, 10% cash"
        elif risk_tolerance.lower() == 'medium':
            return "50% stocks, 40% bonds, 10% alternatives"
        else:  # high
            return "70% stocks, 20% bonds, 10% alternatives"
    
    def _get_expected_returns(self, risk_tolerance: str) -> str:
        """Get expected returns based on risk tolerance."""
        if risk_tolerance.lower() == 'low':
            return "4-6%"
        elif risk_tolerance.lower() == 'medium':
            return "6-8%"
        else:  # high
            return "8-10%"
    
    def _get_risk_description(self, risk_tolerance: str) -> str:
        """Get risk description based on risk tolerance."""
        if risk_tolerance.lower() == 'low':
            return "Lower returns but more stable, with potential 10-15% losses in bad years."
        elif risk_tolerance.lower() == 'medium':
            return "Balanced risk-reward, with potential 20-25% losses during market downturns."
        else:  # high
            return "Higher potential returns but increased volatility, with potential 30-40% losses in bad years."
