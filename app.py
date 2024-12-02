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

app = Flask(__name__, static_url_path='/static', static_folder='static')

# Session and security configurations
app.config.update(
    SECRET_KEY=os.urandom(32),
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    SESSION_TYPE='filesystem',
    SESSION_FILE_DIR='/tmp/flask_session/',
    SESSION_PERMANENT=False,
    SESSION_USE_SIGNER=True
)

# More robust CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": ["https://draft-b.onrender.com", "http://localhost:3000"],
        "supports_credentials": True
    }
})

# Enhanced WebSocket Configuration
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

# Configuration admin
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "bleague2024"

# Initialisation de la base de données et du draft
db = Database()
draft = None
current_team = None

# Décorateur pour protéger les routes admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html', is_admin=False)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        return render_template('admin_login.html', error="Invalid credentials")
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/season')
def season():
    teams = []
    for team in db.get_teams():
        players = db.get_team_players(team['id'])
        teams.append({
            'id': team['id'],
            'name': team['name'],
            'logo_url': team['logo_url'],
            'players': players
        })
    return render_template('season.html', teams=teams)

@socketio.on('connect')
def handle_connect():
    try:
        logger.info(f"New WebSocket connection established: {request.sid}")
        
        # Validate session and authentication
        if 'username' not in session:
            logger.warning("Unauthenticated connection attempt")
            return False
        
        # Retrieve draft state
        draft_state = draft.get_draft_state()
        logger.info(f"Connected - Teams count: {len(draft_state['teams'])}, Available players: {len(draft_state['available_players'])}")
        
        # Emit initial draft state to client
        emit('draft_state', draft_state)
        
    except Exception as e:
        logger.error(f"Connection error: {str(e)}", exc_info=True)
        return False

@socketio.on('disconnect')
def handle_disconnect():
    try:
        logger.info(f"WebSocket disconnection: {request.sid}")
        # Optional: Perform cleanup or logging
    except Exception as e:
        logger.error(f"Disconnection error: {str(e)}", exc_info=True)

@socketio.on_error()
def error_handler(e):
    logger.error(f"SocketIO Error: {str(e)}", exc_info=True)

@socketio.on('start_draft')
def handle_start_draft():
    try:
        # Validate admin session
        if 'username' not in session or session['username'] != ADMIN_USERNAME:
            logger.warning("Unauthorized draft start attempt")
            emit('draft_error', {'message': 'Unauthorized access'}, broadcast=False)
            return False
        
        # Check draft state before starting
        if draft.is_draft_active():
            logger.warning("Draft already in progress")
            emit('draft_error', {'message': 'Draft is already in progress'}, broadcast=False)
            return False
        
        # Initialize draft
        draft.initialize_draft()
        draft_state = draft.get_draft_state()
        
        # Broadcast draft start to all clients
        socketio.emit('draft_started', draft_state)
        logger.info("Draft started successfully")
        
    except Exception as e:
        logger.error(f"Error starting draft: {str(e)}", exc_info=True)
        emit('draft_error', {'message': 'Failed to start draft'}, broadcast=False)

