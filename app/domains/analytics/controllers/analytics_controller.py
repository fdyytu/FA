from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.domains.analytics.services.analytics_service import AnalyticsService
from app.domains.analytics.schemas.analytics_schemas import (
    AnalyticsEventCreate, AnalyticsEventResponse, AnalyticsFilter,
    DashboardSummary, ChartData, AnalyticsReport, PerformanceMetricsResponse,
    GeographicDataResponse, RecentActivityResponse, RecentActivityItem
)
from app.core.database import get_db
from app.shared.responses.api_response import create_response
from app.shared.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    """Dependency untuk mendapatkan AnalyticsService"""
    return AnalyticsService(db)

@router.post("/events", response_model=dict, summary="Track Analytics Event")
async def track_event(
    event_data: AnalyticsEventCreate,
    request: Request,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Track event analytics baru.
    
    - **event_type**: Tipe event (product_view, product_purchase, etc.)
    - **user_id**: ID user (optional)
    - **product_id**: ID produk (optional)
    - **amount**: Jumlah uang terkait (optional)
    """
    try:
        # Auto-populate IP address if not provided
        if not event_data.ip_address:
            event_data.ip_address = request.client.host
        
        # Auto-populate user agent if not provided
        if not event_data.user_agent:
            event_data.user_agent = request.headers.get("user-agent")
        
        event = await service.track_event(event_data)
        
        return create_response(
            success=True,
            message="Event analytics berhasil ditrack",
            data={"event_id": event.id, "event_type": event.event_type}
        )
        
    except Exception as e:
        logger.error(f"Error tracking analytics event: {e}")
        raise HTTPException(status_code=500, detail="Gagal melakukan tracking event")

@router.get("/events", response_model=dict, summary="Get Analytics Events")
async def get_events(
    start_date: Optional[datetime] = Query(None, description="Tanggal mulai filter"),
    end_date: Optional[datetime] = Query(None, description="Tanggal akhir filter"),
    event_type: Optional[str] = Query(None, description="Filter berdasarkan tipe event"),
    user_id: Optional[int] = Query(None, description="Filter berdasarkan user ID"),
    product_id: Optional[int] = Query(None, description="Filter berdasarkan product ID"),
    voucher_id: Optional[int] = Query(None, description="Filter berdasarkan voucher ID"),
    limit: int = Query(100, ge=1, le=1000, description="Jumlah maksimal data"),
    offset: int = Query(0, ge=0, description="Offset untuk pagination"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Mendapatkan daftar events analytics berdasarkan filter.
    
    Mendukung filtering berdasarkan:
    - Tanggal (start_date, end_date)
    - Tipe event
    - User ID
    - Product ID
    - Voucher ID
    """
    try:
        filter_params = AnalyticsFilter(
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            user_id=user_id,
            product_id=product_id,
            voucher_id=voucher_id
        )
        
        events = await service.get_events(filter_params, limit, offset)
        
        # Convert to response format
        events_data = []
        for event in events:
            events_data.append({
                "id": event.id,
                "event_type": event.event_type,
                "user_id": event.user_id,
                "product_id": event.product_id,
                "voucher_id": event.voucher_id,
                "amount": float(event.amount) if event.amount else None,
                "event_timestamp": event.event_timestamp.isoformat(),
                "ip_address": event.ip_address
            })
        
        return create_response(
            success=True,
            message="Data events analytics berhasil diambil",
            data={
                "events": events_data,
                "total": len(events_data),
                "limit": limit,
                "offset": offset
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics events: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil data events")

@router.get("/dashboard/summary", response_model=dict, summary="Get Dashboard Summary")
async def get_dashboard_summary(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Mendapatkan summary data untuk dashboard analytics.
    
    Menampilkan:
    - Total revenue
    - Total transaksi
    - Total users
    - Growth metrics
    - Top products dan vouchers
    """
    try:
        summary = await service.get_dashboard_summary(days)
        
        return create_response(
            success=True,
            message="Dashboard summary berhasil diambil",
            data={
                "total_revenue": float(summary.total_revenue),
                "total_transactions": summary.total_transactions,
                "total_users": summary.total_users,
                "total_products": summary.total_products,
                "revenue_growth": float(summary.revenue_growth) if summary.revenue_growth else None,
                "transaction_growth": float(summary.transaction_growth) if summary.transaction_growth else None,
                "user_growth": float(summary.user_growth) if summary.user_growth else None,
                "top_products": summary.top_products,
                "top_vouchers": summary.top_vouchers,
                "period_days": days
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil dashboard summary")

@router.get("/charts/revenue", response_model=dict, summary="Get Revenue Chart Data")
async def get_revenue_chart(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis"),
    group_by: str = Query("day", regex="^(day|week|month)$", description="Grouping periode"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Mendapatkan data chart untuk revenue trend.
    
    - **days**: Periode analisis dalam hari
    - **group_by**: Grouping data (day, week, month)
    """
    try:
        chart_data = await service.get_revenue_chart_data(days, group_by)
        
        return create_response(
            success=True,
            message="Data chart revenue berhasil diambil",
            data={
                "title": chart_data.title,
                "chart_type": chart_data.chart_type,
                "labels": chart_data.labels,
                "datasets": chart_data.datasets
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting revenue chart: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil data chart revenue")

@router.get("/charts/products", response_model=dict, summary="Get Product Performance Chart")
async def get_product_chart(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Mendapatkan data chart untuk performa produk.
    
    Menampilkan top products berdasarkan revenue.
    """
    try:
        chart_data = await service.get_product_performance_chart(days)
        
        return create_response(
            success=True,
            message="Data chart produk berhasil diambil",
            data={
                "title": chart_data.title,
                "chart_type": chart_data.chart_type,
                "labels": chart_data.labels,
                "datasets": chart_data.datasets
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting product chart: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil data chart produk")

@router.get("/charts/vouchers", response_model=dict, summary="Get Voucher Usage Chart")
async def get_voucher_chart(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Mendapatkan data chart untuk penggunaan voucher.
    
    Menampilkan top vouchers berdasarkan usage count.
    """
    try:
        chart_data = await service.get_voucher_usage_chart(days)
        
        return create_response(
            success=True,
            message="Data chart voucher berhasil diambil",
            data={
                "title": chart_data.title,
                "chart_type": chart_data.chart_type,
                "labels": chart_data.labels,
                "datasets": chart_data.datasets
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting voucher chart: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil data chart voucher")

@router.get("/charts/user-activity", response_model=dict, summary="Get User Activity Chart")
async def get_user_activity_chart(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Mendapatkan data chart untuk aktivitas user.
    
    Menampilkan trend login harian user.
    """
    try:
        chart_data = await service.get_user_activity_chart(days)
        
        return create_response(
            success=True,
            message="Data chart aktivitas user berhasil diambil",
            data={
                "title": chart_data.title,
                "chart_type": chart_data.chart_type,
                "labels": chart_data.labels,
                "datasets": chart_data.datasets
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting user activity chart: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil data chart aktivitas user")

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
                        <div class="bg-white rounded-lg shadow p-6">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-dollar-sign text-2xl text-green-600"></i>
                                </div>
                                <div class="ml-4">
                                    <p class="text-sm font-medium text-gray-500">Total Revenue</p>
                                    <p id="totalRevenue" class="text-2xl font-semibold text-gray-900">-</p>
                                    <p id="revenueGrowth" class="text-sm text-gray-600">-</p>
                                </div>
                            </div>
                        </div>

                        <div class="bg-white rounded-lg shadow p-6">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-shopping-cart text-2xl text-blue-600"></i>
                                </div>
                                <div class="ml-4">
                                    <p class="text-sm font-medium text-gray-500">Total Transaksi</p>
                                    <p id="totalTransactions" class="text-2xl font-semibold text-gray-900">-</p>
                                    <p id="transactionGrowth" class="text-sm text-gray-600">-</p>
                                </div>
                            </div>
                        </div>

                        <div class="bg-white rounded-lg shadow p-6">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-users text-2xl text-purple-600"></i>
                                </div>
                                <div class="ml-4">
                                    <p class="text-sm font-medium text-gray-500">Total Users</p>
                                    <p id="totalUsers" class="text-2xl font-semibold text-gray-900">-</p>
                                    <p id="userGrowth" class="text-sm text-gray-600">-</p>
                                </div>
                            </div>
                        </div>

                        <div class="bg-white rounded-lg shadow p-6">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-box text-2xl text-orange-600"></i>
                                </div>
                                <div class="ml-4">
                                    <p class="text-sm font-medium text-gray-500">Total Produk</p>
                                    <p id="totalProducts" class="text-2xl font-semibold text-gray-900">-</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Charts -->
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                        <!-- Revenue Chart -->
                        <div class="bg-white rounded-lg shadow p-6">
                            <h3 class="text-lg font-semibold text-gray-900 mb-4">
                                <i class="fas fa-chart-line mr-2"></i>Trend Revenue
                            </h3>
                            <canvas id="revenueChart" width="400" height="200"></canvas>
                        </div>

                        <!-- User Activity Chart -->
                        <div class="bg-white rounded-lg shadow p-6">
                            <h3 class="text-lg font-semibold text-gray-900 mb-4">
                                <i class="fas fa-chart-area mr-2"></i>Aktivitas User
                            </h3>
                            <canvas id="userActivityChart" width="400" height="200"></canvas>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        <!-- Product Performance Chart -->
                        <div class="bg-white rounded-lg shadow p-6">
                            <h3 class="text-lg font-semibold text-gray-900 mb-4">
                                <i class="fas fa-chart-bar mr-2"></i>Performa Produk
                            </h3>
                            <canvas id="productChart" width="400" height="200"></canvas>
                        </div>

                        <!-- Voucher Usage Chart -->
                        <div class="bg-white rounded-lg shadow p-6">
                            <h3 class="text-lg font-semibold text-gray-900 mb-4">
                                <i class="fas fa-chart-pie mr-2"></i>Penggunaan Voucher
                            </h3>
                            <canvas id="voucherChart" width="400" height="200"></canvas>
                        </div>
                    </div>
                </div>
            </main>
        </div>

        <script>
            let charts = {};

            async function loadDashboardData() {
                const period = document.getElementById('periodSelect').value;
                
                try {
                    document.getElementById('loadingIndicator').classList.remove('hidden');
                    document.getElementById('dashboardContent').classList.add('hidden');

                    // Load summary data
                    const summaryResponse = await fetch(`/api/v1/analytics/dashboard/summary?days=${period}`);
                    const summaryData = await summaryResponse.json();
                    
                    if (summaryData.success) {
                        updateSummaryCards(summaryData.data);
                    }

                    // Load chart data
                    await Promise.all([
                        loadRevenueChart(period),
                        loadUserActivityChart(period),
                        loadProductChart(period),
                        loadVoucherChart(period)
                    ]);

                    document.getElementById('loadingIndicator').classList.add('hidden');
                    document.getElementById('dashboardContent').classList.remove('hidden');

                } catch (error) {
                    console.error('Error loading dashboard data:', error);
                    alert('Gagal memuat data dashboard');
                }
            }

            function updateSummaryCards(data) {
                document.getElementById('totalRevenue').textContent = 
                    new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR' }).format(data.total_revenue);
                document.getElementById('totalTransactions').textContent = data.total_transactions.toLocaleString('id-ID');
                document.getElementById('totalUsers').textContent = data.total_users.toLocaleString('id-ID');
                document.getElementById('totalProducts').textContent = data.total_products.toLocaleString('id-ID');

                // Growth indicators
                if (data.revenue_growth !== null) {
                    const growthText = data.revenue_growth >= 0 ? `+${data.revenue_growth.toFixed(1)}%` : `${data.revenue_growth.toFixed(1)}%`;
                    const growthColor = data.revenue_growth >= 0 ? 'text-green-600' : 'text-red-600';
                    document.getElementById('revenueGrowth').innerHTML = `<span class="${growthColor}">${growthText}</span> vs periode sebelumnya`;
                }

                if (data.transaction_growth !== null) {
                    const growthText = data.transaction_growth >= 0 ? `+${data.transaction_growth.toFixed(1)}%` : `${data.transaction_growth.toFixed(1)}%`;
                    const growthColor = data.transaction_growth >= 0 ? 'text-green-600' : 'text-red-600';
                    document.getElementById('transactionGrowth').innerHTML = `<span class="${growthColor}">${growthText}</span> vs periode sebelumnya`;
                }

                if (data.user_growth !== null) {
                    const growthText = data.user_growth >= 0 ? `+${data.user_growth.toFixed(1)}%` : `${data.user_growth.toFixed(1)}%`;
                    const growthColor = data.user_growth >= 0 ? 'text-green-600' : 'text-red-600';
                    document.getElementById('userGrowth').innerHTML = `<span class="${growthColor}">${growthText}</span> vs periode sebelumnya`;
                }
            }

            async function loadRevenueChart(period) {
                try {
                    const response = await fetch(`/api/v1/analytics/charts/revenue?days=${period}`);
                    const data = await response.json();
                    
                    if (data.success) {
                        const ctx = document.getElementById('revenueChart').getContext('2d');
                        
                        if (charts.revenue) {
                            charts.revenue.destroy();
                        }
                        
                        charts.revenue = new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: data.data.labels,
                                datasets: data.data.datasets
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                scales: {
                                    y: {
                                        beginAtZero: true,
                                        ticks: {
                                            callback: function(value) {
                                                return new Intl.NumberFormat('id-ID', { 
                                                    style: 'currency', 
                                                    currency: 'IDR',
                                                    minimumFractionDigits: 0
                                                }).format(value);
                                            }
                                        }
                                    }
                                }
                            }
                        });
                    }
                } catch (error) {
                    console.error('Error loading revenue chart:', error);
                }
            }

            async function loadUserActivityChart(period) {
                try {
                    const response = await fetch(`/api/v1/analytics/charts/user-activity?days=${period}`);
                    const data = await response.json();
                    
                    if (data.success) {
                        const ctx = document.getElementById('userActivityChart').getContext('2d');
                        
                        if (charts.userActivity) {
                            charts.userActivity.destroy();
                        }
                        
                        charts.userActivity = new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: data.data.labels,
                                datasets: data.data.datasets
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                scales: {
                                    y: {
                                        beginAtZero: true
                                    }
                                }
                            }
                        });
                    }
                } catch (error) {
                    console.error('Error loading user activity chart:', error);
                }
            }

            async function loadProductChart(period) {
                try {
                    const response = await fetch(`/api/v1/analytics/charts/products?days=${period}`);
                    const data = await response.json();
                    
                    if (data.success) {
                        const ctx = document.getElementById('productChart').getContext('2d');
                        
                        if (charts.product) {
                            charts.product.destroy();
                        }
                        
                        charts.product = new Chart(ctx, {
                            type: 'bar',
                            data: {
                                labels: data.data.labels,
                                datasets: data.data.datasets
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                scales: {
                                    y: {
                                        beginAtZero: true,
                                        ticks: {
                                            callback: function(value) {
                                                return new Intl.NumberFormat('id-ID', { 
                                                    style: 'currency', 
                                                    currency: 'IDR',
                                                    minimumFractionDigits: 0
                                                }).format(value);
                                            }
                                        }
                                    }
                                }
                            }
                        });
                    }
                } catch (error) {
                    console.error('Error loading product chart:', error);
                }
            }

            async function loadVoucherChart(period) {
                try {
                    const response = await fetch(`/api/v1/analytics/charts/vouchers?days=${period}`);
                    const data = await response.json();
                    
                    if (data.success) {
                        const ctx = document.getElementById('voucherChart').getContext('2d');
                        
                        if (charts.voucher) {
                            charts.voucher.destroy();
                        }
                        
                        charts.voucher = new Chart(ctx, {
                            type: 'pie',
                            data: {
                                labels: data.data.labels,
                                datasets: data.data.datasets
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false
                            }
                        });
                    }
                } catch (error) {
                    console.error('Error loading voucher chart:', error);
                }
            }

            function refreshDashboard() {
                loadDashboardData();
            }

            // Event listeners
            document.getElementById('periodSelect').addEventListener('change', loadDashboardData);

            // Load dashboard on page load
            document.addEventListener('DOMContentLoaded', loadDashboardData);
        </script>
    </body>
    </html>
    """

# Helper endpoints untuk tracking events
@router.post("/track/product-view", summary="Track Product View")
async def track_product_view(
    product_id: int,
    user_id: Optional[int] = None,
    session_id: Optional[str] = None,
    request: Request = None,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Helper endpoint untuk track product view"""
    try:
        ip_address = request.client.host if request else None
        await service.track_product_view(product_id, user_id, session_id, ip_address)
        
        return create_response(
            success=True,
            message="Product view berhasil ditrack"
        )
    except Exception as e:
        logger.error(f"Error tracking product view: {e}")
        raise HTTPException(status_code=500, detail="Gagal melakukan tracking")

@router.post("/track/product-purchase", summary="Track Product Purchase")
async def track_product_purchase(
    product_id: int,
    user_id: int,
    amount: float,
    transaction_id: Optional[int] = None,
    session_id: Optional[str] = None,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Helper endpoint untuk track product purchase"""
    try:
        from decimal import Decimal
        await service.track_product_purchase(
            product_id, user_id, Decimal(str(amount)), transaction_id, session_id
        )
        
        return create_response(
            success=True,
            message="Product purchase berhasil ditrack"
        )
    except Exception as e:
        logger.error(f"Error tracking product purchase: {e}")
        raise HTTPException(status_code=500, detail="Gagal melakukan tracking")

@router.post("/track/voucher-usage", summary="Track Voucher Usage")
async def track_voucher_usage(
    voucher_id: int,
    user_id: int,
    discount_amount: float,
    transaction_id: Optional[int] = None,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Helper endpoint untuk track voucher usage"""
    try:
        from decimal import Decimal
        await service.track_voucher_usage(
            voucher_id, user_id, Decimal(str(discount_amount)), transaction_id
        )
        
        return create_response(
            success=True,
            message="Voucher usage berhasil ditrack"
        )
    except Exception as e:
        logger.error(f"Error tracking voucher usage: {e}")
        raise HTTPException(status_code=500, detail="Gagal melakukan tracking")

# Admin Analytics Endpoints
@router.get("/products/categories", summary="Get Product Categories Analytics")
async def get_product_categories_analytics(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Mendapatkan analytics kategori produk untuk admin dashboard
    """
    try:
        # Mock data untuk kategori produk
        categories_data = {
            "categories": [
                {"name": "Pulsa", "count": 450, "revenue": 5400000, "percentage": 35.0},
                {"name": "Paket Data", "count": 320, "revenue": 4800000, "percentage": 25.0},
                {"name": "Token PLN", "count": 280, "revenue": 3360000, "percentage": 22.0},
                {"name": "Voucher Game", "count": 200, "revenue": 2400000, "percentage": 18.0}
            ],
            "total_products": 1250,
            "total_revenue": 16000000,
            "period_days": days,
            "generated_at": datetime.now().isoformat()
        }
        
        return create_response(
            success=True,
            message="Data analytics kategori produk berhasil diambil",
            data=categories_data
        )
        
    except Exception as e:
        logger.error(f"Error getting product categories analytics: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil analytics kategori produk")

@router.get("/transactions/weekly", summary="Get Weekly Transactions Analytics")
async def get_weekly_transactions_analytics(
    weeks: int = Query(4, ge=1, le=52, description="Jumlah minggu untuk analisis"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Mendapatkan analytics transaksi mingguan untuk admin dashboard
    """
    try:
        # Mock data untuk transaksi mingguan
        weekly_data = {
            "weeks": [
                {
                    "week": "Minggu 1",
                    "start_date": (datetime.now() - timedelta(weeks=3)).strftime("%Y-%m-%d"),
                    "end_date": (datetime.now() - timedelta(weeks=2, days=6)).strftime("%Y-%m-%d"),
                    "transactions": 280,
                    "revenue": 3360000,
                    "success_rate": 92.5
                },
                {
                    "week": "Minggu 2", 
                    "start_date": (datetime.now() - timedelta(weeks=2)).strftime("%Y-%m-%d"),
                    "end_date": (datetime.now() - timedelta(weeks=1, days=6)).strftime("%Y-%m-%d"),
                    "transactions": 320,
                    "revenue": 3840000,
                    "success_rate": 89.0
                },
                {
                    "week": "Minggu 3",
                    "start_date": (datetime.now() - timedelta(weeks=1)).strftime("%Y-%m-%d"),
                    "end_date": (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d"),
                    "transactions": 350,
                    "revenue": 4200000,
                    "success_rate": 91.2
                },
                {
                    "week": "Minggu 4",
                    "start_date": datetime.now().strftime("%Y-%m-%d"),
                    "end_date": datetime.now().strftime("%Y-%m-%d"),
                    "transactions": 300,
                    "revenue": 3600000,
                    "success_rate": 88.7
                }
            ],
            "total_transactions": 1250,
            "total_revenue": 15000000,
            "average_success_rate": 90.35,
            "period_weeks": weeks,
            "generated_at": datetime.now().isoformat()
        }
        
        return create_response(
            success=True,
            message="Data analytics transaksi mingguan berhasil diambil",
            data=weekly_data
        )
        
    except Exception as e:
        logger.error(f"Error getting weekly transactions analytics: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil analytics transaksi mingguan")

# Test endpoint untuk memastikan kode berfungsi
@router.get("/test-performance-metrics", response_model=dict, summary="Test Performance Metrics")
async def test_performance_metrics(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis")
):
    """
    Test endpoint untuk performance metrics
    """
    try:
        # Mock data untuk performance metrics
        import random
        
        # Generate daily metrics for the specified period
        daily_metrics = []
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            current_date = base_date + timedelta(days=i)
            daily_metrics.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "transactions": random.randint(50, 200),
                "revenue": random.randint(500000, 2000000),
                "success_rate": round(random.uniform(85.0, 98.0), 2),
                "response_time": round(random.uniform(0.1, 0.8), 3)
            })
        
        total_transactions = sum(day["transactions"] for day in daily_metrics)
        successful_transactions = int(total_transactions * 0.92)
        failed_transactions = total_transactions - successful_transactions
        total_revenue = sum(day["revenue"] for day in daily_metrics)
        
        performance_data = {
            "total_transactions": total_transactions,
            "successful_transactions": successful_transactions,
            "failed_transactions": failed_transactions,
            "success_rate": round((successful_transactions / total_transactions) * 100, 2),
            "total_revenue": float(total_revenue),
            "average_transaction_value": float(total_revenue / total_transactions),
            "peak_hour": "14:00-15:00",
            "peak_day": "Selasa",
            "response_time_avg": 0.245,
            "uptime_percentage": 99.8,
            "period_days": days,
            "generated_at": datetime.now().isoformat(),
            "daily_metrics": daily_metrics
        }
        
        return create_response(
            success=True,
            message="Data performance metrics berhasil diambil",
            data=performance_data
        )
        
    except Exception as e:
        logger.error(f"Error getting test performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil performance metrics")

# Admin Analytics Router
admin_analytics_router = APIRouter()

@admin_analytics_router.get("/overview", response_model=dict, summary="Get Analytics Overview")
async def get_analytics_overview(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis")
):
    """
    Mendapatkan overview analytics untuk admin dashboard
    """
    try:
        # Mock data untuk overview analytics
        import random
        
        overview_data = {
            "total_revenue": 125000000,
            "total_transactions": 4250,
            "total_users": 1850,
            "total_products": 125,
            "revenue_growth": 15.8,
            "transaction_growth": 12.3,
            "user_growth": 8.7,
            "product_growth": 5.2,
            "conversion_rate": 3.4,
            "average_order_value": 29411.76,
            "customer_lifetime_value": 67567.57,
            "churn_rate": 2.1,
            "period_days": days,
            "generated_at": datetime.now().isoformat(),
            "quick_stats": {
                "today_revenue": 4200000,
                "today_transactions": 142,
                "today_new_users": 23,
                "today_orders": 89
            },
            "trends": {
                "revenue_trend": "up",
                "transaction_trend": "up", 
                "user_trend": "up",
                "conversion_trend": "stable"
            }
        }
        
        return create_response(
            success=True,
            message="Data overview analytics berhasil diambil",
            data=overview_data
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics overview: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil overview analytics")

@admin_analytics_router.get("/revenue", response_model=dict, summary="Get Revenue Analytics")
async def get_revenue_analytics(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis")
):
    """
    Mendapatkan analytics revenue untuk admin dashboard
    """
    try:
        # Mock data untuk revenue analytics
        import random
        
        # Generate daily revenue data
        daily_revenue = []
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            current_date = base_date + timedelta(days=i)
            daily_revenue.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "revenue": random.randint(2000000, 6000000),
                "transactions": random.randint(80, 250),
                "average_order_value": random.randint(20000, 35000)
            })
        
        total_revenue = sum(day["revenue"] for day in daily_revenue)
        total_transactions = sum(day["transactions"] for day in daily_revenue)
        
        revenue_data = {
            "total_revenue": total_revenue,
            "total_transactions": total_transactions,
            "average_order_value": round(total_revenue / total_transactions, 2),
            "revenue_growth": 15.8,
            "highest_revenue_day": max(daily_revenue, key=lambda x: x["revenue"]),
            "lowest_revenue_day": min(daily_revenue, key=lambda x: x["revenue"]),
            "revenue_by_category": [
                {"category": "Digital Products", "revenue": total_revenue * 0.45, "percentage": 45.0},
                {"category": "Physical Products", "revenue": total_revenue * 0.35, "percentage": 35.0},
                {"category": "Services", "revenue": total_revenue * 0.20, "percentage": 20.0}
            ],
            "monthly_comparison": [
                {"month": "Januari", "revenue": 45000000, "growth": 12.5},
                {"month": "Februari", "revenue": 52000000, "growth": 15.6},
                {"month": "Maret", "revenue": 48000000, "growth": -7.7},
                {"month": "April", "revenue": 58000000, "growth": 20.8}
            ],
            "period_days": days,
            "generated_at": datetime.now().isoformat(),
            "daily_revenue": daily_revenue
        }
        
        return create_response(
            success=True,
            message="Data revenue analytics berhasil diambil",
            data=revenue_data
        )
        
    except Exception as e:
        logger.error(f"Error getting revenue analytics: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil revenue analytics")

@admin_analytics_router.get("/orders", response_model=dict, summary="Get Orders Analytics")
async def get_orders_analytics(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis")
):
    """
    Mendapatkan analytics pesanan untuk admin dashboard
    """
    try:
        # Mock data untuk orders analytics
        import random
        
        # Generate daily orders data
        daily_orders = []
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            current_date = base_date + timedelta(days=i)
            completed = random.randint(60, 180)
            pending = random.randint(5, 25)
            cancelled = random.randint(2, 15)
            
            daily_orders.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "total_orders": completed + pending + cancelled,
                "completed_orders": completed,
                "pending_orders": pending,
                "cancelled_orders": cancelled,
                "completion_rate": round((completed / (completed + pending + cancelled)) * 100, 2)
            })
        
        total_orders = sum(day["total_orders"] for day in daily_orders)
        completed_orders = sum(day["completed_orders"] for day in daily_orders)
        pending_orders = sum(day["pending_orders"] for day in daily_orders)
        cancelled_orders = sum(day["cancelled_orders"] for day in daily_orders)
        
        orders_data = {
            "total_orders": total_orders,
            "completed_orders": completed_orders,
            "pending_orders": pending_orders,
            "cancelled_orders": cancelled_orders,
            "completion_rate": round((completed_orders / total_orders) * 100, 2),
            "cancellation_rate": round((cancelled_orders / total_orders) * 100, 2),
            "order_growth": 12.3,
            "average_orders_per_day": round(total_orders / days, 2),
            "peak_order_day": max(daily_orders, key=lambda x: x["total_orders"]),
            "order_status_distribution": [
                {"status": "Completed", "count": completed_orders, "percentage": round((completed_orders / total_orders) * 100, 2)},
                {"status": "Pending", "count": pending_orders, "percentage": round((pending_orders / total_orders) * 100, 2)},
                {"status": "Cancelled", "count": cancelled_orders, "percentage": round((cancelled_orders / total_orders) * 100, 2)}
            ],
            "hourly_distribution": [
                {"hour": f"{i:02d}:00", "orders": random.randint(10, 150)} for i in range(24)
            ],
            "period_days": days,
            "generated_at": datetime.now().isoformat(),
            "daily_orders": daily_orders
        }
        
        return create_response(
            success=True,
            message="Data orders analytics berhasil diambil",
            data=orders_data
        )
        
    except Exception as e:
        logger.error(f"Error getting orders analytics: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil orders analytics")

@admin_analytics_router.get("/user-growth", response_model=dict, summary="Get User Growth Analytics")
async def get_user_growth_analytics(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis")
):
    """
    Mendapatkan analytics pertumbuhan user untuk admin dashboard
    """
    try:
        # Mock data untuk user growth analytics
        import random
        
        # Generate daily user growth data
        daily_users = []
        base_date = datetime.now() - timedelta(days=days)
        cumulative_users = 1500  # Starting point
        
        for i in range(days):
            current_date = base_date + timedelta(days=i)
            new_users = random.randint(5, 35)
            active_users = random.randint(200, 800)
            returning_users = random.randint(50, 200)
            cumulative_users += new_users
            
            daily_users.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "new_users": new_users,
                "active_users": active_users,
                "returning_users": returning_users,
                "cumulative_users": cumulative_users,
                "retention_rate": round((returning_users / active_users) * 100, 2)
            })
        
        total_new_users = sum(day["new_users"] for day in daily_users)
        avg_active_users = round(sum(day["active_users"] for day in daily_users) / days, 2)
        avg_retention_rate = round(sum(day["retention_rate"] for day in daily_users) / days, 2)
        
        user_growth_data = {
            "total_users": cumulative_users,
            "new_users_period": total_new_users,
            "user_growth_rate": 8.7,
            "average_active_users": avg_active_users,
            "average_retention_rate": avg_retention_rate,
            "churn_rate": 2.1,
            "user_acquisition_cost": 45000,
            "customer_lifetime_value": 675000,
            "user_segments": [
                {"segment": "New Users", "count": total_new_users, "percentage": 15.2},
                {"segment": "Active Users", "count": int(avg_active_users), "percentage": 42.8},
                {"segment": "Returning Users", "count": int(avg_active_users * 0.3), "percentage": 28.5},
                {"segment": "Inactive Users", "count": int(cumulative_users * 0.13), "percentage": 13.5}
            ],
            "acquisition_channels": [
                {"channel": "Organic Search", "users": int(total_new_users * 0.35), "percentage": 35.0},
                {"channel": "Social Media", "users": int(total_new_users * 0.25), "percentage": 25.0},
                {"channel": "Direct", "users": int(total_new_users * 0.20), "percentage": 20.0},
                {"channel": "Referral", "users": int(total_new_users * 0.15), "percentage": 15.0},
                {"channel": "Paid Ads", "users": int(total_new_users * 0.05), "percentage": 5.0}
            ],
            "period_days": days,
            "generated_at": datetime.now().isoformat(),
            "daily_users": daily_users
        }
        
        return create_response(
            success=True,
            message="Data user growth analytics berhasil diambil",
            data=user_growth_data
        )
        
    except Exception as e:
        logger.error(f"Error getting user growth analytics: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil user growth analytics")

@admin_analytics_router.get("/payment-methods", response_model=dict, summary="Get Payment Methods Analytics")
async def get_payment_methods_analytics(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis")
):
    """
    Mendapatkan analytics metode pembayaran untuk admin dashboard
    """
    try:
        # Mock data untuk payment methods analytics
        import random
        
        payment_methods_data = {
            "total_transactions": 4250,
            "total_revenue": 125000000,
            "payment_methods": [
                {
                    "method": "Bank Transfer",
                    "transactions": 1700,
                    "revenue": 50000000,
                    "percentage": 40.0,
                    "success_rate": 95.2,
                    "average_amount": 29411.76
                },
                {
                    "method": "E-Wallet (OVO, GoPay, DANA)",
                    "transactions": 1275,
                    "revenue": 37500000,
                    "percentage": 30.0,
                    "success_rate": 97.8,
                    "average_amount": 29411.76
                },
                {
                    "method": "Credit Card",
                    "transactions": 850,
                    "revenue": 25000000,
                    "percentage": 20.0,
                    "success_rate": 92.5,
                    "average_amount": 29411.76
                },
                {
                    "method": "Virtual Account",
                    "transactions": 425,
                    "revenue": 12500000,
                    "percentage": 10.0,
                    "success_rate": 98.1,
                    "average_amount": 29411.76
                }
            ],
            "payment_trends": [
                {"month": "Januari", "bank_transfer": 35, "e_wallet": 28, "credit_card": 25, "virtual_account": 12},
                {"month": "Februari", "bank_transfer": 38, "e_wallet": 30, "credit_card": 22, "virtual_account": 10},
                {"month": "Maret", "bank_transfer": 40, "e_wallet": 30, "credit_card": 20, "virtual_account": 10},
                {"month": "April", "bank_transfer": 40, "e_wallet": 30, "credit_card": 20, "virtual_account": 10}
            ],
            "failed_transactions": [
                {"method": "Bank Transfer", "failed": 85, "failure_rate": 4.8},
                {"method": "E-Wallet", "failed": 28, "failure_rate": 2.2},
                {"method": "Credit Card", "failed": 64, "failure_rate": 7.5},
                {"method": "Virtual Account", "failed": 8, "failure_rate": 1.9}
            ],
            "processing_time": [
                {"method": "Bank Transfer", "avg_time": "2-3 jam", "instant_percentage": 0},
                {"method": "E-Wallet", "avg_time": "Instant", "instant_percentage": 100},
                {"method": "Credit Card", "avg_time": "Instant", "instant_percentage": 100},
                {"method": "Virtual Account", "avg_time": "1-2 jam", "instant_percentage": 15}
            ],
            "period_days": days,
            "generated_at": datetime.now().isoformat()
        }
        
        return create_response(
            success=True,
            message="Data payment methods analytics berhasil diambil",
            data=payment_methods_data
        )
        
    except Exception as e:
        logger.error(f"Error getting payment methods analytics: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil payment methods analytics")

@admin_analytics_router.get("/top-products", response_model=dict, summary="Get Top Products Analytics")
async def get_top_products_analytics(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis"),
    limit: int = Query(10, ge=1, le=50, description="Jumlah produk teratas yang ditampilkan")
):
    """
    Mendapatkan analytics produk terlaris untuk admin dashboard
    """
    try:
        # Mock data untuk top products analytics
        import random
        
        # Generate top products data
        product_names = [
            "Premium Gaming Package", "Discord Nitro 1 Month", "Spotify Premium", 
            "Netflix Premium", "YouTube Premium", "Steam Wallet", "Google Play Gift Card",
            "iTunes Gift Card", "PlayStation Plus", "Xbox Game Pass", "Adobe Creative Suite",
            "Microsoft Office 365", "Canva Pro", "Grammarly Premium", "VPN Premium"
        ]
        
        top_products = []
        for i in range(min(limit, len(product_names))):
            sales = random.randint(50, 500)
            revenue = sales * random.randint(15000, 150000)
            
            top_products.append({
                "rank": i + 1,
                "product_id": i + 1,
                "product_name": product_names[i],
                "category": random.choice(["Digital", "Gaming", "Streaming", "Software", "Gift Card"]),
                "sales_count": sales,
                "revenue": revenue,
                "average_price": round(revenue / sales, 2),
                "growth_rate": round(random.uniform(-5.0, 25.0), 2),
                "stock_status": random.choice(["In Stock", "Low Stock", "Out of Stock"]),
                "rating": round(random.uniform(4.0, 5.0), 1),
                "reviews_count": random.randint(10, 200)
            })
        
        total_sales = sum(product["sales_count"] for product in top_products)
        total_revenue = sum(product["revenue"] for product in top_products)
        
        top_products_data = {
            "total_products_analyzed": len(product_names),
            "top_products_count": len(top_products),
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "average_price": round(total_revenue / total_sales, 2),
            "top_products": top_products,
            "category_performance": [
                {"category": "Gaming", "sales": int(total_sales * 0.35), "revenue": int(total_revenue * 0.40), "percentage": 35.0},
                {"category": "Streaming", "sales": int(total_sales * 0.25), "revenue": int(total_revenue * 0.25), "percentage": 25.0},
                {"category": "Software", "sales": int(total_sales * 0.20), "revenue": int(total_revenue * 0.20), "percentage": 20.0},
                {"category": "Digital", "sales": int(total_sales * 0.15), "revenue": int(total_revenue * 0.10), "percentage": 15.0},
                {"category": "Gift Card", "sales": int(total_sales * 0.05), "revenue": int(total_revenue * 0.05), "percentage": 5.0}
            ],
            "trending_products": [
                {"product_name": "Discord Nitro 1 Month", "growth_rate": 45.2, "trend": "up"},
                {"product_name": "Steam Wallet", "growth_rate": 32.1, "trend": "up"},
                {"product_name": "Netflix Premium", "growth_rate": -8.5, "trend": "down"}
            ],
            "period_days": days,
            "generated_at": datetime.now().isoformat()
        }
        
        return create_response(
            success=True,
            message="Data top products analytics berhasil diambil",
            data=top_products_data
        )
        
    except Exception as e:
        logger.error(f"Error getting top products analytics: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil top products analytics")

@admin_analytics_router.get("/performance-metrics", response_model=dict, summary="Get Performance Metrics")
async def get_performance_metrics(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis")
):
    """
    Mendapatkan performance metrics untuk admin dashboard
    """
    try:
        # Mock data untuk performance metrics
        from decimal import Decimal
        import random
        
        # Generate daily metrics for the specified period
        daily_metrics = []
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            current_date = base_date + timedelta(days=i)
            daily_metrics.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "transactions": random.randint(50, 200),
                "revenue": random.randint(500000, 2000000),
                "success_rate": round(random.uniform(85.0, 98.0), 2),
                "response_time": round(random.uniform(0.1, 0.8), 3)
            })
        
        total_transactions = sum(day["transactions"] for day in daily_metrics)
        successful_transactions = int(total_transactions * 0.92)
        failed_transactions = total_transactions - successful_transactions
        total_revenue = sum(day["revenue"] for day in daily_metrics)
        
        performance_data = {
            "total_transactions": total_transactions,
            "successful_transactions": successful_transactions,
            "failed_transactions": failed_transactions,
            "success_rate": round((successful_transactions / total_transactions) * 100, 2),
            "total_revenue": float(total_revenue),
            "average_transaction_value": float(total_revenue / total_transactions),
            "peak_hour": "14:00-15:00",
            "peak_day": "Selasa",
            "response_time_avg": 0.245,
            "uptime_percentage": 99.8,
            "period_days": days,
            "generated_at": datetime.now().isoformat(),
            "daily_metrics": daily_metrics
        }
        
        return create_response(
            success=True,
            message="Data performance metrics berhasil diambil",
            data=performance_data
        )
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil performance metrics")

@admin_analytics_router.get("/geographic", response_model=dict, summary="Get Geographic Data")
async def get_geographic_data(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis")
):
    """
    Mendapatkan data geografis untuk admin dashboard
    """
    try:
        # Mock data untuk geographic analytics
        geographic_data = {
            "total_regions": 34,
            "top_regions": [
                {"region": "DKI Jakarta", "transactions": 1250, "revenue": 15000000, "percentage": 28.5},
                {"region": "Jawa Barat", "transactions": 980, "revenue": 11760000, "percentage": 22.3},
                {"region": "Jawa Timur", "transactions": 750, "revenue": 9000000, "percentage": 17.1},
                {"region": "Jawa Tengah", "transactions": 620, "revenue": 7440000, "percentage": 14.1},
                {"region": "Sumatera Utara", "transactions": 450, "revenue": 5400000, "percentage": 10.2}
            ],
            "country_distribution": [
                {"country": "Indonesia", "transactions": 4050, "revenue": 48600000, "percentage": 92.3},
                {"country": "Malaysia", "transactions": 200, "revenue": 2400000, "percentage": 4.6},
                {"country": "Singapura", "transactions": 100, "revenue": 1200000, "percentage": 2.3},
                {"country": "Thailand", "transactions": 50, "revenue": 600000, "percentage": 1.1}
            ],
            "city_distribution": [
                {"city": "Jakarta", "transactions": 800, "revenue": 9600000, "percentage": 18.2},
                {"city": "Surabaya", "transactions": 450, "revenue": 5400000, "percentage": 10.3},
                {"city": "Bandung", "transactions": 380, "revenue": 4560000, "percentage": 8.7},
                {"city": "Medan", "transactions": 320, "revenue": 3840000, "percentage": 7.3},
                {"city": "Semarang", "transactions": 280, "revenue": 3360000, "percentage": 6.4}
            ],
            "revenue_by_region": [
                {"region": "Pulau Jawa", "revenue": 43200000, "percentage": 82.3},
                {"region": "Pulau Sumatera", "revenue": 6000000, "percentage": 11.4},
                {"region": "Pulau Kalimantan", "revenue": 2400000, "percentage": 4.6},
                {"region": "Pulau Sulawesi", "revenue": 900000, "percentage": 1.7}
            ],
            "period_days": days,
            "generated_at": datetime.now().isoformat()
        }
        
        return create_response(
            success=True,
            message="Data geografis berhasil diambil",
            data=geographic_data
        )
        
    except Exception as e:
        logger.error(f"Error getting geographic data: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil data geografis")

@admin_analytics_router.get("/recent-activity", response_model=dict, summary="Get Recent Activity")
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=100, description="Jumlah aktivitas yang ditampilkan")
):
    """
    Mendapatkan aktivitas terbaru untuk admin dashboard
    """
    try:
        # Mock data untuk recent activity
        import random
        
        activity_types = [
            "USER_REGISTRATION", "PRODUCT_PURCHASE", "VOUCHER_REDEMPTION", 
            "ADMIN_LOGIN", "CONFIG_UPDATE", "TRANSACTION_COMPLETED",
            "PAYMENT_RECEIVED", "DISCORD_COMMAND", "CACHE_CLEARED", "BACKUP_CREATED"
        ]
        
        activities = []
        for i in range(limit):
            activity_type = random.choice(activity_types)
            timestamp = datetime.now() - timedelta(minutes=random.randint(1, 1440))
            
            # Generate description based on activity type
            descriptions = {
                "USER_REGISTRATION": "User baru mendaftar ke sistem",
                "PRODUCT_PURCHASE": "Pembelian produk berhasil dilakukan",
                "VOUCHER_REDEMPTION": "Voucher berhasil ditukarkan",
                "ADMIN_LOGIN": "Admin berhasil login ke sistem",
                "CONFIG_UPDATE": "Konfigurasi sistem diperbarui",
                "TRANSACTION_COMPLETED": "Transaksi berhasil diselesaikan",
                "PAYMENT_RECEIVED": "Pembayaran berhasil diterima",
                "DISCORD_COMMAND": "Command Discord berhasil dieksekusi",
                "CACHE_CLEARED": "Cache sistem berhasil dibersihkan",
                "BACKUP_CREATED": "Backup database berhasil dibuat"
            }
            
            activities.append({
                "id": i + 1,
                "activity_type": activity_type,
                "description": descriptions.get(activity_type, "Aktivitas sistem"),
                "user_id": random.randint(1, 1000) if activity_type in ["USER_REGISTRATION", "PRODUCT_PURCHASE", "VOUCHER_REDEMPTION"] else None,
                "admin_id": random.randint(1, 10) if activity_type in ["ADMIN_LOGIN", "CONFIG_UPDATE", "CACHE_CLEARED", "BACKUP_CREATED"] else None,
                "timestamp": timestamp.isoformat(),
                "metadata": {
                    "ip_address": f"192.168.1.{random.randint(1, 255)}",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            })
        
        recent_activity_data = {
            "activities": activities,
            "total_count": limit,
            "limit": limit,
            "generated_at": datetime.now().isoformat()
        }
        
        return create_response(
            success=True,
            message="Data aktivitas terbaru berhasil diambil",
            data=recent_activity_data
        )
        
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil aktivitas terbaru")
