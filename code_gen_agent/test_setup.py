#!/usr/bin/env python3
"""
Quick validation script to check if all imports work correctly
"""
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all new modules can be imported"""
    print("Testing imports...")
    
    try:
        print("  ✓ Importing core.state...")
        from src.core.state import GraphState
        
        print("  ✓ Importing agents...")
        from src.agents.architect import architect_node
        from src.agents.frontend import frontend_node
        from src.agents.backend import backend_node
        from src.agents.docker_agent import docker_agent_node
        from src.agents.tests_agent import tests_agent_node
        from src.agents.sandbox_execution import sandbox_execution_node
        from src.agents.human import human_node
        from src.agents.reflector import reflector_node
        
        print("  ✓ Importing router...")
        from src.agents.router import route_after_reflection
        
        print("  ✓ Importing graph...")
        from src.core.graph import create_graph
        
        print("  ✓ Importing prompts...")
        from src.prompts.system_prompts import (
            ARCHITECT_PROMPT,
            FRONTEND_PROMPT,
            BACKEND_PROMPT,
            DOCKER_PROMPT,
            TESTS_PROMPT,
            REFLECTOR_PROMPT
        )
        
        print("\n✅ All imports successful!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Import error: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_graph_creation():
    """Test that the graph can be created"""
    print("Testing graph creation...")
    
    try:
        from src.core.graph import create_graph
        graph = create_graph()
        print("✅ Graph created successfully!\n")
        return True
    except Exception as e:
        print(f"❌ Graph creation error: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_state_structure():
    """Test that the GraphState has all required fields"""
    print("Testing GraphState structure...")
    
    try:
        from src.core.state import GraphState
        
        required_fields = [
            "messages",
            "user_story",
            "api_spec",
            "architecture_plan",
            "frontend_files",
            "backend_files",
            "docker_files",
            "tests_files",
            "sandbox_logs",
            "human_feedback",
            "structured_errors",
            "iteration_count"
        ]
        
        # Check if we can access the annotations
        annotations = GraphState.__annotations__
        
        for field in required_fields:
            if field not in annotations:
                print(f"  ❌ Missing field: {field}")
                return False
            print(f"  ✓ {field}")
        
        print("✅ All required fields present!\n")
        return True
        
    except Exception as e:
        print(f"❌ State structure error: {e}\n")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    results = [
        test_imports(),
        test_graph_creation(),
        test_state_structure()
    ]
    
    if all(results):
        print("=" * 60)
        print("✅ ALL TESTS PASSED - System is ready to use!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("=" * 60)
        print("❌ SOME TESTS FAILED - Please check errors above")
        print("=" * 60)
        sys.exit(1)
