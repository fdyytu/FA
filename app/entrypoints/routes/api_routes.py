"""
Flask Server - API Routes
Routes untuk general API endpoints (dashboard, products, users, analytics, settings)
"""

from flask import jsonify


def register_api_routes(app):
    """Register general API routes"""
    
    @app.route('/api/dashboard/stats')
    def dashboard_stats():
        return jsonify({
            'users': 1250,
            'transactions': 5680,
            'revenue': 125000000,
            'growth': 15.5
        })

    @app.route('/api/products')
    def products():
        return jsonify([
            {
                'id': 1,
                'name': 'Diamond 100',
                'price': 10000,
                'category': 'game_currency',
                'stock': 999,
                'sales': 150
            },
            {
                'id': 2,
                'name': 'Gold Package',
                'price': 25000,
                'category': 'premium',
                'stock': 500,
                'sales': 89
            },
            {
                'id': 3,
                'name': 'VIP Membership',
                'price': 50000,
                'category': 'subscription',
                'stock': 100,
                'sales': 45
            }
        ])

    @app.route('/api/users')
    def users():
        return jsonify([
            {
                'id': 1,
                'username': 'user123',
                'email': 'user123@example.com',
                'balance': 150000,
                'status': 'active',
                'joined': '2024-01-10'
            },
            {
                'id': 2,
                'username': 'user456',
                'email': 'user456@example.com',
                'balance': 75000,
                'status': 'active',
                'joined': '2024-01-12'
            },
            {
                'id': 3,
                'username': 'user789',
                'email': 'user789@example.com',
                'balance': 200000,
                'status': 'premium',
                'joined': '2024-01-08'
            }
        ])

    @app.route('/api/analytics/overview')
    def analytics_overview():
        return jsonify({
            'revenue': {
                'today': 2500000,
                'week': 15000000,
                'month': 65000000
            },
            'users': {
                'new_today': 25,
                'new_week': 180,
                'total': 1250
            },
            'transactions': {
                'today': 45,
                'week': 320,
                'success_rate': 98.5
            }
        })

    @app.route('/api/settings')
    def settings():
        return jsonify({
            'maintenance_mode': False,
            'registration_enabled': True,
            'min_topup': 10000,
            'max_topup': 1000000,
            'commission_rate': 5.0
        })
