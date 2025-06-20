"""
Static Routes
Routes untuk serving static files dan admin dashboard
"""

from flask import send_from_directory


def register_static_routes(app):
    """Register static file routes"""
    
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
