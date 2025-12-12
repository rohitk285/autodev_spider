from typing import List, Literal
from src.core.state import GraphState

def route_after_reflection(state: GraphState) -> List[str]:
    """
    Determines next steps. Returns a LIST of node names for parallel execution.
    """
    errors = state.get("structured_errors", [])
    
    # If no errors, we are done
    if not errors:
        return ["end_node"]
    
    # If max iterations reached, stop to prevent infinite loops
    if state.get("iteration_count", 0) > 3:
        print("Max iterations reached. Stopping.")
        return ["end_node"]
    
    # Determine which agents need to work
    agents_to_retry = []
    agent_names = {e.get("agent") for e in errors}
    
    if "frontend" in agent_names:
        agents_to_retry.append("frontend")
    if "backend" in agent_names:
        agents_to_retry.append("backend")
    if "docker" in agent_names:
        agents_to_retry.append("docker_agent")
    if "tests" in agent_names:
        agents_to_retry.append("tests_agent")
        
    # If reflector hallucinated an unknown agent, default to end
    if not agents_to_retry:
        return ["end_node"]
        
    return agents_to_retry