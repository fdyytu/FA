from flask import Flask, send_from_directory, jsonify, request
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
    return send_from_directory('static/admin', 'login_android.html')

@app.route('/admin/<filename>')
def admin_files(filename):
    try:
        return send_from_directory('static/admin', filename)
    except:
        return send_from_directory('static/admin', 'login_android.html')

# Root route
@app.route('/')
def index():
    return send_from_directory('static/admin', 'login_android.html')

# Admin API endpoints
@app.route('/api/v1/admin/auth/login', methods=['POST'])
def admin_login():
    try:
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
    except Exception as e:
        return jsonify({
            'success': False,
            'detail': f'Error: {str(e)}'
        }), 500

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
            }
        ]
    })

@app.route('/api/v1/admin/discord/bots', methods=['POST'])
def create_discord_bot():
    try:
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
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("Starting FA Dashboard Server...")
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
