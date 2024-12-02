from gevent import monkey
monkey.patch_all()

import logging
logging.basicConfig(level=logging.DEBUG)

from app import app, socketio

# Explicit WebSocket configuration
app.config['SOCKETIO_ASYNC_MODE'] = 'gevent'
app.config['SOCKETIO_ASYNC_HANDLERS'] = True

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
else:
    # For Gunicorn deployment
    application = app
