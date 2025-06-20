// Test Framework - Unit Testing untuk Modul
class TestFramework {
    constructor() {
        this.tests = new Map();
        this.results = [];
        this.isRunning = false;
        this.currentSuite = null;
        
        this.stats = {
            total: 0,
            passed: 0,
            failed: 0,
            skipped: 0,
            duration: 0
        };
    }

    // Membuat test suite
    describe(suiteName, callback) {
        console.log(`📋 Test Suite: ${suiteName}`);
        this.currentSuite = suiteName;
        
        if (!this.tests.has(suiteName)) {
            this.tests.set(suiteName, []);
        }
        
        callback();
        this.currentSuite = null;
    }

    // Membuat individual test
    it(testName, callback) {
        if (!this.currentSuite) {
            throw new Error('Test must be inside a describe block');
        }

        const test = {
            name: testName,
            callback: callback,
            suite: this.currentSuite,
            status: 'pending'
        };

        this.tests.get(this.currentSuite).push(test);
    }

    // Assertion methods
    expect(actual) {
        return {
            toBe: (expected) => {
                if (actual !== expected) {
                    throw new Error(`Expected ${actual} to be ${expected}`);
                }
                return true;
            },
            
            toEqual: (expected) => {
                if (JSON.stringify(actual) !== JSON.stringify(expected)) {
                    throw new Error(`Expected ${JSON.stringify(actual)} to equal ${JSON.stringify(expected)}`);
                }
                return true;
            },
            
            toBeTruthy: () => {
                if (!actual) {
                    throw new Error(`Expected ${actual} to be truthy`);
                }
                return true;
            },
            
            toBeFalsy: () => {
                if (actual) {
                    throw new Error(`Expected ${actual} to be falsy`);
                }
                return true;
            },
            
            toBeNull: () => {
                if (actual !== null) {
                    throw new Error(`Expected ${actual} to be null`);
                }
                return true;
            },
            
            toBeUndefined: () => {
                if (actual !== undefined) {
                    throw new Error(`Expected ${actual} to be undefined`);
                }
                return true;
            },
            
            toContain: (expected) => {
                if (Array.isArray(actual)) {
                    if (!actual.includes(expected)) {
                        throw new Error(`Expected array to contain ${expected}`);
                    }
                } else if (typeof actual === 'string') {
                    if (!actual.includes(expected)) {
                        throw new Error(`Expected string to contain ${expected}`);
                    }
                } else {
                    throw new Error('toContain can only be used with arrays or strings');
                }
                return true;
            },
            
            toHaveLength: (expected) => {
                if (!actual.length && actual.length !== 0) {
                    throw new Error(`Expected ${actual} to have length property`);
                }
                if (actual.length !== expected) {
                    throw new Error(`Expected length ${actual.length} to be ${expected}`);
                }
                return true;
            },
            
            toThrow: () => {
                if (typeof actual !== 'function') {
                    throw new Error('Expected a function');
                }
                
                let threw = false;
                try {
                    actual();
                } catch (e) {
                    threw = true;
                }
                
                if (!threw) {
                    throw new Error('Expected function to throw');
                }
                return true;
            }
        };
    }

    // Mock functions
    createMock(implementation = () => {}) {
        const mock = function(...args) {
            mock.calls.push(args);
            mock.callCount++;
            return implementation.apply(this, args);
        };
        
        mock.calls = [];
        mock.callCount = 0;
        mock.mockImplementation = (newImplementation) => {
            implementation = newImplementation;
            return mock;
        };
        mock.mockReturnValue = (value) => {
            implementation = () => value;
            return mock;
        };
        mock.mockResolvedValue = (value) => {
            implementation = () => Promise.resolve(value);
            return mock;
        };
        mock.mockRejectedValue = (error) => {
            implementation = () => Promise.reject(error);
            return mock;
        };
        
        return mock;
    }

    // Spy functions
    spyOn(object, method) {
        const originalMethod = object[method];
        const spy = this.createMock(originalMethod);
        
        spy.restore = () => {
            object[method] = originalMethod;
        };
        
        object[method] = spy;
        return spy;
    }

    // Run all tests
    async runAllTests() {
        console.log('🚀 Starting test execution...');
        this.isRunning = true;
        this.results = [];
        this.stats = { total: 0, passed: 0, failed: 0, skipped: 0, duration: 0 };
        
        const startTime = performance.now();
        
        for (const [suiteName, tests] of this.tests) {
            await this.runTestSuite(suiteName, tests);
        }
        
        const endTime = performance.now();
        this.stats.duration = endTime - startTime;
        this.isRunning = false;
        
        this.printResults();
        return this.getResults();
    }

