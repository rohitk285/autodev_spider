from src.core.state import GraphState
from src.utils.llm_helper import invoke_llm_json, print_message_event
from src.prompts.system_prompts import REFLECTOR_PROMPT
import json

def reflector_node(state: GraphState):
    print("\n" + "="*60)
    print("🔍 REFLECTOR: Analyzing Sandbox Logs")
    print("="*60)
    
    # Get sandbox logs
    sandbox_logs = state.get("sandbox_logs", {})
    iteration = state.get("iteration_count", 0)
    
    print(f"📊 Iteration: {iteration + 1}")
    
    # Check sandbox execution status
    status = sandbox_logs.get("status", "unknown")
    
    # if status == "success":
    #     # Check if frontend is running
    #     frontend_url = sandbox_logs.get("frontend_url")
    #     if frontend_url:
    #         print(f"✅ SUCCESS! Frontend is running at {frontend_url}")
    #         print("   Sandbox logs are ready for review.")
            
    #         # Return the logs as feedback for frontend display
    #         return {
    #             "structured_errors": [],
    #             "iteration_count": iteration + 1
    #         }
    
    # If status is error or partial, extract errors from logs
    logs_content = sandbox_logs.get("container_logs", {})
    
    # Stringify logs for LLM analysis
    logs_text = json.dumps(logs_content, indent=2) if logs_content else "No logs available"
    
    print("\n🤖 Analyzing container logs with AI...")
    structured_errors = invoke_llm_json(
        REFLECTOR_PROMPT, 
        f"Container Logs:\n{logs_text}\n\nStatus: {status}"
    )
    
    # Ensure it's a list
    if not isinstance(structured_errors, list):
        structured_errors = []
    
    if structured_errors:
        print(f"\n📋 Found {len(structured_errors)} error(s) to fix:")
        for i, err in enumerate(structured_errors, 1):
            agent = err.get('agent', 'unknown')
            instruction = err.get('instruction', 'No instruction')[:100]
            print(f"   {i}. [{agent}] {instruction}...")
    else:
        print("\n✅ No specific errors identified. Review logs in frontend.")
    
    return {
        "structured_errors": structured_errors,
        "iteration_count": iteration + 1
    }