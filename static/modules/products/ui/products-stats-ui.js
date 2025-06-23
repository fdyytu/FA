// Products Stats UI Components
// Maksimal 50 baris per file

class ProductsStatsUI {
    // Update product statistics cards
    updateProductStats(stats) {
        const elements = {
            totalProducts: document.getElementById('totalProducts'),
            activeProducts: document.getElementById('activeProducts'),
            lowStockProducts: document.getElementById('lowStockProducts'),
            totalCategories: document.getElementById('totalCategories')
        };
        
        if (elements.totalProducts) {
            elements.totalProducts.textContent = formatNumber(stats.total_products || 0);
        }
        
        if (elements.activeProducts) {
            elements.activeProducts.textContent = formatNumber(stats.active_products || 0);
        }
        
        if (elements.lowStockProducts) {
            elements.lowStockProducts.textContent = formatNumber(stats.low_stock_products || 0);
        }
        
        if (elements.totalCategories) {
            elements.totalCategories.textContent = formatNumber(stats.total_categories || 0);
        }
    }

    // Get status badge HTML
    getStatusBadge(status) {
        const statusConfig = {
            'active': { class: 'bg-green-100 text-green-800', text: 'Aktif' },
            'inactive': { class: 'bg-red-100 text-red-800', text: 'Tidak Aktif' },
            'out_of_stock': { class: 'bg-yellow-100 text-yellow-800', text: 'Stok Habis' },
            'discontinued': { class: 'bg-gray-100 text-gray-800', text: 'Dihentikan' }
        };
        
        const config = statusConfig[status] || statusConfig['inactive'];
        return `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.class}">
            ${config.text}
        </span>`;
    }

    // Render action buttons
    renderActionButtons(productId) {
        return `
            <div class="flex space-x-2">
                <button onclick="editProduct(${productId})" class="text-blue-600 hover:text-blue-900" title="Edit">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="uploadStock(${productId})" class="text-green-600 hover:text-green-900" title="Upload Stock">
                    <i class="fas fa-upload"></i>
                </button>
                <button onclick="deleteProduct(${productId})" class="text-red-600 hover:text-red-900" title="Hapus">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
    }
}

// Export instance
window.productsStatsUI = new ProductsStatsUI();
