#!/usr/bin/env python3
"""Mock FastAPI server that returns dummy responses matching MCP CRUD tool schemas."""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import argparse
import uuid

from fastapi import FastAPI, HTTPException, Path, Body, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Calculator MCP Mock API Server",
    description="Mock API server that returns dummy responses matching MCP CRUD tool schemas",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request validation
class CreateResourceRequest(BaseModel):
    """Request model for creating resources."""
    pass  # Accept any JSON data

class UpdateResourceRequest(BaseModel):
    """Request model for updating resources."""
    pass  # Accept any JSON data


# Response models matching MCP tool schemas
class MCPResponse(BaseModel):
    """Base response model matching MCP tool output."""
    operation: str
    resource_type: str
    status_code: int
    url: str
    data: Dict[str, Any]
    message: str


def generate_dummy_data(resource_type: str, operation: str, resource_id: Optional[str] = None, input_data: Optional[Dict] = None) -> Dict[str, Any]:
    """Generate realistic dummy data for different resource types and operations."""
    current_time = datetime.utcnow().isoformat() + "Z"
    
    # Base dummy data templates for different resource types
    dummy_templates = {
        "users": {
            "id": str(uuid.uuid4())[:8],
            "name": "John Doe",
            "email": "john.doe@example.com",
            "age": 30,
            "department": "Engineering",
            "created_at": current_time,
            "updated_at": current_time,
            "status": "active"
        },
        "products": {
            "id": str(uuid.uuid4())[:8],
            "name": "Sample Product",
            "description": "A high-quality sample product",
            "price": 29.99,
            "category": "Electronics",
            "in_stock": True,
            "created_at": current_time,
            "updated_at": current_time
        },
        "orders": {
            "id": str(uuid.uuid4())[:8],
            "customer_id": str(uuid.uuid4())[:8],
            "total": 59.98,
            "status": "pending",
            "items": [
                {"product_id": str(uuid.uuid4())[:8], "quantity": 2, "price": 29.99}
            ],
            "created_at": current_time,
            "updated_at": current_time
        }
    }
    
    # Get base template or create generic one
    if resource_type in dummy_templates:
        base_data = dummy_templates[resource_type].copy()
    else:
        base_data = {
            "id": str(uuid.uuid4())[:8],
            "name": f"Sample {resource_type.rstrip('s').title()}",
            "created_at": current_time,
            "updated_at": current_time
        }
    
    # Override with resource_id if provided
    if resource_id:
        base_data["id"] = resource_id
    
    # Merge with input data if provided (for create/update operations)
    if input_data:
        base_data.update(input_data)
        base_data["updated_at"] = current_time
    
    # Operation-specific modifications
    if operation == "create":
        base_data["created"] = True
    elif operation == "update":
        base_data["updated"] = True
    elif operation == "delete":
        return {"deleted": True, "id": resource_id, "deleted_at": current_time}
    
    return base_data


def generate_list_data(resource_type: str, count: int = 3) -> list:
    """Generate a list of dummy resources."""
    return [
        generate_dummy_data(resource_type, "read", str(uuid.uuid4())[:8])
        for _ in range(count)
    ]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Calculator MCP Mock API Server",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/{resource_type}")
async def create_resource(
    resource_type: str = Path(..., description="Type of resource to create"),
    data: Dict[str, Any] = Body(..., description="Resource data to create")
):
    """Create a new resource - returns dummy success response."""
    try:
        logger.info(f"POST /{resource_type} - Creating resource with data: {data}")
        
        # Generate dummy response data
        dummy_data = generate_dummy_data(resource_type, "create", input_data=data)
        
        # Construct full URL (mock)
        url = f"http://localhost:8001/{resource_type}"
        
        response_data = {
            "operation": "create",
            "resource_type": resource_type,
            "status_code": 201,
            "url": url,
            "data": dummy_data,
            "message": f"Successfully created {resource_type} resource"
        }
        
        logger.info(f"Created resource successfully. ID: {dummy_data.get('id')}")
        return JSONResponse(content=response_data, status_code=201)
        
    except Exception as error:
        logger.error(f"Error creating resource: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to create resource: {str(error)}")


