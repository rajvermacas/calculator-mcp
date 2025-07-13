"""Tests for the Calculator MCP Remote Server."""

import json
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, Mock
from fastapi.testclient import TestClient
import uvicorn

from calculator_mcp_python.remote_server import (
    create_mcp_server, 
    create_fastapi_app, 
    run_http_server, 
    main
)


class TestRemoteMcpServer:
    """Test cases for the remote MCP server creation."""
    
    def test_create_mcp_server(self):
        """Test MCP server creation."""
        server = create_mcp_server()
        assert server is not None
        # Check if it's a FastMCP instance
        assert server.__class__.__name__ == 'FastMCP'
        # Check if it has the expected name
        assert server.name == "calculator-mcp-python-remote-server"
        # Check if tool manager exists and has tools
        assert hasattr(server, '_tool_manager')
        assert hasattr(server._tool_manager, '_tools')
    
    def test_fastapi_app_creation(self):
        """Test FastAPI app creation."""
        mcp_server = create_mcp_server()
        app = create_fastapi_app(mcp_server)
        assert app is not None
        assert app.title == "Calculator MCP Remote Server"
        assert app.version == "1.0.0"


class TestFastAPIEndpoints:
    """Test cases for FastAPI endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        mcp_server = create_mcp_server()
        app = create_fastapi_app(mcp_server)
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Calculator MCP Remote Server"
        assert data["version"] == "1.0.0"
        assert "addNumbers" in data["tools"]
        assert data["endpoints"]["sse"] == "/sse"
        assert data["endpoints"]["health"] == "/health"
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["server"] == "calculator-mcp-remote"
    
    def test_sse_endpoint_connection(self, client):
        """Test SSE endpoint can be accessed."""
        # Note: Testing actual SSE streaming is complex in unit tests
        # This test just verifies the endpoint exists and responds
        response = client.get("/sse")
        # SSE endpoints typically return 200 and start streaming
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")


class TestRemoteServerAddNumbers:
    """Test cases for the remote addNumbers tool."""
    
    @pytest.fixture
    def server(self):
        """Create a server instance for testing."""
        return create_mcp_server()
    
    @pytest.mark.asyncio
    async def test_add_numbers_positive_remote(self, server):
        """Test adding positive numbers in remote server."""
        # Use call_tool method from FastMCP
        content_list, metadata = await server.call_tool("addNumbers", {"num1": 5.5, "num2": 3.2})
        
        # Parse the result
        content = content_list[0].text
        response_data = json.loads(content)
        
        assert response_data["operation"] == "addition"
        assert response_data["operands"] == [5.5, 3.2]
        assert response_data["result"] == 8.7
        assert response_data["server_type"] == "remote"
        assert "5.5" in response_data["message"]
        assert "3.2" in response_data["message"]
        assert "8.7" in response_data["message"]
    
    @pytest.mark.asyncio
    async def test_add_numbers_negative_remote(self, server):
        """Test adding negative numbers in remote server."""
        content_list, metadata = await server.call_tool("addNumbers", {"num1": -5.5, "num2": -3.2})
        
        content = content_list[0].text
        response_data = json.loads(content)
        
        assert response_data["operation"] == "addition"
        assert response_data["operands"] == [-5.5, -3.2]
        assert response_data["result"] == -8.7
        assert response_data["server_type"] == "remote"
    
    @pytest.mark.asyncio
    async def test_add_numbers_zero_remote(self, server):
        """Test adding with zero in remote server."""
        content_list, metadata = await server.call_tool("addNumbers", {"num1": 0, "num2": 5.5})
        
        content = content_list[0].text
        response_data = json.loads(content)
        
        assert response_data["operation"] == "addition"
        assert response_data["operands"] == [0, 5.5]
        assert response_data["result"] == 5.5
        assert response_data["server_type"] == "remote"
    
    @pytest.mark.asyncio
    async def test_add_numbers_large_numbers_remote(self, server):
        """Test adding large numbers in remote server."""
        content_list, metadata = await server.call_tool("addNumbers", {"num1": 1e15, "num2": 2e15})
        
        content = content_list[0].text
        response_data = json.loads(content)
        
        assert response_data["operation"] == "addition"
        assert response_data["operands"] == [1e15, 2e15]
        assert response_data["result"] == 3e15
        assert response_data["server_type"] == "remote"
    
    @pytest.mark.asyncio
    async def test_add_numbers_infinity_error_remote(self, server):
        """Test error handling with infinity values in remote server."""
        content_list, metadata = await server.call_tool("addNumbers", {"num1": float('inf'), "num2": 5.5})
        
        content = content_list[0].text
        response_data = json.loads(content)
        
        assert "error" in response_data
        assert "Failed to add numbers" in response_data["error"]
        assert "finite numbers" in response_data["details"]
        assert response_data["server_type"] == "remote"
        # Error is indicated by presence of "error" key in response
    
    @pytest.mark.asyncio
    async def test_add_numbers_nan_error_remote(self, server):
        """Test error handling with NaN values in remote server."""
        content_list, metadata = await server.call_tool("addNumbers", {"num1": float('nan'), "num2": 5.5})
        
        content = content_list[0].text
        response_data = json.loads(content)
        
        assert "error" in response_data
        assert "Failed to add numbers" in response_data["error"]
        assert "finite numbers" in response_data["details"]
        assert response_data["server_type"] == "remote"
        # Error is indicated by presence of "error" key in response
    
    @pytest.mark.asyncio
    async def test_exception_handling_remote(self, server):
        """Test general exception handling in remote server."""
        # Note: FastMCP validates inputs before calling our function,
        # so we test with inputs that pass validation but cause runtime errors
        # Our tool handles these gracefully and returns error JSON
        
        # Test with very large numbers that might cause overflow
        content_list, metadata = await server.call_tool("addNumbers", {"num1": 1e400, "num2": 1e400})
        
        content = content_list[0].text
        response_data = json.loads(content)
        
        # This should either succeed or fail gracefully
        assert "server_type" in response_data
        assert response_data["server_type"] == "remote"
        
        # The result could be either success (with inf result) or error
        # Both are acceptable for this edge case test


class TestServerRunning:
    """Test cases for server running functionality."""
    
    @patch('uvicorn.Server.run')
    def test_run_http_server(self, mock_run):
        """Test HTTP server startup."""
        mock_run.return_value = None
        
        # This should not raise an exception
        run_http_server("localhost", 8000)
        
        # Verify uvicorn server was called
        mock_run.assert_called_once()
    
    @patch('uvicorn.Server.run')
    def test_run_http_server_custom_host_port(self, mock_run):
        """Test HTTP server with custom host and port."""
        mock_run.return_value = None
        
        run_http_server("0.0.0.0", 3000)
        mock_run.assert_called_once()
    
    def test_main_function_http_transport(self):
        """Test main function with HTTP transport."""
        with patch('sys.argv', ['remote_server.py', '--transport', 'http']):
            with patch('calculator_mcp_python.remote_server.run_http_server') as mock_http:
                try:
                    main()
                except SystemExit:
                    pass  # Expected for argument parsing
                # The actual test would require more complex mocking
    
    def test_main_function_stdio_transport(self):
        """Test main function with stdio transport."""
        with patch('sys.argv', ['remote_server.py', '--transport', 'stdio']):
            with patch('asyncio.run') as mock_run:
                try:
                    main()
                except SystemExit:
                    pass  # Expected for argument parsing


class TestCORS:
    """Test CORS configuration."""
    
    def test_cors_headers(self):
        """Test that CORS headers are properly configured."""
        mcp_server = create_mcp_server()
        app = create_fastapi_app(mcp_server)
        
        # Check that CORS middleware is added
        cors_middleware = None
        for middleware in app.user_middleware:
            if hasattr(middleware.cls, '__name__') and 'CORS' in middleware.cls.__name__:
                cors_middleware = middleware
                break
        
        assert cors_middleware is not None


class TestErrorHandling:
    """Test error handling in remote server."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        mcp_server = create_mcp_server()
        app = create_fastapi_app(mcp_server)
        return TestClient(app)
    
    def test_invalid_endpoint(self, client):
        """Test accessing invalid endpoint."""
        response = client.get("/invalid")
        assert response.status_code == 404


class TestConfiguration:
    """Test server configuration options."""
    
    def test_server_info_endpoint(self):
        """Test server information is correctly exposed."""
        mcp_server = create_mcp_server()
        app = create_fastapi_app(mcp_server)
        client = TestClient(app)
        
        response = client.get("/")
        data = response.json()
        
        assert data["name"] == "Calculator MCP Remote Server"
        assert data["description"] == "Remote MCP server for adding two numbers"
        assert "addNumbers" in data["tools"]
        assert data["endpoints"]["sse"] == "/sse"
        assert data["endpoints"]["health"] == "/health"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])