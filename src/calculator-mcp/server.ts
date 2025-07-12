#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

/**
 * Calculator MCP Server
 * A simple MCP server that provides addition functionality
 */
export class CalculatorMcpServer {
    private server: McpServer;

    constructor() {
        this.server = new McpServer({
            name: "calculator-mcp-server",
            version: "1.0.0",
            description: "A simple MCP server for adding two numbers"
        });

        this.setupTools();
        this.setupErrorHandling();
    }

    /**
     * Sets up the addition tool
     */
    private setupTools(): void {
        console.log("Setting up calculator tools...");

        this.server.tool(
            "addNumbers",
            {
                description: "Add two numbers together and return the sum",
                inputSchema: z.object({
                    num1: z.number().describe("The first number to add"),
                    num2: z.number().describe("The second number to add")
                })
            },
            async ({ num1, num2 }) => {
                try {
                    console.log(`Adding ${num1} + ${num2}`);
                    
                    // Validate inputs
                    if (!Number.isFinite(num1) || !Number.isFinite(num2)) {
                        throw new Error("Both inputs must be finite numbers");
                    }

                    const result = num1 + num2;
                    console.log(`Result: ${result}`);

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
                    console.error("Error in addNumbers tool:", error);
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

        console.log("Calculator tools setup complete");
    }

    /**
     * Sets up error handling for the server
     */
    private setupErrorHandling(): void {
        process.on('unhandledRejection', (reason, promise) => {
            console.error('Unhandled Rejection at:', promise, 'reason:', reason);
        });

        process.on('uncaughtException', (error) => {
            console.error('Uncaught Exception:', error);
            process.exit(1);
        });
    }

    /**
     * Starts the MCP server with stdio transport
     */
    async start(): Promise<void> {
        try {
            console.log("Starting Calculator MCP Server...");
            const transport = new StdioServerTransport();
            await this.server.connect(transport);
            console.log("Calculator MCP Server started successfully");
        } catch (error) {
            console.error("Failed to start Calculator MCP Server:", error);
            process.exit(1);
        }
    }
}

/**
 * Main function to run the server
 */
async function main(): Promise<void> {
    const server = new CalculatorMcpServer();
    await server.start();
}

// Start the server if this file is run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch((error) => {
        console.error("Fatal error:", error);
        process.exit(1);
    });
}