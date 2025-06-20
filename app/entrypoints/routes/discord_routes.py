"""
Flask Server - Discord Routes
Routes untuk Discord bot management endpoints
"""

from flask import jsonify, request


def register_discord_routes(app):
    """Register Discord management routes"""
    
    @app.route('/api/v1/admin/discord/stats')
    def discord_stats():
        return jsonify({
            'success': True,
            'data': {
                'total_bots': 3,
                'active_bots': 2,
                'total_servers': 15,
                'total_users': 1250
            }
        })

    @app.route('/api/v1/admin/discord/bots')
    def discord_bots():
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': 1,
                    'name': 'FA Bot Main',
                    'token': 'bot_token_***',
                    'status': 'online',
                    'servers': 8,
                    'users': 650,
                    'uptime': '2d 14h 30m',
                    'last_seen': '2024-01-15T10:30:00Z'
                },
                {
                    'id': 2,
                    'name': 'FA Bot Secondary',
                    'token': 'bot_token_***',
                    'status': 'online',
                    'servers': 5,
                    'users': 400,
                    'uptime': '1d 8h 15m',
                    'last_seen': '2024-01-15T10:25:00Z'
                },
                {
                    'id': 3,
                    'name': 'FA Bot Test',
                    'token': 'bot_token_***',
                    'status': 'offline',
                    'servers': 2,
                    'users': 200,
                    'uptime': '0m',
                    'last_seen': '2024-01-14T15:20:00Z'
                }
            ]
        })

    @app.route('/api/v1/admin/discord/bots', methods=['POST'])
    def create_discord_bot():
        data = request.get_json()
        return jsonify({
            'success': True,
            'data': {
                'id': 4,
                'name': data.get('name', 'New Bot'),
                'token': data.get('token', ''),
                'status': 'offline',
                'servers': 0,
                'users': 0,
                'uptime': '0m',
                'last_seen': None
            },
            'message': 'Bot created successfully'
        })

    @app.route('/api/v1/admin/discord/bots/<int:bot_id>', methods=['PUT'])
    def update_discord_bot(bot_id):
        data = request.get_json()
        return jsonify({
            'success': True,
            'data': {
                'id': bot_id,
                'name': data.get('name', f'Bot {bot_id}'),
                'token': data.get('token', 'updated_token'),
                'status': 'offline',
                'servers': 0,
                'users': 0
            },
            'message': 'Bot updated successfully'
        })

    @app.route('/api/v1/admin/discord/bots/<int:bot_id>/start', methods=['POST'])
    def start_discord_bot(bot_id):
        return jsonify({
            'success': True,
            'message': f'Bot {bot_id} started successfully'
        })

    @app.route('/api/v1/admin/discord/bots/<int:bot_id>/stop', methods=['POST'])
    def stop_discord_bot(bot_id):
        return jsonify({
            'success': True,
            'message': f'Bot {bot_id} stopped successfully'
        })

    @app.route('/api/v1/admin/discord/bots/<int:bot_id>', methods=['DELETE'])
    def delete_discord_bot(bot_id):
        return jsonify({
            'success': True,
            'message': f'Bot {bot_id} deleted successfully'
        })
