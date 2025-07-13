#!/usr/bin/env python3
"""Calculator MCP Remote Server - HTTP/SSE transport for adding two numbers."""

import argparse
import asyncio
import json
import logging
import math
import sys
from typing import Any, Dict

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
    
    return mcp


def create_fastapi_app(mcp_server: FastMCP) -> FastAPI:
    """Create FastAPI application with MCP SSE endpoint."""
    
    app = FastAPI(
        title="Calculator MCP Remote Server",
        description="A remote MCP server for adding two numbers via HTTP/SSE",
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
            "description": "Remote MCP server for adding two numbers",
            "endpoints": {
                "sse": "/sse",
                "health": "/health"
            },
            "tools": ["addNumbers"]
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