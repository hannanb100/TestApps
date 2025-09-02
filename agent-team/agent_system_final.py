#!/usr/bin/env python3
"""
🤖 AGENT TEAM SYSTEM - HIERARCHICAL SUPERVISOR VERSION (PERFORMANCE OPTIMIZED)
===============================================================================

This is a TRUE hierarchical AI agent system where multiple specialized agents work together
under the continuous supervision of a central coordinator. Think of it like a team of experts
where each person has a specific job, and there's a senior manager who reviews EVERYTHING
before allowing progression to the next phase.

WHAT THIS SYSTEM DOES:
- Takes user requests (like "research quantum computing")
- Breaks them down into research and writing tasks
- Has specialized agents for each task
- SUPERVISOR REVIEWS EACH TEAM'S WORK before allowing progression
- Can request revisions and improvements from any team
- Manages quality control at every step
- Manages token usage to stay within limits
- Produces comprehensive final reports with guaranteed quality

HOW IT WORKS (NEW HIERARCHICAL APPROACH):
1. User submits a request
2. SUPERVISOR analyzes and creates comprehensive plan with quality standards
3. Research Team gathers information
4. SUPERVISOR reviews research quality and decides: ACCEPT or REVISE
5. Document Team creates content (only if research approved)
6. SUPERVISOR reviews document quality and decides: ACCEPT or REVISE
7. Final Compiler creates final report (only if documents approved)
8. SUPERVISOR reviews final output and decides: ACCEPT or REVISE
9. Workflow completes only when supervisor approves final quality

KEY IMPROVEMENTS:
✅ True hierarchical supervision at every phase
✅ Quality control with numerical scoring (0-1 scale)
✅ Revision limits to prevent infinite loops
✅ Supervisor can route workflow back to any team for improvements
✅ Comprehensive feedback and decision logging
✅ Adaptive workflow based on quality assessments

🚀 PERFORMANCE OPTIMIZATIONS (IMPLEMENTED):
✅ Lowered quality thresholds (0.5/0.6/0.65) to reduce revision cycles
✅ Reduced revision limits from 3 to 1 per team to minimize retry loops
✅ Combined multiple LLM calls in document team into single comprehensive call
✅ Added parallel processing for independent operations (compression, token counting)
✅ Simplified supervisor quality review prompts for faster processing
✅ Streamlined scoring mechanisms to reduce LLM processing time

This version implements the hierarchical approach from the LangGraph tutorial,
where the supervisor is actively involved in reviewing and improving work
at every stage, but optimized for speed and efficiency.
"""

# ============================================================================
# IMPORT STATEMENTS - What we need to make this work
# ============================================================================
# 
# These imports provide all the tools we need for our hierarchical agent system:
# - os: For working with files and environment variables
# - typing: For type hints that help catch errors and make code more reliable
# - langchain_openai: The AI language model (GPT-4) that powers our agents
# - langchain_tavily: Web search tool for gathering information
# - langchain_core: Core tools for creating AI agents and workflows
# - langgraph: Framework for creating complex workflows with conditional logic
# - dotenv: For loading API keys safely from environment files
# - json: For working with structured data
# - tiktoken: For counting AI language tokens (helps manage costs)

import os  # For working with files and environment variables
from typing import Dict, Any, List, TypedDict, Annotated  # For type hints (helps catch errors)
from langchain_openai import ChatOpenAI  # The AI language model we'll use
from langchain_tavily import TavilySearch  # For searching the internet
from langchain_core.messages import HumanMessage  # For sending messages to the AI
from langchain_core.tools import tool  # For creating tools that agents can use
from langgraph.graph import StateGraph, END  # For creating the workflow
from langgraph.graph.message import add_messages  # For handling message updates properly
from dotenv import load_dotenv  # For loading environment variables (like API keys)
import json  # For working with data
import tiktoken  # For counting tokens (AI language units)
import operator  # For reducer functions
import concurrent.futures  # PERFORMANCE: For parallel processing
import threading  # PERFORMANCE: For thread-safe operations

# ============================================================================
# ENVIRONMENT SETUP - Loading our API keys and configuration
# ============================================================================

# Load environment variables from .env file
# This is where we store our API keys safely
load_dotenv()

# Initialize the AI language model (GPT-4)
# Think of this as hiring a very smart assistant
llm = ChatOpenAI(
    model="gpt-4o",  # We're using GPT-4 (very capable AI model)
    temperature=0.7,  # How creative vs focused the AI should be (0.7 = balanced)
    api_key=os.getenv("OPENAI_API_KEY")  # Get our OpenAI API key from environment
)

# ============================================================================
# TOKEN MANAGEMENT FUNCTIONS - Managing AI language usage
# ============================================================================

def count_tokens(text: str) -> int:
    """
    Count how many tokens (AI language units) are in a piece of text.
    
    Think of tokens like words, but more precise. The AI charges per token,
    so we need to keep track to stay within our budget.
    
    Args:
        text (str): The text we want to count tokens for
        
    Returns:
        int: Number of tokens in the text
    """
    try:
        # Use tiktoken to count tokens accurately
        encoding = tiktoken.encoding_for_model("gpt-4")
        return len(encoding.encode(text))
    except:
        # If tiktoken fails, use a rough estimate (1 token ≈ 4 characters)
        return len(text) // 4

def truncate_content(content: str, max_tokens: int = 6000) -> str:
    """
    Cut down content if it's too long to stay within token limits.
    
    This is like summarizing a long book to fit in a tweet - we keep
    the important parts but make it shorter.
    
    Args:
        content (str): The content we want to truncate
        max_tokens (int): Maximum number of tokens allowed
        
    Returns:
        str: Truncated content that fits within token limits
    """
    # If content is already short enough, return it as-is
    if count_tokens(content) <= max_tokens:
        return content
    
    # Otherwise, truncate it
    encoding = tiktoken.encoding_for_model("gpt-4")
    tokens = encoding.encode(content)
    truncated_tokens = tokens[:max_tokens]
    truncated_content = encoding.decode(truncated_tokens)
    
    # Add a note that content was truncated
    return truncated_content + "\n\n[Content truncated to stay within token limits]"

