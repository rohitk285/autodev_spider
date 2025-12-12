import json
from langchain_core.messages import AIMessage
from src.core.state import GraphState
from src.utils.llm_helper import invoke_llm_json, print_message_event
from src.utils.code_exporter import CodeExporter
from src.prompts.system_prompts import TESTS_PROMPT

def tests_agent_node(state: GraphState):
    print("\n" + "="*60)
    print("TESTS: Generating Test Configuration")
    print("="*60)
    
    # 1. Gather Context
    api_spec = state["api_spec"]
    backend_files = state.get("backend_files", {})
    errors = state.get("structured_errors", [])
    
    # 2. Determine Mode (Gen vs Repair)
    my_errors = [e for e in errors if e['agent'] == 'tests']
    
    if not my_errors:
        # Generation Mode
        print("Mode: Initial Test Configuration Generation")
        user_prompt = f"""Generate test configuration (tests/requirements.txt and tests/test_backend_api.py) for this API: {api_spec}

Include:
- tests/requirements.txt with pytest and other testing dependencies
- tests/test_backend_api.py with comprehensive pytest test cases
- tests/README.md with test instructions"""
    else:
        # Repair Mode
        print(f"Mode: Fixing {len(my_errors)} error(s)")
        current_tests = state.get("tests_files", {})
        user_prompt = (
            f"Here is your previous test config: {json.dumps(current_tests)}\n"
            f"Here are the errors you must fix: {json.dumps(my_errors)}\n"
            f"Return the corrected test configuration as JSON with file paths as keys."
        )
    
    # 3. Call LLM
    files = invoke_llm_json(TESTS_PROMPT, user_prompt)
    
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
        exporter.export_by_agent("tests", files, metadata=metadata)
    
    ai_msg = AIMessage(content=f"Test configuration generated/updated with {len(files)} files.")
    print_message_event("tests", ai_msg.content, "new_message_added")
    print(f"Generated {len(files)} test files")
    
    return {
        "tests_files": files,
        "messages": [ai_msg]
    }
