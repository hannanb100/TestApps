import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Define the state structure
class AgentState:
    def __init__(self, messages: list = None):
        self.messages = messages or []
    
    def add_message(self, message):
        self.messages.append(message)
    
    def get_last_message(self):
        return self.messages[-1] if self.messages else None

# Define the agent function
def agent_function(state: Dict[str, Any]) -> Dict[str, Any]:
    """Process the user message and generate a response"""
    messages = state["messages"]
    
    # Get the last user message
    last_message = messages[-1]
    
    # Generate response using the LLM
    response = llm.invoke([last_message])
    
    # Add the AI response to the conversation
    messages.append(response)
    
    return {"messages": messages}

# Create the LangGraph workflow
def create_agent_workflow():
    """Create and return the agent workflow"""
    workflow = StateGraph(AgentState)
    
    # Add the agent node
    workflow.add_node("agent", agent_function)
    
    # Set the entry point
    workflow.set_entry_point("agent")
    
    # Set the end point
    workflow.add_edge("agent", END)
    
    return workflow.compile()

# Initialize the workflow
agent_workflow = create_agent_workflow()

def chat_with_agent(user_message: str, conversation_history: list = None) -> str:
    """Chat with the agent and return the response"""
    if conversation_history is None:
        conversation_history = []
    
    # Create the initial state
    state = {"messages": conversation_history + [HumanMessage(content=user_message)]}
    
    # Run the workflow
    result = agent_workflow.invoke(state)
    
    # Get the last AI message
    last_ai_message = result["messages"][-1]
    
    return last_ai_message.content

if __name__ == "__main__":
    # Test the agent
    response = chat_with_agent("Hello! How are you today?")
    print(f"Agent: {response}")
