# Calculator MCP Server

A simple Model Context Protocol (MCP) server implementation in both TypeScript and Python that provides addition functionality for two numbers.

## Features

- **Addition Tool**: Add two numbers together with robust error handling  
- **Latest MCP SDK**: Uses the newest recommended API patterns (updated 2025)
- **Dual Implementation**: Available in both TypeScript and Python
- **TypeScript Implementation**: Full type safety and modern JavaScript features
- **Python Implementation**: Async/await support with Pydantic validation
- **Comprehensive Testing**: Extensive test suite following TDD principles for both implementations
- **Error Handling**: Proper validation for edge cases (Infinity, NaN, etc.)
- **Enhanced Debugging**: Detailed console logging with improved error tracking and stack traces
- **Simplified Architecture**: Streamlined server implementation following SDK best practices

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd calculator-mcp
```

### TypeScript Server

2. Install dependencies:
```bash
npm install
```

3. Build the project:
```bash
npm run build
```

### Python Server

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

Or for development:
```bash
pip install -e ".[dev]"
```

## Usage

### Starting the TypeScript Server

```bash
npm start
```

Or for development (builds and runs):
```bash
npm run dev
```

### Starting the Python Server

#### Local Server (stdio transport)

```bash
# With virtual environment activated
calculator-mcp-python
```

Or directly:
```bash
python src/calculator_mcp_python/server.py
```

#### Remote Server (HTTP/SSE transport)

```bash
# With virtual environment activated
calculator-mcp-python-remote
```

Or directly:
```bash
python src/calculator_mcp_python/remote_server.py
```

**Remote Server Options:**
```bash
# Start on default host and port (localhost:8000)
calculator-mcp-python-remote

# Start with custom host and port
calculator-mcp-python-remote --host 0.0.0.0 --port 3000

# Start with stdio transport (same as local server)
calculator-mcp-python-remote --transport stdio

# Start with different log level
calculator-mcp-python-remote --log-level DEBUG
```

The remote server will be accessible at:
- **Root**: `http://localhost:8000/` - Server information
- **Health**: `http://localhost:8000/health` - Health check
- **SSE Endpoint**: `http://localhost:8000/sse` - MCP communication endpoint

### Integration with Claude Desktop

To use this MCP server with Claude Desktop, you need to configure it in your Claude Desktop settings:

#### Step 1: Build the Server
```bash
npm run build
```

#### Step 2: Configure Claude Desktop

**For macOS:**
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

**For Windows:**
Edit `%APPDATA%/Claude/claude_desktop_config.json`

Add the following configuration:

**For TypeScript Server:**
```json
{
  "mcpServers": {
    "calculator-ts": {
      "command": "node",
      "args": ["/absolute/path/to/calculator-mcp/dist/src/calculator-mcp/server.js"],
      "env": {}
    }
  }
}
```

**For Python Local Server (stdio):**
```json
{
  "mcpServers": {
    "calculator-py": {
      "command": "python",
      "args": ["/absolute/path/to/calculator-mcp/src/calculator_mcp_python/server.py"],
      "env": {}
    }
  }
}
```

**For Python Remote Server (via mcp-remote):**
```json
{
  "mcpServers": {
    "calculator-py-remote": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:8000/sse"],
      "env": {}
    }
  }
}
```

**Note**: For the remote server configuration, you need to:
1. Start the remote server first: `calculator-mcp-python-remote`
2. Then restart Claude Desktop to connect to the running remote server

**Important:** Replace `/absolute/path/to/calculator-mcp/` with the actual absolute path to your project directory.

#### Step 3: Restart Claude Desktop

After saving the configuration file, restart Claude Desktop completely.

#### Step 4: Verify Integration

Once restarted, Claude Desktop will automatically connect to your MCP server. You can now ask Claude to add numbers and it will use your custom tool:

**Example conversations:**
- "Can you add 25 and 17 for me?"
- "What's the sum of 3.14 and 2.86?"
- "Add these numbers: 1000 + 500"

Claude will use your `addNumbers` tool and return the results in the format you defined.

### Using with MCP Inspector (For Testing)

You can test the server using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector dist/src/calculator-mcp/server.js
```

This will open a web interface at `http://localhost:4000/sse` where you can:
1. Connect to the server
2. Test the `addNumbers` tool
3. View tool responses

### Using the Remote Server

#### Testing with MCP Tools

You can test the remote server using MCP tools:

```bash
# Install MCP tools (if not already installed)
npm install -g @modelcontextprotocol/tools

# Test the remote server
mcp tools http://localhost:8000/sse

# Call the addNumbers tool
mcp call addNumbers --params '{"num1":5,"num2":3}' http://localhost:8000/sse
```

#### Testing with mcp-remote

```bash
# Test connection to remote server
npx mcp-remote http://localhost:8000/sse

# Use with Claude Desktop (add to config)
npx -y mcp-remote http://localhost:8000/sse
```

#### Remote Server Deployment

**Development Deployment:**
```bash
# Start server on localhost
calculator-mcp-python-remote --host localhost --port 8000
```

**Production Deployment:**
```bash
# Start server accessible from any IP
calculator-mcp-python-remote --host 0.0.0.0 --port 8000

# With custom configuration
calculator-mcp-python-remote \
  --host 0.0.0.0 \
  --port 3000 \
  --log-level INFO
```

**Docker Deployment (Optional):**
Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

