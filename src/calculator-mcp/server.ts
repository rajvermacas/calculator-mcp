#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Add comprehensive error logging
console.error("Calculator MCP Server starting...");

try {
    // Create the MCP server instance
    const server = new McpServer({
        name: "calculator-mcp-server",
        version: "1.0.0"
    });

    console.error("Server instance created");

    // Register the addition tool using the SDK pattern
    server.tool(
        "addNumbers",
        {
            num1: z.number().describe("The first number to add"),
            num2: z.number().describe("The second number to add")
        },
        async ({ num1, num2 }) => {
            try {
                console.error(`Tool called: Adding ${num1} + ${num2}`);
                
                // Validate inputs
                if (!Number.isFinite(num1) || !Number.isFinite(num2)) {
                    throw new Error("Both inputs must be finite numbers");
                }

                const result = num1 + num2;
                console.error(`Calculation result: ${result}`);

                return {
                    content: [
                        {
                            type: "text",
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
                console.error("Error in addNumbers tool:", error);
                return {
                    content: [
                        {
                            type: "text",
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

    console.error("Tool registered successfully");

    // Main function to start the server
    async function main() {
        try {
            console.error("Connecting to stdio transport...");
            const transport = new StdioServerTransport();
            
            console.error("Starting server connection...");
            await server.connect(transport);
            
            console.error("Calculator MCP Server running successfully");
        } catch (error) {
            console.error("Fatal error during server startup:", error);
            if (error instanceof Error) {
                console.error("Error message:", error.message);
                console.error("Error stack:", error.stack);
            }
            process.exit(1);
        }
    }

    // Set up process error handlers
    process.on('unhandledRejection', (reason, promise) => {
        console.error('Unhandled Rejection at:', promise, 'reason:', reason);
    });

    process.on('uncaughtException', (error) => {
        console.error('Uncaught Exception:', error);
        if (error.stack) {
            console.error('Stack trace:', error.stack);
        }
        process.exit(1);
    });

    // Start the server
    console.error("Calling main function...");
    main().catch((error) => {
        console.error("Error in main function:", error);
        process.exit(1);
    });

} catch (error) {
    console.error("Top-level error:", error);
    if (error instanceof Error) {
        console.error("Error details:", error.message);
        console.error("Stack trace:", error.stack);
    }
    process.exit(1);
}