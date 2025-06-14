// Dashboard JavaScript
let currentUser = null;
let currentService = null;

document.addEventListener('DOMContentLoaded', async function() {
    // Initialize dashboard
    await initializeDashboard();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load dashboard data
    await loadDashboardData();
});

async function initializeDashboard() {
    try {
        // Get current user info
        currentUser = await APIClient.getCurrentUser();
        
        // Update user name in navigation
        document.getElementById('userName').textContent = currentUser.full_name;
        
    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
        Utils.showAlert('Error', 'Gagal memuat data pengguna', 'error');
    }
}

function setupEventListeners() {
    // Profile dropdown
    const profileDropdown = document.getElementById('profileDropdown');
    const profileMenu = document.getElementById('profileMenu');
    
    profileDropdown.addEventListener('click', (e) => {
        e.stopPropagation();
        profileMenu.classList.toggle('hidden');
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', () => {
        profileMenu.classList.add('hidden');
    });
    
    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);
    
    // PPOB Modal
    document.getElementById('closeModal').addEventListener('click', closePPOBModal);
    document.getElementById('ppobModal').addEventListener('click', (e) => {
        if (e.target.id === 'ppobModal') {
            closePPOBModal();
        }
    });
    
    // PPOB Form
    document.getElementById('inquiryBtn').addEventListener('click', handleInquiry);
    document.getElementById('ppobForm').addEventListener('submit', handlePayment);
}

async function loadDashboardData() {
    try {
        // Load wallet balance
        await loadWalletBalance();
        
        // Load transaction statistics
        await loadTransactionStats();
        
        // Load recent transactions
        await loadRecentTransactions();
        
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
    }
}

async function loadWalletBalance() {
    try {
        const balanceData = await APIClient.getWalletBalance();
        document.getElementById('userBalance').textContent = Utils.formatCurrency(balanceData.balance);
    } catch (error) {
        console.error('Failed to load wallet balance:', error);
        document.getElementById('userBalance').textContent = 'Rp 0';
    }
}

async function loadTransactionStats() {
    try {
        const stats = await APIClient.getPPOBStatistics();
        
        document.getElementById('successTransactions').textContent = stats.success_count || 0;
        document.getElementById('pendingTransactions').textContent = stats.pending_count || 0;
        document.getElementById('totalTransactions').textContent = stats.total_count || 0;
        
    } catch (error) {
        console.error('Failed to load transaction stats:', error);
        document.getElementById('successTransactions').textContent = '0';
        document.getElementById('pendingTransactions').textContent = '0';
        document.getElementById('totalTransactions').textContent = '0';
    }
}

