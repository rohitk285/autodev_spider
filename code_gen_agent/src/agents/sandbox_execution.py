import json
import sys
import os
from langchain_core.messages import AIMessage
from src.core.state import GraphState
from src.utils.llm_helper import print_message_event

def sandbox_execution_node(state: GraphState):
    """
    Executes the sandbox with all 4 JSON outputs (frontend, backend, docker, tests)
    Returns the sandbox execution logs in JSON format
    """
    print("\n" + "="*60)
    print("🏃 SANDBOX EXECUTION: Running Generated Code")
    print("="*60)
    
    # 1. Prepare the 4 JSON inputs
    frontend_json = state.get("frontend_files", {})
    backend_json = state.get("backend_files", {})
    docker_json = state.get("docker_files", {})
    tests_json = state.get("tests_files", {})
    
    print("\n📦 Prepared inputs:")
    print(f"  - Frontend: {len(frontend_json)} files")
    print(f"  - Backend: {len(backend_json)} files")
    print(f"  - Docker: {len(docker_json)} files")
    print(f"  - Tests: {len(tests_json)} files")
    
    # 2. Call sandbox function
    try:
        # Add docker directory to path to import sandbox
        docker_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "docker"))
        if docker_path not in sys.path:
            sys.path.insert(0, docker_path)
        
        from sandbox import sandbox_workflow
        
        print("\n🚀 Starting sandbox workflow...")
        sandbox_result = sandbox_workflow(frontend_json, backend_json, tests_json, docker_json)
        
        print("\n✅ Sandbox execution completed")
        print(f"   Status: {sandbox_result.get('status')}")
        print(f"   Frontend URL: {sandbox_result.get('frontend_url')}")
        print(f"   Logs file: {sandbox_result.get('logs_file')}")
        
        # 3. Read the logs JSON file if it exists
        logs_content = {}
        logs_file = sandbox_result.get('logs_file')
        if logs_file and os.path.exists(logs_file):
            with open(logs_file, 'r', encoding='utf-8') as f:
                logs_content = json.load(f)
        
        # 4. Create structured output
        sandbox_logs = {
            "status": sandbox_result.get("status"),
            "project_root": sandbox_result.get("project_root"),
            "frontend_url": sandbox_result.get("frontend_url"),
            "logs_file": str(logs_file) if logs_file else None,
            "container_logs": logs_content,
            "execution_time": "N/A"
        }
        
        ai_msg = AIMessage(content=f"Sandbox execution completed with status: {sandbox_result.get('status')}")
        print_message_event("sandbox", ai_msg.content, "sandbox_execution")
        
        return {
            "sandbox_logs": sandbox_logs,
            "messages": [ai_msg]
        }
        
    except Exception as e:
        print(f"\n❌ Sandbox execution failed: {str(e)}")
        error_logs = {
            "status": "error",
            "error": str(e),
            "container_logs": {}
        }
        
        ai_msg = AIMessage(content=f"Sandbox execution failed: {str(e)}")
        print_message_event("sandbox", ai_msg.content, "sandbox_error")
        
        return {
            "sandbox_logs": error_logs,
            "messages": [ai_msg]
        }
