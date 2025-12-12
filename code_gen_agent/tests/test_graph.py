import os
import pytest

#if os.getenv("GOOGLE_API_KEY") is None:
# 	 Skip LLM tests when no key is available (e.g., in CI).
# 	pytest.skip("Skipping LLM integration tests - GOOGLE_API_KEY not set", allow_module_level=True)

from code_gen_agent.src.utils.llm_helper import invoke_llm_json

result = invoke_llm_json("", "how are you?")
print(result)