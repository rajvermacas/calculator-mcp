#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Add immediate error handling
process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
});

process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error);
    process.exit(1);
});

// Log startup
console.error("Calculator MCP Server: Starting initialization...");

try {
    // Create the MCP server instance
    const mcpServer = new McpServer({
        name: "calculator-mcp-server",
        version: "1.0.0"
    });
    
    console.error("Calculator MCP Server: Instance created");

    // Register the addition tool using the simpler API
    mcpServer.registerTool(
        "addNumbers",
        {
            description: "Add two numbers together and return the sum",
            inputSchema: {
                num1: z.number().describe("The first number to add"),
                num2: z.number().describe("The second number to add")
            }
        },
        async ({ num1, num2 }) => {
            try {
                console.error(`Calculator MCP Server: Adding ${num1} + ${num2}`);
                
                // Validate inputs
                if (!Number.isFinite(num1) || !Number.isFinite(num2)) {
                    throw new Error("Both inputs must be finite numbers");
                }

                const result = num1 + num2;
                console.error(`Calculator MCP Server: Result: ${result}`);

                return {
                    content: [
                        {
                            type: "text" as const,
                            text: JSON.stringify({
                                operation: "addition",
                                operands: [num1, num2],
                                result: result,
                                message: `The sum of ${num1} and ${num2} is ${result}`
                            }, null, 2)
                        }
                    ]
                };
            } catch (error) {
                console.error("Calculator MCP Server: Error in addNumbers tool:", error);
                return {
                    content: [
                        {
                            type: "text" as const,
                            text: JSON.stringify({
                                error: "Failed to add numbers",
                                details: error instanceof Error ? error.message : "Unknown error",
                                operands: [num1, num2]
                            }, null, 2)
                        }
                    ]
                };
            }
        }
    );

    console.error("Calculator MCP Server: Tool registered");

    /**
     * Main function to run the server
     */
    async function main() {
        try {
            console.error("Calculator MCP Server: Creating transport...");
            const transport = new StdioServerTransport();
            
            console.error("Calculator MCP Server: Connecting to transport...");
            await mcpServer.connect(transport);
            
            console.error("Calculator MCP Server: Successfully started and listening");
        } catch (error) {
            console.error("Calculator MCP Server: Failed to start:", error);
            console.error("Stack trace:", error instanceof Error ? error.stack : "No stack trace");
            process.exit(1);
        }
    }

    // Start the server
    main().catch((error) => {
        console.error("Calculator MCP Server: Fatal error in main():", error);
        console.error("Stack trace:", error instanceof Error ? error.stack : "No stack trace");
        process.exit(1);
    });

} catch (error) {
    console.error("Calculator MCP Server: Failed during initialization:", error);
    console.error("Stack trace:", error instanceof Error ? error.stack : "No stack trace");
    process.exit(1);
}