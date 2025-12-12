import json
from langchain_core.messages import AIMessage
from src.core.state import GraphState
from src.utils.llm_helper import invoke_llm_json, print_message_event
from src.prompts.system_prompts import ARCHITECT_PROMPT

def architect_node(state: GraphState):
    print("\n" + "="*60)
    print("🏗️  ARCHITECT: Designing System Architecture")
    print("="*60)
    user_story = state["user_story"]
    
    # Call LLM
    output = invoke_llm_json(ARCHITECT_PROMPT, f"User Story: {user_story}")
    
    api_spec = output.get("api_spec", "{}")
    plan = output.get("architecture_plan", "No plan generated")
    
    ai_msg = AIMessage(content="Architecture Plan and API Spec created.")
    print_message_event("architect", ai_msg.content, "new_message_added")
    
    return {
        "api_spec": json.dumps(api_spec) if isinstance(api_spec, dict) else api_spec,
        "architecture_plan": plan,
        "messages": [ai_msg]
    }