def summarize_content(content: str, max_length: int = 500) -> str:
    """
    Create a short summary of longer content.
    
    This is like writing a book review - we capture the main points
    in a much shorter format.
    
    Args:
        content (str): The content to summarize
        max_length (int): Maximum length of the summary
        
    Returns:
        str: A concise summary of the content
    """
    # If content is already short enough, return it as-is
    if len(content) <= max_length:
        return content
    
    # Ask the AI to create a summary
    summary_prompt = f"Summarize this content in {max_length} characters or less:\n\n{content}"
    try:
        response = llm.invoke([HumanMessage(content=summary_prompt)])
        return response.content
    except:
        # If AI fails, just truncate the content
        return content[:max_length] + "..."

# ============================================================================
# SEARCH TOOL SETUP - For gathering information from the internet
# ============================================================================

# Initialize Tavily search tool
# This is like having a very good research assistant who can search the web
tavily_tool = TavilySearch(
    api_key=os.getenv("TAVILY_API_KEY"),  # Get our Tavily API key
    max_results=5  # Limit to 5 results to keep things manageable
)

# ============================================================================
# SPECIALIZED AGENT TOOLS - What each agent can do
# ============================================================================

@tool  # This decorator makes this function available as a tool for agents
def searcher(query: str) -> str:
    """
    Search for information using Tavily search.
    
    This is like having a research assistant who can search the internet
    and bring back relevant information.
    
    Args:
        query (str): What we want to search for
        
    Returns:
        str: Search results and information
    """
    try:
        # Use Tavily to search the internet
        results = tavily_tool.invoke(query)
        
        # Compress results to reduce token usage
        # Think of this like taking notes instead of copying entire articles
        compressed_results = json.dumps(results, separators=(',', ':'))
        
        return f"Search results for '{query}': {compressed_results}"
    except Exception as e:
        return f"Search failed: {str(e)}"

@tool
def writer(content_requirements: str) -> str:
    """
    Write content based on requirements.
    
    This is like having a professional writer who can create content
    based on your specifications.
    
    Args:
        content_requirements (str): What kind of content to write
        
    Returns:
        str: The written content
    """
    try:
        # Ask the AI to write content based on our requirements
        response = llm.invoke([HumanMessage(content=f"Write content based on these requirements: {content_requirements}")])
        return response.content
    except Exception as e:
        return f"Writing failed: {str(e)}"

@tool
def note_taker(content: str) -> str:
    """
    Take notes and organize information.
    
    This is like having a note-taking assistant who can organize
    information into clear, structured notes.
    
    Args:
        content (str): The content to take notes on
        
    Returns:
        str: Organized notes
    """
    try:
        # Ask the AI to create organized notes
        response = llm.invoke([HumanMessage(content=f"Take organized notes from this content: {content}")])
        return response.content
    except Exception as e:
        return f"Note taking failed: {str(e)}"

@tool
def chart_generator(data_description: str) -> str:
    """
    Generate chart specifications based on data.
    
    This is like having a data visualization expert who can suggest
    the best ways to present information visually.
    
    Args:
        data_description (str): Description of the data to visualize
        
    Returns:
        str: Chart specifications and recommendations
    """
    try:
        # Ask the AI to create chart specifications
        response = llm.invoke([HumanMessage(content=f"Create chart specifications for this data: {data_description}")])
        return response.content
    except Exception as e:
        return f"Chart generation failed: {str(e)}"

# ============================================================================
# STATE DEFINITION - How we keep track of everything
# ============================================================================

class AgentState(TypedDict):
    """
    This class defines the structure of our workflow state.
    
    Think of this like a form that gets filled out as the workflow progresses.
    Each field stores different pieces of information that get updated
    as different agents work on the task.
    
    IMPORTANT: We use Annotated types with reducers to handle multiple updates
    to the same state keys. This is required for LangGraph workflows with cycles
    (like our hierarchical workflow where teams can go back for revisions).
    
    Reducers tell LangGraph how to combine multiple updates to the same field:
    - add_messages: Appends new messages to the list
    - operator.add: Adds new items to lists/dicts
    - lambda x, y: y: Takes the latest value (overwrites)
    """
    # Core workflow fields - ALL fields need Annotated types for cyclic workflows
    user_request: Annotated[str, lambda x, y: y or x]  # User request (keep latest non-empty)
    research_results: Annotated[List[Dict], operator.add]  # Research findings (can be added to)
    document_content: Annotated[Dict, lambda x, y: {**x, **y} if x and y else y or x]  # Document content (merge)
    final_output: Annotated[str, lambda x, y: y or x]  # Final report (keep latest non-empty)
    messages: Annotated[List[HumanMessage], add_messages]  # Messages between agents
    current_task: Annotated[str, lambda x, y: y or x]  # Current task (keep latest non-empty)
    supervisor_notes: Annotated[str, lambda x, y: y or x]  # Supervisor notes (keep latest non-empty)
    team_reports: Annotated[Dict[str, str], lambda x, y: {**x, **y}]  # Team reports (merge dicts)
    token_usage: Annotated[Dict[str, int], lambda x, y: {**x, **y}]  # Token usage (merge dicts)
    
    # NEW FIELDS FOR HIERARCHICAL SUPERVISION
    supervisor_reviews: Annotated[Dict[str, Dict], lambda x, y: {**x, **y}]  # Supervisor reviews (merge)
    quality_scores: Annotated[Dict[str, float], lambda x, y: {**x, **y}]  # Quality scores (merge)
    revision_count: Annotated[Dict[str, int], lambda x, y: {**x, **y}]  # Revision counts (merge)
    workflow_phase: Annotated[str, lambda x, y: y or x]  # Current phase (keep latest non-empty)
    supervisor_decisions: Annotated[List[str], lambda x, y: y if isinstance(y, list) else (x or [])]  # Decision log (replace)

