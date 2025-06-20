// Performance Monitor - Sistem Monitoring Kinerja Modul
class PerformanceMonitor {
    constructor() {
        this.metrics = {
            moduleLoadTimes: {},
            pageLoadTime: 0,
            memoryUsage: {},
            networkRequests: [],
            errors: [],
            userInteractions: []
        };
        
        this.observers = [];
        this.startTime = performance.now();
        this.isMonitoring = false;
        
        this.init();
    }

    init() {
        // Monitor page load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.metrics.pageLoadTime = performance.now() - this.startTime;
                console.log(`📊 Page loaded in ${this.metrics.pageLoadTime.toFixed(2)}ms`);
            });
        }

        // Monitor memory usage (jika tersedia)
        if ('memory' in performance) {
            this.startMemoryMonitoring();
        }

        // Monitor network requests
        this.startNetworkMonitoring();
        
        // Monitor errors
        this.startErrorMonitoring();
    }

    startMonitoring() {
        this.isMonitoring = true;
        console.log('🔍 Performance monitoring started');
        
        // Monitor setiap 5 detik
        this.monitoringInterval = setInterval(() => {
            this.collectMetrics();
        }, 5000);
    }

    stopMonitoring() {
        this.isMonitoring = false;
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
        }
        console.log('⏹️ Performance monitoring stopped');
    }

    collectMetrics() {
        if (!this.isMonitoring) return;

        // Collect memory usage
        if ('memory' in performance) {
            this.metrics.memoryUsage[Date.now()] = {
                used: performance.memory.usedJSHeapSize,
                total: performance.memory.totalJSHeapSize,
                limit: performance.memory.jsHeapSizeLimit
            };
        }

        // Collect performance entries
        const entries = performance.getEntriesByType('navigation');
        if (entries.length > 0) {
            const navigation = entries[0];
            this.metrics.navigationTiming = {
                domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
                domInteractive: navigation.domInteractive - navigation.fetchStart,
                firstPaint: this.getFirstPaint()
            };
        }
    }

    getFirstPaint() {
        const paintEntries = performance.getEntriesByType('paint');
        const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
        return firstPaint ? firstPaint.startTime : null;
    }

    startMemoryMonitoring() {
        // Monitor memory setiap 10 detik
        setInterval(() => {
            if (this.isMonitoring && 'memory' in performance) {
                const memory = performance.memory;
                const timestamp = Date.now();
                
                this.metrics.memoryUsage[timestamp] = {
                    used: memory.usedJSHeapSize,
                    total: memory.totalJSHeapSize,
                    limit: memory.jsHeapSizeLimit,
                    percentage: (memory.usedJSHeapSize / memory.jsHeapSizeLimit * 100).toFixed(2)
                };

                // Warning jika memory usage tinggi
                const percentage = memory.usedJSHeapSize / memory.jsHeapSizeLimit * 100;
                if (percentage > 80) {
                    console.warn(`⚠️ High memory usage: ${percentage.toFixed(2)}%`);
                }
            }
        }, 10000);
    }

    startNetworkMonitoring() {
        // Monitor resource loading
        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.entryType === 'resource') {
                    this.metrics.networkRequests.push({
                        name: entry.name,
                        duration: entry.duration,
                        size: entry.transferSize || 0,
                        type: entry.initiatorType,
                        timestamp: entry.startTime
                    });

                    // Warning untuk request yang lambat
                    if (entry.duration > 1000) {
                        console.warn(`🐌 Slow request detected: ${entry.name} (${entry.duration.toFixed(2)}ms)`);
                    }
                }
            }
        });

        observer.observe({ entryTypes: ['resource'] });
        this.observers.push(observer);
    }

    startErrorMonitoring() {
        // Monitor JavaScript errors
        window.addEventListener('error', (event) => {
            this.metrics.errors.push({
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                timestamp: Date.now(),
                type: 'javascript'
            });
            
            console.error('🚨 JavaScript Error:', event.message);
        });

        // Monitor unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.metrics.errors.push({
                message: event.reason.toString(),
                timestamp: Date.now(),
                type: 'promise'
            });
            
            console.error('🚨 Unhandled Promise Rejection:', event.reason);
        });
    }

    recordModuleLoad(moduleName, loadTime, size = 0) {
        this.metrics.moduleLoadTimes[moduleName] = {
            loadTime: loadTime,
            size: size,
            timestamp: Date.now()
        };

        console.log(`📦 Module '${moduleName}' loaded in ${loadTime.toFixed(2)}ms`);
    }

    recordUserInteraction(action, element, timestamp = Date.now()) {
        this.metrics.userInteractions.push({
            action: action,
            element: element,
            timestamp: timestamp
        });
    }

    getMetrics() {
        return {
            ...this.metrics,
            summary: this.generateSummary()
        };
    }

    generateSummary() {
        const moduleLoadTimes = Object.values(this.metrics.moduleLoadTimes).map(m => m.loadTime);
        const networkRequests = this.metrics.networkRequests;
        
        return {
            totalModules: Object.keys(this.metrics.moduleLoadTimes).length,
            averageModuleLoadTime: moduleLoadTimes.length > 0 ? 
                (moduleLoadTimes.reduce((sum, time) => sum + time, 0) / moduleLoadTimes.length).toFixed(2) : 0,
            slowestModule: this.getSlowestModule(),
            totalNetworkRequests: networkRequests.length,
            totalNetworkTime: networkRequests.reduce((sum, req) => sum + req.duration, 0).toFixed(2),
            totalErrors: this.metrics.errors.length,
            memoryPeakUsage: this.getPeakMemoryUsage()
        };
    }

    getSlowestModule() {
        let slowest = null;
        let maxTime = 0;

        for (const [name, data] of Object.entries(this.metrics.moduleLoadTimes)) {
            if (data.loadTime > maxTime) {
                maxTime = data.loadTime;
                slowest = { name, loadTime: data.loadTime };
            }
        }

        return slowest;
    }

    getPeakMemoryUsage() {
        const memoryEntries = Object.values(this.metrics.memoryUsage);
        if (memoryEntries.length === 0) return null;

        return memoryEntries.reduce((peak, current) => {
            return current.used > peak.used ? current : peak;
        });
    }

    generateReport() {
        const metrics = this.getMetrics();
        const report = {
            timestamp: new Date().toISOString(),
            pageLoadTime: metrics.pageLoadTime,
            summary: metrics.summary,
            modulePerformance: this.analyzeModulePerformance(),
            networkPerformance: this.analyzeNetworkPerformance(),
            memoryAnalysis: this.analyzeMemoryUsage(),
            recommendations: this.generateRecommendations()
        };

        console.log('📊 Performance Report Generated:', report);
        return report;
    }

    analyzeModulePerformance() {
        const modules = this.metrics.moduleLoadTimes;
        const analysis = {
            totalModules: Object.keys(modules).length,
            fastModules: [],
            slowModules: [],
            averageLoadTime: 0
        };

        const loadTimes = Object.values(modules).map(m => m.loadTime);
        if (loadTimes.length > 0) {
            analysis.averageLoadTime = loadTimes.reduce((sum, time) => sum + time, 0) / loadTimes.length;
        }

        for (const [name, data] of Object.entries(modules)) {
            if (data.loadTime < 50) {
                analysis.fastModules.push({ name, loadTime: data.loadTime });
            } else if (data.loadTime > 200) {
                analysis.slowModules.push({ name, loadTime: data.loadTime });
            }
        }

        return analysis;
    }

    analyzeNetworkPerformance() {
        const requests = this.metrics.networkRequests;
        const analysis = {
            totalRequests: requests.length,
            totalSize: requests.reduce((sum, req) => sum + req.size, 0),
            totalTime: requests.reduce((sum, req) => sum + req.duration, 0),
            slowRequests: requests.filter(req => req.duration > 1000),
            largeRequests: requests.filter(req => req.size > 100000) // > 100KB
        };

        return analysis;
    }

    analyzeMemoryUsage() {
        const memoryEntries = Object.values(this.metrics.memoryUsage);
        if (memoryEntries.length === 0) return null;

        const latest = memoryEntries[memoryEntries.length - 1];
        const peak = this.getPeakMemoryUsage();

        return {
            current: latest,
            peak: peak,
            trend: this.getMemoryTrend(),
            warnings: latest.percentage > 80 ? ['High memory usage detected'] : []
        };
    }

    getMemoryTrend() {
        const entries = Object.values(this.metrics.memoryUsage);
        if (entries.length < 2) return 'insufficient_data';

        const first = entries[0];
        const last = entries[entries.length - 1];
        const change = ((last.used - first.used) / first.used) * 100;

        if (change > 10) return 'increasing';
        if (change < -10) return 'decreasing';
        return 'stable';
    }

    generateRecommendations() {
        const recommendations = [];
        const summary = this.generateSummary();

        // Module loading recommendations
        if (summary.averageModuleLoadTime > 100) {
            recommendations.push({
                type: 'module_performance',
                message: 'Consider optimizing slow-loading modules or implementing better caching',
                priority: 'high'
            });
        }

        // Memory recommendations
        const memoryAnalysis = this.analyzeMemoryUsage();
        if (memoryAnalysis && memoryAnalysis.current.percentage > 70) {
            recommendations.push({
                type: 'memory_usage',
                message: 'High memory usage detected. Consider implementing memory cleanup',
                priority: 'medium'
            });
        }

        // Network recommendations
        const networkAnalysis = this.analyzeNetworkPerformance();
        if (networkAnalysis.slowRequests.length > 0) {
            recommendations.push({
                type: 'network_performance',
                message: `${networkAnalysis.slowRequests.length} slow network requests detected`,
                priority: 'medium'
            });
        }

        return recommendations;
    }

    exportMetrics() {
        const data = JSON.stringify(this.getMetrics(), null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `performance-metrics-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log('📁 Performance metrics exported');
    }

    reset() {
        this.metrics = {
            moduleLoadTimes: {},
            pageLoadTime: 0,
            memoryUsage: {},
            networkRequests: [],
            errors: [],
            userInteractions: []
        };
        
        this.startTime = performance.now();
        console.log('🔄 Performance metrics reset');
    }

    destroy() {
        this.stopMonitoring();
        this.observers.forEach(observer => observer.disconnect());
        this.observers = [];
    }
}

// Global performance monitor instance
const performanceMonitor = new PerformanceMonitor();

// Helper functions
window.startPerformanceMonitoring = () => performanceMonitor.startMonitoring();
window.stopPerformanceMonitoring = () => performanceMonitor.stopMonitoring();
window.getPerformanceMetrics = () => performanceMonitor.getMetrics();
window.generatePerformanceReport = () => performanceMonitor.generateReport();
window.exportPerformanceMetrics = () => performanceMonitor.exportMetrics();
