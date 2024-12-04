from flask import render_template, jsonify, request, redirect, url_for, session
from flask_socketio import emit

def register_routes(app, socketio, db, draft):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/admin')
    def admin():
        return render_template('admin_dashboard.html')

    # Ajoutez vos autres routes ici...

    # Socket.IO events
    @socketio.on('draft_pick')
    def handle_draft_pick(data):
        # Logique de draft pick
        emit('pick_made', data, broadcast=True)

    # Autres événements Socket.IO...
