from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from datetime import timedelta
import os
import logging
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from draft import Draft
from database import Database
from functools import wraps
import json
from gevent import monkey
monkey.patch_all()

# Enhanced logging configuration
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Application Factory Pattern
def create_app():
    # Create Flask app
    app = Flask(__name__, static_url_path='/static', static_folder='static')
    
    # Configuration
    app.config.update(
        SECRET_KEY=os.urandom(32),
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
        SESSION_TYPE='filesystem',
        SESSION_FILE_DIR='/tmp/flask_session/',
        SESSION_PERMANENT=False,
        SESSION_USE_SIGNER=True,
        PROPAGATE_EXCEPTIONS=True
    )

    # CORS Configuration
    CORS(app, resources={
        r"/*": {
            "origins": ["https://draft-b.onrender.com", "http://localhost:3000"],
            "supports_credentials": True
        }
    })

    # Global variables and database initialization
    global db, draft
    db = Database()
    draft = Draft(db)

    # Initialize SocketIO
    global socketio
    socketio = SocketIO(
        app, 
        cors_allowed_origins=["https://draft-b.onrender.com", "http://localhost:3000"],
        async_mode='gevent',
        async_handlers=True,
        ping_timeout=120,
        ping_interval=30,
        max_http_buffer_size=1e8,
        logger=True, 
        engineio_logger=True,
        cors_credentials=True
    )

    # Import and register routes
    from routes import register_routes
    register_routes(app, socketio, db, draft)

    return app

# Configuration admin
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "bleague2024"

# Décorateur pour protéger les routes admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Expose app for Gunicorn compatibility
app = create_app()

# If this file is run directly, create and run the app
if __name__ == '__main__':
    socketio.run(app, debug=True)
