#!/usr/bin/env python3
"""Calculator MCP Remote Server - HTTP/SSE transport for adding two numbers."""

import argparse
import asyncio
import json
import logging
import math
import os
import sys
from typing import Any, Dict, Optional

import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server


# Configure logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with tools."""
    
    # Create the MCP server instance
    mcp = FastMCP("calculator-mcp-python-remote-server")
    
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
            logger.info(f"Remote tool called: Adding {num1} + {num2}")
            
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
            logger.info(f"Remote calculation result: {result}")
            
            response_data = {
                "operation": "addition",
                "operands": [num1, num2],
                "result": result,
                "message": f"The sum of {num1} and {num2} is {result}",
                "server_type": "remote"
            }
            
            return json.dumps(response_data, indent=2)
            
        except (ValueError, TypeError) as error:
            logger.error(f"Validation error in remote addNumbers tool: {error}")
            error_data = {
                "error": "Failed to add numbers",
                "details": str(error),
                "operands": [num1, num2],
                "server_type": "remote"
            }
            return json.dumps(error_data, indent=2)
        except Exception as error:
            logger.error(f"Unexpected error in remote addNumbers tool: {error}")
            error_data = {
                "error": "Failed to add numbers",
                "details": "Unknown error occurred",
                "operands": [num1, num2],
                "server_type": "remote"
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
            logger.info(f"Remote tool called: Creating resource of type '{resource_type}' with data: {data}")
            
            # Get base URL from environment variable
            base_url = os.getenv('REST_API_BASE_URL', "http://127.0.0.1:8001")
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
                "message": f"Successfully created {resource_type} resource",
                "server_type": "remote"
            }
            
            return json.dumps(result_data, indent=2)
            
        except requests.exceptions.RequestException as error:
            logger.error(f"HTTP request error in remote createResource tool: {error}")
            error_data = {
                "error": "Failed to create resource",
                "details": f"HTTP request failed: {str(error)}",
                "resource_type": resource_type,
                "url": url if 'url' in locals() else None,
                "server_type": "remote"
            }
            return json.dumps(error_data, indent=2)
        except (ValueError, TypeError) as error:
            logger.error(f"Validation error in remote createResource tool: {error}")
            error_data = {
                "error": "Failed to create resource",
                "details": str(error),
                "resource_type": resource_type,
                "server_type": "remote"
            }
            return json.dumps(error_data, indent=2)
        except Exception as error:
            logger.error(f"Unexpected error in remote createResource tool: {error}")
            error_data = {
                "error": "Failed to create resource",
                "details": "Unknown error occurred",
                "resource_type": resource_type,
                "server_type": "remote"
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
            logger.info(f"Remote tool called: Reading resource of type '{resource_type}'" + 
                       (f" with ID '{resource_id}'" if resource_id else " (all)"))
            
            # Get base URL from environment variable
            base_url = os.getenv('REST_API_BASE_URL', "http://127.0.0.1:8001")
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
                          (f" with ID {resource_id}" if resource_id else "s"),
                "server_type": "remote"
            }
            
            return json.dumps(result_data, indent=2)
            
        except requests.exceptions.RequestException as error:
            logger.error(f"HTTP request error in remote readResource tool: {error}")
            error_data = {
                "error": "Failed to read resource",
                "details": f"HTTP request failed: {str(error)}",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "url": url if 'url' in locals() else None,
                "server_type": "remote"
            }
            return json.dumps(error_data, indent=2)
        except (ValueError, TypeError) as error:
            logger.error(f"Validation error in remote readResource tool: {error}")
            error_data = {
                "error": "Failed to read resource",
                "details": str(error),
                "resource_type": resource_type,
                "resource_id": resource_id,
                "server_type": "remote"
            }
            return json.dumps(error_data, indent=2)
        except Exception as error:
            logger.error(f"Unexpected error in remote readResource tool: {error}")
            error_data = {
                "error": "Failed to read resource",
                "details": "Unknown error occurred",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "server_type": "remote"
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
            logger.info(f"Remote tool called: Updating resource of type '{resource_type}' with ID '{resource_id}' and data: {data}")
            
            # Get base URL from environment variable
            base_url = os.getenv('REST_API_BASE_URL', "http://127.0.0.1:8001")
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
                "message": f"Successfully updated {resource_type} resource with ID {resource_id}",
                "server_type": "remote"
            }
            
            return json.dumps(result_data, indent=2)
            
        except requests.exceptions.RequestException as error:
            logger.error(f"HTTP request error in remote updateResource tool: {error}")
            error_data = {
                "error": "Failed to update resource",
                "details": f"HTTP request failed: {str(error)}",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "url": url if 'url' in locals() else None,
                "server_type": "remote"
            }
            return json.dumps(error_data, indent=2)
        except (ValueError, TypeError) as error:
            logger.error(f"Validation error in remote updateResource tool: {error}")
            error_data = {
                "error": "Failed to update resource",
                "details": str(error),
                "resource_type": resource_type,
                "resource_id": resource_id,
                "server_type": "remote"
            }
            return json.dumps(error_data, indent=2)
        except Exception as error:
            logger.error(f"Unexpected error in remote updateResource tool: {error}")
            error_data = {
                "error": "Failed to update resource",
                "details": "Unknown error occurred",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "server_type": "remote"
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
            logger.info(f"Remote tool called: Deleting resource of type '{resource_type}' with ID '{resource_id}'")
            
            # Get base URL from environment variable
            base_url = os.getenv('REST_API_BASE_URL', "http://127.0.0.1:8001")
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
                "message": f"Successfully deleted {resource_type} resource with ID {resource_id}",
                "server_type": "remote"
            }
            
            return json.dumps(result_data, indent=2)
            
        except requests.exceptions.RequestException as error:
            logger.error(f"HTTP request error in remote deleteResource tool: {error}")
            error_data = {
                "error": "Failed to delete resource",
                "details": f"HTTP request failed: {str(error)}",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "url": url if 'url' in locals() else None,
                "server_type": "remote"
            }
            return json.dumps(error_data, indent=2)
        except (ValueError, TypeError) as error:
            logger.error(f"Validation error in remote deleteResource tool: {error}")
            error_data = {
                "error": "Failed to delete resource",
                "details": str(error),
                "resource_type": resource_type,
                "resource_id": resource_id,
                "server_type": "remote"
            }
            return json.dumps(error_data, indent=2)
        except Exception as error:
            logger.error(f"Unexpected error in remote deleteResource tool: {error}")
            error_data = {
                "error": "Failed to delete resource",
                "details": "Unknown error occurred",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "server_type": "remote"
            }
            return json.dumps(error_data, indent=2)
    
    return mcp


