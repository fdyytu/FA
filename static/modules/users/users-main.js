// Users Main Controller
class UsersMainController {
    constructor() {
        this.dataService = new UsersDataService();
        this.uiController = new UsersUIController();
    }

    async initUsersDashboard() {
        const token = localStorage.getItem('authToken');
        if (!token) {
            window.location.href = '/login';
            return;
        }

        UIUtils.showLoading(true);
        
        try {
            await Promise.all([
                this.loadUserStats(),
                this.loadUsers()
            ]);
            
            this.initEventListeners();
            UIUtils.showToast('Dashboard users berhasil dimuat', 'success', 3000);
        } catch (error) {
            console.error('Error loading users dashboard:', error);
            UIUtils.showToast('Gagal memuat data users', 'error');
        } finally {
            UIUtils.showLoading(false);
        }
    }

    async loadUserStats() {
        const stats = await this.dataService.loadUserStats();
        this.uiController.updateUserStats(stats);
    }

    async loadUsers(page = 1, search = '') {
        const result = await this.dataService.loadUsers(page, search);
        this.uiController.renderUsersList(result.users);
        this.renderPagination(result.total, result.currentPage);
    }

    renderPagination(total, currentPage) {
        // Implementation for pagination rendering
        console.log(`Pagination: ${currentPage} of ${Math.ceil(total / this.dataService.data.itemsPerPage)}`);
    }

    initEventListeners() {
        // Add search functionality
        if (this.uiController.elements.searchInput) {
            this.uiController.elements.searchInput.addEventListener('input', (e) => {
                this.loadUsers(1, e.target.value);
            });
        }
    }
}

// Global instance
const usersMainController = new UsersMainController();