@socketio.on('make_pick')
def handle_make_pick(data):
    if 'admin_logged_in' not in session:
        logger.warning("Tentative de pick sans authentification admin")
        return
        
    global draft
    if not draft:
        logger.warning("Tentative de pick sans draft initialisé")
        return

    player_id = data.get('player_id')
    if not player_id:
        logger.warning("Aucun ID de joueur fourni")
        return

    try:
        # Obtenir l'équipe actuelle
        current_team_id = draft.get_current_team()
        if not current_team_id:
            logger.warning("Aucune équipe courante trouvée")
            return

        # Obtenir les informations de l'équipe
        current_team = next((t for t in db.get_teams() if t['id'] == current_team_id), None)
        if not current_team:
            logger.warning(f"Équipe non trouvée pour l'ID {current_team_id}")
            return

        # Vérifier si le joueur est disponible
        available_players = db.get_available_players()
        player = next((p for p in available_players if p['id'] == int(player_id)), None)
        if not player:
            logger.warning(f"Joueur {player_id} non disponible")
            return

        # Effectuer le pick
        success = draft.make_pick(current_team_id, player_id)
        if success:
            # Annoncer le pick
            pick_data = {
                'team': current_team['name'],
                'player': player['name'],
                'pickNumber': len(draft.picks),
                'round': draft.current_round,
                'player_id': player_id,
                'team_id': current_team_id
            }
            socketio.emit('draft_pick', pick_data, broadcast=True)
            logger.info(f"Pick effectué : {current_team['name']} a sélectionné {player['name']}")

            # Vérifier si le draft est terminé
            available_players = db.get_available_players()
            if not available_players:
                socketio.emit('draft_complete', broadcast=True)
                logger.info("Draft terminé")

            # Mettre à jour l'état du draft
            emit_draft_state()
            
            # Passer à l'équipe suivante
            update_current_team()
        else:
            logger.warning(f"Échec du pick pour le joueur {player_id}")
            socketio.emit('error', {
                'message': 'Impossible de sélectionner ce joueur',
                'player_id': player_id
            })

    except Exception as e:
        logger.error(f"Erreur lors du pick : {e}", exc_info=True)
        socketio.emit('error', {
            'message': 'Erreur lors de la sélection du joueur',
            'details': str(e)
        })

@socketio.on('reset_draft')
def handle_reset_draft():
    if 'admin_logged_in' not in session:
        return
    
    global draft
    # Réinitialiser la base de données
    db.initialize_database()
    # Réinitialiser l'objet draft
    draft = None
    # Informer tous les clients de la réinitialisation
    emit('draft_reset', broadcast=True)
    emit('announcement', {
        'message': 'Le draft a été réinitialisé par l\'administrateur',
        'type': 'warning'
    }, broadcast=True)

@socketio.on('chat_message')
def handle_chat_message(data):
    message = data.get('message', '').strip()
    if message:
        is_admin = 'admin_logged_in' in session
        emit('chat_message', {
            'user': 'Admin' if is_admin else 'Spectateur',
            'message': message
        }, broadcast=True)

def emit_draft_state():
    if not draft:
        logger.warning("Draft is not initialized")
        return

    try:
        # Récupérer tous les picks
        picks_with_info = []
        for pick in draft.picks:
            team = next((t for t in db.get_teams() if t['id'] == pick['team_id']), None)
            player = next((p for p in db.get_available_players() + sum([db.get_team_players(t['id']) for t in db.get_teams()], [])
                          if p['id'] == pick['player_id']), None)
            if team and player:
                picks_with_info.append({
                    'team_id': team['id'],
                    'team_name': team['name'],
                    'player_id': player['id'],
                    'player_name': player['name'],
                    'pick_number': len(picks_with_info) + 1
                })

        # Récupérer les joueurs disponibles
        available_players = db.get_available_players()
        logger.info(f"Available players: {len(available_players)}")

        # Récupérer l'équipe actuelle
        current_team_id = draft.get_current_team()
        current_team = next((t for t in db.get_teams() if t['id'] == current_team_id), None)

        # Préparer les données à émettre
        draft_state = {
            'picks': picks_with_info,
            'available_players': available_players,
            'current_team': current_team,
            'current_round': draft.current_round
        }

        # Émettre l'état complet du draft
        socketio.emit('draft_state', draft_state)
        logger.info("Draft state emitted successfully")

    except Exception as e:
        logger.error(f"Error in emit_draft_state: {e}", exc_info=True)
        socketio.emit('error', {'message': 'Erreur lors de la récupération de l\'état du draft'})

def update_current_team():
    if not draft:
        return

    current_team = None
    next_team = None
    
    # Obtenir l'équipe actuelle
    current_team_id = draft.get_current_team()
    if current_team_id:
        current_team = next((t for t in db.get_teams() if t['id'] == current_team_id), None)
    
    # Obtenir la prochaine équipe
    next_team_id = draft.get_next_team()
    if next_team_id:
        next_team = next((t for t in db.get_teams() if t['id'] == next_team_id), None)

    # Émettre les informations des équipes
    emit('draft_teams', {
        'current': current_team,
        'next': next_team
    }, broadcast=True)

# Gestion des erreurs WebSocket
@socketio.on_error_default
def default_error_handler(e):
    logger.error(f'WebSocket error: {str(e)}')
    emit('error', {'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
