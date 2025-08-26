# 🤖 Financial Advisor Assistant

A modern, web-based financial advisor application that provides personalized financial advice using AI analysis. The application features a clean, minimal UI with interactive charts and comprehensive financial planning tools.

## ✨ Features

- **🎨 Modern UI/UX**: Clean, responsive design with Bootstrap-like styling
- **🤖 AI-Powered Financial Advice**: Uses OpenAI's GPT models for personalized recommendations
- **📊 Interactive Charts**: Chart.js integration for visualizing financial growth projections
- **💻 Multiple Interfaces**: 
  - Web interface with modern UI (`app.py`)
  - Command-line interface (`main.py`)
  - Demo mode for testing (`demo.py`)
- **📱 Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **🖨️ Print-Friendly**: Optimized CSS for printing financial reports
- **📋 Copy to Clipboard**: Easy sharing of financial advice
- **⚡ Real-time Validation**: Client-side form validation with helpful error messages
- **📈 Growth Projections**: Multiple investment scenarios (Conservative, Moderate, Aggressive)

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- OpenAI API key (optional for demo mode)

### Installation

1. **Clone or download the project**
2. **Set up a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your environment** (optional):
   - Copy `.env.example` to `.env` (or create `.env` manually)
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     ```

## 🎯 Usage

### Demo Mode (No API Key Required)
Test the application with sample data:
```bash
python demo.py
```

### Web Interface
Run the Flask web application:
```bash
python app.py
```
Then open your browser to `http://localhost:8000`

### Command Line Interface
Run the command-line version:
```bash
python main.py
```

## 🎨 UI Features

### Modern Design
- **Clean Layout**: Card-based design with subtle shadows and rounded corners
- **Color Scheme**: Professional blue theme with consistent color variables
- **Typography**: Modern system fonts with excellent readability
- **Responsive Grid**: Adaptive layout that works on all screen sizes

### Interactive Elements
- **Form Validation**: Real-time validation with helpful error messages
- **Loading States**: Visual feedback during AI processing
- **Hover Effects**: Subtle animations and hover states
- **Toast Notifications**: Success messages for user actions

### Charts & Visualizations
- **Growth Projections**: Line charts showing investment growth over time
- **Multiple Scenarios**: Conservative (4%), Moderate (7%), Aggressive (10%) growth rates
- **Interactive Tooltips**: Hover over chart points for detailed information
- **Responsive Charts**: Automatically resize for different screen sizes

## 📊 Input Fields

The application collects comprehensive financial information:

- **Financial Goal**: What you want to achieve (e.g., buy a house, retire early)
- **Timeframe**: How many years to achieve the goal (1-100 years)
- **Current Savings**: Your existing savings/investments
- **Monthly Income**: Your regular monthly income
- **Monthly Expenses**: Your regular monthly expenses
- **Risk Tolerance**: Low, Medium, or High risk preference

## 🧠 AI Analysis

The application uses OpenAI's GPT models to:
- Analyze your financial situation holistically
- Consider your risk tolerance and timeframe
- Generate 3-4 specific, actionable recommendations
- Provide growth projections and risk assessments
- Offer personalized investment strategies

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
DEFAULT_MODEL=gpt-4
MAX_TOKENS=1000
TEMPERATURE=0.7

# Flask Settings
FLASK_SECRET_KEY=your_secret_key_here
FLASK_DEBUG=True
```

### API Key Setup

1. Get an OpenAI API key from [OpenAI's platform](https://platform.openai.com/)
2. Add it to your `.env` file
3. Ensure you have sufficient API credits

## 📁 Project Structure

```
FinanceApp/
├── app.py                 # Flask web application
├── main.py               # Command-line interface
├── demo.py               # Demo script for testing
├── finance_advisor.py    # AI integration module
├── requirements.txt      # Python dependencies
├── .env                  # Environment configuration
├── static/               # Static assets
│   ├── css/
│   │   └── style.css    # Modern CSS styling
│   ├── js/
│   │   └── app.js       # JavaScript functionality
│   └── images/          # Image assets
├── templates/            # HTML templates
│   ├── index.html       # Input form with modern UI
│   └── results.html     # Results with charts and advice
└── README.md            # This file
```

## 🛠️ Development

### Running Tests
```bash
# Install test dependencies
pip install pytest

# Run tests
pytest
```

### Code Style
The project follows PEP 8 style guidelines. Use a linter like `flake8` or `black` for consistent formatting.

### Adding New Features
- **CSS**: Add styles to `static/css/style.css`
- **JavaScript**: Add functionality to `static/js/app.js`
- **Templates**: Modify HTML files in `templates/`
- **Backend**: Update Python files as needed

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Keep your OpenAI API key secure
- The Flask app uses a development secret key by default - change this for production
- All user inputs are validated and sanitized

## 🚨 Disclaimer

This application provides educational financial advice and should not replace professional financial consultation. Always consult with licensed financial advisors for personalized guidance.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **Port 8000 already in use**: The app uses port 8000 by default
2. **OpenAI API errors**: Check your API key and ensure you have sufficient credits
3. **Import errors**: Make sure you're in the virtual environment and dependencies are installed
4. **Chart not displaying**: Ensure Chart.js is loaded and check browser console for errors

### Getting Help

If you encounter issues:
1. Check the error messages in the terminal
2. Verify your `.env` configuration
3. Ensure all dependencies are installed
4. Check that you're using the correct Python version
5. Try the demo mode first: `python demo.py`

## 🎉 What's New

### Version 2.0 Features
- ✨ Modern, responsive UI design
- 📊 Interactive Chart.js visualizations
- 🎨 Professional CSS styling with CSS variables
- 📱 Mobile-first responsive design
- 🖨️ Print-optimized layouts
- ⚡ Real-time form validation
- 📋 Copy to clipboard functionality
- 🎭 Loading states and animations
- 🚀 Demo mode for testing without API keys

---

**Happy Financial Planning! 💰📈**
