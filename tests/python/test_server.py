"""Tests for the Calculator MCP Python server."""

import json
import math
import pytest
from unittest.mock import AsyncMock, patch

from calculator_mcp_python.server import CalculatorMcpServer, AddNumbersInput


class TestAddNumbersInput:
    """Test cases for AddNumbersInput validation."""
    
    def test_valid_inputs(self):
        """Test valid number inputs."""
        # Test positive numbers
        input_data = AddNumbersInput(num1=5.5, num2=3.2)
        assert input_data.num1 == 5.5
        assert input_data.num2 == 3.2
        
        # Test negative numbers
        input_data = AddNumbersInput(num1=-5.5, num2=-3.2)
        assert input_data.num1 == -5.5
        assert input_data.num2 == -3.2
        
        # Test zero
        input_data = AddNumbersInput(num1=0, num2=0)
        assert input_data.num1 == 0
        assert input_data.num2 == 0
        
        # Test integers
        input_data = AddNumbersInput(num1=10, num2=20)
        assert input_data.num1 == 10
        assert input_data.num2 == 20
    
    def test_invalid_inputs(self):
        """Test invalid inputs."""
        # Test missing required fields
        with pytest.raises(Exception):
            AddNumbersInput()
        
        with pytest.raises(Exception):
            AddNumbersInput(num1=5)
        
        with pytest.raises(Exception):
            AddNumbersInput(num2=5)


class TestCalculatorMcpServer:
    """Test cases for the Calculator MCP Server."""
    
    @pytest.fixture
    def server(self):
        """Create a server instance for testing."""
        return CalculatorMcpServer()
    
    @pytest.mark.asyncio
    async def test_server_initialization(self, server):
        """Test server initialization."""
        assert server.server is not None
        assert server.server.name == "calculator-mcp-python-server"
        assert server.server.version == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_add_numbers_positive(self, server):
        """Test adding positive numbers."""
        input_data = AddNumbersInput(num1=5.5, num2=3.2)
        
        # Get the tool function
        tool_func = server.server._tools["addNumbers"].func
        result = await tool_func(input_data)
        
        # Parse the result
        content = result.content[0]["text"]
        response_data = json.loads(content)
        
        assert response_data["operation"] == "addition"
        assert response_data["operands"] == [5.5, 3.2]
        assert response_data["result"] == 8.7
        assert "5.5" in response_data["message"]
        assert "3.2" in response_data["message"]
        assert "8.7" in response_data["message"]
    
    @pytest.mark.asyncio
    async def test_add_numbers_negative(self, server):
        """Test adding negative numbers."""
        input_data = AddNumbersInput(num1=-5.5, num2=-3.2)
        
        tool_func = server.server._tools["addNumbers"].func
        result = await tool_func(input_data)
        
        content = result.content[0]["text"]
        response_data = json.loads(content)
        
        assert response_data["operation"] == "addition"
        assert response_data["operands"] == [-5.5, -3.2]
        assert response_data["result"] == -8.7
    
    @pytest.mark.asyncio
    async def test_add_numbers_zero(self, server):
        """Test adding with zero."""
        input_data = AddNumbersInput(num1=0, num2=5.5)
        
        tool_func = server.server._tools["addNumbers"].func
        result = await tool_func(input_data)
        
        content = result.content[0]["text"]
        response_data = json.loads(content)
        
        assert response_data["operation"] == "addition"
        assert response_data["operands"] == [0, 5.5]
        assert response_data["result"] == 5.5
    
    @pytest.mark.asyncio
    async def test_add_numbers_large_numbers(self, server):
        """Test adding large numbers."""
        input_data = AddNumbersInput(num1=1e15, num2=2e15)
        
        tool_func = server.server._tools["addNumbers"].func
        result = await tool_func(input_data)
        
        content = result.content[0]["text"]
        response_data = json.loads(content)
        
        assert response_data["operation"] == "addition"
        assert response_data["operands"] == [1e15, 2e15]
        assert response_data["result"] == 3e15
    
    @pytest.mark.asyncio
    async def test_add_numbers_infinity_error(self, server):
        """Test error handling with infinity values."""
        input_data = AddNumbersInput(num1=float('inf'), num2=5.5)
        
        tool_func = server.server._tools["addNumbers"].func
        result = await tool_func(input_data)
        
        content = result.content[0]["text"]
        response_data = json.loads(content)
        
        assert "error" in response_data
        assert "Failed to add numbers" in response_data["error"]
        assert "finite numbers" in response_data["details"]
        assert result.isError is True
    
    @pytest.mark.asyncio
    async def test_add_numbers_nan_error(self, server):
        """Test error handling with NaN values."""
        input_data = AddNumbersInput(num1=float('nan'), num2=5.5)
        
        tool_func = server.server._tools["addNumbers"].func
        result = await tool_func(input_data)
        
        content = result.content[0]["text"]
        response_data = json.loads(content)
        
        assert "error" in response_data
        assert "Failed to add numbers" in response_data["error"]
        assert "finite numbers" in response_data["details"]
        assert result.isError is True
    
    @pytest.mark.asyncio
    async def test_exception_handling(self, server):
        """Test general exception handling."""
        # Create a mock input that will cause an exception
        class BadInput:
            def __init__(self):
                self.num1 = None
                self.num2 = None
        
        bad_input = BadInput()
        
        tool_func = server.server._tools["addNumbers"].func
        result = await tool_func(bad_input)
        
        content = result.content[0]["text"]
        response_data = json.loads(content)
        
        assert "error" in response_data
        assert "Failed to add numbers" in response_data["error"]
        assert result.isError is True


class TestIntegration:
    """Integration tests for the full server."""
    
    @pytest.mark.asyncio
    async def test_server_run_mock(self):
        """Test server run method with mocked transport."""
        server = CalculatorMcpServer()
        
        # Mock the serve method to avoid actual stdio connection
        with patch.object(server.server, 'serve', new_callable=AsyncMock) as mock_serve:
            mock_serve.return_value = None
            
            # This should not raise an exception
            await server.run()
            
            # Verify serve was called
            mock_serve.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])