// Shared Module Loader
// Maksimal 50 baris per file

class SharedModuleLoader {
    static async loadAllModules() {
        const modules = [
            '/static/modules/shared/auth/auth-service.js',
            '/static/modules/shared/ui/ui-service.js',
            '/static/modules/shared/ui/notification-service.js',
            '/static/modules/shared/ui/ui-utils.js',
            '/static/modules/shared/api/api-service.js',
            '/static/modules/shared/utils/format-utils.js',
            '/static/modules/shared/utils/validation-utils.js'
        ];

        try {
            await Promise.all(modules.map(module => this.loadScript(module)));
            this.initializeSharedComponents();
            console.log('✅ Shared modules loaded successfully');
        } catch (error) {
            console.error('❌ Error loading shared modules:', error);
        }
    }

    static loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    static initializeSharedComponents() {
        if (typeof AuthService !== 'undefined') {
            AuthService.checkAuth();
            AuthService.initLogout();
        }
        
        if (typeof UIService !== 'undefined') {
            UIService.initMobileMenu();
            UIService.initNavigation();
        }
    }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    SharedModuleLoader.loadAllModules();
});

window.SharedModuleLoader = SharedModuleLoader;
