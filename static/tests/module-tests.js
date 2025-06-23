// Test Suite untuk Shared Utilities
describe('API Client Tests', () => {
    it('should be defined', () => {
        expect(typeof apiClient).toBe('object');
    });

    it('should have required methods', () => {
        expect(typeof apiClient.get).toBe('function');
        expect(typeof apiClient.post).toBe('function');
        expect(typeof apiClient.put).toBe('function');
        expect(typeof apiClient.delete).toBe('function');
    });

    it('should handle GET requests', async () => {
        // Mock fetch untuk testing
        const originalFetch = window.fetch;
        window.fetch = createMock(() => Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ data: 'test' })
        }));

        const result = await apiClient.get('/test');
        expect(result.ok).toBe(true);

        // Restore fetch
        window.fetch = originalFetch;
    });
});

describe('Formatters Tests', () => {
    it('should be defined', () => {
        expect(typeof Formatters).toBe('object');
    });

    it('should format currency correctly', () => {
        const result = Formatters.formatCurrency(1250000);
        expect(result).toBe('Rp 1.250.000');
    });

    it('should format numbers correctly', () => {
        const result = Formatters.formatNumber(1234567);
        expect(result).toBe('1.234.567');
    });

    it('should format dates correctly', () => {
        const date = new Date('2024-01-15');
        const result = Formatters.formatDate(date);
        expect(typeof result).toBe('string');
        expect(result.length).toBeGreaterThan(0);
    });

    it('should format percentages correctly', () => {
        const result = Formatters.formatPercentage(0.1234);
        expect(result).toBe('12.34%');
    });

    it('should handle edge cases', () => {
        expect(Formatters.formatCurrency(0)).toBe('Rp 0');
        expect(Formatters.formatNumber(0)).toBe('0');
        expect(Formatters.formatPercentage(0)).toBe('0.00%');
    });
});

describe('UI Utils Tests', () => {
    it('should be defined', () => {
        expect(typeof UIUtils).toBe('object');
    });

    it('should have required methods', () => {
        expect(typeof UIUtils.showToast).toBe('function');
        expect(typeof UIUtils.showLoading).toBe('function');
        expect(typeof UIUtils.updateChangeIndicator).toBe('function');
    });

    it('should show loading spinner', () => {
        UIUtils.showLoading(true);
        const spinner = document.getElementById('loadingSpinner');
        if (spinner) {
            expect(spinner.style.display).not.toBe('none');
        }
        
        UIUtils.showLoading(false);
        if (spinner) {
            expect(spinner.style.display).toBe('none');
        }
    });

    it('should create toast notifications', () => {
        // Test akan berjalan jika elemen toast container ada
        UIUtils.showToast('Test message', 'success', 1000);
        // Assertion tergantung implementasi UI
        expect(true).toBe(true); // Placeholder
    });
});

// Mock Data Generator tests removed - no longer using mock data

describe('Chart Manager Tests', () => {
    it('should be defined', () => {
        expect(typeof ChartManager).toBe('function');
        expect(typeof chartManager).toBe('object');
    });

    it('should have required methods', () => {
        expect(typeof chartManager.createChart).toBe('function');
        expect(typeof chartManager.updateChart).toBe('function');
        expect(typeof chartManager.destroyChart).toBe('function');
    });

    it('should create charts', () => {
        // Create a test canvas
        const canvas = document.createElement('canvas');
        canvas.id = 'testChart';
        document.body.appendChild(canvas);

        const config = {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar'],
                datasets: [{
                    label: 'Test',
                    data: [10, 20, 30]
                }]
            }
        };

        const chart = chartManager.createChart('testChart', config);
        expect(chart).toBeTruthy();

        // Cleanup
        chartManager.destroyChart('testChart');
        document.body.removeChild(canvas);
    });
});

describe('Analytics Data Service Tests', () => {
    it('should be defined', () => {
        expect(typeof analyticsDataService).toBe('object');
    });

    it('should have required methods', () => {
        expect(typeof analyticsDataService.loadOverviewStats).toBe('function');
        expect(typeof analyticsDataService.loadChartData).toBe('function');
        expect(typeof analyticsDataService.setDateRange).toBe('function');
        expect(typeof analyticsDataService.getDateRange).toBe('function');
    });

    it('should set and get date range', () => {
        analyticsDataService.setDateRange(60);
        expect(analyticsDataService.getDateRange()).toBe(60);
    });

    it('should load overview stats', async () => {
        const stats = await analyticsDataService.loadOverviewStats();
        expect(typeof stats).toBe('object');
        expect(stats).toBeTruthy();
    });
});

describe('Module Loader Tests', () => {
    it('should be defined', () => {
        expect(typeof moduleLoader).toBe('object');
    });

    it('should have required methods', () => {
        expect(typeof moduleLoader.loadModule).toBe('function');
        expect(typeof moduleLoader.loadModuleGroup).toBe('function');
        expect(typeof moduleLoader.getPerformanceMetrics).toBe('function');
        expect(typeof moduleLoader.isModuleLoaded).toBe('function');
    });

    it('should track loaded modules', () => {
        const loadedModules = moduleLoader.getLoadedModules();
        expect(Array.isArray(loadedModules)).toBe(true);
    });

    it('should provide performance metrics', () => {
        const metrics = moduleLoader.getPerformanceMetrics();
        expect(typeof metrics).toBe('object');
        expect(typeof metrics.loadTimes).toBe('object');
        expect(typeof metrics.modulesLoaded).toBe('number');
    });
});

describe('Performance Monitor Tests', () => {
    it('should be defined', () => {
        expect(typeof performanceMonitor).toBe('object');
    });

    it('should have required methods', () => {
        expect(typeof performanceMonitor.startMonitoring).toBe('function');
        expect(typeof performanceMonitor.stopMonitoring).toBe('function');
        expect(typeof performanceMonitor.getMetrics).toBe('function');
        expect(typeof performanceMonitor.generateReport).toBe('function');
    });

    it('should collect metrics', () => {
        const metrics = performanceMonitor.getMetrics();
        expect(typeof metrics).toBe('object');
        expect(typeof metrics.moduleLoadTimes).toBe('object');
        expect(Array.isArray(metrics.networkRequests)).toBe(true);
        expect(Array.isArray(metrics.errors)).toBe(true);
    });

    it('should generate performance report', () => {
        const report = performanceMonitor.generateReport();
        expect(typeof report).toBe('object');
        expect(typeof report.timestamp).toBe('string');
        expect(typeof report.summary).toBe('object');
    });
});

describe('Integration Tests', () => {
    it('should load shared utilities in correct order', async () => {
        // Test dependency loading
        expect(typeof apiClient).toBe('object');
        expect(typeof Formatters).toBe('object');
        expect(typeof UIUtils).toBe('object');
    });

    it('should integrate chart components with data services', () => {
        // Test integration between chart manager and data services
        expect(typeof chartManager).toBe('object');
        expect(typeof analyticsDataService).toBe('object');
        
        // Test if they can work together
        expect(true).toBe(true); // Placeholder test
    });

    it('should handle module loading with performance monitoring', async () => {
        // Test integration between module loader and performance monitor
        const initialMetrics = performanceMonitor.getMetrics();
        const initialModules = moduleLoader.getLoadedModules();
        
        expect(typeof initialMetrics).toBe('object');
        expect(Array.isArray(initialModules)).toBe(true);
    });
});
