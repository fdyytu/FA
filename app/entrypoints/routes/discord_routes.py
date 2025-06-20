"""
Discord Routes
Routes untuk Discord bot management
"""

from flask import jsonify, request


def register_discord_routes(app):
    """Register Discord bot management routes"""
    
    # Discord Bot API endpoints
    @app.route('/api/v1/admin/discord/stats')
    def discord_stats():
        return jsonify({
            'success': True,
            'data': {
                'total_bots': 3,
                'discord_users': 2450,
                'live_products': 156,
                'commands_today': 1234
            }
        })

    @app.route('/api/v1/admin/discord/bots')
    def discord_bots():
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': 1,
                    'name': 'FA Store Bot',
                    'token': 'MTMxODE4MDAyOTA5MTI4NzA3MQ.GXF_u-.vt5Ps5Kna-N_qZkV8rWkCekVyeANPajURfBdy4',
                    'prefix': '!',
                    'guild_id': '123456789012345678',
                    'description': 'Bot utama untuk toko FA',
                    'is_active': True,
                    'auto_start': True,
                    'status': 'online',
                    'uptime': '2d 14h 32m',
                    'commands_count': 1234,
                    'created_at': '2024-01-15T10:30:00Z'
                },
                {
                    'id': 2,
                    'name': 'FA Support Bot',
                    'token': 'MTIzNDU2Nzg5MDEyMzQ1Njc4OTE.YYYYYY.YYYYYYYYYYYYYYYYYYYYYYYYYY',
                    'prefix': '?',
                    'guild_id': '123456789012345679',
                    'description': 'Bot untuk customer support',
                    'is_active': True,
                    'auto_start': False,
                    'status': 'online',
                    'uptime': '1d 8h 15m',
                    'commands_count': 567,
                    'created_at': '2024-01-14T15:45:00Z'
                }
            ]
        })

    @app.route('/api/v1/admin/discord/bots', methods=['POST'])
    def create_discord_bot():
        data = request.get_json()
        return jsonify({
            'success': True,
            'data': {
                'id': 3,
                'name': data.get('name'),
                'token': data.get('token'),
                'prefix': data.get('prefix'),
                'guild_id': data.get('guild_id'),
                'description': data.get('description'),
                'is_active': data.get('is_active', False),
                'auto_start': data.get('auto_start', False),
                'status': 'offline',
                'uptime': '0m',
                'commands_count': 0,
                'created_at': '2024-01-16T11:00:00Z'
            },
            'message': 'Bot berhasil ditambahkan'
        })

    @app.route('/api/v1/admin/discord/bots/<int:bot_id>', methods=['PUT'])
    def update_discord_bot(bot_id):
        data = request.get_json()
        return jsonify({
            'success': True,
            'data': {
                'id': bot_id,
                'name': data.get('name'),
                'token': data.get('token'),
                'prefix': data.get('prefix'),
                'guild_id': data.get('guild_id'),
                'description': data.get('description'),
                'is_active': data.get('is_active', False),
                'auto_start': data.get('auto_start', False)
            },
            'message': 'Bot berhasil diperbarui'
        })

    @app.route('/api/v1/admin/discord/bots/<int:bot_id>/start', methods=['POST'])
    def start_discord_bot(bot_id):
        return jsonify({
            'success': True,
            'message': f'Bot {bot_id} berhasil dijalankan'
        })

    @app.route('/api/v1/admin/discord/bots/<int:bot_id>/stop', methods=['POST'])
    def stop_discord_bot(bot_id):
        return jsonify({
            'success': True,
            'message': f'Bot {bot_id} berhasil dihentikan'
        })

    @app.route('/api/v1/admin/discord/bots/<int:bot_id>', methods=['DELETE'])
    def delete_discord_bot(bot_id):
        return jsonify({
            'success': True,
            'message': f'Bot {bot_id} berhasil dihapus'
        })
