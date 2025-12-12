import os
from pathlib import Path

def create_clean_structure():
    # Root project directory
    root_dir = "code_gen_agent"
    
    # List of directories to create
    directories = [
        f"{root_dir}/src",
        f"{root_dir}/src/core",
        f"{root_dir}/src/agents",
        f"{root_dir}/src/prompts",
        f"{root_dir}/src/utils",
        f"{root_dir}/tests",
        f"{root_dir}/output",  # For generated code
    ]

    # List of files to create (initially empty)
    files = [
        # Configuration
        f"{root_dir}/.env",
        f"{root_dir}/requirements.txt",
        f"{root_dir}/README.md",
        
        # Root Source
        f"{root_dir}/src/__init__.py",
        f"{root_dir}/src/main.py",
        
        # Core Module
        f"{root_dir}/src/core/__init__.py",
        f"{root_dir}/src/core/state.py",
        f"{root_dir}/src/core/graph.py",

        # Agents Module
        f"{root_dir}/src/agents/__init__.py",
        f"{root_dir}/src/agents/architect.py",
        f"{root_dir}/src/agents/frontend.py",
        f"{root_dir}/src/agents/backend.py",
        f"{root_dir}/src/agents/reflector.py",
        f"{root_dir}/src/agents/router.py",

        # Prompts Module
        f"{root_dir}/src/prompts/__init__.py",
        f"{root_dir}/src/prompts/system_prompts.py",
        f"{root_dir}/src/prompts/fix_templates.py",

        # Utils Module
        f"{root_dir}/src/utils/__init__.py",
        f"{root_dir}/src/utils/io_utils.py",
        f"{root_dir}/src/utils/llm_helper.py",
        
        # Tests
        f"{root_dir}/tests/__init__.py",
        f"{root_dir}/tests/test_graph.py",
    ]

    print(f"Creating project structure for '{root_dir}'...")

    # 1. Create Directories
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"[DIR]  Created folder: {directory}")

    # 2. Create Empty Files
    for file_path in files:
        path = Path(file_path)
        if not path.exists():
            # Create an empty file
            path.touch()
            print(f"[FILE] Created file:   {file_path}")
        else:
            print(f"[SKIP] File exists:    {file_path}")

    print("\n[DONE] Structure created successfully.")
    print(f"To start, open VS Code:  code {root_dir}")

if __name__ == "__main__":
    create_clean_structure()