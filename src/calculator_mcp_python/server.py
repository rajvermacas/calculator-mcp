#!/usr/bin/env python3
"""Calculator MCP Server - Python implementation for adding two numbers."""

import json
import logging
import math
import os
import sys
from typing import Dict, Any, Optional

import requests
from mcp.server.fastmcp import FastMCP


# Configure logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Create the MCP server instance
mcp = FastMCP("calculator-mcp-python-server")


@mcp.tool()
def addNumbers(num1: float, num2: float) -> str:
    """Add two numbers together and return the result.
    
    Args:
        num1: The first number to add
        num2: The second number to add
        
    Returns:
        JSON string containing the addition result or error information
    """
    try:
        logger.info(f"Tool called: Adding {num1} + {num2}")
        
        # Validate inputs are finite numbers
        if not (
            isinstance(num1, (int, float)) and 
            isinstance(num2, (int, float))
        ):
            raise ValueError("Both inputs must be numbers")
        
        # Check for infinity or NaN
        if (
            math.isinf(num1) or 
            math.isnan(num1) or
            math.isinf(num2) or 
            math.isnan(num2)
        ):
            raise ValueError("Both inputs must be finite numbers")
        
        result = num1 + num2
        logger.info(f"Calculation result: {result}")
        
        response_data = {
            "operation": "addition",
            "operands": [num1, num2],
            "result": result,
            "message": f"The sum of {num1} and {num2} is {result}"
        }
        
        return json.dumps(response_data, indent=2)
        
    except (ValueError, TypeError) as error:
        logger.error(f"Validation error in addNumbers tool: {error}")
        error_data = {
            "error": "Failed to add numbers",
            "details": str(error),
            "operands": [num1, num2]
        }
        return json.dumps(error_data, indent=2)
    except Exception as error:
        logger.error(f"Unexpected error in addNumbers tool: {error}")
        error_data = {
            "error": "Failed to add numbers",
            "details": "Unknown error occurred",
            "operands": [num1, num2]
        }
        return json.dumps(error_data, indent=2)


