// Products Main Controller
class ProductsMainController {
    constructor() {
        this.dataService = new ProductsDataService();
        this.uiController = new ProductsUIController();
    }

    async initProductsDashboard() {
        const token = localStorage.getItem('authToken');
        if (!token) {
            window.location.href = '/login';
            return;
        }

        UIUtils.showLoading(true);
        
        try {
            await Promise.all([
                this.loadProductStats(),
                this.loadProducts()
            ]);
            
            this.initEventListeners();
            UIUtils.showToast('Dashboard products berhasil dimuat', 'success', 3000);
        } catch (error) {
            console.error('Error loading products dashboard:', error);
            UIUtils.showToast('Gagal memuat data products', 'error');
        } finally {
            UIUtils.showLoading(false);
        }
    }

    async loadProductStats() {
        const stats = await this.dataService.loadProductStats();
        this.uiController.updateProductStats(stats);
    }

    async loadProducts(page = 1, search = '', category = '') {
        const result = await this.dataService.loadProducts(page, search, category);
        this.uiController.renderProductsList(result.products);
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
                this.loadProducts(1, e.target.value);
            });
        }

        // Add category filter
        if (this.uiController.elements.categoryFilter) {
            this.uiController.elements.categoryFilter.addEventListener('change', (e) => {
                this.loadProducts(1, '', e.target.value);
            });
        }
    }
}

// Global instance
const productsMainController = new ProductsMainController();
