# Calculator MCP Server

A simple Model Context Protocol (MCP) server implementation in TypeScript that provides addition functionality for two numbers.

## Features

- **Addition Tool**: Add two numbers together with robust error handling
- **TypeScript Implementation**: Full type safety and modern JavaScript features
- **Comprehensive Testing**: Extensive test suite following TDD principles
- **Error Handling**: Proper validation for edge cases (Infinity, NaN, etc.)
- **Logging**: Detailed console logging for debugging and monitoring

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd calculator-mcp
```

2. Install dependencies:
```bash
npm install
```

3. Build the project:
```bash
npm run build
```

## Usage

### Starting the Server

```bash
npm start
```

Or for development (builds and runs):
```bash
npm run dev
```

### Using with MCP Inspector

You can test the server using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector dist/src/calculator-mcp/server.js
```

This will open a web interface at `http://localhost:4000/sse` where you can:
1. Connect to the server
2. Test the `addNumbers` tool
3. View tool responses

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

**Example Output**:
```json
{
  "operation": "addition",
  "operands": [5, 3],
  "result": 8,
  "message": "The sum of 5 and 3 is 8"
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
│   └── calculator-mcp/
│       └── server.ts          # Main MCP server implementation
├── tests/
│   └── server.test.ts         # Comprehensive test suite
├── scripts/
│   └── generate-test-data.ts  # Test data generation utilities
├── dist/                      # Compiled JavaScript output
├── package.json
├── tsconfig.json
└── README.md
```

### Available Scripts

- `npm run build` - Compile TypeScript to JavaScript
- `npm start` - Run the compiled server
- `npm run dev` - Build and run in development mode
- `npm test` - Run the test suite
- `npm run clean` - Remove compiled files

### Testing

The project includes comprehensive tests covering:

- **Valid Operations**: Positive/negative numbers, decimals, zeros, large numbers
- **Error Cases**: Infinity, NaN, invalid inputs
- **Edge Cases**: Floating point precision, safe integer limits

Run tests with:
```bash
npm test
```

### Test Data Generation

Generate test data for various scenarios:
```bash
node dist/scripts/generate-test-data.js
```

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