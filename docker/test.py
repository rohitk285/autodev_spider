from sandbox import run_sandbox
import json
import os

# Get the directory where this script is located
current_dir = os.path.dirname(os.path.abspath(__file__))

frontend_json = json.load(open(os.path.join(current_dir, "frontend.json")))
backend_json = json.load(open(os.path.join(current_dir, "backend.json")))
tests_json = json.load(open(os.path.join(current_dir, "tests.json")))
docker_json = json.load(open(os.path.join(current_dir, "docker-compose.json")))

result=run_sandbox(frontend_json, backend_json, tests_json, docker_json)
print("Logs saved to:", result)