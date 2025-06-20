"""
Flask Server - Modular Implementation
Server Flask yang telah dipecah menjadi beberapa module routes
"""

from flask import Flask
import os

# Import route modules
from .routes.static_routes import register_static_routes
from .routes.auth_routes import register_auth_routes
from .routes.admin_routes import register_admin_routes
from .routes.discord_routes import register_discord_routes

app = Flask(__name__)

# Register all route modules
register_static_routes(app)
register_auth_routes(app)
register_admin_routes(app)
register_discord_routes(app)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
