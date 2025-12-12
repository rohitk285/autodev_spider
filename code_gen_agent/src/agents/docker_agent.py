import json
from langchain_core.messages import AIMessage
from src.core.state import GraphState
from src.utils.llm_helper import invoke_llm_json, print_message_event
from src.utils.code_exporter import CodeExporter
from src.prompts.system_prompts import DOCKER_PROMPT

def docker_agent_node(state: GraphState):
    print("\n" + "="*60)
    print("DOCKER: Generating Docker Configuration")
    print("="*60)
    
    # 1. Gather Context
    api_spec = state["api_spec"]
    errors = state.get("structured_errors", [])
    
    # 2. Determine Mode (Gen vs Repair)
    my_errors = [e for e in errors if e['agent'] == 'docker']
    
    if not my_errors:
        # Generation Mode
        print("Mode: Initial Docker Configuration Generation")
        user_prompt = f"""Generate Docker Compose configuration for this API: {api_spec}
        
Include docker-compose.yml with services for database, backend, and frontend.
Also include a .env file with required environment variables."""
    else:
        # Repair Mode
        print(f"Mode: Fixing {len(my_errors)} error(s)")
        current_config = state.get("docker_files", {})
        user_prompt = (
            f"Here is your previous docker config: {json.dumps(current_config)}\n"
            f"Here are the errors you must fix: {json.dumps(my_errors)}\n"
            f"Return the corrected docker configuration files as JSON with file paths as keys."
        )
    
    # 3. Call LLM
    files = invoke_llm_json(DOCKER_PROMPT, user_prompt)
    
    # Ensure files is a dict
    if not isinstance(files, dict):
        files = {}
    
    # 4. Export to JSON (optional, for logging)
    if files:
        exporter = CodeExporter()
        metadata = {
            "user_story": state.get("user_story", ""),
            "iteration": state.get("iteration_count", 0),
            "mode": "repair" if my_errors else "generation"
        }
        exporter.export_by_agent("docker", files, metadata=metadata)
    
    ai_msg = AIMessage(content=f"Docker configuration generated/updated with {len(files)} files.")
    print_message_event("docker", ai_msg.content, "new_message_added")
    print(f"Generated {len(files)} docker files")
    
    return {
        "docker_files": files,
        "messages": [ai_msg]
    }