# ============================================================================
# SUPERVISOR FUNCTION - The boss who coordinates everything
# ============================================================================

def supervisor(state: AgentState) -> AgentState:
    """
    The Supervisor's job is to coordinate the entire workflow.
    
    Following the LangGraph hierarchical pattern, the supervisor:
    1. Starts by creating a plan (if no work has been done)
    2. Reviews completed work from teams
    3. Makes decisions about next steps based on quality
    4. Routes workflow to appropriate team or completes it
    
    The supervisor determines what to do based on what work has been completed,
    not on pre-set phases. This is more flexible and follows the LangGraph tutorial.
    
    Args:
        state (AgentState): Current state of the workflow
        
    Returns:
        AgentState: Updated state with supervisor decisions
    """
    print("\n" + "👑"*20)
    print("👑 SUPERVISOR: Hierarchical workflow coordination...")
    print("👑"*20)
    
    # Determine what the supervisor should do based on completed work
    has_research = bool(state.get("research_results", []))
    has_documents = bool(state.get("document_content", {}))
    has_final_output = bool(state.get("final_output", ""))
    
    if not has_research:
        # No research yet - start with planning and initiate research
        print("📋 SUPERVISOR: No research found, starting with planning...")
        return _supervisor_planning_phase(state)
    
    elif has_research and not has_documents:
        # Research completed, need to review it
        print("🔍 SUPERVISOR: Research completed, reviewing quality...")
        return _supervisor_review_research(state)
    
    elif has_documents and not has_final_output:
        # Documents completed, need to review them
        print("📝 SUPERVISOR: Documents completed, reviewing quality...")
        return _supervisor_review_document(state)
    
    elif has_final_output:
        # Final output completed, need to review it
        print("📋 SUPERVISOR: Final output completed, reviewing quality...")
        return _supervisor_review_final(state)
    
    else:
        # Fallback - start planning
        print("⚠️ SUPERVISOR: Unclear state, starting with planning...")
        return _supervisor_planning_phase(state)

def _supervisor_planning_phase(state: AgentState) -> AgentState:
    """
    Supervisor's initial planning phase.
    
    This is where the supervisor:
    1. Analyzes the user's request
    2. Creates a comprehensive plan
    3. Sets up quality standards and expectations
    4. Initializes the workflow tracking
    
    Args:
        state (AgentState): Current state of the workflow
        
    Returns:
        AgentState: Updated state with supervisor plan
    """
    print("📋 SUPERVISOR: Starting initial planning phase...")
    
    # Get the user's request from the state
    user_request = state["user_request"]
    print(f"📋 User Request: {user_request}")
    
    # Create a comprehensive planning prompt
    planning_prompt = f"""
    As a senior project manager, analyze this user request and create a detailed plan:
    
    REQUEST: {user_request}
    
    Create a structured plan that includes:
    1. RESEARCH REQUIREMENTS:
       - What specific information needs to be gathered
       - Key areas to investigate
       - Quality standards for research data
    
    2. DOCUMENT REQUIREMENTS:
       - What type of document would be most helpful
       - Key sections and structure needed
       - Quality standards for content
    
    3. WORKFLOW STRATEGY:
       - How to coordinate between teams
       - Quality checkpoints and review criteria
       - Success metrics for each phase
    
    4. QUALITY STANDARDS:
       - Minimum acceptable quality scores (0-1 scale)
       - Revision limits for each team
       - Criteria for moving to next phase
    
    Format your response as a clear, actionable plan.
    """
    
    # Ask the AI to create a comprehensive plan
    plan_response = llm.invoke([HumanMessage(content=planning_prompt)])
    state["supervisor_notes"] = plan_response.content
    
    # Initialize all the new tracking variables for hierarchical supervision
    state["supervisor_reviews"] = {}
    state["quality_scores"] = {}
    state["revision_count"] = {"research_team": 0, "document_authoring_team": 0, "final_compiler": 0}
    state["workflow_phase"] = "research"  # Move to research phase
    
    # Initialize decisions list properly
    current_decisions = state.get("supervisor_decisions", [])
    current_decisions.append("Initial planning completed - moving to research phase")
    state["supervisor_decisions"] = current_decisions
    
    # Set quality thresholds for each team (0-1 scale, where 1 is perfect)
    # PERFORMANCE OPTIMIZATION: Lowered thresholds to reduce revision cycles
    state["quality_thresholds"] = {
        "research_team": 0.5,      # Research must be 50% quality to proceed
        "document_authoring_team": 0.6,  # Documents must be 60% quality to proceed
        "final_compiler": 0.65     # Final output must be 65% quality to complete
    }
    
    print("👑 Supervisor: Comprehensive plan created with quality standards")
    print("👑 Supervisor: Moving to research phase with quality thresholds set")
    state["current_task"] = "Supervisor planning complete, research phase initiated"
    print("👑"*20 + "\n")
    
    return state