    // Run specific test suite
    async runTestSuite(suiteName, tests) {
        console.log(`
📦 Running suite: ${suiteName}`);
        
        for (const test of tests) {
            await this.runSingleTest(test);
        }
    }

    // Run single test
    async runSingleTest(test) {
        this.stats.total++;
        const startTime = performance.now();
        
        try {
            await test.callback();
            const endTime = performance.now();
            
            test.status = 'passed';
            test.duration = endTime - startTime;
            this.stats.passed++;
            
            console.log(`  ✅ ${test.name} (${test.duration.toFixed(2)}ms)`);
            
        } catch (error) {
            const endTime = performance.now();
            
            test.status = 'failed';
            test.duration = endTime - startTime;
            test.error = error.message;
            this.stats.failed++;
            
            console.log(`  ❌ ${test.name} (${test.duration.toFixed(2)}ms)`);
            console.log(`     Error: ${error.message}`);
        }
        
        this.results.push({ ...test });
    }

    // Print test results
    printResults() {
        console.log('
📊 Test Results Summary:');
        console.log(`Total: ${this.stats.total}`);
        console.log(`✅ Passed: ${this.stats.passed}`);
        console.log(`❌ Failed: ${this.stats.failed}`);
        console.log(`⏭️ Skipped: ${this.stats.skipped}`);
        console.log(`⏱️ Duration: ${this.stats.duration.toFixed(2)}ms`);
        
        const successRate = this.stats.total > 0 ? 
            ((this.stats.passed / this.stats.total) * 100).toFixed(1) : 0;
        console.log(`📈 Success Rate: ${successRate}%`);
        
        if (this.stats.failed > 0) {
            console.log('
❌ Failed Tests:');
            this.results
                .filter(test => test.status === 'failed')
                .forEach(test => {
                    console.log(`  - ${test.suite} > ${test.name}: ${test.error}`);
                });
        }
    }

    // Get test results
    getResults() {
        return {
            stats: this.stats,
            results: this.results,
            summary: {
                successRate: this.stats.total > 0 ? 
                    ((this.stats.passed / this.stats.total) * 100).toFixed(1) : 0,
                averageTestTime: this.stats.total > 0 ? 
                    (this.stats.duration / this.stats.total).toFixed(2) : 0
            }
        };
    }

    // Setup and teardown hooks
    beforeEach(callback) {
        this.beforeEachCallback = callback;
    }

    afterEach(callback) {
        this.afterEachCallback = callback;
    }

    beforeAll(callback) {
        this.beforeAllCallback = callback;
    }

    afterAll(callback) {
        this.afterAllCallback = callback;
    }

    // Test utilities
    async waitFor(condition, timeout = 5000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            if (await condition()) {
                return true;
            }
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        throw new Error(`Condition not met within ${timeout}ms`);
    }

    // Generate test report
    generateReport() {
        const report = {
            timestamp: new Date().toISOString(),
            stats: this.stats,
            results: this.results,
            suites: {}
        };

        // Group results by suite
        for (const result of this.results) {
            if (!report.suites[result.suite]) {
                report.suites[result.suite] = {
                    total: 0,
                    passed: 0,
                    failed: 0,
                    tests: []
                };
            }
            
            const suite = report.suites[result.suite];
            suite.total++;
            suite[result.status]++;
            suite.tests.push(result);
        }

        return report;
    }

    // Export test results
    exportResults() {
        const report = this.generateReport();
        const data = JSON.stringify(report, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `test-results-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log('📁 Test results exported');
    }

    // Clear all tests
    clear() {
        this.tests.clear();
        this.results = [];
        this.stats = { total: 0, passed: 0, failed: 0, skipped: 0, duration: 0 };
    }
}

// Global test framework instance
const testFramework = new TestFramework();

// Global test functions
window.describe = (name, callback) => testFramework.describe(name, callback);
window.it = (name, callback) => testFramework.it(name, callback);
window.expect = (actual) => testFramework.expect(actual);
window.createMock = (implementation) => testFramework.createMock(implementation);
window.spyOn = (object, method) => testFramework.spyOn(object, method);
window.runTests = () => testFramework.runAllTests();
window.beforeEach = (callback) => testFramework.beforeEach(callback);
window.afterEach = (callback) => testFramework.afterEach(callback);
window.beforeAll = (callback) => testFramework.beforeAll(callback);
window.afterAll = (callback) => testFramework.afterAll(callback);
window.waitFor = (condition, timeout) => testFramework.waitFor(condition, timeout);
window.exportTestResults = () => testFramework.exportResults();
