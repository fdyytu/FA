// Shared Main Module
class SharedMain {
    constructor() {
        this.authService = new SharedAuthService();
        this.uiService = new SharedUIService();
        this.apiService = new SharedAPIService();
        this.utilitiesService = new SharedUtilitiesService();
    }

    // Initialize common functionality
    initSharedComponents() {
        this.authService.checkAuth();
        this.uiService.initMobileMenu();
        this.uiService.initNavigation();
        this.authService.initLogout();
    }

    // Get all services for external use
    getServices() {
        return {
            auth: this.authService,
            ui: this.uiService,
            api: this.apiService,
            utilities: this.utilitiesService
        };
    }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const sharedMain = new SharedMain();
    sharedMain.initSharedComponents();
    
    // Make services globally available
    window.DashboardShared = sharedMain.getServices();
});

// Export for use in other modules
window.SharedMain = SharedMain;
