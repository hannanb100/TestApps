"""
AI agent service for analyzing stock movements and generating insights.

This service uses LangChain with OpenAI to analyze stock price changes,
fetch relevant news, and generate user-friendly summaries.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import aiohttp
import json
import yfinance as yf

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

from ..models.stock import StockAlert, StockAnalysis, StockNews
from ..models.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class NewsService:
    """
    Service for fetching stock-related news.
    
    This service provides methods for retrieving news articles
    that might explain stock price movements.
    """
    
    def __init__(self):
        """Initialize the news service."""
        self.session = None
        self.news_api_key = settings.news_api_key
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_stock_news(self, symbol: str, days: int = 1) -> List[StockNews]:
        """
        Get recent news articles for a stock.
        
        Args:
            symbol: Stock symbol
            days: Number of days to look back
            
        Returns:
            List of StockNews objects
        """
        try:
            if not self.news_api_key:
                logger.warning("No News API key provided, using mock data")
                return self._get_mock_news(symbol)
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Build News API URL
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": f"{symbol} stock",
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
                "sortBy": "publishedAt",
                "language": "en",
                "apiKey": self.news_api_key,
                "pageSize": 10
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get("articles", [])
                    
                    news_list = []
                    for article in articles:
                        news = StockNews(
                            title=article.get("title", ""),
                            summary=article.get("description", ""),
                            url=article.get("url"),
                            published_at=self._parse_date(article.get("publishedAt")),
                            source=article.get("source", {}).get("name", ""),
                            relevance_score=self._calculate_relevance(article, symbol)
                        )
                        news_list.append(news)
                    
                    # Sort by relevance
                    news_list.sort(key=lambda x: x.relevance_score or 0, reverse=True)
                    
                    logger.info(f"Retrieved {len(news_list)} news articles for {symbol}")
                    return news_list[:5]  # Return top 5
                else:
                    logger.error(f"News API error: {response.status}")
                    return self._get_mock_news(symbol)
                    
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {str(e)}")
            return self._get_mock_news(symbol)
    
    def _get_mock_news(self, symbol: str) -> List[StockNews]:
        """Generate mock news data for testing."""
        return [
            StockNews(
                title=f"{symbol} Shows Strong Performance in Recent Trading",
                summary=f"Recent market activity shows {symbol} experiencing significant movement with strong investor interest.",
                url=f"https://example.com/news/{symbol.lower()}",
                published_at=datetime.now() - timedelta(hours=2),
                source="Market News",
                relevance_score=0.8
            ),
            StockNews(
                title=f"Analysts Update {symbol} Price Target",
                summary=f"Financial analysts have updated their price targets for {symbol} based on recent market conditions.",
                url=f"https://example.com/analysis/{symbol.lower()}",
                published_at=datetime.now() - timedelta(hours=6),
                source="Financial Times",
                relevance_score=0.7
            )
        ]
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string from News API."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
    
    def _calculate_relevance(self, article: Dict[str, Any], symbol: str) -> float:
        """Calculate relevance score for a news article."""
        title = article.get("title", "").lower()
        description = article.get("description", "").lower()
        content = f"{title} {description}"
        
        # Simple relevance scoring
        score = 0.0
        if symbol.lower() in content:
            score += 0.5
        if any(word in content for word in ["stock", "price", "market", "trading"]):
            score += 0.3
        if any(word in content for word in ["earnings", "revenue", "profit"]):
            score += 0.2
        
        return min(score, 1.0)


class AgentService:
    """
    Service for AI-powered stock movement analysis.
    
    This service uses LangChain agents to analyze stock price changes,
    fetch relevant news, and generate comprehensive summaries.
    """
    
    def __init__(self):
        """Initialize the agent service."""
        try:
            # Initialize OpenAI LLM
            self.llm = ChatOpenAI(
                openai_api_key=settings.openai_api_key,
                temperature=0.3,  # Balanced creativity and consistency
                max_tokens=500,
                model_name="gpt-3.5-turbo"
            )
            
            # Initialize news service
            self.news_service = NewsService()
            
            # Create enhanced analysis prompt
            self.analysis_prompt = PromptTemplate(
                input_variables=["symbol", "price_change", "change_percent", "previous_close", 
                               "current_price", "volume", "news_summary", "market_context", 
                               "technical_analysis"],
                template="""