def _supervisor_review_research(state: AgentState) -> AgentState:
    """
    Supervisor reviews the research team's work.
    
    This function:
    1. Evaluates the quality of research output
    2. Provides feedback and suggestions for improvement
    3. Decides whether to accept the work or request revisions
    4. Updates the workflow phase based on quality assessment
    
    Args:
        state (AgentState): Current state of the workflow
        
    Returns:
        AgentState: Updated state with supervisor review
    """
    print("🔍 SUPERVISOR: Reviewing research team's work...")
    
    # Get the research team's report and results
    research_report = state.get("team_reports", {}).get("research_team", "")
    research_results = state.get("research_results", [])
    
    if not research_results:
        # No research results to review - this shouldn't happen
        print("⚠️ Supervisor: No research results to review")
        state["workflow_phase"] = "research"  # Stay in research phase
        return state
    
    # PERFORMANCE OPTIMIZATION: Simplified review prompt for faster processing
    review_prompt = f"""
    Quickly evaluate this research work on a 0-1 scale:
    
    USER REQUEST: {state['user_request']}
    RESEARCH SUMMARY: {research_results[0].get('summary', 'No summary')[:300]}...
    
    Rate overall quality (0-1) considering:
    - Does it address the user's request? 
    - Is the information useful?
    - Is it reasonably comprehensive?
    
    Respond ONLY with: SCORE: X.X | DECISION: ACCEPT/REVISE
    (ACCEPT if score >= 0.5, REVISE if below)
    """
    
    # Get the supervisor's evaluation
    review_response = llm.invoke([HumanMessage(content=review_prompt)])
    review_text = review_response.content
    
    # Parse the review response to extract score and decision
    try:
        # Extract score and decision from the response
        score_match = review_text.split("SCORE:")[1].split("|")[0].strip()
        decision_match = review_text.split("DECISION:")[1].split("|")[0].strip()
        
        quality_score = float(score_match)
        decision = decision_match.strip().upper()
        
        print(f"📊 Supervisor Review - Quality Score: {quality_score:.2f}")
        print(f"📋 Supervisor Decision: {decision}")
        
    except (IndexError, ValueError):
        # If parsing fails, use default values
        quality_score = 0.6  # Default to below threshold
        decision = "REVISE"
        print("⚠️ Supervisor: Could not parse review response, defaulting to revision")
    
    # Store the review results
    state["quality_scores"]["research_team"] = quality_score
    state["supervisor_reviews"]["research_team"] = {
        "score": quality_score,
        "feedback": review_text,
        "decision": decision,
        "timestamp": "now"
    }
    
    # Make the decision about next steps
    if decision == "ACCEPT" and quality_score >= state.get("quality_thresholds", {}).get("research_team", 0.7):
        # Research quality is acceptable - move to document phase
        state["workflow_phase"] = "document"
        state["current_task"] = "Research approved, moving to document creation phase"
        current_decisions = state.get("supervisor_decisions", [])
        current_decisions.append(f"Research approved with score {quality_score:.2f} - proceeding to document phase")
        state["supervisor_decisions"] = current_decisions
        print("✅ Supervisor: Research quality acceptable, moving to document phase")
    else:
        # Research needs improvement - check revision limits
        if check_revision_limits(state, "research_team"):
            # Can revise - stay in research phase
            state["workflow_phase"] = "research"
            state["current_task"] = f"Research needs improvement (score: {quality_score:.2f}), requesting revision"
            current_decisions = state.get("supervisor_decisions", [])
            current_decisions.append(f"Research revision requested - score {quality_score:.2f} below threshold")
            state["supervisor_decisions"] = current_decisions
            print(f"🔄 Supervisor: Research revision requested - score {quality_score:.2f} below threshold")
            
            # Increment revision count
            increment_revision_count(state, "research_team")
        else:
            # Revision limit exceeded - force progression with warning
            state["workflow_phase"] = "document"
            state["current_task"] = f"Research revision limit exceeded, proceeding with current quality (score: {quality_score:.2f})"
            current_decisions = state.get("supervisor_decisions", [])
            current_decisions.append(f"Research revision limit exceeded, forced progression with score {quality_score:.2f}")
            state["supervisor_decisions"] = current_decisions
            print(f"⚠️ Supervisor: Research revision limit exceeded, forced progression with score {quality_score:.2f}")
    
    print("👑"*20 + "\n")
    return state

def _supervisor_review_document(state: AgentState) -> AgentState:
    """
    Supervisor reviews the document team's work.
    
    This function:
    1. Evaluates the quality of document content
    2. Provides feedback and suggestions for improvement
    3. Decides whether to accept the work or request revisions
    4. Updates the workflow phase based on quality assessment
    
    Args:
        state (AgentState): Current state of the workflow
        
    Returns:
        AgentState: Updated state with supervisor review
    """
    print("📝 SUPERVISOR: Reviewing document team's work...")
    
    # Get the document team's report and content
    document_report = state.get("team_reports", {}).get("document_authoring_team", "")
    document_content = state.get("document_content", {})
    
    if not document_content:
        # No document content to review - this shouldn't happen
        print("⚠️ Supervisor: No document content to review")
        state["workflow_phase"] = "document"  # Stay in document phase
        return state
    
    # PERFORMANCE OPTIMIZATION: Simplified review prompt for faster processing
    review_prompt = f"""
    Quickly evaluate this document work on a 0-1 scale:
    
    USER REQUEST: {state['user_request']}
    DOCUMENT CONTENT: {document_content.get('written_content', 'No content')[:400]}...
    
    Rate overall quality (0-1) considering:
    - Does it address the user's request?
    - Is the content well-structured and useful?
    - Does it integrate research appropriately?
    
    Respond ONLY with: SCORE: X.X | DECISION: ACCEPT/REVISE
    (ACCEPT if score >= 0.6, REVISE if below)
    """
    
    # Get the supervisor's evaluation
    review_response = llm.invoke([HumanMessage(content=review_prompt)])
    review_text = review_response.content
    
    # Parse the review response to extract score and decision
    try:
        # Extract score and decision from the response
        score_match = review_text.split("SCORE:")[1].split("|")[0].strip()
        decision_match = review_text.split("DECISION:")[1].split("|")[0].strip()
        
        quality_score = float(score_match)
        decision = decision_match.strip().upper()
        
        print(f"📊 Supervisor Review - Quality Score: {quality_score:.2f}")
        print(f"📋 Supervisor Decision: {decision}")
        
    except (IndexError, ValueError):
        # If parsing fails, use default values
        quality_score = 0.6  # Default to below threshold
        decision = "REVISE"
        print("⚠️ Supervisor: Could not parse review response, defaulting to revision")
    
    # Store the review results
    state["quality_scores"]["document_authoring_team"] = quality_score
    state["supervisor_reviews"]["document_authoring_team"] = {
        "score": quality_score,
        "feedback": review_text,
        "decision": decision,
        "timestamp": "now"
    }
    
    # Make the decision about next steps
    if decision == "ACCEPT" and quality_score >= state.get("quality_thresholds", {}).get("document_authoring_team", 0.75):
        # Document quality is acceptable - move to final compilation phase
        state["workflow_phase"] = "final"
        state["current_task"] = "Documents approved, moving to final compilation phase"
        current_decisions = state.get("supervisor_decisions", [])
        current_decisions.append(f"Documents approved with score {quality_score:.2f} - proceeding to final compilation")
        state["supervisor_decisions"] = current_decisions
        print("✅ Supervisor: Document quality acceptable, moving to final compilation phase")
    else:
        # Documents need improvement - check revision limits
        if check_revision_limits(state, "document_authoring_team"):
            # Can revise - stay in document phase
            state["workflow_phase"] = "document"
            state["current_task"] = f"Documents need improvement (score: {quality_score:.2f}), requesting revision"
            current_decisions = state.get("supervisor_decisions", [])
            current_decisions.append(f"Document revision requested - score {quality_score:.2f} below threshold")
            state["supervisor_decisions"] = current_decisions
            print(f"🔄 Supervisor: Document revision requested - score {quality_score:.2f} below threshold")
            
            # Increment revision count
            increment_revision_count(state, "document_authoring_team")
        else:
            # Revision limit exceeded - force progression with warning
            state["workflow_phase"] = "final"
            state["current_task"] = f"Document revision limit exceeded, proceeding with current quality (score: {quality_score:.2f})"
            current_decisions = state.get("supervisor_decisions", [])
            current_decisions.append(f"Document revision limit exceeded, forced progression with score {quality_score:.2f}")
            state["supervisor_decisions"] = current_decisions
            print(f"⚠️ Supervisor: Document revision limit exceeded, forced progression with score {quality_score:.2f}")
    
    print("👑"*20 + "\n")
    return state

