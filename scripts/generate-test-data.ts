#!/usr/bin/env node

/**
 * Test data generation script for Calculator MCP Server
 * Generates various test cases for addition operations
 */

interface TestCase {
    name: string;
    num1: number;
    num2: number;
    expectedResult: number;
    description: string;
}

interface ErrorTestCase {
    name: string;
    num1: number;
    num2: number;
    expectedError: string;
    description: string;
}

/**
 * Generates valid test cases for addition
 */
function generateValidTestCases(): TestCase[] {
    return [
        {
            name: "basic_positive_addition",
            num1: 5,
            num2: 3,
            expectedResult: 8,
            description: "Basic addition of two positive integers"
        },
        {
            name: "negative_addition",
            num1: -10,
            num2: -5,
            expectedResult: -15,
            description: "Addition of two negative numbers"
        },
        {
            name: "mixed_sign_addition",
            num1: 15,
            num2: -7,
            expectedResult: 8,
            description: "Addition of positive and negative numbers"
        },
        {
            name: "decimal_addition",
            num1: 2.5,
            num2: 3.7,
            expectedResult: 6.2,
            description: "Addition of decimal numbers"
        },
        {
            name: "zero_addition",
            num1: 0,
            num2: 0,
            expectedResult: 0,
            description: "Addition with zeros"
        },
        {
            name: "large_numbers",
            num1: 999999999,
            num2: 1,
            expectedResult: 1000000000,
            description: "Addition of large numbers"
        },
        {
            name: "very_small_decimals",
            num1: 0.000001,
            num2: 0.000002,
            expectedResult: 0.000003,
            description: "Addition of very small decimal numbers"
        },
        {
            name: "max_safe_integer",
            num1: Number.MAX_SAFE_INTEGER,
            num2: 0,
            expectedResult: Number.MAX_SAFE_INTEGER,
            description: "Addition with maximum safe integer"
        },
        {
            name: "min_safe_integer",
            num1: Number.MIN_SAFE_INTEGER,
            num2: 0,
            expectedResult: Number.MIN_SAFE_INTEGER,
            description: "Addition with minimum safe integer"
        },
        {
            name: "floating_point_precision",
            num1: 0.1,
            num2: 0.2,
            expectedResult: 0.30000000000000004, // JavaScript floating point precision
            description: "Addition demonstrating floating point precision"
        }
    ];
}

/**
 * Generates error test cases for addition
 */
function generateErrorTestCases(): ErrorTestCase[] {
    return [
        {
            name: "infinity_input",
            num1: Infinity,
            num2: 5,
            expectedError: "Both inputs must be finite numbers",
            description: "Addition with Infinity input"
        },
        {
            name: "negative_infinity_input",
            num1: -Infinity,
            num2: 10,
            expectedError: "Both inputs must be finite numbers",
            description: "Addition with negative Infinity input"
        },
        {
            name: "nan_input_first",
            num1: NaN,
            num2: 5,
            expectedError: "Both inputs must be finite numbers",
            description: "Addition with NaN as first input"
        },
        {
            name: "nan_input_second",
            num1: 5,
            num2: NaN,
            expectedError: "Both inputs must be finite numbers",
            description: "Addition with NaN as second input"
        },
        {
            name: "both_nan_inputs",
            num1: NaN,
            num2: NaN,
            expectedError: "Both inputs must be finite numbers",
            description: "Addition with both inputs as NaN"
        }
    ];
}

/**
 * Generates random test cases for stress testing
 */
function generateRandomTestCases(count: number = 50): TestCase[] {
    const testCases: TestCase[] = [];
    
    for (let i = 0; i < count; i++) {
        const num1 = (Math.random() - 0.5) * 1000000; // Random number between -500000 and 500000
        const num2 = (Math.random() - 0.5) * 1000000;
        const expectedResult = num1 + num2;
        
        testCases.push({
            name: `random_case_${i + 1}`,
            num1: Math.round(num1 * 100) / 100, // Round to 2 decimal places
            num2: Math.round(num2 * 100) / 100,
            expectedResult: Math.round(expectedResult * 100) / 100,
            description: `Random test case ${i + 1}`
        });
    }
    
    return testCases;
}

/**
 * Main function to generate and export test data
 */
function generateTestData() {
    const validTestCases = generateValidTestCases();
    const errorTestCases = generateErrorTestCases();
    const randomTestCases = generateRandomTestCases(25);
    
    const testData = {
        metadata: {
            generatedAt: new Date().toISOString(),
            totalValidCases: validTestCases.length,
            totalErrorCases: errorTestCases.length,
            totalRandomCases: randomTestCases.length,
            description: "Test data for Calculator MCP Server addition functionality"
        },
        validTestCases,
        errorTestCases,
        randomTestCases
    };
    
    return testData;
}

// Export for use in tests
export { generateTestData, TestCase, ErrorTestCase };

// If run directly, output test data
if (import.meta.url === `file://${process.argv[1]}`) {
    const testData = generateTestData();
    console.log("Calculator MCP Server Test Data");
    console.log("================================");
    console.log();
    console.log("Valid Test Cases:", testData.validTestCases.length);
    console.log("Error Test Cases:", testData.errorTestCases.length);
    console.log("Random Test Cases:", testData.randomTestCases.length);
    console.log();
    console.log("Sample Valid Test Cases:");
    testData.validTestCases.slice(0, 3).forEach(testCase => {
        console.log(`- ${testCase.name}: ${testCase.num1} + ${testCase.num2} = ${testCase.expectedResult}`);
    });
    console.log();
    console.log("Sample Error Test Cases:");
    testData.errorTestCases.slice(0, 2).forEach(testCase => {
        console.log(`- ${testCase.name}: Expected error: "${testCase.expectedError}"`);
    });
    console.log();
    console.log("Full test data exported to variable for programmatic use");
}