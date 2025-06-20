// Module Loader - Sistem Lazy Loading untuk Modul
class ModuleLoader {
    constructor() {
        this.loadedModules = new Set();
        this.loadingPromises = new Map();
        this.dependencies = {
            // Shared utilities (harus dimuat pertama)
            'api-client': [],
            'formatters': [],
            'ui-utils': [],
            'mock-data': [],
            
            // Chart components
            'chart-manager': ['api-client', 'formatters', 'ui-utils'],
            'analytics-charts': ['chart-manager', 'mock-data'],
            
            // Analytics module
            'analytics-data-service': ['api-client', 'mock-data'],
            'analytics-ui-controller': ['ui-utils', 'formatters'],
            'analytics-main': ['analytics-data-service', 'analytics-ui-controller', 'analytics-charts'],
            
            // Android module
            'android-data-service': ['api-client', 'mock-data'],
            'android-ui-controller': ['ui-utils', 'formatters'],
            'android-chart-manager': ['chart-manager'],
            'android-main': ['android-data-service', 'android-ui-controller', 'android-chart-manager'],
            
            // Discord module
            'discord-data-service': ['api-client', 'mock-data'],
            'discord-data-service-extended': ['discord-data-service'],
            'discord-ui-controller': ['ui-utils', 'formatters'],
            'discord-bot-manager': ['discord-data-service'],
            'discord-main': ['discord-data-service-extended', 'discord-ui-controller', 'discord-bot-manager'],
            
            // Shared module
            'shared-auth-service': ['api-client'],
            'shared-ui-service': ['ui-utils'],
            'shared-api-service': ['api-client'],
            'shared-utilities-service': ['formatters'],
            'shared-main': ['shared-auth-service', 'shared-ui-service', 'shared-api-service', 'shared-utilities-service'],
            
            // Other modules
            'products-data-service': ['api-client', 'mock-data'],
            'products-ui-controller': ['ui-utils', 'formatters'],
            'products-main': ['products-data-service', 'products-ui-controller'],
            
            'users-data-service': ['api-client', 'mock-data'],
            'users-ui-controller': ['ui-utils', 'formatters'],
            'users-main': ['users-data-service', 'users-ui-controller'],
            
            'settings-data-service': ['api-client', 'mock-data'],
            'settings-ui-controller': ['ui-utils', 'formatters'],
            'settings-main': ['settings-data-service', 'settings-ui-controller'],
            
            'main-data-service': ['api-client', 'mock-data'],
            'main-ui-controller': ['ui-utils', 'formatters'],
            'main-controller': ['main-data-service', 'main-ui-controller'],
        };
        
        this.modulesPaths = {
            // Shared utilities
            'api-client': '/static/shared/js/api-client.js',
            'formatters': '/static/shared/js/formatters.js',
            'ui-utils': '/static/shared/js/ui-utils.js',
            'mock-data': '/static/shared/js/mock-data.js',
            
            // Chart components
            'chart-manager': '/static/components/charts/chart-manager.js',
            'analytics-charts': '/static/components/charts/analytics-charts.js',
            
            // Analytics module
            'analytics-data-service': '/static/modules/analytics/analytics-data-service.js',
            'analytics-ui-controller': '/static/modules/analytics/analytics-ui-controller.js',
            'analytics-main': '/static/modules/analytics/analytics-main.js',
            
            // Android module
            'android-data-service': '/static/modules/android/android-data-service.js',
            'android-ui-controller': '/static/modules/android/android-ui-controller.js',
            'android-chart-manager': '/static/modules/android/android-chart-manager.js',
            'android-main': '/static/modules/android/android-main.js',
            
            // Discord module
            'discord-data-service': '/static/modules/discord/discord-data-service.js',
            'discord-data-service-extended': '/static/modules/discord/discord-data-service-extended.js',
            'discord-ui-controller': '/static/modules/discord/discord-ui-controller.js',
            'discord-bot-manager': '/static/modules/discord/discord-bot-manager.js',
            'discord-main': '/static/modules/discord/discord-main.js',
            
            // Shared module
            'shared-auth-service': '/static/modules/shared/shared-auth-service.js',
            'shared-ui-service': '/static/modules/shared/shared-ui-service.js',
            'shared-api-service': '/static/modules/shared/shared-api-service.js',
            'shared-utilities-service': '/static/modules/shared/shared-utilities-service.js',
            'shared-main': '/static/modules/shared/shared-main.js',
            
            // Other modules
            'products-data-service': '/static/modules/products/products-data-service.js',
            'products-ui-controller': '/static/modules/products/products-ui-controller.js',
            'products-main': '/static/modules/products/products-main.js',
            
            'users-data-service': '/static/modules/users/users-data-service.js',
            'users-ui-controller': '/static/modules/users/users-ui-controller.js',
            'users-main': '/static/modules/users/users-main.js',
            
            'settings-data-service': '/static/modules/settings/settings-data-service.js',
            'settings-ui-controller': '/static/modules/settings/settings-ui-controller.js',
            'settings-main': '/static/modules/settings/settings-main.js',
            
            'main-data-service': '/static/modules/main/main-data-service.js',
            'main-ui-controller': '/static/modules/main/main-ui-controller.js',
            'main-controller': '/static/modules/main/main-controller.js',
        };
        
        this.performanceMetrics = {
            loadTimes: {},
            totalLoadTime: 0,
            modulesLoaded: 0
        };
    }

