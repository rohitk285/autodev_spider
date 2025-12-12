import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
api_key = os.getenv("GOOGLE_API_KEY")

# --- Imports & Initialization ---
llm = None
ChatPromptTemplate = None

try:
    # UPDATED: Use the correct modern package for Google Gemini
    # pip install langchain-google-genai langchain-core
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.prompts import ChatPromptTemplate
    
    if api_key:
        # Initialize the model with a standard version tag
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0
        )
except ImportError:
    print("⚠️ Warning: 'langchain_google_genai' or 'langchain_core' not found.")
    print("   Please run: pip install langchain-google-genai langchain-core")


def print_message_event(role: str, content, label: str = ""):
    """
    Pretty-print a message event to the console.
    
    Args:
        role: "user", "system", "ai", or custom role name
        content: The message content (can be str, list, or dict)
        label: Optional label for the message (e.g., which agent/node)
    """
    role_emoji = {
        "user": "👤",
        "system": "⚙️",
        "ai": "🤖",
        "human": "👨‍💼",
        "architect": "🏗️",
        "frontend": "🎨",
        "backend": "⚙️",
        "reflector": "🔍"
    }
    
    # Convert content to string if it's not already
    if isinstance(content, (list, dict)):
        content_str = str(content)
    else:
        content_str = str(content)
    
    emoji = role_emoji.get(role, "📝")
    label_str = f" [{label}]" if label else ""
    content_preview = content_str[:150] + "..." if len(content_str) > 150 else content_str
    
    print(f"\n{emoji} {role.upper()}{label_str}:")
    print(f"   {content_preview}\n")


def invoke_llm_json(system_prompt: str, user_prompt: str) -> dict:
    """
    Helper to invoke Gemini and parse JSON output.
    Logs all messages for debugging.
    """
    if llm is None or ChatPromptTemplate is None:
        raise RuntimeError(
            "Gemini LLM is not configured.\n"
            "1. Install packages: pip install langchain-google-genai langchain-core\n"
            "2. Set GOOGLE_API_KEY in your .env file."
        )

    # Print the messages being sent to the LLM
    print_message_event("system", system_prompt, "system_prompt")
    print_message_event("user", user_prompt, "user_prompt")

    # 1. Define the Template with variables
    # We use {sys} and {usr} placeholders to prevent LangChain from crashing 
    # if your actual prompt text contains curly braces (common in code).
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{sys}"),
        ("user", "{usr}")
    ])

    # 2. Create Chain
    chain = prompt | llm

    content = ""  # Initialize here to avoid unbound reference in exception handler
    
    try:
        # 3. Invoke with specific inputs
        response = chain.invoke({
            "sys": system_prompt, 
            "usr": user_prompt
        })

        # Handle response.content which may be a string or list
        if isinstance(response.content, list):
            # If it's a list, join the items (common in some LLM responses)
            content = "".join(str(item) for item in response.content).strip()
        else:
            # Otherwise treat it as a string
            content = str(response.content).strip()

        # Print AI response
        print_message_event("ai", content, "ai_response")

        # 4. robust JSON Cleanup
        # Remove Markdown fences if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        # Fallback: finding the first '{' or '[' if the LLM was chatty
        if not (content.startswith("{") or content.startswith("[")):
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end != -1:
                content = content[start:end]
            else:
                # Try list format
                start = content.find("[")
                end = content.rfind("]") + 1
                if start != -1 and end != -1:
                    content = content[start:end]

        return json.loads(content)

    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")
        print(f"   Raw Content: {content[:200] if content else 'Unknown'}...")  # Print first 200 chars for debug
        return {}
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        return {}