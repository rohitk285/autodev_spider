from langgraph.graph import StateGraph
from pydantic import BaseModel
from groq import Groq


class MasterState(BaseModel):
    user_story: str
    frontend_prompt: str | None = None
    backend_prompt: str | None = None
    database_prompt: str | None = None


def master_agent_node(state: MasterState):

    hardcoded_user_story = (
        "Build a simple TODO web application: React frontend with task list, "
        "add/edit/delete tasks, user authentication (signup/login), "
        "FastAPI backend with REST endpoints, and PostgreSQL database "
        "for persistent storage. Include validation and basic error handling."
    )
    state.user_story = hardcoded_user_story

    system_prompt = """
    Convert this user story into three highly detailed prompts for frontend,
    backend and database agents.
    Output valid JSON with keys:
    - frontend_prompt
    - backend_prompt
    - database_prompt

    DO NOT generate code. Only produce text prompts.
    STRICTLY output only valid JSON. Make no mistakes. 
    """

    client = Groq(api_key="YOUR_API_KEY")

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User story:\n{state.user_story}"}
        ]
    )

    text = response.choices[0].message.content

    import json
    parsed = json.loads(text)

    state.frontend_prompt = parsed["frontend_prompt"]
    state.backend_prompt = parsed["backend_prompt"]
    state.database_prompt = parsed["database_prompt"]

    return state


def build_master_graph():
    graph = StateGraph(MasterState)
    graph.add_node("master", master_agent_node)
    graph.set_entry_point("master")
    return graph.compile()


def main():
    master_graph = build_master_graph()

    initial_state = {
        "user_story": "",
        "frontend_prompt": None,
        "backend_prompt": None,
        "database_prompt": None
    }

    final_state = master_graph.invoke(initial_state)

    import json
    output = {
        "frontend_prompt": final_state.get("frontend_prompt"),
        "backend_prompt": final_state.get("backend_prompt"),
        "database_prompt": final_state.get("database_prompt"),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
