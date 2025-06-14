// Wallet JavaScript
let currentUser = null;
let currentTopUpType = null;

document.addEventListener('DOMContentLoaded', async function() {
    // Initialize wallet page
    await initializeWallet();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load wallet data
    await loadWalletData();
});

async function initializeWallet() {
    try {
        // Get current user info
        currentUser = await APIClient.getCurrentUser();
        
    } catch (error) {
        console.error('Failed to initialize wallet:', error);
        Utils.showAlert('Error', 'Gagal memuat data pengguna', 'error');
    }
}

function setupEventListeners() {
    // Top Up Modal
    document.getElementById('closeTopUpModal').addEventListener('click', closeTopUpModal);
    document.getElementById('topUpModal').addEventListener('click', (e) => {
        if (e.target.id === 'topUpModal') {
            closeTopUpModal();
        }
    });
    
    // Transfer Modal
    document.getElementById('closeTransferModal').addEventListener('click', closeTransferModal);
    document.getElementById('transferModal').addEventListener('click', (e) => {
        if (e.target.id === 'transferModal') {
            closeTransferModal();
        }
    });
    
    // Forms
    document.getElementById('topUpForm').addEventListener('submit', handleTopUp);
    document.getElementById('transferForm').addEventListener('submit', handleTransfer);
    
    // Filter
    document.getElementById('filterType').addEventListener('change', loadTransactionHistory);
}

