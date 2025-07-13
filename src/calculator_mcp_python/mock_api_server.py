#!/usr/bin/env python3
"""Mock FastAPI server that returns dummy responses matching MCP CRUD tool schemas."""

import json
import logging
import sys
import sqlite3
import os
from datetime import datetime
from typing import Any, Dict, Optional, List
import argparse
import uuid
from contextlib import contextmanager

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


# Database management class
class DatabaseManager:
    """Manages SQLite database operations for the CRUD API."""
    
    def __init__(self, db_path: str = "resources/data/crud_api.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self._initialize_database()
    
    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:  # Only create directory if there is a directory component
            os.makedirs(db_dir, exist_ok=True)
    
    def _initialize_database(self):
        """Initialize the database and create tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create resources table with generic schema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resources (
                    id TEXT PRIMARY KEY,
                    resource_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
            """)
            
            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_resource_type 
                ON resources(resource_type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON resources(created_at)
            """)
            
            conn.commit()
            logger.info(f"Database initialized at: {self.db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper cleanup."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def create_resource(self, resource_type: str, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new resource in the database."""
        resource_id = str(uuid.uuid4())[:8]
        current_time = datetime.utcnow().isoformat() + "Z"
        
        # Prepare the complete resource data
        complete_data = {
            "id": resource_id,
            "created_at": current_time,
            "updated_at": current_time,
            **resource_data
        }
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO resources (id, resource_type, data, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (resource_id, resource_type, json.dumps(complete_data), current_time, current_time)
            )
            conn.commit()
            
        logger.info(f"Created {resource_type} resource with ID: {resource_id}")
        return complete_data
    
    def get_resources(self, resource_type: str) -> List[Dict[str, Any]]:
        """Get all resources of a specific type."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT data FROM resources WHERE resource_type = ? ORDER BY created_at DESC",
                (resource_type,)
            )
            
            resources = []
            for row in cursor.fetchall():
                resources.append(json.loads(row[0]))
            
        logger.info(f"Retrieved {len(resources)} {resource_type} resources")
        return resources
    
    def get_resource_by_id(self, resource_type: str, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific resource by ID and type."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT data FROM resources WHERE id = ? AND resource_type = ?",
                (resource_id, resource_type)
            )
            
            row = cursor.fetchone()
            if row:
                resource_data = json.loads(row[0])
                logger.info(f"Retrieved {resource_type} resource: {resource_id}")
                return resource_data
            
        logger.warning(f"Resource not found: {resource_type}/{resource_id}")
        return None
    
    def update_resource(self, resource_type: str, resource_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing resource."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # First, check if resource exists
            cursor.execute(
                "SELECT data FROM resources WHERE id = ? AND resource_type = ?",
                (resource_id, resource_type)
            )
            
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Cannot update non-existent resource: {resource_type}/{resource_id}")
                return None
            
            # Merge existing data with updates
            existing_data = json.loads(row[0])
            updated_data = {
                **existing_data,
                **update_data,
                "updated_at": datetime.utcnow().isoformat() + "Z"
            }
            
            # Update the resource
            cursor.execute(
                "UPDATE resources SET data = ?, updated_at = ? WHERE id = ? AND resource_type = ?",
                (json.dumps(updated_data), updated_data["updated_at"], resource_id, resource_type)
            )
            conn.commit()
            
        logger.info(f"Updated {resource_type} resource: {resource_id}")
        return updated_data
    
    def delete_resource(self, resource_type: str, resource_id: str) -> bool:
        """Delete a resource from the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if resource exists before deletion
            cursor.execute(
                "SELECT id FROM resources WHERE id = ? AND resource_type = ?",
                (resource_id, resource_type)
            )
            
            if not cursor.fetchone():
                logger.warning(f"Cannot delete non-existent resource: {resource_type}/{resource_id}")
                return False
            
            # Delete the resource
            cursor.execute(
                "DELETE FROM resources WHERE id = ? AND resource_type = ?",
                (resource_id, resource_type)
            )
            conn.commit()
            
        logger.info(f"Deleted {resource_type} resource: {resource_id}")
        return True
    
    def clear_all_resources(self):
        """Clear all resources from the database (for testing)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM resources")
            conn.commit()
        logger.info("Cleared all resources from database")


# Global database manager instance
db_manager = None

def get_db_manager():
    """Get the database manager instance."""
    global db_manager
    if db_manager is None:
        # Initialize with default path if not set
        db_manager = DatabaseManager()
    return db_manager

# Create FastAPI app
app = FastAPI(
    title="Calculator MCP CRUD API Server",
    description="CRUD API server with SQLite database for persistent resource management",
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
    """Create a new resource in the database."""
    try:
        logger.info(f"POST /{resource_type} - Creating resource with data: {data}")
        
        # Create resource in database
        created_data = get_db_manager().create_resource(resource_type, data)
        
        # Construct full URL (mock)
        url = f"http://localhost:8001/{resource_type}"
        
        response_data = {
            "operation": "create",
            "resource_type": resource_type,
            "status_code": 201,
            "url": url,
            "data": created_data,
            "message": f"Successfully created {resource_type} resource"
        }
        
        logger.info(f"Created resource successfully. ID: {created_data.get('id')}")
        return JSONResponse(content=response_data, status_code=201)
        
    except Exception as error:
        logger.error(f"Error creating resource: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to create resource: {str(error)}")


@app.get("/{resource_type}")
async def read_resources(
    resource_type: str = Path(..., description="Type of resource to read")
):
    """Read all resources of a given type from the database."""
    try:
        logger.info(f"GET /{resource_type} - Reading all resources")
        
        # Get resources from database
        resources_data = get_db_manager().get_resources(resource_type)
        
        # Construct full URL (mock)
        url = f"http://localhost:8001/{resource_type}"
        
        response_data = {
            "operation": "read",
            "resource_type": resource_type,
            "resource_id": None,
            "status_code": 200,
            "url": url,
            "data": resources_data,
            "message": f"Successfully read {resource_type} resources"
        }
        
        logger.info(f"Read {len(resources_data)} resources successfully")
        return response_data
        
    except Exception as error:
        logger.error(f"Error reading resources: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to read resources: {str(error)}")


@app.get("/{resource_type}/{resource_id}")
async def read_resource(
    resource_type: str = Path(..., description="Type of resource to read"),
    resource_id: str = Path(..., description="ID of the resource to read")
):
    """Read a specific resource by ID from the database."""
    try:
        logger.info(f"GET /{resource_type}/{resource_id} - Reading specific resource")
        
        # Get resource from database
        resource_data = get_db_manager().get_resource_by_id(resource_type, resource_id)
        
        if resource_data is None:
            raise HTTPException(
                status_code=404, 
                detail=f"{resource_type} resource with ID {resource_id} not found"
            )
        
        # Construct full URL (mock)
        url = f"http://localhost:8001/{resource_type}/{resource_id}"
        
        response_data = {
            "operation": "read",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "status_code": 200,
            "url": url,
            "data": resource_data,
            "message": f"Successfully read {resource_type} resource with ID {resource_id}"
        }
        
        logger.info(f"Read resource {resource_id} successfully")
        return response_data
        
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Error reading resource: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to read resource: {str(error)}")


@app.put("/{resource_type}/{resource_id}")
async def update_resource(
    resource_type: str = Path(..., description="Type of resource to update"),
    resource_id: str = Path(..., description="ID of the resource to update"),
    data: Dict[str, Any] = Body(..., description="Updated resource data")
):
    """Update an existing resource in the database."""
    try:
        logger.info(f"PUT /{resource_type}/{resource_id} - Updating resource with data: {data}")
        
        # Update resource in database
        updated_data = get_db_manager().update_resource(resource_type, resource_id, data)
        
        if updated_data is None:
            raise HTTPException(
                status_code=404, 
                detail=f"{resource_type} resource with ID {resource_id} not found"
            )
        
        # Construct full URL (mock)
        url = f"http://localhost:8001/{resource_type}/{resource_id}"
        
        response_data = {
            "operation": "update",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "status_code": 200,
            "url": url,
            "data": updated_data,
            "message": f"Successfully updated {resource_type} resource with ID {resource_id}"
        }
        
        logger.info(f"Updated resource {resource_id} successfully")
        return response_data
        
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Error updating resource: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to update resource: {str(error)}")


@app.delete("/{resource_type}/{resource_id}")
async def delete_resource(
    resource_type: str = Path(..., description="Type of resource to delete"),
    resource_id: str = Path(..., description="ID of the resource to delete")
):
    """Delete a resource from the database."""
    try:
        logger.info(f"DELETE /{resource_type}/{resource_id} - Deleting resource")
        
        # Delete resource from database
        deleted = get_db_manager().delete_resource(resource_type, resource_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404, 
                detail=f"{resource_type} resource with ID {resource_id} not found"
            )
        
        # Generate deletion confirmation
        current_time = datetime.utcnow().isoformat() + "Z"
        deletion_data = {
            "deleted": True, 
            "id": resource_id, 
            "deleted_at": current_time
        }
        
        # Construct full URL (mock)
        url = f"http://localhost:8001/{resource_type}/{resource_id}"
        
        response_data = {
            "operation": "delete",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "status_code": 200,
            "url": url,
            "data": deletion_data,
            "message": f"Successfully deleted {resource_type} resource with ID {resource_id}"
        }
        
        logger.info(f"Deleted resource {resource_id} successfully")
        return JSONResponse(content=response_data, status_code=200)
        
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Error deleting resource: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to delete resource: {str(error)}")


# Add a cleanup endpoint for testing
@app.delete("/admin/clear")
async def clear_all_resources():
    """Clear all resources from the database (for testing purposes)."""
    try:
        logger.info("DELETE /admin/clear - Clearing all resources")
        get_db_manager().clear_all_resources()
        
        response_data = {
            "operation": "clear",
            "message": "All resources have been cleared from the database",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        logger.info("Cleared all resources successfully")
        return response_data
        
    except Exception as error:
        logger.error(f"Error clearing resources: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to clear resources: {str(error)}")


def main():
    """Main entry point for the CRUD API server."""
    global db_manager
    
    parser = argparse.ArgumentParser(description="Calculator MCP CRUD API Server with SQLite Database")
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
        "--db-path",
        default="resources/data/crud_api.db",
        help="Path to SQLite database file (default: resources/data/crud_api.db)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    args = parser.parse_args()
    
    # Initialize database manager
    db_manager = DatabaseManager(args.db_path)
    
    logger.info(f"Starting Calculator MCP CRUD API Server on {args.host}:{args.port}")
    logger.info(f"Database: {args.db_path}")
    logger.info("Available endpoints:")
    logger.info("  GET /health - Health check")
    logger.info("  POST /{resource_type} - Create resource")
    logger.info("  GET /{resource_type} - List all resources")
    logger.info("  GET /{resource_type}/{id} - Get specific resource")
    logger.info("  PUT /{resource_type}/{id} - Update resource")
    logger.info("  DELETE /{resource_type}/{id} - Delete resource")
    logger.info("  DELETE /admin/clear - Clear all resources (testing)")
    
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