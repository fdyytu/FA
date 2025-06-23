// Android Module Loader
// Maksimal 50 baris per file

class AndroidModuleLoader {
    static async loadAllModules() {
        const modules = [
            // Load shared modules first
            '/static/modules/shared/shared-module-loader.js',
            // Load android specific modules
            '/static/modules/android/api/android-api-service.js',
            '/static/modules/android/ui/android-ui-service.js',
            '/static/modules/android/charts/android-chart-service.js',
            '/static/modules/android/android-main-controller.js'
        ];

        try {
            // Load shared modules first
            await this.loadScript('/static/modules/shared/shared-module-loader.js');
            
            // Wait for shared modules to load
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Load android specific modules
            const androidModules = modules.slice(1);
            await Promise.all(androidModules.map(module => this.loadScript(module)));
            
            console.log('✅ Android modules loaded successfully');
        } catch (error) {
            console.error('❌ Error loading android modules:', error);
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
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    AndroidModuleLoader.loadAllModules();
});

window.AndroidModuleLoader = AndroidModuleLoader;
