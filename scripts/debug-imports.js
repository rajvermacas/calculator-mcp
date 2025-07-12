#!/usr/bin/env node

// Debug script to test imports
console.log("Testing imports...");

try {
    const { McpServer } = await import("@modelcontextprotocol/sdk/server/mcp.js");
    console.log("✓ McpServer imported successfully");
    console.log("McpServer constructor:", typeof McpServer);
} catch (error) {
    console.error("✗ Failed to import McpServer:", error);
}

try {
    const { StdioServerTransport } = await import("@modelcontextprotocol/sdk/server/stdio.js");
    console.log("✓ StdioServerTransport imported successfully");
    console.log("StdioServerTransport constructor:", typeof StdioServerTransport);
} catch (error) {
    console.error("✗ Failed to import StdioServerTransport:", error);
}

try {
    const { z } = await import("zod");
    console.log("✓ zod imported successfully");
    console.log("z object:", typeof z);
} catch (error) {
    console.error("✗ Failed to import zod:", error);
}

console.log("\nNode version:", process.version);
console.log("Module type:", import.meta.url ? "ESM" : "CommonJS");