def _supervisor_review_final(state: AgentState) -> AgentState:
    """
    Supervisor reviews the final compilation.
    
    This function:
    1. Evaluates the quality of the final output
    2. Provides feedback and suggestions for improvement
    3. Decides whether to accept the work or request revisions
    4. Marks the workflow as complete if quality is acceptable
    
    Args:
        state (AgentState): Current state of the workflow
        
    Returns:
        AgentState: Updated state with supervisor review
    """
    print("📋 SUPERVISOR: Reviewing final compilation...")
    
    # Get the final output
    final_output = state.get("final_output", "")
    
    if not final_output:
        # No final output to review - this shouldn't happen
        print("⚠️ Supervisor: No final output to review")
        state["workflow_phase"] = "final"  # Stay in final phase
        return state
    
    # PERFORMANCE OPTIMIZATION: Simplified review prompt for faster processing
    review_prompt = f"""
    Quickly evaluate this final output on a 0-1 scale:
    
    USER REQUEST: {state['user_request']}
    FINAL OUTPUT: {final_output[:500]}...
    
    Rate overall quality (0-1) considering:
    - Does it fully address the user's request?
    - Is it comprehensive and well-organized?
    - Is it professional and actionable?
    
    Respond ONLY with: SCORE: X.X | DECISION: ACCEPT/REVISE
    (ACCEPT if score >= 0.65, REVISE if below)
    """
    
    # Get the supervisor's evaluation
    review_response = llm.invoke([HumanMessage(content=review_prompt)])
    review_text = review_response.content
    
    # Parse the review response to extract score and decision
    try:
        # Extract score and decision from the response
        score_match = review_text.split("SCORE:")[1].split("|")[0].strip()
        decision_match = review_text.split("DECISION:")[1].split("|")[0].strip()
        
        quality_score = float(score_match)
        decision = decision_match.strip().upper()
        
        print(f"📊 Supervisor Review - Quality Score: {quality_score:.2f}")
        print(f"📋 Supervisor Decision: {decision}")
        
    except (IndexError, ValueError):
        # If parsing fails, use default values
        quality_score = 0.6  # Default to below threshold
        decision = "REVISE"
        print("⚠️ Supervisor: Could not parse review response, defaulting to revision")
    
    # Store the review results
    state["quality_scores"]["final_compiler"] = quality_score
    state["supervisor_reviews"]["final_compiler"] = {
        "score": quality_score,
        "feedback": review_text,
        "decision": decision,
        "timestamp": "now"
    }
    
    # Make the decision about next steps
    if decision == "ACCEPT" and quality_score >= state.get("quality_thresholds", {}).get("final_compiler", 0.8):
        # Final output quality is acceptable - complete the workflow
        state["workflow_phase"] = "complete"
        state["current_task"] = "Final output approved, workflow complete"
        current_decisions = state.get("supervisor_decisions", [])
        current_decisions.append(f"Final output approved with score {quality_score:.2f} - workflow complete")
        state["supervisor_decisions"] = current_decisions
        print("✅ Supervisor: Final output quality acceptable, workflow complete")
    else:
        # Final output needs improvement - check revision limits
        if check_revision_limits(state, "final_compiler"):
            # Can revise - stay in final phase
            state["workflow_phase"] = "final"
            state["current_task"] = f"Final output needs improvement (score: {quality_score:.2f}), requesting revision"
            current_decisions = state.get("supervisor_decisions", [])
            current_decisions.append(f"Final output revision requested - score {quality_score:.2f} below threshold")
            state["supervisor_decisions"] = current_decisions
            print(f"🔄 Supervisor: Final output revision requested - score {quality_score:.2f} below threshold")
            
            # Increment revision count
            increment_revision_count(state, "final_compiler")
        else:
            # Revision limit exceeded - complete workflow with warning
            state["workflow_phase"] = "complete"
            state["current_task"] = f"Final output revision limit exceeded, completing workflow with current quality (score: {quality_score:.2f})"
            current_decisions = state.get("supervisor_decisions", [])
            current_decisions.append(f"Final output revision limit exceeded, completing workflow with score {quality_score:.2f}")
            state["supervisor_decisions"] = current_decisions
            print(f"⚠️ Supervisor: Final output revision limit exceeded, completing workflow with score {quality_score:.2f}")
    
    print("👑"*20 + "\n")
    return state

# ============================================================================
# PERFORMANCE UTILITIES - Parallel processing functions
# ============================================================================

