// Main Module Loader
// Maksimal 50 baris per file

class MainModuleLoader {
    static async loadAllModules() {
        const modules = [
            // Load shared modules first
            '/static/modules/shared/shared-module-loader.js',
            // Load main specific modules
            '/static/modules/main/api/main-api-service.js',
            '/static/modules/main/ui/main-ui-service.js',
            '/static/modules/main/bridge/main-bridge-service.js',
            '/static/modules/main/main-controller.js'
        ];

        try {
            // Load shared modules first
            await this.loadScript('/static/modules/shared/shared-module-loader.js');
            
            // Wait for shared modules to load
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Load main specific modules
            const mainModules = modules.slice(1);
            await Promise.all(mainModules.map(module => this.loadScript(module)));
            
            this.initializeMainDashboard();
            console.log('✅ Main modules loaded successfully');
        } catch (error) {
            console.error('❌ Error loading main modules:', error);
        }
    }

    static loadScript(src) {
        return new Promise((resolve, reject) => {
            // Check if script already loaded
            if (document.querySelector(`script[src="${src}"]`)) {
                resolve();
                return;
            }
            
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    static initializeMainDashboard() {
        // Use bridge initialization if available, fallback to original
        if (window.DashboardBridge) {
            MainController.initDashboardWithBridge();
            MainBridgeService.loadDiscordStatsWithBridge();
        } else {
            MainController.initDashboard();
            if (window.loadDiscordStats) {
                window.loadDiscordStats();
            }
        }
        
        // Auto-refresh every 15 seconds
        setInterval(() => {
            if (window.DashboardBridge && window.DashboardBridge.isInitialized) {
                MainBridgeService.refreshDashboardWithBridge();
                MainBridgeService.loadDiscordStatsWithBridge();
            } else {
                MainController.initDashboard();
                if (window.loadDiscordStats) {
                    window.loadDiscordStats();
                }
            }
        }, 15 * 1000);
    }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    MainModuleLoader.loadAllModules();
});

window.MainModuleLoader = MainModuleLoader;
