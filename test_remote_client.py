#!/usr/bin/env python3
"""
Test client for the Calculator MCP Remote Server
"""
import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastmcp import Client

async def test_remote_server():
    """Test the remote server running on localhost:8000"""
    print("🔗 Connecting to Calculator MCP Remote Server at http://localhost:8000/sse")
    
    try:
        # Connect to the remote server via SSE
        async with Client("http://localhost:8000/sse") as client:
            print("✅ Connected successfully!")
            
            # Test ping
            print("\n📡 Testing ping...")
            await client.ping()
            print("✅ Ping successful!")
            
            # List available tools
            print("\n🛠️  Listing available tools...")
            tools = await client.list_tools()
            print(f"Available tools: {[tool.name for tool in tools]}")
            
            # Test the addNumbers tool
            print("\n🧮 Testing addNumbers tool...")
            test_cases = [
                {"num1": 5, "num2": 3},
                {"num1": 10.5, "num2": 2.7},
                {"num1": -5, "num2": 10},
                {"num1": 0, "num2": 0}
            ]
            
            for i, test_case in enumerate(test_cases, 1):
                print(f"\nTest {i}: Adding {test_case['num1']} + {test_case['num2']}")
                result = await client.call_tool("addNumbers", test_case)
                print(f"Result: {result[0].text}")
            
            print("\n🎉 All tests completed successfully!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(test_remote_server())
    sys.exit(exit_code)