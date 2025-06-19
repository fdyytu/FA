from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse, summary="Analytics Dashboard")
async def analytics_dashboard():
    """
    Menampilkan halaman dashboard analytics dengan visualisasi data.
    """
    return """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FA Analytics Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    </head>
    <body class="bg-gray-100">
        <!-- Dashboard HTML content -->
        <div class="min-h-screen">
            <!-- Header -->
            <header class="bg-white shadow-sm border-b">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between items-center py-6">
                        <div class="flex items-center">
                            <h1 class="text-3xl font-bold text-gray-900">
                                <i class="fas fa-chart-line text-blue-600 mr-3"></i>
                                FA Analytics Dashboard
                            </h1>
                        </div>
                        <div class="flex items-center space-x-4">
                            <select id="periodSelect" class="border border-gray-300 rounded-md px-3 py-2">
                                <option value="7">7 Hari Terakhir</option>
                                <option value="30" selected>30 Hari Terakhir</option>
                                <option value="90">90 Hari Terakhir</option>
                            </select>
                            <button onclick="refreshDashboard()" class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                                <i class="fas fa-sync-alt mr-2"></i>Refresh
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <!-- Main Content -->
            <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <!-- Loading Indicator -->
                <div id="loadingIndicator" class="text-center py-8">
                    <i class="fas fa-spinner fa-spin text-4xl text-blue-600"></i>
                    <p class="mt-2 text-gray-600">Memuat data dashboard...</p>
                </div>

                <!-- Dashboard Content -->
                <div id="dashboardContent" class="hidden">
                    <!-- Summary Cards -->
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        <!-- Summary cards content -->
                    </div>

                    <!-- Charts -->
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        <!-- Charts content -->
                    </div>
                </div>
            </main>
        </div>

        <script>
            // Dashboard JavaScript code
            let charts = {};
            
            async function loadDashboardData() {
                // Dashboard loading logic
                try {
                    const response = await fetch('/dashboard/summary?days=' + document.getElementById('periodSelect').value);
                    const data = await response.json();
                    
                    if (data.success) {
                        updateDashboard(data.data);
                    } else {
                        showError('Gagal memuat data dashboard');
                    }
                } catch (error) {
                    console.error('Error loading dashboard:', error);
                    showError('Terjadi kesalahan saat memuat dashboard');
                }
            }

            function updateDashboard(data) {
                // Update summary cards
                document.getElementById('totalRevenue').textContent = formatCurrency(data.total_revenue);
                document.getElementById('totalTransactions').textContent = formatNumber(data.total_transactions);
                document.getElementById('totalUsers').textContent = formatNumber(data.total_users);
                
                // Update charts
                updateCharts(data);
                
                // Show dashboard content
                document.getElementById('loadingIndicator').classList.add('hidden');
                document.getElementById('dashboardContent').classList.remove('hidden');
            }

            function refreshDashboard() {
                document.getElementById('loadingIndicator').classList.remove('hidden');
                document.getElementById('dashboardContent').classList.add('hidden');
                loadDashboardData();
            }

            // Helper functions
            function formatCurrency(amount) {
                return new Intl.NumberFormat('id-ID', { 
                    style: 'currency', 
                    currency: 'IDR' 
                }).format(amount);
            }

            function formatNumber(num) {
                return new Intl.NumberFormat('id-ID').format(num);
            }

            function showError(message) {
                // Implement error display logic
            }

            // Load dashboard on page load
            document.addEventListener('DOMContentLoaded', loadDashboardData);
        </script>
    </body>
    </html>
    """