    async loadModule(moduleName) {
        // Jika modul sudah dimuat, return langsung
        if (this.loadedModules.has(moduleName)) {
            return Promise.resolve();
        }

        // Jika sedang dalam proses loading, return promise yang sama
        if (this.loadingPromises.has(moduleName)) {
            return this.loadingPromises.get(moduleName);
        }

        const startTime = performance.now();
        
        // Buat promise untuk loading modul ini
        const loadingPromise = this._loadModuleWithDependencies(moduleName, startTime);
        this.loadingPromises.set(moduleName, loadingPromise);
        
        try {
            await loadingPromise;
            this.loadedModules.add(moduleName);
            this.loadingPromises.delete(moduleName);
            
            const endTime = performance.now();
            this.performanceMetrics.loadTimes[moduleName] = endTime - startTime;
            this.performanceMetrics.modulesLoaded++;
            
            console.log(`✓ Module '${moduleName}' loaded in ${(endTime - startTime).toFixed(2)}ms`);
            
        } catch (error) {
            this.loadingPromises.delete(moduleName);
            console.error(`✗ Failed to load module '${moduleName}':`, error);
            throw error;
        }
    }

    async _loadModuleWithDependencies(moduleName, startTime) {
        // Load dependencies terlebih dahulu
        const dependencies = this.dependencies[moduleName] || [];
        
        if (dependencies.length > 0) {
            console.log(`Loading dependencies for '${moduleName}': [${dependencies.join(', ')}]`);
            await Promise.all(dependencies.map(dep => this.loadModule(dep)));
        }

        // Load modul utama
        return this._loadScript(moduleName);
    }

    async _loadScript(moduleName) {
        const scriptPath = this.modulesPaths[moduleName];
        
        if (!scriptPath) {
            throw new Error(`Module path not found for: ${moduleName}`);
        }

        return new Promise((resolve, reject) => {
            // Cek apakah script sudah ada
            const existingScript = document.querySelector(`script[src="${scriptPath}"]`);
            if (existingScript) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = scriptPath;
            script.async = true;
            
            script.onload = () => {
                console.log(`Script loaded: ${scriptPath}`);
                resolve();
            };
            
            script.onerror = () => {
                reject(new Error(`Failed to load script: ${scriptPath}`));
            };
            
            document.head.appendChild(script);
        });
    }

    async loadModuleGroup(groupName) {
        const groups = {
            'shared': ['api-client', 'formatters', 'ui-utils', 'mock-data'],
            'charts': ['chart-manager', 'analytics-charts'],
            'analytics': ['analytics-data-service', 'analytics-ui-controller', 'analytics-main'],
            'android': ['android-data-service', 'android-ui-controller', 'android-chart-manager', 'android-main'],
            'discord': ['discord-data-service', 'discord-data-service-extended', 'discord-ui-controller', 'discord-bot-manager', 'discord-main'],
            'products': ['products-data-service', 'products-ui-controller', 'products-main'],
            'users': ['users-data-service', 'users-ui-controller', 'users-main'],
            'settings': ['settings-data-service', 'settings-ui-controller', 'settings-main'],
            'main': ['main-data-service', 'main-ui-controller', 'main-controller'],
            'shared-module': ['shared-auth-service', 'shared-ui-service', 'shared-api-service', 'shared-utilities-service', 'shared-main']
        };

        const modules = groups[groupName];
        if (!modules) {
            throw new Error(`Module group not found: ${groupName}`);
        }

        console.log(`Loading module group: ${groupName}`);
        const startTime = performance.now();
        
        await Promise.all(modules.map(module => this.loadModule(module)));
        
        const endTime = performance.now();
        console.log(`✓ Module group '${groupName}' loaded in ${(endTime - startTime).toFixed(2)}ms`);
    }

    getPerformanceMetrics() {
        return {
            ...this.performanceMetrics,
            totalLoadTime: Object.values(this.performanceMetrics.loadTimes).reduce((sum, time) => sum + time, 0)
        };
    }

    getLoadedModules() {
        return Array.from(this.loadedModules);
    }

    isModuleLoaded(moduleName) {
        return this.loadedModules.has(moduleName);
    }

    // Preload modules untuk performance
    async preloadModules(moduleNames) {
        console.log(`Preloading modules: [${moduleNames.join(', ')}]`);
        return Promise.all(moduleNames.map(module => this.loadModule(module)));
    }

    // Reset loader (untuk testing)
    reset() {
        this.loadedModules.clear();
        this.loadingPromises.clear();
        this.performanceMetrics = {
            loadTimes: {},
            totalLoadTime: 0,
            modulesLoaded: 0
        };
    }
}

// Global module loader instance
const moduleLoader = new ModuleLoader();

// Helper functions untuk kemudahan penggunaan
window.loadModule = (moduleName) => moduleLoader.loadModule(moduleName);
window.loadModuleGroup = (groupName) => moduleLoader.loadModuleGroup(groupName);
window.getModuleMetrics = () => moduleLoader.getPerformanceMetrics();