@app.get("/{resource_type}")
async def read_resources(
    resource_type: str = Path(..., description="Type of resource to read")
):
    """Read all resources of a given type - returns dummy list response."""
    try:
        logger.info(f"GET /{resource_type} - Reading all resources")
        
        # Generate dummy list data
        dummy_data = generate_list_data(resource_type)
        
        # Construct full URL (mock)
        url = f"http://localhost:8001/{resource_type}"
        
        response_data = {
            "operation": "read",
            "resource_type": resource_type,
            "resource_id": None,
            "status_code": 200,
            "url": url,
            "data": dummy_data,
            "message": f"Successfully read {resource_type} resources"
        }
        
        logger.info(f"Read {len(dummy_data)} resources successfully")
        return response_data
        
    except Exception as error:
        logger.error(f"Error reading resources: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to read resources: {str(error)}")


@app.get("/{resource_type}/{resource_id}")
async def read_resource(
    resource_type: str = Path(..., description="Type of resource to read"),
    resource_id: str = Path(..., description="ID of the resource to read")
):
    """Read a specific resource by ID - returns dummy single resource response."""
    try:
        logger.info(f"GET /{resource_type}/{resource_id} - Reading specific resource")
        
        # Generate dummy data for specific resource
        dummy_data = generate_dummy_data(resource_type, "read", resource_id)
        
        # Construct full URL (mock)
        url = f"http://localhost:8001/{resource_type}/{resource_id}"
        
        response_data = {
            "operation": "read",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "status_code": 200,
            "url": url,
            "data": dummy_data,
            "message": f"Successfully read {resource_type} resource with ID {resource_id}"
        }
        
        logger.info(f"Read resource {resource_id} successfully")
        return response_data
        
    except Exception as error:
        logger.error(f"Error reading resource: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to read resource: {str(error)}")


@app.put("/{resource_type}/{resource_id}")
async def update_resource(
    resource_type: str = Path(..., description="Type of resource to update"),
    resource_id: str = Path(..., description="ID of the resource to update"),
    data: Dict[str, Any] = Body(..., description="Updated resource data")
):
    """Update an existing resource - returns dummy success response."""
    try:
        logger.info(f"PUT /{resource_type}/{resource_id} - Updating resource with data: {data}")
        
        # Generate dummy updated data
        dummy_data = generate_dummy_data(resource_type, "update", resource_id, data)
        
        # Construct full URL (mock)
        url = f"http://localhost:8001/{resource_type}/{resource_id}"
        
        response_data = {
            "operation": "update",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "status_code": 200,
            "url": url,
            "data": dummy_data,
            "message": f"Successfully updated {resource_type} resource with ID {resource_id}"
        }
        
        logger.info(f"Updated resource {resource_id} successfully")
        return response_data
        
    except Exception as error:
        logger.error(f"Error updating resource: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to update resource: {str(error)}")


@app.delete("/{resource_type}/{resource_id}")
async def delete_resource(
    resource_type: str = Path(..., description="Type of resource to delete"),
    resource_id: str = Path(..., description="ID of the resource to delete")
):
    """Delete a resource - returns dummy success response."""
    try:
        logger.info(f"DELETE /{resource_type}/{resource_id} - Deleting resource")
        
        # Generate dummy deletion confirmation
        dummy_data = generate_dummy_data(resource_type, "delete", resource_id)
        
        # Construct full URL (mock)
        url = f"http://localhost:8001/{resource_type}/{resource_id}"
        
        response_data = {
            "operation": "delete",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "status_code": 200,
            "url": url,
            "data": dummy_data,
            "message": f"Successfully deleted {resource_type} resource with ID {resource_id}"
        }
        
        logger.info(f"Deleted resource {resource_id} successfully")
        return JSONResponse(content=response_data, status_code=200)
        
    except Exception as error:
        logger.error(f"Error deleting resource: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to delete resource: {str(error)}")


def main():
    """Main entry point for the mock API server."""
    parser = argparse.ArgumentParser(description="Calculator MCP Mock API Server")
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind the server to (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to bind the server to (default: 8001)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting Calculator MCP Mock API Server on {args.host}:{args.port}")
    logger.info("Available endpoints:")
    logger.info("  GET /health - Health check")
    logger.info("  POST /{resource_type} - Create resource")
    logger.info("  GET /{resource_type} - List all resources")
    logger.info("  GET /{resource_type}/{id} - Get specific resource")
    logger.info("  PUT /{resource_type}/{id} - Update resource")
    logger.info("  DELETE /{resource_type}/{id} - Delete resource")
    
    try:
        uvicorn.run(
            "calculator_mcp_python.mock_api_server:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as error:
        logger.error(f"Server error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()