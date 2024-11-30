from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from draft import Draft
from database import Database
from functools import wraps
import json
import logging
import os

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config['SECRET_KEY'] = 'votre_clé_secrète'
CORS(app)

# Configuration Socket.IO avec gestion des erreurs
socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   async_mode='eventlet',
                   logger=True,
                   engineio_logger=True)

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
    print('Client connected')
    if draft:
        emit_draft_state()

@socketio.on('start_draft')
def handle_start_draft():
    if 'admin_logged_in' not in session:
        return
    
    global draft
    draft = Draft(db)
    draft.initialize_draft()
    emit_draft_state()
    update_current_team()

@socketio.on('make_pick')
def handle_make_pick(data):
    if 'admin_logged_in' not in session:
        return
        
    global draft
    if not draft:
        return

    player_id = data.get('player_id')
    if not player_id:
        return

    # Obtenir l'équipe actuelle
    current_team_id = draft.get_current_team()
    if not current_team_id:
        return

    # Obtenir les informations de l'équipe
    current_team = next((t for t in db.get_teams() if t['id'] == current_team_id), None)
    if not current_team:
        return

    success = draft.make_pick(current_team_id, player_id)
    if success:
        # Récupérer les informations du joueur
        player = next((p for p in db.get_available_players() + sum([db.get_team_players(t['id']) for t in db.get_teams()], []) 
                      if p['id'] == int(player_id)), None)
        
        if player:
            # Annoncer le pick
            pick_data = {
                'team': current_team['name'],
                'player': player['name'],
                'pickNumber': len(draft.picks),
                'round': draft.current_round,
                'player_id': player_id,
                'team_id': current_team_id
            }
            emit('draft_pick', pick_data, broadcast=True)

            # Vérifier si le draft est terminé
            available_players = db.get_available_players()
            if not available_players:
                emit('draft_complete', broadcast=True)

            # Mettre à jour l'état du draft
            emit_draft_state()
            
            # Passer à l'équipe suivante
            update_current_team()

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
        return

    # Récupérer tous les picks avec les informations complètes
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

    # Log des informations des équipes
    teams = db.get_teams()
    logger.debug(f"Teams data: {json.dumps(teams, indent=2)}")

    # Récupérer les joueurs par équipe
    teams_with_players = []
    for team in teams:
        team_players = db.get_team_players(team['id'])
        team_data = {
            'id': team['id'],
            'name': team['name'],
            'logo_url': team['logo_url'],
            'players': team_players
        }
        teams_with_players.append(team_data)
        logger.debug(f"Team {team['name']} data: {json.dumps(team_data, indent=2)}")

    draft_data = {
        'teams': teams_with_players,
        'availablePlayers': db.get_available_players(),
        'draftState': {
            'phase': 'TOP12' if len(draft.picks) < 12 else 'BOTTOM20',
            'current_round': draft.current_round,
            'picks': picks_with_info
        },
        'is_admin': 'admin_logged_in' in session
    }
    
    logger.debug(f"Emitting draft_update with data: {json.dumps(draft_data, indent=2)}")
    emit('draft_update', draft_data, broadcast=True)

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
