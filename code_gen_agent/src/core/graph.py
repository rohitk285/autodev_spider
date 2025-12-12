from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.core.state import GraphState

# Import Nodes
from src.agents.architect import architect_node
from src.agents.frontend import frontend_node
from src.agents.backend import backend_node
from src.agents.docker_agent import docker_agent_node
from src.agents.tests_agent import tests_agent_node
from src.agents.sandbox_execution import sandbox_execution_node
from src.agents.human import human_node
from src.agents.reflector import reflector_node
from src.agents.router import route_after_reflection

def create_graph():
    workflow = StateGraph(GraphState)

    # 1. Add Nodes
    workflow.add_node("architect", architect_node)
    workflow.add_node("frontend", frontend_node)
    workflow.add_node("backend", backend_node)
    workflow.add_node("docker_agent", docker_agent_node)
    workflow.add_node("tests_agent", tests_agent_node)
    workflow.add_node("sandbox", sandbox_execution_node)
    workflow.add_node("human", human_node)
    workflow.add_node("reflector", reflector_node)
    
    # 2. Define Edges
    # Start with architect
    workflow.set_entry_point("architect")
    
    # After architect completes, all 4 agents run in parallel
    workflow.add_edge("architect", "frontend")
    workflow.add_edge("architect", "backend")
    workflow.add_edge("architect", "docker_agent")
    workflow.add_edge("architect", "tests_agent")
    
    # All 4 agents route to sandbox (they all update state independently)
    # The sandbox waits for all 4 to complete before running
    workflow.add_edge("frontend", "sandbox")
    workflow.add_edge("backend", "sandbox")
    workflow.add_edge("docker_agent", "sandbox")
    workflow.add_edge("tests_agent", "sandbox")
    
    # Sandbox result flows to human review
    workflow.add_edge("sandbox", "human")
    
    # Human feedback flows to reflector for analysis
    workflow.add_edge("human", "reflector")
    
    # Reflector routes to agents that need fixing or ends
    workflow.add_conditional_edges(
        "reflector",
        route_after_reflection,
        {
            "frontend": "frontend",
            "backend": "backend",
            "docker_agent": "docker_agent",
            "tests_agent": "tests_agent",
            "end_node": END
        }
    )
    
    # 3. Compile with Persistence and Interrupt
    # We pause before the human node to let user review sandbox results
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory, interrupt_before=["human"])