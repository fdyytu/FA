// Dashboard Utility Functions

// Initialize floating action button
function initFloatingActionButton() {
    const fab = document.querySelector('.floating-action-button');
    if (fab) {
        fab.addEventListener('click', () => {
            showQuickActionsMenu();
        });
    }
}

// Show quick actions menu
function showQuickActionsMenu() {
    const menu = document.createElement('div');
    menu.className = 'fixed bottom-20 right-6 bg-white rounded-lg shadow-xl p-4 z-50 animate-fade-in';
    menu.innerHTML = `
        <div class="space-y-2">
            <a href="dashboard_products.html" class="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">
                <i class="fas fa-plus mr-3 text-blue-600"></i>
                Tambah Produk
            </a>
            <a href="dashboard_discord.html" class="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">
                <i class="fab fa-discord mr-3 text-purple-600"></i>
                Kelola Discord
            </a>
            <a href="dashboard_users.html" class="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">
                <i class="fas fa-user-plus mr-3 text-green-600"></i>
                Tambah User
            </a>
            <button onclick="refreshAllData()" class="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg w-full text-left">
                <i class="fas fa-sync-alt mr-3 text-orange-600"></i>
                Refresh Semua Data
            </button>
        </div>
    `;
    
    document.body.appendChild(menu);
    
    // Remove menu when clicking outside
    setTimeout(() => {
        document.addEventListener('click', function removeMenu(e) {
            if (!menu.contains(e.target) && !e.target.closest('.floating-action-button')) {
                menu.remove();
                document.removeEventListener('click', removeMenu);
            }
        });
    }, 100);
}

// Refresh all data
async function refreshAllData() {
    showLoading(true);
    try {
        await Promise.all([
            refreshDashboard(),
            loadDiscordStats()
        ]);
        showToast('Semua data berhasil diperbarui', 'success', 3000);
    } catch (error) {
        showToast('Gagal memperbarui beberapa data', 'warning');
    } finally {
        showLoading(false);
    }
}
