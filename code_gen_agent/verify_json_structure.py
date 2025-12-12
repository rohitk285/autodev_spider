#!/usr/bin/env python3
"""
Verification script to validate JSON output structure from agents
"""

import json
import os
from pathlib import Path

def check_json_structure(file_path, expected_keys_pattern=None):
    """
    Load and validate JSON structure
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n✓ Valid JSON: {file_path}")
        print(f"  Type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"  Keys ({len(data)}): {list(data.keys())[:5]}...")
            
            # Check if values are strings
            all_strings = all(isinstance(v, str) for v in data.values())
            if all_strings:
                print(f"  ✓ All values are strings (file contents)")
            else:
                print(f"  ✗ Some values are NOT strings")
                for k, v in data.items():
                    if not isinstance(v, str):
                        print(f"    - {k}: {type(v)}")
        
        return True
    except json.JSONDecodeError as e:
        print(f"\n✗ Invalid JSON: {file_path}")
        print(f"  Error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Error reading {file_path}: {e}")
        return False

def validate_agent_output(agent_dict, agent_name):
    """
    Validate agent output structure
    """
    print(f"\n{'='*60}")
    print(f"Validating {agent_name} Output")
    print(f"{'='*60}")
    
    if not isinstance(agent_dict, dict):
        print(f"✗ Output is not a dict, it's {type(agent_dict)}")
        return False
    
    print(f"✓ Output is a dict with {len(agent_dict)} files")
    
    # Check file paths
    valid_prefixes = {
        'frontend': 'frontend/',
        'backend': 'backend/',
        'docker': ['docker-compose.yml', '.env'],
        'tests': 'tests/'
    }
    
    if agent_name in valid_prefixes:
        prefix = valid_prefixes[agent_name]
        if isinstance(prefix, list):
            # Docker files
            for key in agent_dict.keys():
                if key not in prefix:
                    print(f"  ⚠ Unexpected file: {key}")
        else:
            for key in agent_dict.keys():
                if not key.startswith(prefix):
                    print(f"  ⚠ File doesn't start with '{prefix}': {key}")
    
    # Check content is string
    for key, value in agent_dict.items():
        if not isinstance(value, str):
            print(f"  ✗ File content is not string: {key} ({type(value)})")
            return False
    
    print(f"✓ All files have string content")
    return True

def main():
    print("JSON Structure Verification Tool")
    print("="*60)
    
    docker_dir = Path("../docker")
    
    # Check existing JSON files
    for json_file in docker_dir.glob("*.json"):
        check_json_structure(json_file)

if __name__ == "__main__":
    main()
