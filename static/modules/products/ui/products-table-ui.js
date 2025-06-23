// Products Table UI Components
// Maksimal 50 baris per file

class ProductsTableUI {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.totalItems = 0;
    }

    // Render products table
    renderProductsTable(products) {
        const tbody = document.getElementById('productsTableBody');
        if (!tbody) return;
        
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageProducts = products.slice(startIndex, endIndex);
        
        tbody.innerHTML = pageProducts.map(product => `
            <tr class="table-row">
                <td class="px-6 py-4 whitespace-nowrap">
                    <input type="checkbox" class="product-checkbox rounded border-gray-300" value="${product.id}">
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="flex-shrink-0 h-10 w-10">
                            <div class="h-10 w-10 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                                <i class="fas fa-box text-white text-sm"></i>
                            </div>
                        </div>
                        <div class="ml-4">
                            <div class="text-sm font-medium text-gray-900">${product.name}</div>
                            <div class="text-sm text-gray-500">${product.code}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        ${product.category.replace('_', ' ').toUpperCase()}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">${formatCurrency(product.price)}</div>
                    ${product.price_wl ? `<div class="text-xs text-gray-500">WL: ${formatCurrency(product.price_wl)}</div>` : ''}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">${formatNumber(product.stock_quantity)}</div>
                    ${product.stock_quantity < 10 ? '<div class="text-xs text-red-500">Stok rendah</div>' : ''}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    ${this.getStatusBadge(product.status)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    ${this.renderActionButtons(product.id)}
                </td>
            </tr>
        `).join('');
        
        this.updateTableInfo();
    }
}

// Export instance
window.productsTableUI = new ProductsTableUI();