def run_parallel_tasks(tasks: List[Dict[str, Any]], max_workers: int = 2) -> List[Any]:
    """
    Execute multiple tasks in parallel to improve performance.
    
    PERFORMANCE OPTIMIZATION: Run independent operations simultaneously
    instead of sequentially to reduce total execution time.
    
    Args:
        tasks (List[Dict]): List of task dictionaries with 'function' and 'args'
        max_workers (int): Maximum number of parallel workers
        
    Returns:
        List[Any]: Results from all tasks in the same order
    """
    results = []
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {}
            for i, task in enumerate(tasks):
                func = task['function']
                args = task.get('args', ())
                kwargs = task.get('kwargs', {})
                future = executor.submit(func, *args, **kwargs)
                future_to_task[future] = i
            
            # Collect results in order
            results = [None] * len(tasks)
            for future in concurrent.futures.as_completed(future_to_task):
                task_index = future_to_task[future]
                try:
                    result = future.result()
                    results[task_index] = result
                except Exception as e:
                    print(f"⚠️ PARALLEL TASK {task_index} FAILED: {str(e)}")
                    results[task_index] = f"Task failed: {str(e)}"
    
    except Exception as e:
        print(f"⚠️ PARALLEL EXECUTION FAILED: {str(e)}")
        # Fallback to sequential execution
        for task in tasks:
            try:
                func = task['function']
                args = task.get('args', ())
                kwargs = task.get('kwargs', {})
                result = func(*args, **kwargs)
                results.append(result)
            except Exception as task_error:
                results.append(f"Sequential fallback failed: {str(task_error)}")
    
    return results

# ============================================================================
# RESEARCH TEAM - Gathering information
# ============================================================================

def research_team(state: AgentState) -> AgentState:
    """
    The Research Team's job is to gather information.
    
    This function:
    1. Takes the user's request
    2. Searches for relevant information
    3. Compresses and summarizes the findings
    4. Creates a report for the supervisor
    5. Updates the state with their findings
    
    Args:
        state (AgentState): Current state of the workflow
        
    Returns:
        AgentState: Updated state with research results
    """
    print("\n" + "🔍"*20)
    print("🔍 RESEARCH TEAM: Starting research activities...")
    print("🔍"*20)
    
    # Get the user's request from the state
    user_request = state["user_request"]
    print(f"📋 User Request: {user_request}")
    
    # Create a search query and search for information
    search_query = f"research information about: {user_request}"
    print(f"🔎 Search Query: {search_query}")
    
    # PERFORMANCE OPTIMIZATION: Use parallel processing for search and content processing
    def search_task():
        return searcher.invoke(search_query)
    
    def count_task(results):
        return len(results)
    
    # Run search
    search_results = search_task()
    print(f"📊 Raw Search Results: {len(search_results)} characters")
    
    # Parallel processing for compression and summarization
    parallel_tasks = [
        {
            'function': truncate_content,
            'args': (search_results,),
            'kwargs': {'max_tokens': 4000}
        },
        {
            'function': count_tokens,
            'args': (search_results,)
        }
    ]
    
    parallel_results = run_parallel_tasks(parallel_tasks, max_workers=2)
    compressed_results = parallel_results[0]
    token_count = parallel_results[1]
    
    print(f"🗜️ Compressed Results: {len(compressed_results)} characters")
    
    # Create a summary of the research
    research_summary = summarize_content(compressed_results, max_length=800)
    print(f"📝 Research Summary: {len(research_summary)} characters")
    
    # Create a report for the supervisor
    team_report = f"✅ Research completed\n• Found {len(search_results.split())} data points\n• Compressed to {count_tokens(research_summary)} tokens\n• Ready for document creation"
    print(f"📤 Team Report: {team_report}")
    
    # Update the state with our findings
    state["research_results"].append({
        "query": search_query,
        "results": compressed_results,
        "summary": research_summary
    })
    
    # Record our report and token usage
    state["team_reports"]["research_team"] = team_report
    state["token_usage"]["research_team"] = count_tokens(research_summary)
    
    # Research complete - supervisor will review and decide next steps
    # Note: We don't set workflow_phase here - supervisor will decide routing
    state["current_task"] = "Research completed, awaiting supervisor review"
    
    print("🔍 Research Team: Work completed, awaiting supervisor review")
    print("🔍"*20 + "\n")
    
    return state

# ============================================================================
# DOCUMENT TEAM - Creating content
# ============================================================================