async function loadWalletData() {
    try {
        // Load wallet balance
        await loadWalletBalance();
        
        // Load transaction history
        await loadTransactionHistory();
        
    } catch (error) {
        console.error('Failed to load wallet data:', error);
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

async function loadTransactionHistory() {
    const container = document.getElementById('transactionHistory');
    const filterType = document.getElementById('filterType').value;
    
    try {
        container.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-spinner fa-spin text-2xl mb-2"></i>
                <p>Memuat riwayat transaksi...</p>
            </div>
        `;
        
        const filters = {};
        if (filterType) {
            filters.transaction_type = filterType;
        }
        
        const response = await APIClient.getWalletTransactions(1, 20);
        const transactions = response.items || [];
        
        if (transactions.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <i class="fas fa-wallet text-4xl mb-4"></i>
                    <p>Belum ada transaksi wallet</p>
                    <p class="text-sm">Mulai dengan top up atau transfer untuk melihat riwayat</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = transactions.map(transaction => `
            <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition duration-300">
                <div class="flex items-center">
                    <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center mr-3">
                        <i class="${getWalletTransactionIcon(transaction.transaction_type)}"></i>
                    </div>
                    <div>
                        <p class="font-medium text-gray-900">${getTransactionTitle(transaction)}</p>
                        <p class="text-sm text-gray-600">${getTransactionDescription(transaction)}</p>
                        <p class="text-xs text-gray-500">${Utils.formatDate(transaction.created_at)}</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="font-semibold ${getAmountColor(transaction.transaction_type)}">
                        ${getAmountPrefix(transaction.transaction_type)}${Utils.formatCurrency(Math.abs(transaction.amount))}
                    </p>
                    ${Utils.getStatusBadge(transaction.status)}
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Failed to load transaction history:', error);
        container.innerHTML = `
            <div class="text-center py-8 text-red-500">
                <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                <p>Gagal memuat riwayat transaksi</p>
            </div>
        `;
    }
}

function getWalletTransactionIcon(type) {
    const iconMap = {
        topup: 'fas fa-plus text-green-600',
        transfer_out: 'fas fa-arrow-up text-red-600',
        transfer_in: 'fas fa-arrow-down text-green-600',
        payment: 'fas fa-credit-card text-blue-600',
        refund: 'fas fa-undo text-purple-600'
    };
    return iconMap[type] || 'fas fa-exchange-alt text-gray-600';
}

function getTransactionTitle(transaction) {
    const titleMap = {
        topup: 'Top Up Saldo',
        transfer_out: 'Transfer Keluar',
        transfer_in: 'Transfer Masuk',
        payment: 'Pembayaran PPOB',
        refund: 'Refund'
    };
    return titleMap[transaction.transaction_type] || 'Transaksi';
}

function getTransactionDescription(transaction) {
    switch (transaction.transaction_type) {
        case 'topup':
            return transaction.notes || 'Top up saldo wallet';
        case 'transfer_out':
            return `Ke: ${transaction.recipient_username || 'Unknown'}`;
        case 'transfer_in':
            return `Dari: ${transaction.sender_username || 'Unknown'}`;
        case 'payment':
            return transaction.notes || 'Pembayaran layanan PPOB';
        case 'refund':
            return transaction.notes || 'Refund transaksi';
        default:
            return transaction.notes || 'Transaksi wallet';
    }
}

function getAmountColor(type) {
    return ['transfer_in', 'topup', 'refund'].includes(type) ? 'text-green-600' : 'text-red-600';
}

function getAmountPrefix(type) {
    return ['transfer_in', 'topup', 'refund'].includes(type) ? '+' : '-';
}

function openTopUpModal(type) {
    currentTopUpType = type;
    const modal = document.getElementById('topUpModal');
    const modalTitle = document.getElementById('topUpModalTitle');
    const manualFields = document.getElementById('manualFields');
    const buttonText = document.getElementById('topUpButtonText');
    
    // Reset form
    document.getElementById('topUpForm').reset();
    manualFields.classList.add('hidden');
    
    if (type === 'manual') {
        modalTitle.textContent = 'Top Up via Transfer Bank';
        manualFields.classList.remove('hidden');
        buttonText.textContent = 'Buat Permintaan Top Up';
    } else {
        modalTitle.textContent = 'Top Up via Kartu Kredit/Debit';
        buttonText.textContent = 'Lanjut ke Pembayaran';
    }
    
    modal.classList.remove('hidden');
}

function closeTopUpModal() {
    document.getElementById('topUpModal').classList.add('hidden');
    currentTopUpType = null;
}

function openTransferModal() {
    const modal = document.getElementById('transferModal');
    document.getElementById('transferForm').reset();
    modal.classList.remove('hidden');
}

function closeTransferModal() {
    document.getElementById('transferModal').classList.add('hidden');
}

async function handleTopUp(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const amount = parseInt(formData.get('amount'));
    
    // Validation
    if (amount < 10000) {
        Utils.showAlert('Validasi', 'Minimal top up adalah Rp 10.000', 'warning');
        return;
    }
    
    const submitBtn = form.querySelector('button[type="submit"]');
    const buttonText = document.getElementById('topUpButtonText');
    const spinner = document.getElementById('topUpSpinner');
    
    try {
        // Show loading state
        submitBtn.disabled = true;
        spinner.classList.remove('hidden');
        
        let topupData = { amount };
        
        if (currentTopUpType === 'manual') {
            // Manual transfer - collect additional data
            topupData.bank_name = formData.get('bank_name');
            topupData.account_name = formData.get('account_name');
            topupData.account_number = formData.get('account_number');
            topupData.notes = formData.get('notes');
            
            buttonText.textContent = 'Membuat permintaan...';
            
            const result = await APIClient.createManualTopup(topupData);
            
            Utils.showAlert(
                'Permintaan Top Up Dibuat!',
                `Silakan transfer ke rekening yang tertera. Kode unik: ${result.unique_code}`,
                'success'
            );
            
        } else {
            // Midtrans payment
            buttonText.textContent = 'Memproses...';
            
            const result = await APIClient.createMidtransTopup(topupData);
            
            // Redirect to Midtrans payment page
            if (result.payment_url) {
                window.open(result.payment_url, '_blank');
                Utils.showAlert(
                    'Pembayaran Dibuat!',
                    'Silakan selesaikan pembayaran di tab yang baru dibuka.',
                    'info'
                );
            }
        }
        
        // Close modal and refresh data
        closeTopUpModal();
        await loadWalletData();
        
    } catch (error) {
        Utils.showAlert('Top Up Gagal', error.message, 'error');
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        spinner.classList.add('hidden');
        buttonText.textContent = currentTopUpType === 'manual' ? 'Buat Permintaan Top Up' : 'Lanjut ke Pembayaran';
    }
}

async function handleTransfer(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const transferData = {
        recipient_username: formData.get('recipient_username'),
        amount: parseInt(formData.get('amount')),
        notes: formData.get('notes')
    };
    
    // Validation
    if (transferData.amount < 1000) {
        Utils.showAlert('Validasi', 'Minimal transfer adalah Rp 1.000', 'warning');
        return;
    }
    
    if (!transferData.recipient_username) {
        Utils.showAlert('Validasi', 'Username penerima wajib diisi', 'warning');
        return;
    }
    
    const submitBtn = form.querySelector('button[type="submit"]');
    const buttonText = document.getElementById('transferButtonText');
    const spinner = document.getElementById('transferSpinner');
    
    try {
        // Show loading state
        submitBtn.disabled = true;
        buttonText.textContent = 'Memproses...';
        spinner.classList.remove('hidden');
        
        const result = await APIClient.transferMoney(transferData);
        
        Utils.showAlert(
            'Transfer Berhasil!',
            `Transfer sebesar ${Utils.formatCurrency(transferData.amount)} berhasil dikirim ke ${transferData.recipient_username}`,
            'success'
        );
        
        // Close modal and refresh data
        closeTransferModal();
        await loadWalletData();
        
    } catch (error) {
        Utils.showAlert('Transfer Gagal', error.message, 'error');
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        buttonText.textContent = 'Transfer Sekarang';
        spinner.classList.add('hidden');
    }
}

// Amount formatting
document.addEventListener('DOMContentLoaded', function() {
    const amountInputs = document.querySelectorAll('input[type="number"]');
    
    amountInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            // Remove any non-digit characters
            let value = e.target.value.replace(/\D/g, '');
            
            // Limit to reasonable amount (100 million)
            if (parseInt(value) > 100000000) {
                value = '100000000';
            }
            
            e.target.value = value;
        });
    });
});

// Auto-refresh wallet data every 30 seconds
setInterval(async () => {
    try {
        await loadWalletBalance();
    } catch (error) {
        console.error('Auto-refresh failed:', error);
    }
}, 30000);
