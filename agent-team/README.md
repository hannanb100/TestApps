# 🤖 Agent Team System - Final Working Version

## 🎯 What This System Does

This is a **hierarchical AI agent system** where multiple specialized AI agents work together under the supervision of a central coordinator. Think of it like a team of experts where each person has a specific job, and there's a manager overseeing everything.

### ✨ Key Features

- **Takes user requests** (like "research quantum computing")
- **Breaks them down** into research and writing tasks
- **Has specialized agents** for each task
- **Coordinates everything** through a supervisor
- **Manages token usage** to stay within limits
- **Produces comprehensive final reports**

## 🔄 How It Works

```
1. User submits a request
2. Supervisor analyzes and plans the approach
3. Research Team gathers information
4. Document Team creates content
5. Final Compiler puts everything together
6. User gets a complete report
```

## 🏗️ System Architecture

### 👑 Supervisor Agent
- **Role**: Central coordinator and workflow manager
- **Responsibilities**: 
  - Analyzes user requests
  - Creates execution plans
  - Coordinates between teams
  - Ensures quality control

### 🔍 Research Team
- **Role**: Information gathering specialists
- **Tools**: Internet search (Tavily), content compression
- **Output**: Research summaries and data points

### 📝 Document Team
- **Role**: Content creation specialists
- **Tools**: AI writing, note-taking, chart generation
- **Output**: Written content, organized notes, visual specifications

### 📋 Final Compiler
- **Role**: Report synthesis and final output
- **Tools**: AI compilation, content integration
- **Output**: Comprehensive final reports

## 🚀 Getting Started

### Prerequisites

1. **Python 3.8+** installed
2. **Virtual environment** activated
3. **API keys** configured:
   - OpenAI API key (for GPT-4)
   - Tavily API key (for web search)

### Installation

1. **Navigate to the project directory**:
   ```bash
   cd agent-team
   ```

2. **Install dependencies** (from the parent APPS directory):
   ```bash
   cd ..
   pip install -r requirements.txt
   cd agent-team
   ```

3. **Set up environment variables**:
   Create a `.env` file in the `APPS` directory with:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

### Running the System

#### Option 1: Web Interface (Recommended)
```bash
python web_interface_clean.py
```
Then open your browser to: `http://localhost:8002`

#### Option 2: Command Line
```bash
python agent_system_final.py
```

#### Option 3: Test Script
```bash
python test_clean_system.py
```

## 📁 File Structure

```
agent-team/
├── agent_system_final.py      # Main agent system (WORKING VERSION)
├── web_interface_clean.py     # Web server interface
├── test_clean_system.py       # Testing script
├── README.md                  # This file
└── (other files are deprecated)
```

## 💡 How to Use

### 1. Start the Web Server
```bash
python web_interface_clean.py
```

### 2. Open Your Browser
Go to: `http://localhost:8002`

### 3. Submit a Request
Fill out the form with your request. Examples:
- "Create a comprehensive report on renewable energy trends"
- "Analyze the current state of the electric vehicle market"
- "Write a beginner's guide to machine learning"
- "Compare different approaches to sustainable agriculture"

### 4. Watch the System Work
The interface will show you:
- Current status
- What each team is doing
- Progress updates
- Final results

### 5. View Results
You'll get:
- Team reports from each agent
- Token usage statistics
- A comprehensive final report
- Option to submit another request

## 🔧 Technical Details

### Workflow Structure
The system uses a **linear workflow** to avoid LangGraph cycle issues while maintaining hierarchical supervisor control:

```
Supervisor → Research Team → Document Team → Final Compiler → END
```

### Token Management
- **Automatic compression** of long content
- **Smart summarization** to stay within limits
- **Usage tracking** for cost monitoring
- **Fallback handling** for errors

### Error Handling
- **Graceful degradation** when services fail
- **Informative error messages** for users
- **Fallback mechanisms** for critical functions
- **Comprehensive logging** for debugging

## 🧪 Testing

### Run the Test Suite
```bash
python test_clean_system.py
```

This will:
1. Test workflow creation
2. Test a simple request
3. Verify all components work
4. Show detailed results

### Expected Output
```
🚀 Starting Clean Agent System Tests
==================================================
🔧 Testing workflow creation...
✅ Workflow created successfully!
📊 Workflow type: <class 'langgraph.graph.state.CompiledStateGraph'>

🧪 Testing simple request...
📋 Test request: Research the benefits of renewable energy
✅ Request processed successfully!
📊 Result type: <class 'dict'>
🔑 Result keys: ['user_request', 'research_results', 'document_content', 'final_output', 'current_task', 'team_reports', 'token_usage']

✅ All expected keys present

📝 Current Task: Complete
👥 Team Reports: 3 teams reported
💰 Token Usage: {'research_team': 136, 'document_authoring_team': 1234, 'final_compiler': 567}
📋 Final Output Length: 3494 characters
📋 Final Output Preview: [Report content preview]...

==================================================
📊 TEST SUMMARY
==================================================
✅ Workflow Creation: PASSED
✅ Request Processing: PASSED

🎉 ALL TESTS PASSED! The system is ready to use.
🌐 You can now start the web server with: python web_interface_clean.py
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: `ModuleNotFoundError` when importing
**Solution**: Make sure you're in the virtual environment and dependencies are installed

#### 2. API Key Errors
**Problem**: `OPENAI_API_KEY` or `TAVILY_API_KEY` not found
**Solution**: Check your `.env` file is in the `APPS` directory and contains valid keys

#### 3. Port Already in Use
**Problem**: `Address already in use` error
**Solution**: Kill existing processes on port 8002:
```bash
lsof -ti:8002 | xargs kill -9
```

#### 4. LangGraph Errors
**Problem**: Workflow compilation fails
**Solution**: Use the `agent_system_final.py` file (the working version)

### Getting Help

1. **Check the logs** in your terminal
2. **Verify API keys** are correct
3. **Ensure dependencies** are installed
4. **Run the test script** to identify issues

## 🎨 Customization

### Adding New Agents
1. Create a new function in `agent_system_final.py`
2. Add it to the workflow in `create_agent_workflow()`
3. Update the state structure if needed

### Modifying Agent Behavior
1. Edit the agent functions in `agent_system_final.py`
2. Adjust prompts and parameters
3. Test with the test script

### Changing the Web Interface
1. Modify `web_interface_clean.py`
2. Update HTML/CSS as needed
3. Test the interface locally

## 📚 Learning Resources

### For Beginners
- **Python basics**: Variables, functions, classes
- **Web development**: HTML, CSS, HTTP
- **AI concepts**: Language models, tokens, APIs

### For Advanced Users
- **LangGraph**: Workflow management
- **LangChain**: AI application framework
- **State management**: TypedDict, state graphs

## 🤝 Contributing

### Code Style
- **Comprehensive comments** for beginners
- **Type hints** for all functions
- **Clear variable names** and structure
- **Error handling** throughout

### Testing
- **Test all changes** before committing
- **Use the test script** to verify functionality
- **Check web interface** works correctly

## 📄 License

This project is part of the APPS monorepo and follows the same licensing terms.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 language model
- **Tavily** for web search capabilities
- **LangChain** for the AI application framework
- **LangGraph** for workflow management

---

## 🎉 Ready to Use!

Your Agent Team System is now ready! Start the web server and begin processing requests:

```bash
python web_interface_clean.py
```

The system will guide you through each step and provide comprehensive results for your research and writing needs.