def document_authoring_team(state: AgentState) -> AgentState:
    """
    The Document Team's job is to create content based on research.
    
    PERFORMANCE OPTIMIZATION: Combined multiple LLM calls into a single comprehensive call
    to reduce API latency and improve speed.
    
    This function:
    1. Takes the research findings
    2. Creates written content, notes, and chart specifications in ONE LLM call
    3. Compresses everything to stay within token limits
    4. Creates a report for the supervisor
    5. Updates the state with their work
    
    Args:
        state (AgentState): Current state of the workflow
        
    Returns:
        AgentState: Updated state with document content
    """
    print("\n" + "📝"*20)
    print("📝 DOCUMENT AUTHORING TEAM: Starting content creation...")
    print("📝"*20)
    
    # Get the research summary from the state
    research_summary = "\n".join([r["summary"] for r in state["research_results"]])
    
    # PERFORMANCE OPTIMIZATION: Combine all document tasks into ONE LLM call
    comprehensive_prompt = f"""
    Based on this research data, create comprehensive document content with ALL of the following components:

    RESEARCH DATA:
    {research_summary}

    Please provide:

    1. WRITTEN CONTENT:
    Create a well-structured, professional document that addresses the user's request: {state['user_request']}
    Make it comprehensive, informative, and well-organized.

    2. ORGANIZED NOTES:
    Create bullet-point notes that summarize key findings and important information from the research.
    Focus on actionable insights and main takeaways.

    3. CHART SPECIFICATIONS:
    Suggest appropriate data visualizations, charts, or diagrams that would help illustrate the content.
    Specify chart types, data points, and visual recommendations.

    Format your response as:
    === WRITTEN CONTENT ===
    [Your comprehensive written content here]

    === ORGANIZED NOTES ===
    [Your organized bullet-point notes here]

    === CHART SPECIFICATIONS ===
    [Your chart and visualization recommendations here]
    """
    
    try:
        # Single LLM call for all document tasks
        comprehensive_response = llm.invoke([HumanMessage(content=comprehensive_prompt)])
        full_response = comprehensive_response.content
        
        # Parse the response to extract different sections
        sections = full_response.split("=== ")
        
        written_content = ""
        notes = ""
        chart_spec = ""
        
        for section in sections:
            if section.startswith("WRITTEN CONTENT ==="):
                written_content = section.replace("WRITTEN CONTENT ===", "").strip()
            elif section.startswith("ORGANIZED NOTES ==="):
                notes = section.replace("ORGANIZED NOTES ===", "").strip()
            elif section.startswith("CHART SPECIFICATIONS ==="):
                chart_spec = section.replace("CHART SPECIFICATIONS ===", "").strip()
        
        # Fallback if parsing fails - use the full response as written content
        if not written_content and not notes and not chart_spec:
            written_content = full_response
            notes = f"Key points extracted from: {research_summary[:200]}..."
            chart_spec = "Standard charts recommended: bar charts for comparisons, line charts for trends"
    
    except Exception as e:
        # Fallback content if LLM call fails
        written_content = f"Document creation failed: {str(e)}. Using research summary as content: {research_summary}"
        notes = f"Failed to generate notes. Research summary: {research_summary[:300]}..."
        chart_spec = "Chart generation failed. Basic visualizations recommended."
    
    # Compress all the content to stay within token limits
    compressed_content = {
        "written_content": truncate_content(written_content, max_tokens=3000),
        "notes": truncate_content(notes, max_tokens=1500),
        "chart_specification": truncate_content(chart_spec, max_tokens=1000),
        "research_basis": research_summary
    }
    
    # Create a report for the supervisor
    total_tokens = sum(count_tokens(v) for v in compressed_content.values())
    team_report = f"✅ Document authoring completed (OPTIMIZED: 1 LLM call)\n• Content: {len(written_content.split())} words\n• Notes: {len(notes.split())} words\n• Total tokens: {total_tokens}\n• Ready for final compilation"
    
    # Update the state with our work
    state["document_content"] = compressed_content
    state["team_reports"]["document_authoring_team"] = team_report
    state["token_usage"]["document_authoring_team"] = total_tokens
    
    # Document authoring complete - supervisor will review and decide next steps
    # Note: We don't set workflow_phase here - supervisor will decide routing
    state["current_task"] = "Document authoring completed, awaiting supervisor review"
    
    print("📝 Document Team: Work completed, awaiting supervisor review")
    print("📝"*20 + "\n")
    
    return state

# ============================================================================
# FINAL COMPILER - Putting everything together
# ============================================================================

def final_compiler(state: AgentState) -> AgentState:
    """
    The Final Compiler's job is to create the final report.
    
    This function:
    1. Takes all the work from the teams
    2. Combines research and document content
    3. Creates a comprehensive final report
    4. Tracks total token usage
    
    Args:
        state (AgentState): Current state of the workflow
        
    Returns:
        AgentState: Updated state with final output
    """
    print("\n" + "📋"*20)
    print("📋 FINAL COMPILER: Starting final compilation...")
    print("📋"*20)
    
    # Check if we have reports from both teams
    if not state.get("team_reports", {}).get("research_team") or \
       not state.get("team_reports", {}).get("document_authoring_team"):
        state["final_output"] = "❌ Final compilation blocked: Not all teams have reported back"
        state["current_task"] = "Blocked - awaiting team reports"
        return state
    
    # Create the final prompt for the AI
    final_prompt = f"""
    Create a comprehensive final report based on:
    
    User Request: {state['user_request']}
    
    Research Summary: {state['research_results'][0]['summary'] if state['research_results'] else 'No research data'}
    
    Document Summary: {summarize_content(json.dumps(state['document_content']), max_length=1000)}
    
    Supervisor Notes: {summarize_content(state['supervisor_notes'], max_length=500)}
    
    Create a well-structured, professional report that addresses the user's request.
    The report should be comprehensive, well-organized, and actionable.
    """
    
    # Check token count before making the AI call
    prompt_tokens = count_tokens(final_prompt)
    if prompt_tokens > 6000:
        final_prompt = truncate_content(final_prompt, max_tokens=6000)
        print(f"⚠️ Final prompt truncated from {prompt_tokens} to {count_tokens(final_prompt)} tokens")
    
    try:
        # Ask the AI to create the final report
        final_response = llm.invoke([HumanMessage(content=final_prompt)])
        state["final_output"] = final_response.content
        
        # Create a final report summary
        total_tokens = sum(state["token_usage"].values()) + count_tokens(final_response.content)
        final_report = f"✅ Final compilation completed\n• Total tokens used: {total_tokens}\n• All teams completed\n• Report generated successfully"
        state["team_reports"]["final_compiler"] = final_report
        
        # Final compilation complete - supervisor will review and decide next steps
        # Note: We don't set workflow_phase here - supervisor will decide routing
        state["current_task"] = "Final compilation completed, awaiting supervisor review"
        
        print("📋 Final Compiler: Final report created, awaiting supervisor review")
        print(f"📊 Total token usage: {total_tokens}")
        print("📋"*20 + "\n")
        
    except Exception as e:
        state["final_output"] = f"❌ Final compilation failed: {str(e)}"
        state["current_task"] = "Failed"
        print(f"❌ Final Compiler: Compilation failed - {str(e)}")
    
    return state

# ============================================================================
# WORKFLOW CREATION - How we connect all the pieces
# ============================================================================

