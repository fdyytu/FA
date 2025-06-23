// Products Pagination Component
// Maksimal 50 baris per file

class ProductsPagination {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.totalItems = 0;
    }

    // Update table pagination info
    updateTableInfo() {
        const showingFrom = document.getElementById('showingFrom');
        const showingTo = document.getElementById('showingTo');
        const totalItemsElement = document.getElementById('totalItems');
        
        const startIndex = (this.currentPage - 1) * this.itemsPerPage + 1;
        const endIndex = Math.min(this.currentPage * this.itemsPerPage, this.totalItems);
        
        if (showingFrom) showingFrom.textContent = startIndex;
        if (showingTo) showingTo.textContent = endIndex;
        if (totalItemsElement) totalItemsElement.textContent = this.totalItems;
    }

    // Update pagination
    updatePagination() {
        const totalPages = Math.ceil(this.totalItems / this.itemsPerPage);
        const pageNumbers = document.getElementById('pageNumbers');
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');
        
        // Update prev/next buttons
        if (prevBtn) {
            prevBtn.disabled = this.currentPage === 1;
            prevBtn.onclick = () => this.goToPreviousPage();
        }
        
        if (nextBtn) {
            nextBtn.disabled = this.currentPage === totalPages;
            nextBtn.onclick = () => this.goToNextPage();
        }
        
        // Generate page numbers
        if (pageNumbers) {
            this.generatePageNumbers(pageNumbers, totalPages);
        }
    }

    // Generate page numbers HTML
    generatePageNumbers(container, totalPages) {
        let paginationHTML = '';
        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage < maxVisiblePages - 1) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
    }
}

// Export instance
window.productsPagination = new ProductsPagination();
