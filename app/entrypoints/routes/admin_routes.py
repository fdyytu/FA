"""
Flask Server - Admin Dashboard Routes
Routes untuk admin dashboard dan analytics endpoints
"""

from flask import jsonify


def register_admin_routes(app):
    """Register admin dashboard routes"""
    
    @app.route('/api/v1/admin/dashboard/stats')
    def admin_dashboard_stats():
        return jsonify({
            'success': True,
            'data': {
                'total_users': 1250,
                'total_transactions': 5680,
                'total_revenue': 125000000,
                'active_bots': 2,
                'pending_transactions': 15
            }
        })

    @app.route('/api/v1/admin/transactions/recent')
    def recent_transactions():
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': 1,
                    'user': 'user123',
                    'amount': 50000,
                    'type': 'topup',
                    'status': 'completed',
                    'timestamp': '2024-01-15T10:30:00Z'
                },
                {
                    'id': 2,
                    'user': 'user456',
                    'amount': 25000,
                    'type': 'purchase',
                    'status': 'pending',
                    'timestamp': '2024-01-15T10:25:00Z'
                }
            ]
        })

    @app.route('/api/v1/admin/discord/worlds')
    def discord_worlds():
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': 1,
                    'name': 'WORLD1',
                    'players': 45,
                    'status': 'online'
                },
                {
                    'id': 2,
                    'name': 'WORLD2',
                    'players': 32,
                    'status': 'online'
                }
            ]
        })

    @app.route('/api/v1/admin/discord/commands/recent')
    def recent_commands():
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': 1,
                    'command': '/balance',
                    'user': 'user123',
                    'timestamp': '2024-01-15T10:30:00Z'
                },
                {
                    'id': 2,
                    'command': '/buy',
                    'user': 'user456',
                    'timestamp': '2024-01-15T10:25:00Z'
                }
            ]
        })

    @app.route('/api/v1/admin/discord/logs')
    def bot_logs():
        return jsonify({
            'success': True,
            'data': [
                {
                    'timestamp': '2024-01-15T10:30:00Z',
                    'level': 'INFO',
                    'message': 'Bot connected successfully'
                },
                {
                    'timestamp': '2024-01-15T10:25:00Z',
                    'level': 'ERROR',
                    'message': 'Failed to process command'
                }
            ]
        })
