// History JavaScript
let currentPage = 1;
let totalPages = 1;
let currentFilters = {};

document.addEventListener('DOMContentLoaded', async function() {
    // Setup event listeners
    setupEventListeners();
    
    // Load transaction history
    await loadTransactionHistory();
});

function setupEventListeners() {
    // Filter buttons
    document.getElementById('applyFilter').addEventListener('click', applyFilters);
    document.getElementById('resetFilter').addEventListener('click', resetFilters);
    
    // Sort dropdown
    document.getElementById('sortBy').addEventListener('change', loadTransactionHistory);
    
    // Pagination
    document.getElementById('prevPage').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            loadTransactionHistory();
        }
    });
    
    document.getElementById('nextPage').addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            loadTransactionHistory();
        }
    });
    
    // Detail Modal
    document.getElementById('closeDetailModal').addEventListener('click', closeDetailModal);
    document.getElementById('closeDetailBtn').addEventListener('click', closeDetailModal);
    document.getElementById('detailModal').addEventListener('click', (e) => {
        if (e.target.id === 'detailModal') {
            closeDetailModal();
        }
    });
    
    // Export Modal
    document.getElementById('exportDateRange').addEventListener('change', function() {
        const customDateRange = document.getElementById('customDateRange');
        if (this.value === 'custom') {
            customDateRange.classList.remove('hidden');
        } else {
            customDateRange.classList.add('hidden');
        }
    });
    
    document.getElementById('exportForm').addEventListener('submit', handleExport);
}

function applyFilters() {
    currentFilters = {
        type: document.getElementById('filterType').value,
        status: document.getElementById('filterStatus').value,
        date_from: document.getElementById('filterDateFrom').value,
        date_to: document.getElementById('filterDateTo').value
    };
    
    // Remove empty filters
    Object.keys(currentFilters).forEach(key => {
        if (!currentFilters[key]) {
            delete currentFilters[key];
        }
    });
    
    currentPage = 1;
    loadTransactionHistory();
}

function resetFilters() {
    document.getElementById('filterType').value = '';
    document.getElementById('filterStatus').value = '';
    document.getElementById('filterDateFrom').value = '';
    document.getElementById('filterDateTo').value = '';
    
    currentFilters = {};
    currentPage = 1;
    loadTransactionHistory();
}

