"""
Auth Routes
Routes untuk authentication dan authorization
"""

from flask import jsonify, request


def register_auth_routes(app):
    """Register authentication routes"""
    
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
