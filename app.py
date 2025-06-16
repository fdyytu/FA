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