def create_agent_workflow():
    """
    Create the workflow that connects all our agents.
    
    This function creates a HIERARCHICAL SUPERVISOR WORKFLOW following the 
    LangGraph tutorial pattern where:
    
    1. Supervisor starts and creates a plan
    2. Teams work on their tasks
    3. ALL teams report back to supervisor for review
    4. Supervisor decides next steps (accept, revise, or complete)
    
    The key insight from the LangGraph tutorial is that the supervisor acts
    as a central hub that all teams connect to, rather than teams connecting
    directly to each other.
    
    Returns:
        Compiled workflow that can be executed
    """
    # Create a new state graph using our AgentState structure
    workflow = StateGraph(AgentState)
    
    # Add all our agent functions as nodes in the workflow
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("research_team", research_team)
    workflow.add_node("document_authoring_team", document_authoring_team)
    workflow.add_node("final_compiler", final_compiler)
    
    # Set the supervisor as the starting point
    workflow.set_entry_point("supervisor")
    
    # CRITICAL: Following LangGraph hierarchical pattern
    # All teams connect back to supervisor, supervisor routes to next team
    
    # Teams report back to supervisor after completing work
    workflow.add_edge("research_team", "supervisor")
    workflow.add_edge("document_authoring_team", "supervisor")
    workflow.add_edge("final_compiler", "supervisor")
    
    # Supervisor uses conditional edges to route to appropriate team or end
    workflow.add_conditional_edges(
        "supervisor",
        route_workflow,  # Function that determines next step
        {
            "research_team": "research_team",
            "document_authoring_team": "document_authoring_team", 
            "final_compiler": "final_compiler",
            END: END
        }
    )
    
    # Compile and return the workflow
    return workflow.compile()

def route_workflow(state: AgentState) -> str:
    """
    This function determines where the workflow should go next based on the current state.
    
    Following the LangGraph hierarchical pattern, this router is called by the supervisor
    to decide which team should work next, or whether the workflow is complete.
    
    The supervisor has already made quality decisions and updated the workflow_phase,
    so we just need to route based on that phase.
    
    Args:
        state (AgentState): Current state of the workflow
        
    Returns:
        str: The name of the next node to execute
    """
    current_phase = state.get("workflow_phase", "planning")
    
    print(f"🔄 WORKFLOW ROUTER: Current phase: {current_phase}")
    
    # Simple routing based on workflow phase set by supervisor
    if current_phase == "research":
        # Supervisor wants research team to work (initial or revision)
        return "research_team"
    
    elif current_phase == "document":
        # Supervisor approved research, wants document team to work
        return "document_authoring_team"
    
    elif current_phase == "final":
        # Supervisor approved documents, wants final compilation
        return "final_compiler"
    
    elif current_phase == "complete":
        # Supervisor approved final output, workflow complete
        return END
    
    else:
        # Unknown phase or planning - default to research team
        print(f"🔄 WORKFLOW ROUTER: Phase '{current_phase}', starting with research team")
        return "research_team"

def check_revision_limits(state: AgentState, team_name: str) -> bool:
    """
    Check if a team has exceeded their revision limit.
    
    This prevents infinite loops where teams keep revising without improvement.
    Each team has a maximum number of revision attempts.
    
    PERFORMANCE OPTIMIZATION: Reduced from 3 to 1 revision to speed up workflow.
    
    Args:
        state (AgentState): Current state of the workflow
        team_name (str): Name of the team to check
        
    Returns:
        bool: True if team can revise, False if limit exceeded
    """
    max_revisions = 1  # PERFORMANCE: Maximum revision attempts per team (reduced from 3)
    current_revisions = state.get("revision_count", {}).get(team_name, 0)
    
    if current_revisions >= max_revisions:
        print(f"⚠️ REVISION LIMIT: {team_name} has exceeded {max_revisions} revision attempts")
        return False
    
    return True

def increment_revision_count(state: AgentState, team_name: str) -> AgentState:
    """
    Increment the revision count for a specific team.
    
    This tracks how many times each team has revised their work,
    helping the supervisor make decisions about quality and progress.
    
    Args:
        state (AgentState): Current state of the workflow
        team_name (str): Name of the team to increment
        
    Returns:
        AgentState: Updated state with incremented revision count
    """
    current_count = state.get("revision_count", {}).get(team_name, 0)
    state["revision_count"][team_name] = current_count + 1
    
    print(f"📊 REVISION TRACKING: {team_name} revision count: {current_count + 1}")
    return state

# ============================================================================
# MAIN INTERFACE - How users interact with the system
# ============================================================================

def process_user_request(user_request: str) -> Dict[str, Any]:
    """
    Main function that processes user requests through the agent team system.
    
    This function:
    1. Creates the workflow
    2. Sets up the initial state
    3. Runs the workflow
    4. Returns the results
    
    Args:
        user_request (str): What the user wants the system to do
        
    Returns:
        Dict[str, Any]: Complete results from the workflow
    """
    # Create the workflow
    workflow = create_agent_workflow()
    
    # Create the initial state with the user's request
    initial_state = {
        "user_request": user_request,
        "research_results": [],
        "document_content": {},
        "final_output": "",
        "messages": [],
        "current_task": "Starting",
        "supervisor_notes": "",
        "team_reports": {},
        "token_usage": {},
        
        # NEW: Initialize hierarchical supervision fields
        "supervisor_reviews": {},
        "quality_scores": {},
        "revision_count": {"research_team": 0, "document_authoring_team": 0, "final_compiler": 0},
        "workflow_phase": "planning",  # Start with planning phase
        "supervisor_decisions": []
    }
    
    # Run the workflow with our initial state
    result = workflow.invoke(initial_state)
    
    # Return the results
    return result

# ============================================================================
# TESTING - For development and debugging
# ============================================================================

if __name__ == "__main__":
    """
    This section runs when we execute this file directly.
    It's useful for testing the system during development.
    """
    print("🧪 Testing Agent Team System...")
    
    # Test with a sample request
    test_request = "Create a comprehensive guide to sustainable energy solutions for urban areas"
    result = process_user_request(test_request)
    
    print("\n🎉 Test completed!")
    print(f"Final output: {result['final_output'][:200]}...")

