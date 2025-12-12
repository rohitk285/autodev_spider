import json
from langchain_core.messages import AIMessage
from src.core.state import GraphState
from src.utils.llm_helper import invoke_llm_json, print_message_event
from src.utils.code_exporter import CodeExporter
from src.prompts.system_prompts import BACKEND_PROMPT

def backend_node(state: GraphState):
    print("\n" + "="*60)
    print("BACKEND: Generating FastAPI Code")
    print("="*60)
    
    api_spec = state["api_spec"]
    errors = state.get("structured_errors", [])
    
    my_errors = [e for e in errors if e['agent'] == 'backend']
    
    if not my_errors:
        print("Mode: Initial Code Generation")
        user_prompt = f"Generate a FastAPI app for this API: {api_spec}"
    else:
        print(f"Mode: Fixing {len(my_errors)} error(s)")
        current_code = state.get("backend_files", {})
        user_prompt = (
            f"Here is your previous code: {json.dumps(current_code)}\n"
            f"Here are the errors you must fix: {json.dumps(my_errors)}\n"
            f"Return the full corrected code as JSON with file paths as keys."
        )
    
    files = invoke_llm_json(BACKEND_PROMPT, user_prompt)
    
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
        exporter.export_by_agent("backend", files, metadata=metadata)
    
    ai_msg = AIMessage(content=f"Backend code generated/updated with {len(files)} files.")
    print_message_event("backend", ai_msg.content, "new_message_added")
    print(f"Generated {len(files)} backend files")
    
    return {
        "backend_files": files,
        "messages": [ai_msg]
    }