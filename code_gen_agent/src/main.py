from dotenv import load_dotenv
from src.core.graph import create_graph
from src.core.state import GraphState
from langchain_core.runnables import RunnableConfig

# Load API keys
load_dotenv()

if __name__ == "__main__":
    print("🚀 AutoDev Agent Starting...")
    
    app = create_graph()
    
    user_input = input("Enter your User Story: ")
    
    initial_state: GraphState = {
        "user_story": user_input,
        "iteration_count": 0,
        "messages": [],
        "api_spec": "",
        "architecture_plan": "",
        "frontend_files": {},
        "backend_files": {},
        "infra_files": {},
        "human_feedback": "",
        "structured_errors": []
    }
    
    # Run the graph
    app.invoke(initial_state)
    
    print("✅ Process Finished.")