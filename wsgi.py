import os
import sys

# Add the project directory to Python path
project_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_dir)

from gevent import monkey
monkey.patch_all()

import logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from app import create_app, socketio

# Create the Flask app
app = create_app()

# Explicit WebSocket configuration
app.config['SOCKETIO_ASYNC_MODE'] = 'gevent'
app.config['SOCKETIO_ASYNC_HANDLERS'] = True

# Ensure secret key is set
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_secret_key_change_in_production')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
else:
    # For Gunicorn deployment
    application = app
