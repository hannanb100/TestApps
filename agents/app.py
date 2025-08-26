from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from agent import chat_with_agent
import json

app = FastAPI(title="Agentic Chatbot", description="A LangGraph-powered chatbot agent")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# In-memory storage for conversation history (in production, use a database)
conversation_history = []

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(message: str = Form(...)):
    """Handle chat messages and return agent response"""
    global conversation_history
    
    # Get response from agent
    response = chat_with_agent(message, conversation_history)
    
    # Update conversation history
    conversation_history.append({"role": "user", "content": message})
    conversation_history.append({"role": "assistant", "content": response})
    
    # Keep only last 20 messages to prevent memory issues
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]
    
    return {"response": response, "history": conversation_history}

@app.get("/history")
async def get_history():
    """Get conversation history"""
    return {"history": conversation_history}

@app.post("/clear")
async def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return {"message": "History cleared"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
