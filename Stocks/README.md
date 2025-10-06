# 📈 AI Stock Tracking Agent

An intelligent stock tracking system that monitors stock prices and sends SMS alerts with AI-powered analysis. Built with FastAPI, LangChain, and Twilio.

## 🚀 Features

- **📱 SMS Interface**: Interact with the system using natural language SMS commands
- **🤖 AI Analysis**: Get AI-powered insights on stock movements with news integration
- **⏰ Automated Monitoring**: Configurable price checks with automatic alert generation
- **📊 Multi-Site Data**: Real-time stock data from yfinance
- **🔔 Smart Alerts**: Receive alerts when stocks move beyond your threshold
- **🌐 REST API**: Full REST API for programmatic access
- **🐳 Docker Ready**: Containerized deployment with Docker

## 📋 SMS Commands

Send these commands to your configured Twilio phone number:

- `Add AAPL` - Add Apple stock to your watchlist
- `Remove TSLA` - Remove Tesla from your watchlist
- `List` - Show all tracked stocks
- `Status` - Check system status
- `Help` - Show available commands

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SMS (Twilio)  │───▶│   FastAPI App   │───▶│  Stock Service  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Chatbot Service │    │   yfinance API  │
                       │   (LangChain)   │    │                 │
                       └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Agent Service  │
                       │   (AI Analysis) │
                       └─────────────────┘
```

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **AI/ML**: LangChain + OpenAI GPT
- **SMS**: Twilio API
- **Stock Data**: yfinance
- **Scheduling**: APScheduler
- **Database**: SQLite (extensible to PostgreSQL)
- **Deployment**: Docker + Docker Compose

## 📦 Installation

### Prerequisites

- Python 3.11+
- Docker (optional)
- Twilio Account
- OpenAI API Key

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stocks
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker Deployment

1. **Build the image**
   ```bash
   docker build -t ai-stock-tracker .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name stock-tracker \
     -p 8000:8000 \
     --env-file .env \
     ai-stock-tracker
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# User Configuration
USER_PHONE_NUMBER=+0987654321

# Stock Tracking Settings
ALERT_THRESHOLD_PERCENT=5.0
CHECK_INTERVAL_MINUTES=60

# Database
DATABASE_URL=sqlite:///./stocks.db

# Application Settings
APP_NAME=AI Stock Tracker
DEBUG=false
LOG_LEVEL=INFO

# Optional: News API
NEWS_API_KEY=your_news_api_key_here
```

### Twilio Setup

1. **Create a Twilio Account**
   - Sign up at [twilio.com](https://www.twilio.com)
   - Get your Account SID and Auth Token

2. **Purchase a Phone Number**
   - Buy a phone number in the Twilio Console
   - Configure webhook URL: `https://your-domain.com/webhooks/twilio/sms`

3. **Configure Webhooks**
   - Set SMS webhook to: `https://your-domain.com/webhooks/twilio/sms`
   - Set status webhook to: `https://your-domain.com/webhooks/twilio/status`

## 🚀 Usage

### SMS Commands

Once configured, send SMS messages to your Twilio number:

```
Add AAPL
```
Response: `✅ AAPL added to your watchlist!`

```
List
```
Response: 
```
📋 Your tracked stocks:
• AAPL
• TSLA
• GOOGL
```

```
Remove TSLA
```
Response: `✅ TSLA removed from your watchlist!`

### API Endpoints

The system provides a comprehensive REST API:

- `GET /api/v1/stocks` - List tracked stocks
- `POST /api/v1/stocks/{symbol}` - Add stock
- `DELETE /api/v1/stocks/{symbol}` - Remove stock
- `GET /api/v1/stocks/{symbol}/quote` - Get current quote
- `GET /api/v1/alerts` - List alerts
- `GET /health` - System health check

### Webhook Endpoints

- `POST /webhooks/twilio/sms` - Receive SMS messages
- `POST /webhooks/twilio/status` - SMS status updates

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_stock_service.py
```

## 📊 Monitoring

### Health Checks

- `GET /health/` - Basic health check
- `GET /health/detailed` - Detailed service status
- `GET /health/readiness` - Kubernetes readiness probe
- `GET /health/liveness` - Kubernetes liveness probe

### Metrics

- `GET /health/metrics` - System metrics
- `GET /api/v1/scheduler/status` - Scheduler status
- `GET /api/v1/scheduler/tasks` - Scheduled tasks

## 🔧 Development

### Project Structure

```
stocks/
├── app/
│   ├── models/          # Pydantic models
│   ├── routes/          # FastAPI routes
│   ├── services/        # Business logic
│   └── main.py         # Application entry point
├── tests/              # Unit tests
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container configuration
└── README.md          # This file
```

### Adding New Features

1. **Models**: Add Pydantic models in `app/models/`
2. **Services**: Implement business logic in `app/services/`
3. **Routes**: Create API endpoints in `app/routes/`
4. **Tests**: Add unit tests in `tests/`

### Code Style

The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/

# Type check
mypy app/
```

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Use secure secret management
2. **Database**: Consider PostgreSQL for production
3. **Caching**: Add Redis for improved performance
4. **Monitoring**: Implement proper logging and monitoring
5. **Security**: Use HTTPS and secure webhook endpoints

### Scaling

- **Horizontal Scaling**: Use multiple FastAPI instances behind a load balancer
- **Database**: Use connection pooling and read replicas
- **Caching**: Implement Redis for stock price caching
- **Queue**: Use Celery for background task processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check this README and API docs at `/docs`
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions

## 🔮 Roadmap

- [ ] Web dashboard for stock management
- [ ] Email alerts in addition to SMS
- [ ] Portfolio performance tracking
- [ ] Advanced AI analysis with technical indicators
- [ ] Integration with more data sources
- [ ] Mobile app companion
- [ ] Social trading features

---

**Built with ❤️ using FastAPI, LangChain, and modern Python practices.**
# Deployment triggered Mon Oct  6 11:12:41 PDT 2025
