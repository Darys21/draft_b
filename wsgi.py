from gevent import monkey
monkey.patch_all()

import logging
logging.basicConfig(level=logging.DEBUG)

from app import app, socketio

# Configuration pour le WebSocket
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SECRET_KEY'] = 'votre_clé_secrète_sécurisée'  # Utilisez une clé secrète forte

if __name__ == '__main__':
    socketio.run(app, debug=True)
