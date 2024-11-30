from gevent import monkey
monkey.patch_all()

import logging
logging.basicConfig(level=logging.DEBUG)

from app import app, socketio

# Configuration pour le WebSocket
app.config['PROPAGATE_EXCEPTIONS'] = True

if __name__ == '__main__':
    socketio.run(app)
