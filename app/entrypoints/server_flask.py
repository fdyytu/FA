from flask import Flask, render_template, send_from_directory, jsonify, request
import os

app = Flask(__name__)

# Serve static files
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Admin dashboard routes
@app.route('/admin')
@app.route('/admin/')
def admin_dashboard():
    return send_from_directory('static/admin', 'dashboard_main.html')

@app.route('/admin/<filename>')
def admin_files(filename):
    try:
        return send_from_directory('static/admin', filename)
    except:
        return send_from_directory('static/admin', 'dashboard_main.html')

# Root route
@app.route('/')
def index():
    return send_from_directory('static/admin', 'dashboard_main.html')

# API endpoints for testing
@app.route('/api/auth/login', methods=['POST'])
def login():
    return jsonify({
        'success': True,
        'data': {
            'token': 'mock_token_123',
            'user': {
                'id': 1,
                'username': 'admin',
                'email': 'admin@fa-application.com',
                'role': 'admin'
            }
        }
    })

# Admin API endpoints
@app.route('/api/v1/admin/auth/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Simple authentication check
    if username == 'admin' and password == 'admin123':
        return jsonify({
            'success': True,
            'access_token': 'admin_token_12345',
            'user': {
                'id': 1,
                'username': 'admin',
                'email': 'admin@fa-application.com',
                'role': 'admin'
            }
        })
    else:
        return jsonify({
            'success': False,
            'detail': 'Username atau password salah'
        }), 401

@app.route('/api/v1/admin/auth/logout', methods=['POST'])
def admin_logout():
    return jsonify({
        'success': True,
        'message': 'Logout berhasil'
    })

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

# Additional endpoints for dashboard functionality
@app.route('/api/v1/admin/transactions/recent')
def recent_transactions():
    return jsonify({
        'success': True,
        'data': [
            {
                'id': 1,
                'user': 'John Doe',
                'product': 'Pulsa Telkomsel 50K',
                'amount': 52000,
                'status': 'success',
                'created_at': '2024-01-16T09:30:00Z'
            },
            {
                'id': 2,
                'user': 'Jane Smith',
                'product': 'Token PLN 100K',
                'amount': 102500,
                'status': 'pending',
                'created_at': '2024-01-16T09:25:00Z'
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
                'owner': 'ADMIN',
                'bot_id': 1,
                'is_active': True,
                'created_at': '2024-01-15T10:30:00Z'
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
                'command': '!buy diamond',
                'user': 'user123',
                'bot': 'FA Store Bot',
                'status': 'success',
                'created_at': '2024-01-16T10:30:00Z'
            }
        ]
    })

@app.route('/api/v1/admin/discord/logs')
def bot_logs():
    return jsonify({
        'success': True,
        'data': [
            {
                'id': 1,
                'level': 'INFO',
                'message': 'Bot started successfully',
                'bot': 'FA Store Bot',
                'created_at': '2024-01-16T10:00:00Z'
            }
        ]
    })

@app.route('/api/dashboard/stats')
def dashboard_stats():
    return jsonify({
        'success': True,
        'data': {
            'total_revenue': 125000000,
            'total_orders': 1847,
            'total_users': 1250,
            'total_products': 156
        }
    })

@app.route('/api/products')
def products():
    return jsonify({
        'success': True,
        'data': [
            {
                'id': 1,
                'name': 'Diamond Mobile Legends',
                'category': 'Mobile Legends',
                'price': 50000,
                'stock': 100,
                'status': 'active'
            },
            {
                'id': 2,
                'name': 'UC PUBG Mobile',
                'category': 'PUBG Mobile',
                'price': 25000,
                'stock': 50,
                'status': 'active'
            }
        ]
    })

@app.route('/api/users')
def users():
    return jsonify({
        'success': True,
        'data': [
            {
                'id': 1,
                'username': 'user123',
                'email': 'user123@example.com',
                'status': 'active',
                'created_at': '2024-01-15T10:30:00Z'
            },
            {
                'id': 2,
                'username': 'gamer456',
                'email': 'gamer456@example.com',
                'status': 'active',
                'created_at': '2024-01-14T15:45:00Z'
            }
        ]
    })

@app.route('/api/analytics/overview')
def analytics_overview():
    return jsonify({
        'success': True,
        'data': {
            'total_revenue': 125000000,
            'revenue_change': 12.5,
            'total_orders': 1847,
            'orders_change': 8.2,
            'conversion_rate': 3.4,
            'conversion_change': 2.1,
            'avg_order_value': 67500,
            'aov_change': 5.7
        }
    })

@app.route('/api/settings')
def settings():
    return jsonify({
        'success': True,
        'data': {
            'general': {
                'site_name': 'FA Application',
                'site_description': 'Platform jual beli game online terpercaya',
                'site_url': 'https://fa-application.com',
                'contact_email': 'admin@fa-application.com'
            }
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