async function loadRecentTransactions() {
    const container = document.getElementById('recentTransactions');
    
    try {
        const response = await APIClient.getPPOBTransactions(1, 5);
        const transactions = response.items || [];
        
        if (transactions.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <i class="fas fa-receipt text-4xl mb-4"></i>
                    <p>Belum ada transaksi</p>
                    <p class="text-sm">Mulai gunakan layanan PPOB untuk melihat riwayat transaksi</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = transactions.map(transaction => `
            <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition duration-300">
                <div class="flex items-center">
                    <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center mr-3">
                        <i class="${Utils.getTransactionTypeIcon(transaction.service_type)}"></i>
                    </div>
                    <div>
                        <p class="font-medium text-gray-900">${transaction.product_name || transaction.service_type}</p>
                        <p class="text-sm text-gray-600">${transaction.customer_number}</p>
                        <p class="text-xs text-gray-500">${Utils.formatDate(transaction.created_at)}</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="font-semibold text-gray-900">${Utils.formatCurrency(transaction.amount)}</p>
                    ${Utils.getStatusBadge(transaction.status)}
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Failed to load recent transactions:', error);
        container.innerHTML = `
            <div class="text-center py-8 text-red-500">
                <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                <p>Gagal memuat transaksi terbaru</p>
            </div>
        `;
    }
}

function openPPOBService(serviceType) {
    currentService = serviceType;
    const modal = document.getElementById('ppobModal');
    const modalTitle = document.getElementById('modalTitle');
    const customerNumberLabel = document.querySelector('label[for="customerNumber"]');
    const customerNumberInput = document.getElementById('customerNumber');
    const productSelection = document.getElementById('productSelection');
    const inquiryResult = document.getElementById('inquiryResult');
    const payBtn = document.getElementById('payBtn');
    
    // Reset form
    document.getElementById('ppobForm').reset();
    productSelection.classList.add('hidden');
    inquiryResult.classList.add('hidden');
    payBtn.classList.add('hidden');
    
    // Set modal title and labels based on service type
    const serviceConfig = {
        pulsa: {
            title: 'Isi Pulsa',
            label: 'Nomor Telepon',
            placeholder: '08xxxxxxxxxx',
            needsProduct: true
        },
        listrik: {
            title: 'Token Listrik',
            label: 'Nomor Meter / ID Pelanggan',
            placeholder: 'Masukkan nomor meter',
            needsProduct: true
        },
        pdam: {
            title: 'Tagihan PDAM',
            label: 'Nomor Pelanggan PDAM',
            placeholder: 'Masukkan nomor pelanggan',
            needsProduct: false
        },
        internet: {
            title: 'Tagihan Internet',
            label: 'Nomor Pelanggan / User ID',
            placeholder: 'Masukkan nomor pelanggan',
            needsProduct: false
        },
        bpjs: {
            title: 'Tagihan BPJS',
            label: 'Nomor Peserta BPJS',
            placeholder: 'Masukkan nomor peserta',
            needsProduct: false
        },
        multifinance: {
            title: 'Tagihan Multifinance',
            label: 'Nomor Kontrak',
            placeholder: 'Masukkan nomor kontrak',
            needsProduct: false
        }
    };
    
    const config = serviceConfig[serviceType] || serviceConfig.pulsa;
    modalTitle.textContent = config.title;
    customerNumberLabel.textContent = config.label;
    customerNumberInput.placeholder = config.placeholder;
    
    // Load products if needed
    if (config.needsProduct) {
        loadPPOBProducts(serviceType);
    }
    
    modal.classList.remove('hidden');
}

function closePPOBModal() {
    document.getElementById('ppobModal').classList.add('hidden');
    currentService = null;
}

async function loadPPOBProducts(serviceType) {
    const productSelection = document.getElementById('productSelection');
    const productSelect = document.getElementById('productCode');
    
    try {
        const products = await APIClient.getPPOBProducts(serviceType);
        
        productSelect.innerHTML = '<option value="">Pilih produk...</option>';
        products.forEach(product => {
            const option = document.createElement('option');
            option.value = product.code;
            option.textContent = `${product.name} - ${Utils.formatCurrency(product.price)}`;
            option.dataset.price = product.price;
            productSelect.appendChild(option);
        });
        
        productSelection.classList.remove('hidden');
        
    } catch (error) {
        console.error('Failed to load products:', error);
        Utils.showAlert('Error', 'Gagal memuat daftar produk', 'error');
    }
}

async function handleInquiry() {
    const customerNumber = document.getElementById('customerNumber').value;
    const productCode = document.getElementById('productCode').value;
    
    if (!customerNumber) {
        Utils.showAlert('Validasi', 'Nomor pelanggan wajib diisi', 'warning');
        return;
    }
    
    // For services that need product selection
    if (document.getElementById('productSelection').classList.contains('hidden') === false && !productCode) {
        Utils.showAlert('Validasi', 'Pilih produk terlebih dahulu', 'warning');
        return;
    }
    
    const inquiryBtn = document.getElementById('inquiryBtn');
    const originalText = inquiryBtn.textContent;
    
    try {
        inquiryBtn.disabled = true;
        inquiryBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Mengecek...';
        
        const inquiryData = {
            service_type: currentService,
            customer_number: customerNumber,
            product_code: productCode || null
        };
        
        const result = await APIClient.inquiryPPOB(inquiryData);
        
        // Display inquiry result
        displayInquiryResult(result);
        
    } catch (error) {
        Utils.showAlert('Inquiry Gagal', error.message, 'error');
    } finally {
        inquiryBtn.disabled = false;
        inquiryBtn.textContent = originalText;
    }
}

function displayInquiryResult(result) {
    const inquiryResult = document.getElementById('inquiryResult');
    const inquiryDetails = document.getElementById('inquiryDetails');
    const payBtn = document.getElementById('payBtn');
    
    let detailsHtml = '';
    
    if (result.customer_name) {
        detailsHtml += `<p><strong>Nama:</strong> ${result.customer_name}</p>`;
    }
    
    if (result.bill_amount) {
        detailsHtml += `<p><strong>Tagihan:</strong> ${Utils.formatCurrency(result.bill_amount)}</p>`;
    }
    
    if (result.admin_fee) {
        detailsHtml += `<p><strong>Biaya Admin:</strong> ${Utils.formatCurrency(result.admin_fee)}</p>`;
    }
    
    if (result.total_amount) {
        detailsHtml += `<p><strong>Total Bayar:</strong> ${Utils.formatCurrency(result.total_amount)}</p>`;
    }
    
    if (result.due_date) {
        detailsHtml += `<p><strong>Jatuh Tempo:</strong> ${Utils.formatDateOnly(result.due_date)}</p>`;
    }
    
    inquiryDetails.innerHTML = detailsHtml;
    inquiryResult.classList.remove('hidden');
    payBtn.classList.remove('hidden');
    
    // Store inquiry result for payment
    payBtn.dataset.inquiryResult = JSON.stringify(result);
}

async function handlePayment(event) {
    event.preventDefault();
    
    const payBtn = document.getElementById('payBtn');
    const inquiryResult = JSON.parse(payBtn.dataset.inquiryResult || '{}');
    
    if (!inquiryResult.total_amount) {
        Utils.showAlert('Error', 'Data inquiry tidak valid', 'error');
        return;
    }
    
    const originalText = payBtn.textContent;
    
    try {
        payBtn.disabled = true;
        payBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Memproses...';
        
        const paymentData = {
            service_type: currentService,
            customer_number: document.getElementById('customerNumber').value,
            product_code: document.getElementById('productCode').value || null,
            inquiry_data: inquiryResult
        };
        
        const result = await APIClient.paymentPPOB(paymentData);
        
        Utils.showAlert(
            'Pembayaran Berhasil!', 
            `Transaksi berhasil diproses. ID Transaksi: ${result.transaction_id}`, 
            'success'
        );
        
        // Close modal and refresh data
        closePPOBModal();
        await loadDashboardData();
        
    } catch (error) {
        Utils.showAlert('Pembayaran Gagal', error.message, 'error');
    } finally {
        payBtn.disabled = false;
        payBtn.textContent = originalText;
    }
}

function handleLogout() {
    if (confirm('Apakah Anda yakin ingin keluar?')) {
        TokenManager.removeToken();
        window.location.href = 'login.html';
    }
}

// Phone number formatting for pulsa service
document.addEventListener('DOMContentLoaded', function() {
    const customerNumberInput = document.getElementById('customerNumber');
    
    customerNumberInput.addEventListener('input', function(e) {
        if (currentService === 'pulsa') {
            let value = e.target.value.replace(/\D/g, '');
            
            // Ensure it starts with 08
            if (value.length > 0 && !value.startsWith('08')) {
                if (value.startsWith('8')) {
                    value = '0' + value;
                } else if (value.startsWith('62')) {
                    value = '0' + value.substring(2);
                }
            }
            
            // Limit length
            if (value.length > 13) {
                value = value.substring(0, 13);
            }
            
            e.target.value = value;
        }
    });
});

// Auto-refresh dashboard data every 30 seconds
setInterval(async () => {
    try {
        await loadWalletBalance();
        await loadTransactionStats();
    } catch (error) {
        console.error('Auto-refresh failed:', error);
    }
}, 30000);
