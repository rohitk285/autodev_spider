from typing import TypedDict, List, Dict, Annotated, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    """
    Represents the state of our graph.
    """
    # --- Conversation History ---
    messages: Annotated[List[BaseMessage], add_messages]
    
    # --- The Contract (Immutable after Architect) ---
    user_story: str
    api_spec: str          # JSON string of the API Schema
    architecture_plan: str # Text summary of the plan
    
    # --- The Codebase (Mutable) ---
    frontend_files: Dict[str, str]  # {'App.js': 'code'}
    backend_files: Dict[str, str]   # {'main.py': 'code'}
    docker_files: Dict[str, str]    # {'docker-compose.yml': 'code', 'backend/Dockerfile': 'code'}
    tests_files: Dict[str, str]     # {'tests.json': 'code'}
    infra_files: Dict[str, str]     # {'docker-compose.yml': 'code'}
    
    # --- Sandbox Execution ---
    sandbox_logs: Dict                # Logs from sandbox execution
    
    # --- Feedback Loop ---
    human_feedback: str             # Raw error pasted by you
    structured_errors: List[Dict]   # Parsed errors: [{'agent': 'backend', 'instruction': '...'}]
    iteration_count: int            # Safety breaker