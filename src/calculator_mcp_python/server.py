#!/usr/bin/env python3
"""Calculator MCP Server - Python implementation for adding two numbers."""

import json
import logging
import math
import sys

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


if __name__ == "__main__":
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