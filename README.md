# APPS - Python Applications Monorepo

A collection of Python applications sharing a common virtual environment and dependencies.

## 🏗️ **Project Structure**

```
APPS/
├── venv/                    # Shared virtual environment
├── requirements.txt         # Consolidated dependencies
├── financeapp/             # Financial advisor application
└── agents/                 # LangGraph-powered chatbot agent
```

## 🚀 **Quick Start**

### 1. **Clone the Repository**
```bash
git clone <your-repo-url>
cd APPS
```

### 2. **Set Up Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

## 📱 **Applications**

### **Finance App** (`/financeapp`)
- **Description**: Financial advisor application with AI-powered insights
- **Framework**: Flask
- **Run**: `cd financeapp && python app.py`
- **Port**: 8000

### **Agents** (`/agents`)
- **Description**: LangGraph-powered chatbot agent with web interface
- **Framework**: FastAPI + LangGraph
- **Run**: `cd agents && python run.py`
- **Port**: 8000 (different from finance app)

## 🔧 **Environment Setup**

### **Required Environment Variables**
Create a `.env` file in the root directory:

```bash
# OpenAI API Key (required for both apps)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Customize ports
FINANCE_APP_PORT=8000
AGENTS_PORT=8001
```

## 📦 **Dependencies**

The `requirements.txt` file contains consolidated dependencies for both applications:

- **Web Frameworks**: Flask, FastAPI, Uvicorn
- **AI/ML**: LangGraph, LangChain, OpenAI
- **Utilities**: python-dotenv, requests, jinja2

## 🏃‍♂️ **Running Applications**

### **Option 1: Run Individually**
```bash
# Terminal 1 - Finance App
cd financeapp
python app.py

# Terminal 2 - Agents
cd agents
python run.py
```

### **Option 2: Use Startup Scripts**
```bash
# Finance App
cd financeapp
python main.py

# Agents
cd agents
python run.py
```

## 🧪 **Development**

### **Adding New Dependencies**
1. Install in your active virtual environment: `pip install package_name`
2. Update requirements.txt: `pip freeze > requirements.txt`
3. Commit both changes

### **Adding New Applications**
1. Create new folder in root
2. Add dependencies to main `requirements.txt`
3. Update this README

## 📚 **Documentation**

- **Finance App**: See `/financeapp/README.md`
- **Agents**: See `/agents/README.md`

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both applications
5. Submit a pull request

## 📄 **License**

This project is open source and available under the MIT License.
