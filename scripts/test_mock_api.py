#!/usr/bin/env python3
"""Test script to verify the mock API server endpoints and response schemas."""

import json
import logging
import sys
import time
import subprocess
import signal
import requests
from typing import Dict, Any, Optional
import threading


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockAPITester:
    """Test class for the mock API server."""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.server_process = None
        
    def start_server(self) -> bool:
        """Start the mock API server in background."""
        try:
            logger.info("Starting mock API server...")
            self.server_process = subprocess.Popen(
                ["python", "-m", "calculator_mcp_python.mock_api_server", "--host", "localhost", "--port", "8001"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd="/root/projects/calculator-mcp"
            )
            
            # Wait for server to start
            max_attempts = 10
            for attempt in range(max_attempts):
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=2)
                    if response.status_code == 200:
                        logger.info(f"Mock API server started successfully on {self.base_url}")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    continue
            
            logger.error("Failed to start mock API server")
            return False
            
        except Exception as error:
            logger.error(f"Error starting server: {error}")
            return False
    
    def stop_server(self):
        """Stop the mock API server."""
        if self.server_process:
            logger.info("Stopping mock API server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Server didn't stop gracefully, forcing termination")
                self.server_process.kill()
            self.server_process = None
    
    def test_health_endpoint(self) -> bool:
        """Test the health check endpoint."""
        try:
            logger.info("Testing health endpoint...")
            response = requests.get(f"{self.base_url}/health")
            
            if response.status_code != 200:
                logger.error(f"Health check failed with status: {response.status_code}")
                return False
            
            data = response.json()
            required_fields = ["status", "service", "timestamp"]
            for field in required_fields:
                if field not in data:
                    logger.error(f"Health response missing field: {field}")
                    return False
            
            if data["status"] != "healthy":
                logger.error(f"Server not healthy: {data['status']}")
                return False
            
            logger.info("✓ Health endpoint test passed")
            return True
            
        except Exception as error:
            logger.error(f"Health endpoint test failed: {error}")
            return False
    
    def test_create_resource(self, resource_type: str = "users") -> Optional[Dict[str, Any]]:
        """Test creating a resource."""
        try:
            logger.info(f"Testing CREATE /{resource_type}...")
            test_data = {
                "name": "Test User",
                "email": "test@example.com",
                "age": 25,
                "department": "QA"
            }
            
            response = requests.post(
                f"{self.base_url}/{resource_type}",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 201:
                logger.error(f"Create request failed with status: {response.status_code}")
                return None
            
            data = response.json()
            
            # Verify response schema matches MCP tool output
            required_fields = ["operation", "resource_type", "status_code", "url", "data", "message"]
            for field in required_fields:
                if field not in data:
                    logger.error(f"Create response missing field: {field}")
                    return None
            
            # Verify field values
            if data["operation"] != "create":
                logger.error(f"Expected operation 'create', got: {data['operation']}")
                return None
            
            if data["resource_type"] != resource_type:
                logger.error(f"Expected resource_type '{resource_type}', got: {data['resource_type']}")
                return None
            
            if data["status_code"] != 201:
                logger.error(f"Expected status_code 201, got: {data['status_code']}")
                return None
            
            if "Successfully created" not in data["message"]:
                logger.error(f"Unexpected message: {data['message']}")
                return None
            
            # Verify created data includes input data
            created_data = data["data"]
            for key, value in test_data.items():
                if created_data.get(key) != value:
                    logger.error(f"Created data missing or incorrect for {key}: expected {value}, got {created_data.get(key)}")
                    return None
            
            logger.info("✓ Create resource test passed")
            return data
            
        except Exception as error:
            logger.error(f"Create resource test failed: {error}")
            return None
    
    def test_read_resources(self, resource_type: str = "users") -> Optional[Dict[str, Any]]:
        """Test reading all resources."""
        try:
            logger.info(f"Testing READ /{resource_type} (list all)...")
            
            response = requests.get(f"{self.base_url}/{resource_type}")
            
            if response.status_code != 200:
                logger.error(f"Read request failed with status: {response.status_code}")
                return None
            
            data = response.json()
            
            # Verify response schema
            required_fields = ["operation", "resource_type", "resource_id", "status_code", "url", "data", "message"]
            for field in required_fields:
                if field not in data:
                    logger.error(f"Read response missing field: {field}")
                    return None
            
            # Verify field values
            if data["operation"] != "read":
                logger.error(f"Expected operation 'read', got: {data['operation']}")
                return None
            
            if data["resource_id"] is not None:
                logger.error(f"Expected resource_id None for list operation, got: {data['resource_id']}")
                return None
            
            if not isinstance(data["data"], list):
                logger.error(f"Expected data to be a list, got: {type(data['data'])}")
                return None
            
            if len(data["data"]) == 0:
                logger.error("Expected non-empty list of resources")
                return None
            
            logger.info(f"✓ Read resources test passed (got {len(data['data'])} items)")
            return data
            
        except Exception as error:
            logger.error(f"Read resources test failed: {error}")
            return None
    
    def test_read_resource_by_id(self, resource_type: str = "users", resource_id: str = "test-123") -> Optional[Dict[str, Any]]:
        """Test reading a specific resource by ID."""
        try:
            logger.info(f"Testing READ /{resource_type}/{resource_id}...")
            
            response = requests.get(f"{self.base_url}/{resource_type}/{resource_id}")
            
            if response.status_code != 200:
                logger.error(f"Read by ID request failed with status: {response.status_code}")
                return None
            
            data = response.json()
            
            # Verify response schema
            required_fields = ["operation", "resource_type", "resource_id", "status_code", "url", "data", "message"]
            for field in required_fields:
                if field not in data:
                    logger.error(f"Read by ID response missing field: {field}")
                    return None
            
            # Verify field values
            if data["resource_id"] != resource_id:
                logger.error(f"Expected resource_id '{resource_id}', got: {data['resource_id']}")
                return None
            
            if not isinstance(data["data"], dict):
                logger.error(f"Expected data to be a dict, got: {type(data['data'])}")
                return None
            
            # Verify the resource has the correct ID
            if data["data"].get("id") != resource_id:
                logger.error(f"Resource data ID mismatch: expected {resource_id}, got {data['data'].get('id')}")
                return None
            
            logger.info("✓ Read resource by ID test passed")
            return data
            
        except Exception as error:
            logger.error(f"Read resource by ID test failed: {error}")
            return None
    
    def test_update_resource(self, resource_type: str = "users", resource_id: str = "test-123") -> Optional[Dict[str, Any]]:
        """Test updating a resource."""
        try:
            logger.info(f"Testing UPDATE /{resource_type}/{resource_id}...")
            
            update_data = {
                "name": "Updated User",
                "email": "updated@example.com",
                "department": "Engineering"
            }
            
            response = requests.put(
                f"{self.base_url}/{resource_type}/{resource_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                logger.error(f"Update request failed with status: {response.status_code}")
                return None
            
            data = response.json()
            
            # Verify response schema
            required_fields = ["operation", "resource_type", "resource_id", "status_code", "url", "data", "message"]
            for field in required_fields:
                if field not in data:
                    logger.error(f"Update response missing field: {field}")
                    return None
            
            # Verify field values
            if data["operation"] != "update":
                logger.error(f"Expected operation 'update', got: {data['operation']}")
                return None
            
            if data["resource_id"] != resource_id:
                logger.error(f"Expected resource_id '{resource_id}', got: {data['resource_id']}")
                return None
            
            # Verify updated data includes input data
            updated_data = data["data"]
            for key, value in update_data.items():
                if updated_data.get(key) != value:
                    logger.error(f"Updated data missing or incorrect for {key}: expected {value}, got {updated_data.get(key)}")
                    return None
            
            logger.info("✓ Update resource test passed")
            return data
            
        except Exception as error:
            logger.error(f"Update resource test failed: {error}")
            return None
    
    def test_delete_resource(self, resource_type: str = "users", resource_id: str = "test-123") -> Optional[Dict[str, Any]]:
        """Test deleting a resource."""
        try:
            logger.info(f"Testing DELETE /{resource_type}/{resource_id}...")
            
            response = requests.delete(f"{self.base_url}/{resource_type}/{resource_id}")
            
            if response.status_code != 200:
                logger.error(f"Delete request failed with status: {response.status_code}")
                return None
            
            data = response.json()
            
            # Verify response schema
            required_fields = ["operation", "resource_type", "resource_id", "status_code", "url", "data", "message"]
            for field in required_fields:
                if field not in data:
                    logger.error(f"Delete response missing field: {field}")
                    return None
            
            # Verify field values
            if data["operation"] != "delete":
                logger.error(f"Expected operation 'delete', got: {data['operation']}")
                return None
            
            if data["resource_id"] != resource_id:
                logger.error(f"Expected resource_id '{resource_id}', got: {data['resource_id']}")
                return None
            
            if data["status_code"] != 200:
                logger.error(f"Expected status_code 200, got: {data['status_code']}")
                return None
            
            # Verify deletion confirmation in data
            if not data["data"].get("deleted"):
                logger.error("Delete response should include 'deleted: true' in data")
                return None
            
            logger.info("✓ Delete resource test passed")
            return data
            
        except Exception as error:
            logger.error(f"Delete resource test failed: {error}")
            return None
    
    def run_all_tests(self) -> bool:
        """Run all API tests."""
        logger.info("Starting comprehensive mock API tests...")
        
        all_passed = True
        
        # Test different resource types
        resource_types = ["users", "products", "orders"]
        
        for resource_type in resource_types:
            logger.info(f"\n--- Testing {resource_type} endpoints ---")
            
            # Test each CRUD operation
            if not self.test_create_resource(resource_type):
                all_passed = False
            
            if not self.test_read_resources(resource_type):
                all_passed = False
            
            if not self.test_read_resource_by_id(resource_type, f"test-{resource_type}-123"):
                all_passed = False
            
            if not self.test_update_resource(resource_type, f"test-{resource_type}-123"):
                all_passed = False
            
            if not self.test_delete_resource(resource_type, f"test-{resource_type}-123"):
                all_passed = False
        
        return all_passed


def main():
    """Main test execution."""
    tester = MockAPITester()
    
    try:
        # Start the server
        if not tester.start_server():
            logger.error("Failed to start mock API server")
            sys.exit(1)
        
        # Test health endpoint first
        if not tester.test_health_endpoint():
            logger.error("Health check failed")
            sys.exit(1)
        
        # Run all CRUD tests
        if tester.run_all_tests():
            logger.info("\n🎉 All mock API tests passed successfully!")
            logger.info("The mock API server is working correctly and responses match MCP tool schemas.")
        else:
            logger.error("\n❌ Some tests failed")
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
    except Exception as error:
        logger.error(f"Test execution failed: {error}")
        sys.exit(1)
    finally:
        # Always stop the server
        tester.stop_server()


if __name__ == "__main__":
    main()