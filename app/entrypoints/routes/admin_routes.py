"""
Admin Dashboard Routes
Routes untuk admin dashboard dan statistik
"""

from flask import jsonify


def register_admin_routes(app):
    """Register admin dashboard routes"""
    
    @app.route('/api/v1/admin/dashboard/stats')
    def admin_dashboard_stats():
        return jsonify({
            'success': True,
            'data': {
                'total_revenue': 125000000,
                'total_orders': 1847,
                'total_users': 1250,
                'total_products': 156,
                'total_transactions': 3420,
                'discord_bots': 3,
                'active_users': 892
            }
        })

    @app.route('/api/v1/admin/users')
    def admin_users():
        return jsonify({
            'success': True,
            'data': {
                'users': [
                    {
                        'id': 1,
                        'username': 'user1',
                        'email': 'user1@example.com',
                        'is_active': True,
                        'created_at': '2024-01-01T00:00:00Z'
                    },
                    {
                        'id': 2,
                        'username': 'user2',
                        'email': 'user2@example.com',
                        'is_active': True,
                        'created_at': '2024-01-02T00:00:00Z'
                    }
                ],
                'total': 1250,
                'page': 1,
                'per_page': 20
            }
        })

    @app.route('/api/v1/admin/products')
    def admin_products():
        return jsonify({
            'success': True,
            'data': {
                'products': [
                    {
                        'id': 1,
                        'name': 'Pulsa Telkomsel 10K',
                        'price': 11000,
                        'category': 'pulsa',
                        'is_active': True
                    },
                    {
                        'id': 2,
                        'name': 'Token PLN 20K',
                        'price': 21000,
                        'category': 'pln',
                        'is_active': True
                    }
                ],
                'total': 156,
                'page': 1,
                'per_page': 20
            }
        })
