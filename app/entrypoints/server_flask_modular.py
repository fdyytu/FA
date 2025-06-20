"""
Flask Server - Main Application
Server Flask yang telah direfactor dengan routes yang dipecah menjadi modul terpisah
"""

from flask import Flask
import os

# Import route modules
from .routes.static_routes import register_static_routes
from .routes.auth_routes import register_auth_routes
from .routes.discord_routes import register_discord_routes
from .routes.admin_routes import register_admin_routes
from .routes.api_routes import register_api_routes


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Register all route modules
    register_static_routes(app)
    register_auth_routes(app)
    register_discord_routes(app)
    register_admin_routes(app)
    register_api_routes(app)
    
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
