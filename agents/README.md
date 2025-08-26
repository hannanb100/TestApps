# Agentic Chatbot

A modern, intelligent chatbot built with LangGraph and LangChain, featuring a beautiful web interface.

## Features

- 🤖 **LangGraph-powered Agent**: Built on the latest LangGraph framework for intelligent conversation flows
- 🌐 **Modern Web UI**: Beautiful, responsive chat interface with real-time messaging
- 💬 **Conversation Memory**: Maintains chat history and context
- 📱 **Mobile Responsive**: Works seamlessly on all devices
- 🎨 **Beautiful Design**: Modern gradient design with smooth animations
- 📤 **Export Functionality**: Export your chat conversations
- 🧹 **Chat Management**: Clear chat history and manage conversations

## Tech Stack

- **Backend**: FastAPI (Python)
- **AI Framework**: LangGraph + LangChain
- **LLM**: OpenAI GPT-3.5-turbo (configurable)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Styling**: Modern CSS with gradients and animations

## Setup Instructions

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the `agents` directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the Application

```bash
python3 app.py
```

The application will be available at `http://localhost:8000`

## Project Structure

```
agents/
├── app.py              # FastAPI web application
├── agent.py            # LangGraph agent implementation
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── templates/         # HTML templates
│   └── index.html    # Main chat interface
└── static/           # Static assets
    ├── css/
    │   └── style.css # Styling
    └── js/
        └── app.js    # Frontend JavaScript
```

## Usage

1. Open your browser and navigate to `http://localhost:8000`
2. Start chatting with your AI agent!
3. Use the control buttons to:
   - Clear chat history
   - Export conversations

## Customization

### Changing the LLM Model

Edit `agent.py` and modify the `ChatOpenAI` configuration:

```python
llm = ChatOpenAI(
    model="gpt-4",  # Change to your preferred model
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### Adding Tools

The current implementation is a basic conversational agent. To add tools:

1. Import your tool functions in `agent.py`
2. Modify the `agent_function` to use tools based on user input
3. Update the LangGraph workflow to include tool nodes

## Development

### Adding New Features

- **Tools Integration**: Extend the agent with specific capabilities
- **Memory Persistence**: Add database storage for chat history
- **User Authentication**: Implement user accounts and chat isolation
- **Multi-modal Support**: Add image, file, or voice input capabilities

### Running in Development Mode

For development with auto-reload:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Main chat interface
- `POST /chat` - Send message and get response
- `GET /history` - Get conversation history
- `POST /clear` - Clear conversation history

## Contributing

Feel free to contribute to this project by:
- Adding new features
- Improving the UI/UX
- Optimizing the agent logic
- Adding new tools and capabilities

## License

This project is open source and available under the MIT License.
