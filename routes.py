from flask import render_template, request, session, redirect, url_for
from functools import wraps

# Configuration admin
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "bleague2024"

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def register_routes(app, socketio, db, draft):
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
                session['username'] = username
                return redirect(url_for('admin_dashboard'))
            return render_template('admin_login.html', error="Invalid credentials")
        return render_template('admin_login.html')

    @app.route('/admin/logout')
    def admin_logout():
        session.pop('admin_logged_in', None)
        session.pop('username', None)
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

    # Add WebSocket event handlers
    from app import (
        handle_connect, handle_disconnect, handle_start_draft, 
        handle_make_pick, handle_reset_draft, handle_chat_message, 
        emit_draft_state, update_current_team
    )

    socketio.on_namespace(socketio.namespace)
    socketio.on('connect')(handle_connect)
    socketio.on('disconnect')(handle_disconnect)
    socketio.on('start_draft')(handle_start_draft)
    socketio.on('make_pick')(handle_make_pick)
    socketio.on('reset_draft')(handle_reset_draft)
    socketio.on('chat_message')(handle_chat_message)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app