def create_fastapi_app(mcp_server: FastMCP) -> FastAPI:
    """Create FastAPI application with MCP SSE endpoint."""
    
    app = FastAPI(
        title="Calculator MCP Remote Server",
        description="A remote MCP server for calculator operations and CRUD resource management via HTTP/SSE",
        version="1.0.0"
    )
    
    # Add CORS middleware for remote access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify allowed origins
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        """Root endpoint with server information."""
        return {
            "name": "Calculator MCP Remote Server",
            "version": "1.0.0",
            "description": "Remote MCP server for calculator operations and CRUD resource management",
            "endpoints": {
                "sse": "/sse",
                "health": "/health"
            },
            "tools": ["addNumbers", "createResource", "readResource", "updateResource", "deleteResource"]
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "server": "calculator-mcp-remote"}
    
    # Mount FastMCP's built-in SSE app instead of custom implementation
    app.mount("/sse", mcp_server.sse_app())
    
    return app


async def run_stdio_server():
    """Run the server with stdio transport (for local use)."""
    logger.info("Starting Calculator MCP Server with stdio transport...")
    
    mcp_server = create_mcp_server()
    
    try:
        async with stdio_server(mcp_server.server) as stdio:
            await stdio.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as error:
        logger.error(f"Stdio server error: {error}")
        sys.exit(1)


def run_sse_server_simple():
    """Run the server using FastMCP's built-in SSE capabilities."""
    logger.info(f"Starting Calculator MCP Remote Server (FastMCP SSE)")
    
    mcp_server = create_mcp_server()
    
    try:
        # Use FastMCP's native SSE server
        mcp_server.run(transport='sse')
    except KeyboardInterrupt:
        logger.info("Remote server stopped by user")
    except Exception as error:
        logger.error(f"Remote server error: {error}")
        sys.exit(1)


def run_http_server(host: str = "localhost", port: int = 8000):
    """Run the server with HTTP/SSE transport (for remote use)."""
    logger.info(f"Starting Calculator MCP Remote Server on {host}:{port}")
    
    mcp_server = create_mcp_server()
    app = create_fastapi_app(mcp_server)
    
    # Configure uvicorn for production
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        server_header=False,
        date_header=False
    )
    
    server = uvicorn.Server(config)
    
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("Remote server stopped by user")
    except Exception as error:
        logger.error(f"Remote server error: {error}")
        sys.exit(1)


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Calculator MCP Remote Server"
    )
    
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default="http",
        help="Transport type to use (default: http)"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to for HTTP/SSE transport (default: localhost)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to for HTTP/SSE transport (default: 8000)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    logger.info(f"Transport: {args.transport}")
    
    try:
        if args.transport == "stdio":
            asyncio.run(run_stdio_server())
        else:  # http or sse (use FastMCP's native SSE server)
            run_sse_server_simple()
            
    except Exception as error:
        logger.error(f"Server startup error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()