You are an expert financial analyst with 15+ years of experience. Analyze this stock movement with professional insight.

STOCK MOVEMENT:
- Symbol: {symbol}
- Price Change: {price_change} ({change_percent:+.2f}%)
- Previous Close: ${previous_close:.2f}
- Current Price: ${current_price:.2f}
- Volume: {volume:,} shares

RECENT NEWS & EVENTS:
{news_summary}

MARKET CONTEXT:
{market_context}

TECHNICAL ANALYSIS:
{technical_analysis}

ANALYSIS REQUIREMENTS:
1. **Root Cause Analysis**: What specific factors drove this movement?
2. **Market Context**: How does this compare to sector/overall market?
3. **Technical Perspective**: Any notable technical patterns or levels?
4. **Risk Assessment**: What are the key risks/opportunities?
5. **Forward Outlook**: What to watch for in coming days?

FORMAT:
- Lead with the most important insight
- Use bullet points for key factors
- Include specific data points when relevant
- Keep analysis concise but actionable (1-2 paragraphs max)
- End with a clear recommendation (HOLD/SELL/BUY with brief reasoning)
- Use short, punchy sentences
- Focus on the most critical insights only

TONE: Professional, data-driven, but accessible to retail investors. Be concise and direct.
                """.strip()
            )
            
            # Create LLM chain for analysis
            self.analysis_chain = LLMChain(
                llm=self.llm,
                prompt=self.analysis_prompt
            )
            
            logger.info("Agent service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent service: {str(e)}")
            raise
    
    async def analyze_stock_movement(self, symbol: str, previous_price: float, 
                                   current_price: float, volume: int = 0) -> StockAnalysis:
        """
        Analyze stock price movement and generate enhanced insights.
        
        Args:
            symbol: Stock symbol
            previous_price: Previous price
            current_price: Current price
            volume: Current volume (optional)
            
        Returns:
            StockAnalysis object with AI-generated insights
        """
        try:
            logger.info(f"Analyzing movement for {symbol}: ${previous_price} -> ${current_price}")
            
            # Calculate price change
            change = current_price - previous_price
            change_percent = (change / previous_price) * 100 if previous_price > 0 else 0
            
            # Fetch relevant news
            async with self.news_service as news_svc:
                news_articles = await news_svc.get_stock_news(symbol, days=1)
            
            # Create news summary
            news_summary = self._create_news_summary(news_articles)
            
            # Get market context
            market_context = await self._get_market_context(symbol)
            
            # Get technical analysis
            technical_analysis = await self._get_technical_analysis(
                symbol, current_price, previous_price, volume
            )
            
            # Generate enhanced AI analysis
            analysis_text = await self._generate_enhanced_analysis(
                symbol, change, change_percent, previous_price, current_price, 
                volume, news_summary, market_context, technical_analysis
            )
            
            # Extract key factors from data
            key_factors = self._extract_enhanced_key_factors(
                symbol, change_percent, volume, market_context, technical_analysis, news_articles
            )
            
            # Generate recommendation
            recommendation = self._generate_recommendation(change_percent, analysis_text)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(news_articles, change_percent)
            
            analysis = StockAnalysis(
                symbol=symbol,
                analysis=analysis_text,
                confidence_score=confidence,
                key_factors=key_factors,
                recommendation=recommendation,
                created_at=datetime.utcnow()
            )
            
            logger.info(f"Generated enhanced analysis for {symbol} with confidence {confidence:.2f}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing stock movement: {str(e)}")
            # Return fallback analysis
            return self._create_fallback_analysis(symbol, previous_price, current_price)
    
    async def _generate_enhanced_analysis(self, symbol: str, change: float, 
                                        change_percent: float, previous_close: float,
                                        current_price: float, volume: int,
                                        news_summary: str, market_context: str,
                                        technical_analysis: str) -> str:
        """
        Generate enhanced AI analysis using LangChain with market context and technical analysis.
        
        Args:
            symbol: Stock symbol
            change: Price change amount
            change_percent: Price change percentage
            previous_close: Previous close price
            current_price: Current price
            volume: Current volume
            news_summary: Summary of recent news
            market_context: Market sentiment and performance
            technical_analysis: Technical analysis data
            
        Returns:
            AI-generated analysis text
        """
        try:
            result = self.analysis_chain.run(
                symbol=symbol,
                price_change=f"${change:+.2f}",
                change_percent=change_percent,
                previous_close=previous_close,
                current_price=current_price,
                volume=volume,
                news_summary=news_summary,
                market_context=market_context,
                technical_analysis=technical_analysis
            )
            return result.strip()
        except Exception as e:
            logger.error(f"Error generating enhanced analysis: {str(e)}")
            return f"Analysis unavailable for {symbol}. Recent market activity and news may be influencing the price."

    async def _generate_analysis(self, symbol: str, change: float, 
                               change_percent: float, news_summary: str) -> str:
        """
        Generate AI analysis using LangChain.
        
        Args:
            symbol: Stock symbol
            change: Price change amount
            change_percent: Price change percentage
            news_summary: Summary of recent news
            
        Returns:
            AI-generated analysis text
        """
        try:
            result = self.analysis_chain.run(
                symbol=symbol,
                price_change=f"${change:+.2f}",
                change_percent=f"{change_percent:+.2f}%",
                news_summary=news_summary
            )
            return result.strip()
        except Exception as e:
            logger.error(f"Error generating analysis: {str(e)}")
            return f"{symbol} moved {change_percent:+.2f}%. Recent market activity and news may be influencing the price."
    
    def _create_news_summary(self, news_articles: List[StockNews]) -> str:
        """
        Create a summary of news articles.
        
        Args:
            news_articles: List of StockNews objects
            
        Returns:
            News summary string
        """
        if not news_articles:
            return "No recent news available."
        
        summary_parts = []
        for i, article in enumerate(news_articles[:3], 1):  # Top 3 articles
            summary_parts.append(f"{i}. {article.title}")
            if article.summary:
                summary_parts.append(f"   {article.summary[:100]}...")
        
        return "\n".join(summary_parts)
    
    def _extract_enhanced_key_factors(self, symbol: str, change_percent: float, volume: int,
                                    market_context: str, technical_analysis: str, 
                                    news_articles: List[StockNews]) -> List[str]:
        """
        Extract key factors from all available data sources.
        
        Args:
            symbol: Stock symbol
            change_percent: Price change percentage
            volume: Current volume
            market_context: Market context string
            technical_analysis: Technical analysis string
            news_articles: List of news articles
            
        Returns:
            List of key factors
        """
        factors = []
        
        # Price movement factor
        if abs(change_percent) > 5:
            factors.append(f"Major price move ({change_percent:+.1f}%)")
        elif abs(change_percent) > 2:
            factors.append(f"Significant move ({change_percent:+.1f}%)")
        else:
            factors.append(f"Price change ({change_percent:+.1f}%)")
        
        # Market context factors
        if "High volatility" in market_context:
            factors.append("High market volatility")
        elif "Low volatility" in market_context:
            factors.append("Low market volatility")
        
        if "S&P 500" in market_context:
            if "+" in market_context and change_percent < 0:
                factors.append("Underperforming vs market")
            elif "-" in market_context and change_percent > 0:
                factors.append("Outperforming vs market")
        
        # Technical factors
        if "High volume" in technical_analysis:
            factors.append("High trading volume")
        elif "Low volume" in technical_analysis:
            factors.append("Low trading volume")
        
        if "Near 30-day high" in technical_analysis:
            factors.append("Near recent highs")
        elif "Near 30-day low" in technical_analysis:
            factors.append("Near recent lows")
        
        # News factors
        if news_articles:
            relevant_news = [a for a in news_articles if a.relevance_score and a.relevance_score > 0.5]
            if relevant_news:
                factors.append(f"Recent news ({len(relevant_news)} articles)")
            else:
                factors.append("No significant news")
        else:
            factors.append("No recent news")
        
        return factors[:6]  # Limit to 6 factors

    def _extract_key_factors(self, news_articles: List[StockNews], 
                           change_percent: float) -> List[str]:
        """
        Extract key factors from news and price movement.
        
        Args:
            news_articles: List of news articles
            change_percent: Price change percentage
            
        Returns:
            List of key factors
        """
        factors = []
        
        # Add price movement factor
        if abs(change_percent) > 5:
            factors.append(f"Significant price movement ({change_percent:+.1f}%)")
        elif abs(change_percent) > 2:
            factors.append(f"Moderate price movement ({change_percent:+.1f}%)")
        
        # Extract factors from news
        for article in news_articles[:2]:  # Top 2 articles
            title_lower = article.title.lower()
            if any(word in title_lower for word in ["earnings", "revenue", "profit"]):
                factors.append("Earnings/Financial performance")
            elif any(word in title_lower for word in ["merger", "acquisition", "deal"]):
                factors.append("Corporate actions")
            elif any(word in title_lower for word in ["analyst", "upgrade", "downgrade"]):
                factors.append("Analyst recommendations")
            elif any(word in title_lower for word in ["market", "trading", "volume"]):
                factors.append("Market conditions")
        
        return factors[:3]  # Limit to 3 factors
    
    def _generate_recommendation(self, change_percent: float, analysis: str) -> str:
        """
        Generate a simple recommendation based on analysis.
        
        Args:
            change_percent: Price change percentage
            analysis: Analysis text
            
        Returns:
            Recommendation string
        """
        if change_percent > 5:
            return "Strong positive movement - monitor for continuation"
        elif change_percent > 2:
            return "Positive trend - consider monitoring"
        elif change_percent < -5:
            return "Significant decline - watch for recovery signals"
        elif change_percent < -2:
            return "Negative trend - monitor closely"
        else:
            return "Stable movement - continue monitoring"
    
    def _calculate_confidence(self, news_articles: List[StockNews], 
                            change_percent: float) -> float:
        """
        Calculate confidence score for the analysis.
        
        Args:
            news_articles: List of news articles
            change_percent: Price change percentage
            
        Returns:
            Confidence score between 0 and 1
        """
        confidence = 0.5  # Base confidence
        
        # Increase confidence with more news
        if len(news_articles) > 0:
            confidence += 0.2
        if len(news_articles) > 2:
            confidence += 0.1
        
        # Increase confidence with significant movement
        if abs(change_percent) > 5:
            confidence += 0.2
        elif abs(change_percent) > 2:
            confidence += 0.1
        
        # Increase confidence with high-relevance news
        if news_articles:
            avg_relevance = sum(article.relevance_score or 0 for article in news_articles) / len(news_articles)
            confidence += avg_relevance * 0.2
        
        return min(confidence, 1.0)
    
    async def _get_market_context(self, symbol: str) -> str:
        """
        Get market context including sentiment and sector performance.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Market context string
        """
        try:
            # Get VIX (fear index) for market sentiment
            vix = yf.Ticker("^VIX")
            vix_data = vix.history(period="1d")
            vix_value = vix_data['Close'].iloc[-1] if not vix_data.empty else 20
            
            # Determine market sentiment based on VIX
            if vix_value > 30:
                sentiment = "High volatility/Fear (VIX: {:.1f})".format(vix_value)
            elif vix_value > 20:
                sentiment = "Moderate volatility (VIX: {:.1f})".format(vix_value)
            else:
                sentiment = "Low volatility/Complacency (VIX: {:.1f})".format(vix_value)
            
            # Get S&P 500 performance for context
            sp500 = yf.Ticker("^GSPC")
            sp500_data = sp500.history(period="2d")
            if len(sp500_data) >= 2:
                sp500_change = ((sp500_data['Close'].iloc[-1] - sp500_data['Close'].iloc[-2]) / 
                               sp500_data['Close'].iloc[-2]) * 100
                market_performance = f"S&P 500: {sp500_change:+.2f}%"
            else:
                market_performance = "S&P 500: Data unavailable"
            
            return f"Market Sentiment: {sentiment}\nMarket Performance: {market_performance}"
            
        except Exception as e:
            logger.warning(f"Could not fetch market context: {e}")
            return "Market context unavailable"
    
    async def _get_technical_analysis(self, symbol: str, current_price: float, 
                                    previous_close: float, volume: int) -> str:
        """
        Get basic technical analysis using yfinance data.
        
        Args:
            symbol: Stock symbol
            current_price: Current stock price
            previous_close: Previous close price
            volume: Current volume
            
        Returns:
            Technical analysis string
        """
        try:
            # Get historical data for technical indicators
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(period="30d")
            
            if hist_data.empty:
                return "Technical data unavailable"
            
            # Calculate basic technical indicators
            current_volume = volume
            avg_volume = hist_data['Volume'].mean()
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Price levels
            high_30d = hist_data['High'].max()
            low_30d = hist_data['Low'].min()
            current_position = (current_price - low_30d) / (high_30d - low_30d) * 100 if high_30d != low_30d else 50
            
            # Volume analysis
            if volume_ratio > 2:
                volume_analysis = f"High volume ({volume_ratio:.1f}x average)"
            elif volume_ratio > 1.5:
                volume_analysis = f"Above average volume ({volume_ratio:.1f}x average)"
            elif volume_ratio < 0.5:
                volume_analysis = f"Low volume ({volume_ratio:.1f}x average)"
            else:
                volume_analysis = f"Normal volume ({volume_ratio:.1f}x average)"
            
            # Price position analysis
            if current_position > 80:
                price_position = f"Near 30-day high (${high_30d:.2f})"
            elif current_position < 20:
                price_position = f"Near 30-day low (${low_30d:.2f})"
            else:
                price_position = f"Mid-range (${low_30d:.2f} - ${high_30d:.2f})"
            
            return f"Volume: {volume_analysis}\nPrice Position: {price_position}\n30-day Range: ${low_30d:.2f} - ${high_30d:.2f}"
            
        except Exception as e:
            logger.warning(f"Could not perform technical analysis: {e}")
            return "Technical analysis unavailable"

    def _create_fallback_analysis(self, symbol: str, previous_price: float, 
                                current_price: float) -> StockAnalysis:
        """
        Create a fallback analysis when AI analysis fails.
        
        Args:
            symbol: Stock symbol
            previous_price: Previous price
            current_price: Current price
            
        Returns:
            Basic StockAnalysis object
        """
        change = current_price - previous_price
        change_percent = (change / previous_price) * 100 if previous_price > 0 else 0
        
        analysis_text = f"{symbol} price changed from ${previous_price:.2f} to ${current_price:.2f} ({change_percent:+.2f}%). This movement may be due to market conditions, company news, or investor sentiment."
        
        return StockAnalysis(
            symbol=symbol,
            analysis=analysis_text,
            confidence_score=0.3,
            key_factors=["Price movement", "Market conditions"],
            recommendation="Monitor for additional developments",
            created_at=datetime.utcnow()
        )
    
    async def generate_alert_message(self, alert: StockAlert, 
                                   analysis: StockAnalysis) -> str:
        """
        Generate a comprehensive alert message.
        
        Args:
            alert: StockAlert object
            analysis: StockAnalysis object
            
        Returns:
            Formatted alert message
        """
        try:
            # Determine emoji and direction
            if alert.change_percent > 0:
                emoji = "📈"
                direction = "up"
            else:
                emoji = "📉"
                direction = "down"
            
            # Build message
            message = f"{emoji} {alert.symbol} Alert\n\n"
            message += f"Price: ${alert.current_price:.2f} ({alert.change_percent:+.2f}%)\n"
            message += f"Previous: ${alert.previous_price:.2f}\n\n"
            message += f"Analysis: {analysis.analysis}\n"
            
            # Add key factors if available
            if analysis.key_factors:
                factors_text = ", ".join(analysis.key_factors)
                message += f"\nKey factors: {factors_text}"
            
            # Add recommendation
            if analysis.recommendation:
                message += f"\n\nRecommendation: {analysis.recommendation}"
            
            return message
            
        except Exception as e:
            logger.error(f"Error generating alert message: {str(e)}")
            return f"📊 {alert.symbol} Alert: Price changed {alert.change_percent:+.2f}% to ${alert.current_price:.2f}"
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get agent service status.
        
        Returns:
            Dictionary with service status information
        """
        return {
            "service": "Agent Service",
            "llm_provider": "OpenAI",
            "news_service": "Available" if settings.news_api_key else "Mock data only",
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }
