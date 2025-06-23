// Products Main Controller
// Maksimal 50 baris per file

class ProductsMainController {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.totalItems = 0;
    }

    // Initialize products dashboard
    async initProductsDashboard() {
        const token = checkAuth();
        if (!token) return;

        showLoading(true);
        
        try {
            await Promise.all([
                this.loadProductStats(),
                this.loadProducts()
            ]);
            
            this.initEventListeners();
            showToast('Dashboard produk berhasil dimuat', 'success', 3000);
        } catch (error) {
            console.error('Error loading products dashboard:', error);
            showToast('Gagal memuat data produk', 'error');
        } finally {
            showLoading(false);
        }
    }

    // Load product statistics
    async loadProductStats() {
        try {
            const stats = await productsApiService.loadProductStats();
            productsStatsUI.updateProductStats(stats);
        } catch (error) {
            console.error('Error loading product stats:', error);
            showError('Gagal memuat statistik produk');
            productsStatsUI.updateProductStats({
                total_products: 0,
                active_products: 0,
                low_stock_products: 0,
                total_categories: 0
            });
        }
    }

    // Load products
    async loadProducts() {
        const loadingElement = document.getElementById('loadingProducts');
        const tableContainer = document.getElementById('productsTableContainer');
        
        if (loadingElement) loadingElement.classList.remove('hidden');
        if (tableContainer) tableContainer.classList.add('hidden');
        
        try {
            const products = await productsApiService.loadProducts();
            productsDataHandler.setProducts(products);
        } catch (error) {
            console.error('Error loading products:', error);
        }
    }
}

// Export instance
window.productsMainController = new ProductsMainController();
