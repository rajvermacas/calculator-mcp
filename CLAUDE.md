# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Calculator MCP (Model Context Protocol) server with dual implementations in TypeScript and Python. It provides a simple `addNumbers` tool for adding two numbers with comprehensive error handling and validation.

## Development Commands

### TypeScript Server
- `npm run build` - Compile TypeScript to JavaScript (outputs to `dist/`)
- `npm start` - Run the compiled TypeScript server
- `npm run dev` - Build and run in development mode
- `npm test` - Run TypeScript test suite
- `npm run clean` - Remove compiled JavaScript files

### Python Server
- `pip install -e .` - Install in development mode
- `pip install -e ".[dev]"` - Install with dev dependencies for testing
- `calculator-mcp-python` - Run local Python server (stdio transport)
- `calculator-mcp-python-remote` - Run remote Python server (HTTP/SSE transport)
- `python -m pytest tests/python/ -v` - Run Python test suite

### Test Commands
- `node --test dist/tests/server.test.js` - Run compiled TypeScript tests
- `python scripts/test_python_server.py` - Debug Python server functionality
- `node dist/scripts/generate-test-data.js` - Generate TypeScript test data

## Architecture

### Dual Implementation Structure
- **TypeScript**: Uses `@modelcontextprotocol/sdk` with stdio transport
- **Python**: Uses `mcp.server.fastmcp` (FastMCP) with both stdio and HTTP/SSE transports

### Core Components

#### TypeScript Implementation (`src/calculator-mcp/server.ts`)
- Uses MCP SDK with Zod schema validation
- Stdio transport for local communication
- Comprehensive error logging to stderr
- Tool registration using `server.tool()` pattern

#### Python Local Server (`src/calculator_mcp_python/server.py`)
- FastMCP-based implementation with stdio transport
- Uses `@mcp.tool()` decorator for tool registration
- JSON response formatting

#### Python Remote Server (`src/calculator_mcp_python/remote_server.py`)
- FastAPI + FastMCP for HTTP/SSE transport
- Command-line arguments for host/port configuration
- CORS-enabled for remote access
- Built-in health check endpoints

### Tool Implementation
Both implementations provide the `addNumbers` tool:
- Parameters: `num1: number`, `num2: number`
- Validates finite numbers (rejects Infinity, NaN)
- Returns JSON-formatted response with operation details
- Comprehensive error handling with structured error responses

## Testing Strategy

### Test Structure
- TypeScript tests: `tests/server.test.ts` (compiled to `dist/tests/`)
- Python tests: `tests/python/test_server.py` and `tests/python/test_remote_server.py`
- Test data: `test_data/` directory with JSON test cases
- Remote client tests: `test_*.py` files in root directory

### Test Coverage Areas
- Valid number addition (positive, negative, decimals, zeros)
- Error cases (Infinity, NaN, invalid inputs)
- Edge cases (large numbers, floating point precision)
- Transport-specific testing (stdio vs HTTP/SSE)

## MCP Integration

### Local Development
Use MCP Inspector for testing:
```bash
npx @modelcontextprotocol/inspector dist/src/calculator-mcp/server.js
```

### Claude Desktop Integration
Configure in `claude_desktop_config.json`:
- TypeScript: Point to `dist/src/calculator-mcp/server.js`
- Python Local: Point to `src/calculator_mcp_python/server.py`
- Python Remote: Use `mcp-remote` with SSE endpoint

### Remote Server Usage
- Default endpoint: `http://localhost:8000/sse`
- Health check: `http://localhost:8000/health`
- Supports custom host/port via CLI arguments

## Key Development Notes

### TypeScript Specific
- Uses ES2022 modules with Node16 module resolution
- All console output goes to stderr for MCP compatibility
- Requires Node.js >= 18

### Python Specific
- Supports Python 3.8+
- FastMCP handles both stdio and SSE transports
- Virtual environment recommended (`venv/`)
- Entry points defined in `pyproject.toml` for CLI commands

### Error Handling Philosophy
- Validate inputs strictly (finite numbers only)
- Structured error responses with operation context
- Comprehensive logging for debugging
- Graceful handling of edge cases

### Project Structure Conventions
- Main implementations in `src/`
- Compiled output in `dist/` (TypeScript)
- Tests in `tests/` with language-specific subdirectories
- Test data in `test_data/`
- Debug/utility scripts in `scripts/`