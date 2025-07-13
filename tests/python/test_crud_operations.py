"""Tests for CRUD operations in the Calculator MCP Python server."""

import json
import os
import pytest
from unittest.mock import Mock, patch
import requests

from calculator_mcp_python.server import createResource, readResource, updateResource, deleteResource


class TestCreateResource:
    """Test cases for createResource tool."""
    
    @patch('calculator_mcp_python.server.requests.post')
    @patch.dict(os.environ, {'REST_API_BASE_URL': 'https://api.example.com'})
    def test_create_resource_success(self, mock_post):
        """Test successful resource creation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "123", "name": "test", "created": True}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Test data
        resource_type = "users"
        data = {"name": "John Doe", "email": "john@example.com"}
        
        # Call the function
        result = createResource(resource_type, data)
        response_data = json.loads(result)
        
        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            'https://api.example.com/users',
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        # Verify the response
        assert response_data["operation"] == "create"
        assert response_data["resource_type"] == "users"
        assert response_data["status_code"] == 201
        assert response_data["url"] == "https://api.example.com/users"
        assert response_data["data"]["id"] == "123"
        assert "Successfully created" in response_data["message"]
    
    @patch.dict(os.environ, {}, clear=True)
    def test_create_resource_no_env_var(self):
        """Test error when REST_API_BASE_URL is not set."""
        result = createResource("users", {"name": "test"})
        response_data = json.loads(result)
        
        assert "error" in response_data
        assert "REST_API_BASE_URL environment variable is not set" in response_data["details"]
    
    @patch.dict(os.environ, {'REST_API_BASE_URL': 'https://api.example.com'})
    def test_create_resource_invalid_resource_type(self):
        """Test error with invalid resource_type."""
        result = createResource("", {"name": "test"})
        response_data = json.loads(result)
        
        assert "error" in response_data
        assert "resource_type must be a non-empty string" in response_data["details"]
    
    @patch.dict(os.environ, {'REST_API_BASE_URL': 'https://api.example.com'})
    def test_create_resource_invalid_data(self):
        """Test error with invalid data type."""
        result = createResource("users", "invalid_data")
        response_data = json.loads(result)
        
        assert "error" in response_data
        assert "data must be a dictionary" in response_data["details"]
    
    @patch('calculator_mcp_python.server.requests.post')
    @patch.dict(os.environ, {'REST_API_BASE_URL': 'https://api.example.com'})
    def test_create_resource_http_error(self, mock_post):
        """Test HTTP error handling."""
        # Mock HTTP error
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")
        
        result = createResource("users", {"name": "test"})
        response_data = json.loads(result)
        
        assert "error" in response_data
        assert "HTTP request failed" in response_data["details"]
        assert "Connection error" in response_data["details"]


class TestReadResource:
    """Test cases for readResource tool."""
    
    @patch('calculator_mcp_python.server.requests.get')
    @patch.dict(os.environ, {'REST_API_BASE_URL': 'https://api.example.com'})
    def test_read_resource_success_with_id(self, mock_get):
        """Test successful resource read with specific ID."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123", "name": "John Doe"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the function
        result = readResource("users", "123")
        response_data = json.loads(result)
        
        # Verify the request was made correctly
        mock_get.assert_called_once_with('https://api.example.com/users/123', timeout=30)
        
        # Verify the response
        assert response_data["operation"] == "read"
        assert response_data["resource_type"] == "users"
        assert response_data["resource_id"] == "123"
        assert response_data["status_code"] == 200
        assert response_data["data"]["id"] == "123"
        assert "with ID 123" in response_data["message"]
    
    @patch('calculator_mcp_python.server.requests.get')
    @patch.dict(os.environ, {'REST_API_BASE_URL': 'https://api.example.com'})
    def test_read_resource_success_without_id(self, mock_get):
        """Test successful resource read without specific ID (list all)."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "123", "name": "John"}, {"id": "456", "name": "Jane"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the function
        result = readResource("users")
        response_data = json.loads(result)
        
        # Verify the request was made correctly
        mock_get.assert_called_once_with('https://api.example.com/users', timeout=30)
        
        # Verify the response
        assert response_data["operation"] == "read"
        assert response_data["resource_type"] == "users"
        assert response_data["resource_id"] is None
        assert response_data["status_code"] == 200
        assert len(response_data["data"]) == 2
        assert "resources" in response_data["message"]
    
    @patch.dict(os.environ, {'REST_API_BASE_URL': 'https://api.example.com'})
    def test_read_resource_invalid_resource_id(self):
        """Test error with invalid resource_id."""
        result = readResource("users", "")
        response_data = json.loads(result)
        
        assert "error" in response_data
        assert "resource_id must be a non-empty string or None" in response_data["details"]


class TestUpdateResource:
    """Test cases for updateResource tool."""
    
    @patch('calculator_mcp_python.server.requests.put')
    @patch.dict(os.environ, {'REST_API_BASE_URL': 'https://api.example.com'})
    def test_update_resource_success(self, mock_put):
        """Test successful resource update."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123", "name": "Jane Doe", "updated": True}
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response
        
        # Test data
        resource_type = "users"
        resource_id = "123"
        data = {"name": "Jane Doe", "email": "jane@example.com"}
        
        # Call the function
        result = updateResource(resource_type, resource_id, data)
        response_data = json.loads(result)
        
        # Verify the request was made correctly
        mock_put.assert_called_once_with(
            'https://api.example.com/users/123',
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        # Verify the response
        assert response_data["operation"] == "update"
        assert response_data["resource_type"] == "users"
        assert response_data["resource_id"] == "123"
        assert response_data["status_code"] == 200
        assert response_data["data"]["updated"] is True
        assert "Successfully updated" in response_data["message"]
    
    @patch.dict(os.environ, {'REST_API_BASE_URL': 'https://api.example.com'})
    def test_update_resource_invalid_resource_id(self):
        """Test error with invalid resource_id."""
        result = updateResource("users", "", {"name": "test"})
        response_data = json.loads(result)
        
        assert "error" in response_data
        assert "resource_id must be a non-empty string" in response_data["details"]


class TestDeleteResource:
    """Test cases for deleteResource tool."""
    
    @patch('calculator_mcp_python.server.requests.delete')
    @patch.dict(os.environ, {'REST_API_BASE_URL': 'https://api.example.com'})
    def test_delete_resource_success(self, mock_delete):
        """Test successful resource deletion."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.text = ""
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response
        
        # Call the function
        result = deleteResource("users", "123")
        response_data = json.loads(result)
        
        # Verify the request was made correctly
        mock_delete.assert_called_once_with('https://api.example.com/users/123', timeout=30)
        
        # Verify the response
        assert response_data["operation"] == "delete"
        assert response_data["resource_type"] == "users"
        assert response_data["resource_id"] == "123"
        assert response_data["status_code"] == 204
        assert response_data["data"] == {}
        assert "Successfully deleted" in response_data["message"]
    
    @patch('calculator_mcp_python.server.requests.delete')
    @patch.dict(os.environ, {'REST_API_BASE_URL': 'https://api.example.com'})
    def test_delete_resource_with_response_body(self, mock_delete):
        """Test resource deletion with response body."""
        # Mock successful response with body
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"deleted": true, "id": "123"}'
        mock_response.json.return_value = {"deleted": True, "id": "123"}
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response
        
        # Call the function
        result = deleteResource("users", "123")
        response_data = json.loads(result)
        
        # Verify the response
        assert response_data["operation"] == "delete"
        assert response_data["data"]["deleted"] is True
        assert response_data["data"]["id"] == "123"
    
    @patch.dict(os.environ, {'REST_API_BASE_URL': 'https://api.example.com'})
    def test_delete_resource_invalid_resource_id(self):
        """Test error with invalid resource_id."""
        result = deleteResource("users", "")
        response_data = json.loads(result)
        
        assert "error" in response_data
        assert "resource_id must be a non-empty string" in response_data["details"]


class TestEnvironmentHandling:
    """Test cases for environment variable handling across all CRUD operations."""
    
    @patch.dict(os.environ, {'REST_API_BASE_URL': 'https://api.example.com/'})
    @patch('calculator_mcp_python.server.requests.post')
    def test_base_url_trailing_slash_handling(self, mock_post):
        """Test that trailing slashes in base URL are handled correctly."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "123"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        createResource("users", {"name": "test"})
        
        # Verify the URL doesn't have double slashes
        mock_post.assert_called_once_with(
            'https://api.example.com/users',
            json={"name": "test"},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )


class TestErrorHandling:
    """Test cases for comprehensive error handling."""
    
    @patch('calculator_mcp_python.server.requests.post')
    @patch.dict(os.environ, {'REST_API_BASE_URL': 'https://api.example.com'})
    def test_json_decode_error(self, mock_post):
        """Test handling of invalid JSON responses."""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = "Invalid JSON response"
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = createResource("users", {"name": "test"})
        response_data = json.loads(result)
        
        # Should handle JSON decode error gracefully
        assert response_data["operation"] == "create"
        assert response_data["data"]["raw_response"] == "Invalid JSON response"
    
    @patch('calculator_mcp_python.server.requests.get')
    @patch.dict(os.environ, {'REST_API_BASE_URL': 'https://api.example.com'})
    def test_timeout_error(self, mock_get):
        """Test handling of timeout errors."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        result = readResource("users", "123")
        response_data = json.loads(result)
        
        assert "error" in response_data
        assert "HTTP request failed" in response_data["details"]
        assert "Request timed out" in response_data["details"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])