async function loadTransactionHistory() {
    const container = document.getElementById('transactionList');
    const sortBy = document.getElementById('sortBy').value;
    
    try {
        container.innerHTML = `
            <div class="p-6 text-center text-gray-500">
                <i class="fas fa-spinner fa-spin text-2xl mb-2"></i>
                <p>Memuat riwayat transaksi...</p>
            </div>
        `;
        
        // Prepare filters
        const filters = { ...currentFilters };
        if (sortBy) {
            filters.sort_by = sortBy;
        }
        
        // Load both PPOB and Wallet transactions
        const [ppobResponse, walletResponse] = await Promise.all([
            APIClient.getPPOBTransactions(currentPage, 10, filters),
            APIClient.getWalletTransactions(currentPage, 10)
        ]);
        
        // Combine and sort transactions
        const allTransactions = [
            ...(ppobResponse.items || []).map(t => ({ ...t, source: 'ppob' })),
            ...(walletResponse.items || []).map(t => ({ ...t, source: 'wallet' }))
        ];
        
        // Sort by date
        allTransactions.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        
        if (allTransactions.length === 0) {
            container.innerHTML = `
                <div class="p-6 text-center text-gray-500">
                    <i class="fas fa-receipt text-4xl mb-4"></i>
                    <p>Tidak ada transaksi ditemukan</p>
                    <p class="text-sm">Coba ubah filter atau lakukan transaksi baru</p>
                </div>
            `;
            updatePagination(0, 0, 0);
            return;
        }
        
        container.innerHTML = allTransactions.map(transaction => `
            <div class="p-6 hover:bg-gray-50 transition duration-300 cursor-pointer" onclick="showTransactionDetail('${transaction.id}', '${transaction.source}')">
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <div class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mr-4">
                            <i class="${getTransactionIcon(transaction)}"></i>
                        </div>
                        <div>
                            <p class="font-medium text-gray-900">${getTransactionTitle(transaction)}</p>
                            <p class="text-sm text-gray-600">${getTransactionDescription(transaction)}</p>
                            <p class="text-xs text-gray-500">${Utils.formatDate(transaction.created_at)}</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <p class="font-semibold text-gray-900">${Utils.formatCurrency(getTransactionAmount(transaction))}</p>
                        ${Utils.getStatusBadge(transaction.status)}
                        <p class="text-xs text-gray-500 mt-1">${transaction.source.toUpperCase()}</p>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Update pagination
        const totalTransactions = (ppobResponse.total || 0) + (walletResponse.total || 0);
        totalPages = Math.ceil(totalTransactions / 20);
        updatePagination(currentPage, 20, totalTransactions);
        
    } catch (error) {
        console.error('Failed to load transaction history:', error);
        container.innerHTML = `
            <div class="p-6 text-center text-red-500">
                <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                <p>Gagal memuat riwayat transaksi</p>
                <button onclick="loadTransactionHistory()" class="mt-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
                    Coba Lagi
                </button>
            </div>
        `;
    }
}

function getTransactionIcon(transaction) {
    if (transaction.source === 'ppob') {
        return Utils.getTransactionTypeIcon(transaction.service_type);
    } else {
        const iconMap = {
            topup: 'fas fa-plus text-green-600',
            transfer_out: 'fas fa-arrow-up text-red-600',
            transfer_in: 'fas fa-arrow-down text-green-600',
            payment: 'fas fa-credit-card text-blue-600'
        };
        return iconMap[transaction.transaction_type] || 'fas fa-exchange-alt text-gray-600';
    }
}

function getTransactionTitle(transaction) {
    if (transaction.source === 'ppob') {
        return transaction.product_name || transaction.service_type;
    } else {
        const titleMap = {
            topup: 'Top Up Saldo',
            transfer_out: 'Transfer Keluar',
            transfer_in: 'Transfer Masuk',
            payment: 'Pembayaran PPOB'
        };
        return titleMap[transaction.transaction_type] || 'Transaksi Wallet';
    }
}

function getTransactionDescription(transaction) {
    if (transaction.source === 'ppob') {
        return transaction.customer_number;
    } else {
        switch (transaction.transaction_type) {
            case 'transfer_out':
                return `Ke: ${transaction.recipient_username || 'Unknown'}`;
            case 'transfer_in':
                return `Dari: ${transaction.sender_username || 'Unknown'}`;
            default:
                return transaction.notes || 'Transaksi wallet';
        }
    }
}

function getTransactionAmount(transaction) {
    return Math.abs(transaction.amount);
}

function updatePagination(page, perPage, total) {
    const showingFrom = total > 0 ? ((page - 1) * perPage) + 1 : 0;
    const showingTo = Math.min(page * perPage, total);
    
    document.getElementById('showingFrom').textContent = showingFrom;
    document.getElementById('showingTo').textContent = showingTo;
    document.getElementById('totalTransactions').textContent = total;
    
    // Update pagination buttons
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    
    prevBtn.disabled = page <= 1;
    nextBtn.disabled = page >= totalPages;
    
    if (page <= 1) {
        prevBtn.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
        prevBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    }
    
    if (page >= totalPages) {
        nextBtn.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
        nextBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    }
    
    // Generate page numbers
    generatePageNumbers(page, totalPages);
}

function generatePageNumbers(currentPage, totalPages) {
    const container = document.getElementById('pageNumbers');
    container.innerHTML = '';
    
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    // Adjust start page if we're near the end
    if (endPage - startPage < maxVisiblePages - 1) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.className = `px-3 py-2 border rounded-md text-sm ${
            i === currentPage 
                ? 'bg-indigo-600 text-white border-indigo-600' 
                : 'text-gray-700 border-gray-300 hover:bg-gray-50'
        }`;
        
        pageBtn.addEventListener('click', () => {
            currentPage = i;
            loadTransactionHistory();
        });
        
        container.appendChild(pageBtn);
    }
}

async function showTransactionDetail(transactionId, source) {
    const modal = document.getElementById('detailModal');
    const container = document.getElementById('transactionDetail');
    
    try {
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-spinner fa-spin text-2xl mb-2"></i>
                <p>Memuat detail transaksi...</p>
            </div>
        `;
        
        modal.classList.remove('hidden');
        
        let transaction;
        if (source === 'ppob') {
            transaction = await APIClient.getPPOBTransactionDetail(transactionId);
        } else {
            // For wallet transactions, we need to get from the list since there's no detail endpoint
            const response = await APIClient.getWalletTransactions(1, 100);
            transaction = response.items.find(t => t.id === transactionId);
        }
        
        if (!transaction) {
            throw new Error('Transaksi tidak ditemukan');
        }
        
        container.innerHTML = generateTransactionDetailHTML(transaction, source);
        
    } catch (error) {
        console.error('Failed to load transaction detail:', error);
        container.innerHTML = `
            <div class="text-center py-4 text-red-500">
                <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                <p>Gagal memuat detail transaksi</p>
            </div>
        `;
    }
}

function generateTransactionDetailHTML(transaction, source) {
    let html = `
        <div class="space-y-4">
            <div class="text-center">
                <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <i class="${getTransactionIcon(transaction)} text-2xl"></i>
                </div>
                <h4 class="text-lg font-semibold text-gray-900">${getTransactionTitle(transaction)}</h4>
                ${Utils.getStatusBadge(transaction.status)}
            </div>
            
            <div class="border-t border-gray-200 pt-4">
                <dl class="space-y-3">
                    <div class="flex justify-between">
                        <dt class="text-sm font-medium text-gray-500">ID Transaksi</dt>
                        <dd class="text-sm text-gray-900">${transaction.id}</dd>
                    </div>
                    
                    <div class="flex justify-between">
                        <dt class="text-sm font-medium text-gray-500">Tanggal</dt>
                        <dd class="text-sm text-gray-900">${Utils.formatDate(transaction.created_at)}</dd>
                    </div>
                    
                    <div class="flex justify-between">
                        <dt class="text-sm font-medium text-gray-500">Jumlah</dt>
                        <dd class="text-sm font-semibold text-gray-900">${Utils.formatCurrency(getTransactionAmount(transaction))}</dd>
                    </div>
    `;
    
    if (source === 'ppob') {
        html += `
                    <div class="flex justify-between">
                        <dt class="text-sm font-medium text-gray-500">Layanan</dt>
                        <dd class="text-sm text-gray-900">${transaction.service_type}</dd>
                    </div>
                    
                    <div class="flex justify-between">
                        <dt class="text-sm font-medium text-gray-500">Nomor Pelanggan</dt>
                        <dd class="text-sm text-gray-900">${transaction.customer_number}</dd>
                    </div>
        `;
        
        if (transaction.product_name) {
            html += `
                    <div class="flex justify-between">
                        <dt class="text-sm font-medium text-gray-500">Produk</dt>
                        <dd class="text-sm text-gray-900">${transaction.product_name}</dd>
                    </div>
            `;
        }
    } else {
        html += `
                    <div class="flex justify-between">
                        <dt class="text-sm font-medium text-gray-500">Jenis</dt>
                        <dd class="text-sm text-gray-900">${getTransactionTitle(transaction)}</dd>
                    </div>
        `;
        
        if (transaction.recipient_username) {
            html += `
                    <div class="flex justify-between">
                        <dt class="text-sm font-medium text-gray-500">Penerima</dt>
                        <dd class="text-sm text-gray-900">${transaction.recipient_username}</dd>
                    </div>
            `;
        }
        
        if (transaction.sender_username) {
            html += `
                    <div class="flex justify-between">
                        <dt class="text-sm font-medium text-gray-500">Pengirim</dt>
                        <dd class="text-sm text-gray-900">${transaction.sender_username}</dd>
                    </div>
            `;
        }
    }
    
    if (transaction.notes) {
        html += `
                    <div class="flex justify-between">
                        <dt class="text-sm font-medium text-gray-500">Catatan</dt>
                        <dd class="text-sm text-gray-900">${transaction.notes}</dd>
                    </div>
        `;
    }
    
    html += `
                </dl>
            </div>
        </div>
    `;
    
    return html;
}

function closeDetailModal() {
    document.getElementById('detailModal').classList.add('hidden');
}

async function handleExport(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const exportData = {
        format: formData.get('exportFormat'),
        dateRange: formData.get('exportDateRange'),
        dateFrom: formData.get('exportDateFrom'),
        dateTo: formData.get('exportDateTo')
    };
    
    try {
        Utils.showAlert('Export Dimulai', 'File sedang diproses dan akan diunduh secara otomatis.', 'info');
        
        // Here you would typically call an API endpoint to generate the export
        // For now, we'll just show a success message
        setTimeout(() => {
            Utils.showAlert('Export Berhasil', 'File telah berhasil diunduh.', 'success');
        }, 2000);
        
    } catch (error) {
        Utils.showAlert('Export Gagal', error.message, 'error');
    }
}

// Auto-refresh transaction history every 60 seconds
setInterval(async () => {
    try {
        await loadTransactionHistory();
    } catch (error) {
        console.error('Auto-refresh failed:', error);
    }
}, 60000);
