#!/usr/bin/env python3
"""Debug script to test the Python MCP server functionality."""

import asyncio
import json
import sys
from pathlib import Path

# Add src to Python path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calculator_mcp_python.server import CalculatorMcpServer, AddNumbersInput


async def test_server_functionality():
    """Test the server functionality without stdio transport."""
    print("Testing Calculator MCP Python Server...")
    
    # Initialize server
    server = CalculatorMcpServer()
    print("✓ Server initialized successfully")
    
    # Load test cases
    test_data_path = Path(__file__).parent.parent / "test_data" / "python_test_cases.json"
    with open(test_data_path, 'r') as f:
        test_cases = json.load(f)
    
    # Test valid additions
    print("\n--- Testing Valid Additions ---")
    for test_case in test_cases["valid_additions"]:
        try:
            input_data = AddNumbersInput(**test_case["input"])
            tool_func = server.server._tools["addNumbers"].func
            result = await tool_func(input_data)
            
            content = result.content[0]["text"]
            response_data = json.loads(content)
            
            actual_result = response_data["result"]
            expected_result = test_case["expected_result"]
            
            # Handle floating point precision
            if abs(actual_result - expected_result) < 1e-10:
                print(f"✓ {test_case['description']}: {actual_result}")
            else:
                print(f"✗ {test_case['description']}: Expected {expected_result}, got {actual_result}")
                
        except Exception as e:
            print(f"✗ {test_case['description']}: Exception - {e}")
    
    # Test edge cases
    print("\n--- Testing Edge Cases ---")
    for test_case in test_cases["edge_cases"]:
        try:
            input_data = AddNumbersInput(**test_case["input"])
            tool_func = server.server._tools["addNumbers"].func
            result = await tool_func(input_data)
            
            content = result.content[0]["text"]
            response_data = json.loads(content)
            
            actual_result = response_data["result"]
            expected_result = test_case["expected_result"]
            
            if abs(actual_result - expected_result) < 1e-10:
                print(f"✓ {test_case['description']}: {actual_result}")
            else:
                print(f"✗ {test_case['description']}: Expected {expected_result}, got {actual_result}")
                
        except Exception as e:
            print(f"✗ {test_case['description']}: Exception - {e}")
    
    # Test error cases (manually since test data contains string representations)
    print("\n--- Testing Error Cases ---")
    
    error_test_cases = [
        {"description": "Infinity value", "input": {"num1": float('inf'), "num2": 5.5}},
        {"description": "Negative infinity", "input": {"num1": float('-inf'), "num2": 5.5}},
        {"description": "NaN value", "input": {"num1": float('nan'), "num2": 5.5}},
    ]
    
    for test_case in error_test_cases:
        try:
            input_data = AddNumbersInput(**test_case["input"])
            tool_func = server.server._tools["addNumbers"].func
            result = await tool_func(input_data)
            
            if result.isError:
                content = result.content[0]["text"]
                response_data = json.loads(content)
                print(f"✓ {test_case['description']}: Error correctly handled - {response_data['details']}")
            else:
                print(f"✗ {test_case['description']}: Expected error but got success")
                
        except Exception as e:
            print(f"✗ {test_case['description']}: Unexpected exception - {e}")
    
    print("\n--- Server Testing Complete ---")


if __name__ == "__main__":
    asyncio.run(test_server_functionality())