@mcp.tool()
def createResource(resource_type: str, data: Dict[str, Any]) -> str:
    """Create a new resource via REST API POST request.
    
    Args:
        resource_type: The type/endpoint of the resource to create
        data: The data to send in the POST request body
        
    Returns:
        JSON string containing the created resource details or error information
    """
    try:
        logger.info(f"Tool called: Creating resource of type '{resource_type}' with data: {data}")
        
        # Get base URL from environment variable
        base_url = os.getenv('REST_API_BASE_URL')
        if not base_url:
            raise ValueError("REST_API_BASE_URL environment variable is not set")
        
        # Construct the full URL
        url = f"{base_url.rstrip('/')}/{resource_type}"
        
        # Validate inputs
        if not isinstance(resource_type, str) or not resource_type.strip():
            raise ValueError("resource_type must be a non-empty string")
        
        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")
        
        # Make POST request
        response = requests.post(
            url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse response
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {"raw_response": response.text}
        
        logger.info(f"Resource created successfully. Status: {response.status_code}")
        
        result_data = {
            "operation": "create",
            "resource_type": resource_type,
            "status_code": response.status_code,
            "url": url,
            "data": response_data,
            "message": f"Successfully created {resource_type} resource"
        }
        
        return json.dumps(result_data, indent=2)
        
    except requests.exceptions.RequestException as error:
        logger.error(f"HTTP request error in createResource tool: {error}")
        error_data = {
            "error": "Failed to create resource",
            "details": f"HTTP request failed: {str(error)}",
            "resource_type": resource_type,
            "url": url if 'url' in locals() else None
        }
        return json.dumps(error_data, indent=2)
    except (ValueError, TypeError) as error:
        logger.error(f"Validation error in createResource tool: {error}")
        error_data = {
            "error": "Failed to create resource",
            "details": str(error),
            "resource_type": resource_type
        }
        return json.dumps(error_data, indent=2)
    except Exception as error:
        logger.error(f"Unexpected error in createResource tool: {error}")
        error_data = {
            "error": "Failed to create resource",
            "details": "Unknown error occurred",
            "resource_type": resource_type
        }
        return json.dumps(error_data, indent=2)


@mcp.tool()
def readResource(resource_type: str, resource_id: Optional[str] = None) -> str:
    """Read/fetch a resource via REST API GET request.
    
    Args:
        resource_type: The type/endpoint of the resource to read
        resource_id: Optional specific ID of the resource to read
        
    Returns:
        JSON string containing the resource data or error information
    """
    try:
        logger.info(f"Tool called: Reading resource of type '{resource_type}'" + 
                   (f" with ID '{resource_id}'" if resource_id else " (all)"))
        
        # Get base URL from environment variable
        base_url = os.getenv('REST_API_BASE_URL')
        if not base_url:
            raise ValueError("REST_API_BASE_URL environment variable is not set")
        
        # Construct the full URL
        url = f"{base_url.rstrip('/')}/{resource_type}"
        if resource_id:
            url += f"/{resource_id}"
        
        # Validate inputs
        if not isinstance(resource_type, str) or not resource_type.strip():
            raise ValueError("resource_type must be a non-empty string")
        
        if resource_id is not None and (not isinstance(resource_id, str) or not resource_id.strip()):
            raise ValueError("resource_id must be a non-empty string or None")
        
        # Make GET request
        response = requests.get(url, timeout=30)
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse response
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {"raw_response": response.text}
        
        logger.info(f"Resource read successfully. Status: {response.status_code}")
        
        result_data = {
            "operation": "read",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "status_code": response.status_code,
            "url": url,
            "data": response_data,
            "message": f"Successfully read {resource_type} resource" + 
                      (f" with ID {resource_id}" if resource_id else "s")
        }
        
        return json.dumps(result_data, indent=2)
        
    except requests.exceptions.RequestException as error:
        logger.error(f"HTTP request error in readResource tool: {error}")
        error_data = {
            "error": "Failed to read resource",
            "details": f"HTTP request failed: {str(error)}",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "url": url if 'url' in locals() else None
        }
        return json.dumps(error_data, indent=2)
    except (ValueError, TypeError) as error:
        logger.error(f"Validation error in readResource tool: {error}")
        error_data = {
            "error": "Failed to read resource",
            "details": str(error),
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        return json.dumps(error_data, indent=2)
    except Exception as error:
        logger.error(f"Unexpected error in readResource tool: {error}")
        error_data = {
            "error": "Failed to read resource",
            "details": "Unknown error occurred",
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        return json.dumps(error_data, indent=2)


@mcp.tool()
def updateResource(resource_type: str, resource_id: str, data: Dict[str, Any]) -> str:
    """Update an existing resource via REST API PUT request.
    
    Args:
        resource_type: The type/endpoint of the resource to update
        resource_id: The ID of the resource to update
        data: The updated data to send in the PUT request body
        
    Returns:
        JSON string containing the updated resource details or error information
    """
    try:
        logger.info(f"Tool called: Updating resource of type '{resource_type}' with ID '{resource_id}' and data: {data}")
        
        # Get base URL from environment variable
        base_url = os.getenv('REST_API_BASE_URL')
        if not base_url:
            raise ValueError("REST_API_BASE_URL environment variable is not set")
        
        # Construct the full URL
        url = f"{base_url.rstrip('/')}/{resource_type}/{resource_id}"
        
        # Validate inputs
        if not isinstance(resource_type, str) or not resource_type.strip():
            raise ValueError("resource_type must be a non-empty string")
        
        if not isinstance(resource_id, str) or not resource_id.strip():
            raise ValueError("resource_id must be a non-empty string")
        
        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")
        
        # Make PUT request
        response = requests.put(
            url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse response
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {"raw_response": response.text}
        
        logger.info(f"Resource updated successfully. Status: {response.status_code}")
        
        result_data = {
            "operation": "update",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "status_code": response.status_code,
            "url": url,
            "data": response_data,
            "message": f"Successfully updated {resource_type} resource with ID {resource_id}"
        }
        
        return json.dumps(result_data, indent=2)
        
    except requests.exceptions.RequestException as error:
        logger.error(f"HTTP request error in updateResource tool: {error}")
        error_data = {
            "error": "Failed to update resource",
            "details": f"HTTP request failed: {str(error)}",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "url": url if 'url' in locals() else None
        }
        return json.dumps(error_data, indent=2)
    except (ValueError, TypeError) as error:
        logger.error(f"Validation error in updateResource tool: {error}")
        error_data = {
            "error": "Failed to update resource",
            "details": str(error),
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        return json.dumps(error_data, indent=2)
    except Exception as error:
        logger.error(f"Unexpected error in updateResource tool: {error}")
        error_data = {
            "error": "Failed to update resource",
            "details": "Unknown error occurred",
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        return json.dumps(error_data, indent=2)


@mcp.tool()
def deleteResource(resource_type: str, resource_id: str) -> str:
    """Delete a resource via REST API DELETE request.
    
    Args:
        resource_type: The type/endpoint of the resource to delete
        resource_id: The ID of the resource to delete
        
    Returns:
        JSON string containing deletion confirmation or error information
    """
    try:
        logger.info(f"Tool called: Deleting resource of type '{resource_type}' with ID '{resource_id}'")
        
        # Get base URL from environment variable
        base_url = os.getenv('REST_API_BASE_URL')
        if not base_url:
            raise ValueError("REST_API_BASE_URL environment variable is not set")
        
        # Construct the full URL
        url = f"{base_url.rstrip('/')}/{resource_type}/{resource_id}"
        
        # Validate inputs
        if not isinstance(resource_type, str) or not resource_type.strip():
            raise ValueError("resource_type must be a non-empty string")
        
        if not isinstance(resource_id, str) or not resource_id.strip():
            raise ValueError("resource_id must be a non-empty string")
        
        # Make DELETE request
        response = requests.delete(url, timeout=30)
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse response (DELETE might return empty body)
        try:
            response_data = response.json() if response.text.strip() else {}
        except json.JSONDecodeError:
            response_data = {"raw_response": response.text} if response.text.strip() else {}
        
        logger.info(f"Resource deleted successfully. Status: {response.status_code}")
        
        result_data = {
            "operation": "delete",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "status_code": response.status_code,
            "url": url,
            "data": response_data,
            "message": f"Successfully deleted {resource_type} resource with ID {resource_id}"
        }
        
        return json.dumps(result_data, indent=2)
        
    except requests.exceptions.RequestException as error:
        logger.error(f"HTTP request error in deleteResource tool: {error}")
        error_data = {
            "error": "Failed to delete resource",
            "details": f"HTTP request failed: {str(error)}",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "url": url if 'url' in locals() else None
        }
        return json.dumps(error_data, indent=2)
    except (ValueError, TypeError) as error:
        logger.error(f"Validation error in deleteResource tool: {error}")
        error_data = {
            "error": "Failed to delete resource",
            "details": str(error),
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        return json.dumps(error_data, indent=2)
    except Exception as error:
        logger.error(f"Unexpected error in deleteResource tool: {error}")
        error_data = {
            "error": "Failed to delete resource",
            "details": "Unknown error occurred",
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        return json.dumps(error_data, indent=2)


def main():
    """Main entry point for the stdio MCP server."""
    # Set up process error handlers
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.error(
            "Uncaught exception", 
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    sys.excepthook = handle_exception
    
    # Run the server
    try:
        logger.info("Calculator MCP Server starting...")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as error:
        logger.error(f"Top-level error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()