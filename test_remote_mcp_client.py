#!/usr/bin/env python3
"""
Test client for the Calculator MCP Remote Server using standard MCP SDK
"""
import asyncio
import json
import sys
import httpx
from mcp import ClientSession
from mcp.client.sse import SSETransport

async def test_remote_server():
    """Test the remote server running on localhost:8000"""
    print("🔗 Connecting to Calculator MCP Remote Server at http://localhost:8000/sse")
    
    try:
        # Create SSE transport
        transport = SSETransport("http://localhost:8000/sse")
        
        async with ClientSession(transport) as session:
            print("✅ Connected successfully!")
            
            # Initialize the session
            result = await session.initialize()
            print(f"Server info: {result.server_info.name} v{result.server_info.version}")
            
            # List available tools
            print("\n🛠️  Listing available tools...")
            tools_result = await session.list_tools()
            tools = tools_result.tools
            print(f"Available tools: {[tool.name for tool in tools]}")
            
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test the addNumbers tool
            if any(tool.name == "addNumbers" for tool in tools):
                print("\n🧮 Testing addNumbers tool...")
                test_cases = [
                    {"num1": 5, "num2": 3},
                    {"num1": 10.5, "num2": 2.7}, 
                    {"num1": -5, "num2": 10},
                    {"num1": 0, "num2": 0}
                ]
                
                for i, test_case in enumerate(test_cases, 1):
                    print(f"\nTest {i}: Adding {test_case['num1']} + {test_case['num2']}")
                    result = await session.call_tool("addNumbers", arguments=test_case)
                    
                    if result.isError:
                        print(f"❌ Error: {result.content}")
                    else:
                        # Extract the text content from the result
                        content = result.content[0] if result.content else None
                        if content and hasattr(content, 'text'):
                            print(f"✅ Result: {content.text}")
                        else:
                            print(f"✅ Result: {content}")
                            
            print("\n🎉 All tests completed successfully!")
            
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("Make sure the remote server is running on http://localhost:8000")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(test_remote_server())
    sys.exit(exit_code)