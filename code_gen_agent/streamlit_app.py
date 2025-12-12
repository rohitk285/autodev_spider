import streamlit as st
import json
import os
from dotenv import load_dotenv
from src.core.graph import create_graph
from src.core.state import GraphState
from langchain_core.messages import HumanMessage
from typing import Any, Dict, cast
from langchain_core.runnables import RunnableConfig

# Load Env
load_dotenv()

st.set_page_config(page_title="AutoDev Agent", layout="wide")
st.title("🤖 AutoDev: AI Software Architect with Sandbox")

# --- Session State Management ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "demo_thread_1"
if "graph" not in st.session_state:
    st.session_state.graph = create_graph()
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar: Project Controls ---
with st.sidebar:
    st.header("Project Configuration")
    user_story = st.text_area("User Story", "Build a simple To-Do List app with a REST API backend and React frontend.")
    start_btn = st.button("🚀 Start New Project")
    
    if start_btn:
        st.session_state.messages = []
        # Initial Run
        config: RunnableConfig = {"configurable": {"thread_id": st.session_state.thread_id}}
        initial_state: GraphState = {
            "user_story": user_story,
            "iteration_count": 0,
            "messages": [],
            "api_spec": "",
            "architecture_plan": "",
            "frontend_files": {},
            "backend_files": {},
            "docker_files": {},
            "tests_files": {},
            "infra_files": {},
            "sandbox_logs": {},
            "human_feedback": "",
            "structured_errors": []
        }
        
        with st.spinner("Architecting, Coding & Running Sandbox..."):
            # Run until the interrupt (Human Node)
            for event in st.session_state.graph.stream(initial_state, config=config):
                pass 
            st.rerun()

# --- Main Logic: Retrieve Current State ---
config: RunnableConfig = {"configurable": {"thread_id": st.session_state.thread_id}}
# Get the current snapshot of the graph (paused state)
snapshot = st.session_state.graph.get_state(config)

if snapshot.values:
    state = snapshot.values
    
    # 1. Display Architecture Plan
    if "api_spec" in state and state["api_spec"]:
        with st.expander("📄 Architecture Plan & API Spec", expanded=False):
            try:
                st.json(json.loads(state["api_spec"]))
                st.markdown(state.get("architecture_plan", ""))
            except:
                st.text(state.get("api_spec", "N/A"))

    # 2. Code Review Tabs
    st.subheader("💻 Generated Codebase")
    tab1, tab2, tab3, tab4 = st.tabs(["Frontend", "Backend", "Docker", "Tests"])
    
    with tab1:
        files = state.get("frontend_files", {})
        if files:
            for fname, code in files.items():
                st.markdown(f"**`{fname}`**")
                st.code(code, language="javascript")
        else:
            st.info("Frontend code not generated yet.")

    with tab2:
        files = state.get("backend_files", {})
        if files:
            for fname, code in files.items():
                st.markdown(f"**`{fname}`**")
                st.code(code, language="python")
        else:
            st.info("Backend code not generated yet.")
    
    with tab3:
        files = state.get("docker_files", {})
        if files:
            for fname, code in files.items():
                st.markdown(f"**`{fname}`**")
                st.code(code, language="yaml")
        else:
            st.info("Docker config not generated yet.")
    
    with tab4:
        files = state.get("tests_files", {})
        if files:
            for fname, code in files.items():
                st.markdown(f"**`{fname}`**")
                st.code(code, language="json")
        else:
            st.info("Tests config not generated yet.")

    # 3. Sandbox Execution Results
    st.divider()
    st.subheader("🏃 Sandbox Execution Results")
    
    sandbox_logs = state.get("sandbox_logs", {})
    if sandbox_logs:
        col1, col2, col3 = st.columns(3)
        with col1:
            status = sandbox_logs.get("status", "unknown")
            st.metric("Status", status)
        with col2:
            url = sandbox_logs.get("frontend_url", "N/A")
            st.metric("Frontend URL", url)
        with col3:
            logs_file = sandbox_logs.get("logs_file", "N/A")
            st.metric("Logs File", os.path.basename(logs_file) if logs_file else "N/A")
        
        # Display container logs
        st.markdown("### Container Logs")
        container_logs = sandbox_logs.get("container_logs", {})
        if container_logs:
            log_tabs = st.tabs([f"[{service}]" for service in container_logs.keys()])
            for tab, (service, log_content) in zip(log_tabs, container_logs.items()):
                with tab:
                    st.code(log_content if isinstance(log_content, str) else json.dumps(log_content, indent=2), language="bash")
        else:
            st.info("No container logs available yet.")
    else:
        st.info("Sandbox has not been executed yet.")

    # 4. Human Feedback Loop
    st.divider()
    st.subheader("📝 Review & Iterate")
    st.markdown("**Is the output working correctly? Provide feedback:**")
    
    col1, col2 = st.columns([3, 1])
    feedback = None
    full_feedback = None
    
    with col1:
        feedback_options = [
            "success",
            "error: [describe issue]",
            "modify: [request change]",
            "skip"
        ]
        feedback = st.selectbox(
            "Feedback Type",
            feedback_options,
            help="Choose how to proceed"
        )
        
        if feedback.startswith(("error:", "modify:")):
            extra_info = st.text_input(
                "Provide details:",
                placeholder="Describe the issue or modification needed..."
            )
            full_feedback = f"{feedback.split(':')[0]}: {extra_info}" if extra_info else feedback
        else:
            full_feedback = feedback
    
    with col2:
        submit_feedback = st.button("Submit & Iterate", key="submit_feedback")

    if submit_feedback:
        if full_feedback:
            with st.spinner("Analyzing feedback and regenerating..."):
                # Update the state with feedback
                st.session_state.graph.update_state(
                    config, 
                    {"human_feedback": full_feedback},
                    as_node="human"
                )
                
                # Continue execution
                for event in st.session_state.graph.stream(None, config=config):
                    pass
                
                st.rerun()
        else:
            st.warning("Please provide feedback.")

else:
    st.info("👈 Enter a User Story in the sidebar and click Start to begin.")