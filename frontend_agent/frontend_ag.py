import os
import json
from groq import Groq
from pydantic import BaseModel
from langgraph.graph import StateGraph


class FrontendState(BaseModel):
    prompt: str
    codebase_path: str
    file_updates: dict | None = None


def read_codebase(directory: str) -> dict:
    """
    Walk the directory and return:
    {
        "relative/path/file1.jsx": "file content...",
        "relative/path/file2.css": "file content..."...
    }
    """
    file_map = {}

    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)

            rel_path = os.path.relpath(full_path, directory)

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    file_map[rel_path] = f.read()
            except Exception:
                continue

    return file_map


def frontend_agent_node(state: FrontendState):

    codebase_files = read_codebase(state.codebase_path)

    codebase_json = json.dumps(codebase_files, indent=2, ensure_ascii=False)

    system_prompt = """
You are a FRONTEND CODE MODIFICATION AGENT.

You will be given:
1. A frontend requirement prompt.
2. The ENTIRE existing frontend codebase as JSON (file_path → content).

Your job:
- Analyse ALL provided existing code files.
- Decide which files must be updated, created, or replaced.
- Return STRICT JSON ONLY.
- Keep the existing code files as it is and show that in the output. 
- JSON format MUST be:

{
  "relative/path/to/file": "<FULL UPDATED FILE CONTENT>",
  ...
}

Rules:
- DO NOT explain anything.
- DO NOT include comments outside JSON.
- Every value MUST contain the FULL output file content (not patches).
- If a file must change even slightly, return the whole file.
- If a new file is required, include it as a new key.
"""

    client = Groq(api_key="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")

    # USER MESSAGE
    user_message = f"""
Frontend Prompt:
{state.prompt}

Existing Codebase (JSON file listing):
{codebase_json}

Now generate the STRICT JSON file-updates output.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )

    text = response.choices[0].message.content

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("LLM did NOT return valid JSON. Returned:\n" + text)

    state.file_updates = parsed
    return state


def build_frontend_graph():
    graph = StateGraph(FrontendState)
    graph.add_node("frontend_agent", frontend_agent_node)
    graph.set_entry_point("frontend_agent")
    return graph.compile()


def run_frontend_agent(frontend_prompt: str, folder_path: str):
    graph = build_frontend_graph()

    initial_state = {
        "prompt": frontend_prompt,
        "codebase_path": folder_path,
        "file_updates": None
    }

    final_state = graph.invoke(initial_state)
    return final_state["file_updates"]


if __name__ == "__main__":
    prompt = """
        description: Implement a React frontend for the TODO web application
        tasks:
        - Create a list component to display tasks
        - Implement add task functionality with input forms and buttons
        - Implement edit task functionality
        - Implement delete task functionality
        - Create user authentication components (signup/login)
        - Implement validation for task additions and editing
        - Implement basic error handling for user interface
        deliverables:
        - A functional React frontend with task list and user authentication
        - Task addition, editing, and deletion functionality
        - Validated and error-handled user experience
        """
    folder = "../frontend"
    result = run_frontend_agent(prompt, folder)
    output_path = os.path.join(os.getcwd(), "frontend_prompt.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Wrote frontend prompt output to {output_path}")
