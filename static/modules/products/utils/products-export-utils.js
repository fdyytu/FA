// Products Export/Import Utils
// Maksimal 50 baris per file

class ProductsExportUtils {
    // Convert data to CSV
    convertToCSV(data) {
        if (data.length === 0) return '';
        
        const headers = ['ID', 'Nama', 'Kode', 'Kategori', 'Provider', 'Harga', 'Harga WL', 'Stok', 'Status', 'Aktif', 'Unggulan'];
        const rows = data.map(product => [
            product.id,
            product.name,
            product.code,
            product.category,
            product.provider,
            product.price,
            product.price_wl || '',
            product.stock_quantity,
            product.status,
            product.is_active ? 'Ya' : 'Tidak',
            product.is_featured ? 'Ya' : 'Tidak'
        ]);
        
        const csvContent = [headers, ...rows]
            .map(row => row.map(field => `"${field}"`).join(','))
            .join('\n');
        
        return csvContent;
    }

    // Download CSV file
    downloadCSV(csvContent, filename) {
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }

    // Export products
    exportProducts(products) {
        const csv = this.convertToCSV(products);
        this.downloadCSV(csv, 'products.csv');
        return products.length;
    }

    // Create file input for import
    createFileInput(onFileSelect) {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.csv,.xlsx,.xls';
        input.onchange = onFileSelect;
        return input;
    }
}

// Export instance
window.productsExportUtils = new ProductsExportUtils();
