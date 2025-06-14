from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.domains.analytics.services.analytics_service import AnalyticsService
from app.domains.analytics.schemas.analytics_schemas import (
    AnalyticsEventCreate, AnalyticsEventResponse, AnalyticsFilter,
    DashboardSummary, ChartData, AnalyticsReport
)
from app.infrastructure.database.database_manager import get_db
from app.shared.responses.api_response import create_response
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
