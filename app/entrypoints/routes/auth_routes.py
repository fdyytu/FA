"""
Flask Server - Auth Routes
Routes untuk authentication endpoints
"""

from flask import jsonify, request


def register_auth_routes(app):
    """Register authentication routes"""
    
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

    @app.route('/api/v1/admin/auth/login', methods=['POST'])
    def admin_login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Mock authentication
        if username == 'admin' and password == 'admin123':
            return jsonify({
                'success': True,
                'data': {
                    'token': 'admin_token_456',
                    'user': {
                        'id': 1,
                        'username': 'admin',
                        'email': 'admin@fa-application.com',
                        'role': 'admin'
                    }
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401

    @app.route('/api/v1/admin/auth/logout', methods=['POST'])
    def admin_logout():
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
