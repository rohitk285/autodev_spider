import os
import json
from langchain_core.messages import HumanMessage
from src.core.state import GraphState
from src.utils.llm_helper import print_message_event

def save_files(base_path, files_dict):
    """Helper to write dict of files to disk"""
    if not files_dict: return
    for path, content in files_dict.items():
        full_path = os.path.join(base_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

def human_node(state: GraphState):
    print("\n" + "="*60)
    print("👁️  REVIEW NODE: Examining Sandbox Execution")
    print("="*60)
    
    # Get sandbox logs
    sandbox_logs = state.get("sandbox_logs", {})
    iteration = state.get("iteration_count", 0)
    
    print(f"\n📊 Iteration #{iteration}")
    print(f"Status: {sandbox_logs.get('status', 'unknown')}")
    print(f"Frontend URL: {sandbox_logs.get('frontend_url', 'N/A')}")
    
    # Display container logs
    container_logs = sandbox_logs.get("container_logs", {})
    if container_logs:
        print("\n📋 CONTAINER LOGS:")
        print("="*60)
        for service, log in container_logs.items():
            print(f"\n[{service}]")
            # Show first 500 chars of each service log
            log_preview = log[:500] if isinstance(log, str) else str(log)[:500]
            print(log_preview)
            if len(log) > 500:
                print(f"... (truncated, see full logs at {sandbox_logs.get('logs_file', 'N/A')})")
    
    print("\n" + "="*60)
    print("FEEDBACK OPTIONS:")
    print("  'success' - Code is working correctly")
    print("  'error: [description]' - Describe what's wrong")
    print("  'modify: [description]' - Request a modification")
    print("  'skip' - Skip review and continue")
    print("="*60)
    
    # Capture feedback
    feedback = input("\n>> ").strip()
    
    human_msg = HumanMessage(content=feedback)
    print_message_event("review", human_msg.content, "feedback_provided")
    
    return {
        "human_feedback": feedback,
        "messages": [human_msg]
    }