EXPOSE 8000
CMD ["calculator-mcp-python-remote", "--host", "0.0.0.0", "--port", "8000"]
```

**Security Considerations:**
- The server includes CORS headers for remote access
- For production, configure specific allowed origins in CORS settings
- Consider using HTTPS in production environments
- Implement authentication if needed for your use case

### Tool Usage

The server provides one tool:

#### `addNumbers`

**Description**: Add two numbers together and return the sum

**Parameters**:
- `num1` (number): The first number to add
- `num2` (number): The second number to add

**Example Input**:
```json
{
  "num1": 5,
  "num2": 3
}
```

**Example Output (Local Server):**
```json
{
  "operation": "addition",
  "operands": [5, 3],
  "result": 8,
  "message": "The sum of 5 and 3 is 8"
}
```

**Example Output (Remote Server):**
```json
{
  "operation": "addition", 
  "operands": [5, 3],
  "result": 8,
  "message": "The sum of 5 and 3 is 8",
  "server_type": "remote"
}
```

**Error Handling**:
The tool validates inputs and handles edge cases:
- Infinity values
- NaN values
- Non-finite numbers

Error responses include:
```json
{
  "error": "Failed to add numbers",
  "details": "Both inputs must be finite numbers",
  "operands": [Infinity, 5]
}
```

## Development

### Project Structure

```
calculator-mcp/
├── src/
│   ├── calculator-mcp/
│   │   └── server.ts          # TypeScript MCP server implementation
│   └── calculator_mcp_python/
│       ├── __init__.py
│       └── server.py          # Python MCP server implementation
├── tests/
│   ├── server.test.ts         # TypeScript test suite
│   └── python/
│       ├── __init__.py
│       └── test_server.py     # Python test suite
├── scripts/
│   ├── generate-test-data.ts  # TypeScript test data generation
│   └── test_python_server.py  # Python server testing script
├── test_data/
│   └── python_test_cases.json # Python test data
├── dist/                      # Compiled JavaScript output
├── package.json               # TypeScript dependencies
├── pyproject.toml             # Python dependencies
├── tsconfig.json
└── README.md
```

### Available Scripts

**TypeScript:**
- `npm run build` - Compile TypeScript to JavaScript
- `npm start` - Run the compiled server
- `npm run dev` - Build and run in development mode
- `npm test` - Run the test suite
- `npm run clean` - Remove compiled files

**Python:**
- `python -m pytest tests/python/` - Run Python test suite
- `python scripts/test_python_server.py` - Run Python server debug script

### Testing

The project includes comprehensive tests for both implementations covering:

- **Valid Operations**: Positive/negative numbers, decimals, zeros, large numbers
- **Error Cases**: Infinity, NaN, invalid inputs
- **Edge Cases**: Floating point precision, safe integer limits

**Run TypeScript tests:**
```bash
npm test
```

**Run Python tests:**
```bash
# With virtual environment activated
python -m pytest tests/python/ -v
```

**Test Python server functionality:**
```bash
python scripts/test_python_server.py
```

### Test Data Generation

**TypeScript test data:**
```bash
node dist/scripts/generate-test-data.js
```

**Python test data:**
Test cases are stored in `test_data/python_test_cases.json`

## Troubleshooting Claude Desktop Integration

### Common Issues

#### 1. MCP Server Crashes After Initialize Message
- **Solution**: The server has been updated with enhanced error handling and debugging
- **Check logs**: Run the server manually to see detailed error messages:
  ```bash
  node dist/src/calculator-mcp/server.js 2>&1
  ```
- **Module issues**: Ensure TypeScript is compiled with correct module settings
- **Node version**: Requires Node.js 18 or higher

#### 2. MCP Server Not Connecting
- **Check file paths**: Ensure the path in `claude_desktop_config.json` is absolute and correct
- **Check Node.js**: Make sure Node.js >= 18 is installed and accessible from command line
- **Check build**: Ensure you've run `npm run build` and the dist folder exists

#### 3. Tool Not Available in Claude
- **Restart Claude Desktop**: Always restart completely after config changes
- **Check logs**: Look for error messages in Claude Desktop's developer console
- **Verify config**: Ensure the JSON syntax in config file is valid

#### 4. Permission Issues
- **File permissions**: Ensure the server file is executable
- **Path permissions**: Make sure Claude Desktop can access the project directory

#### 5. Debugging Steps
1. Test the server startup manually:
   ```bash
   node dist/src/calculator-mcp/server.js 2>&1
   ```
   You should see:
   ```
   Calculator MCP Server: Starting initialization...
   Calculator MCP Server: Instance created
   Calculator MCP Server: Tool registered
   Calculator MCP Server: Creating transport...
   Calculator MCP Server: Connecting to transport...
   Calculator MCP Server: Successfully started and listening
   ```
2. Check Node.js version: `node --version` (must be >= 18)
3. Run the debug script to verify imports:
   ```bash
   node scripts/debug-imports.js
   ```
4. Test with MCP Inspector first to verify the server works
5. Check Claude Desktop logs for connection errors

### Getting Your Absolute Path

**On macOS/Linux:**
```bash
cd /path/to/calculator-mcp
pwd
```

**On Windows:**
```cmd
cd C:\path\to\calculator-mcp
echo %cd%
```

Use this full path in your Claude Desktop configuration.

## Configuration

The server is configured with:
- **Name**: `calculator-mcp-server`
- **Version**: `1.0.0`
- **Transport**: Standard I/O (stdio)
- **Tool**: `addNumbers` with zod schema validation

## Error Handling

The server implements robust error handling:

1. **Input Validation**: Ensures numbers are finite
2. **Tool-level Errors**: Catches and returns formatted error responses
3. **Server-level Errors**: Logs unhandled rejections and exceptions
4. **Process Handling**: Graceful shutdown on uncaught exceptions

## Logging

Console logging is implemented throughout:
- Server startup/shutdown events
- Tool execution details
- Error conditions
- Input/output values for debugging

## Contributing

1. Follow the existing code style and patterns
2. Add tests for new functionality
3. Ensure all tests pass before submitting
4. Update documentation as needed

## License

MIT License