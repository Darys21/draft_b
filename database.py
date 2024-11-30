import sqlite3
import os
import json

class Database:
    def __init__(self):
        self.db_path = "draft.db"
        self.initialize_database()
        self.initialize_data_if_empty()

    def initialize_database(self):
        """Initialise la base de données"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Créer la table des équipes si elle n'existe pas
        c.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                logo_url TEXT
            )
        ''')

        # Créer la table des joueurs si elle n'existe pas
        c.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                position TEXT,
                stats TEXT,
                is_top12 INTEGER,
                team_id INTEGER,
                FOREIGN KEY (team_id) REFERENCES teams(id)
            )
        ''')

        conn.commit()
        conn.close()

    def initialize_data_if_empty(self):
        """Initialise les données par défaut si les tables sont vides"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Vérifier si la table teams est vide
        c.execute("SELECT COUNT(*) FROM teams")
        teams_count = c.fetchone()[0]
        
        if teams_count == 0:
            # Insérer les équipes par défaut
            teams_data = [
                (1, "WILD HOOPS", "wildhoops.jpg"),
                (2, "THE UNDEFEATED", "theundefeated.jpg"),
                (3, "Fear of God Athletics", "fearofgod.jpg"),
                (4, "Ours Boys Academy", "oursboysacademy.jpg")
            ]
            c.executemany("INSERT INTO teams (id, name, logo_url) VALUES (?, ?, ?)", teams_data)
            
            # Insérer les joueurs par défaut
            top_players = [
                (1, "Ousmane", "SF", "PPG: 22.5, RPG: 6.8", 1, None),
                (2, "Isaac", "PG", "PPG: 18.3, APG: 7.5", 1, None),
                (3, "Rodrigue", "SG", "PPG: 20.1, RPG: 4.2", 1, None),
                (4, "Paul", "PF", "PPG: 16.8, RPG: 9.3", 1, None),
                (5, "Joan", "C", "PPG: 15.5, RPG: 11.2", 1, None),
                (6, "Léo", "PG", "PPG: 17.9, APG: 6.8", 1, None),
                (7, "Felipe", "SF", "PPG: 19.2, RPG: 5.5", 1, None),
                (8, "Kevin", "SG", "PPG: 21.3, RPG: 4.7", 1, None),
                (9, "Charlin", "PF", "PPG: 17.5, RPG: 8.9", 1, None),
                (10, "Christo", "C", "PPG: 14.8, RPG: 10.5", 1, None),
                (11, "Arfan", "PG", "PPG: 16.9, APG: 8.2", 1, None),
                (12, "Assane", "SF", "PPG: 18.7, RPG: 6.3", 1, None)
            ]
            bottom_players = [
                (13, "Pascal", "PG", "PPG: 11.2, APG: 4.5", 0, None),
                (14, "Malick Charles", "SG", "PPG: 10.5, RPG: 3.2", 0, None),
                (15, "Marco Milwaukee", "SG", "PPG: 15.3, RPG: 4.2", 0, None),
                (16, "NTOUTOUME Claude-Engel", "SF", "PPG: 13.8, RPG: 5.5", 0, None),
                (17, "Carlisme", "PF", "PPG: 12.5, RPG: 7.3", 0, None),
                (18, "Glenn MEYO", "C", "PPG: 11.2, RPG: 8.8", 0, None),
                (19, "Kevin Huchard", "PG", "PPG: 13.9, APG: 6.2", 0, None),
                (20, "Mayeul Adéola SANNY", "SG", "PPG: 14.7, RPG: 3.9", 0, None),
                (21, "Mael-Olivier", "SF", "PPG: 12.8, RPG: 4.5", 0, None),
                (22, "Marc", "PF", "PPG: 11.5, RPG: 6.8", 0, None),
                (23, "Kevin Mesmero", "C", "PPG: 10.8, RPG: 7.9", 0, None),
                (24, "Jordan", "PG", "PPG: 13.2, APG: 5.5", 0, None),
                (25, "Cagil", "SG", "PPG: 12.9, RPG: 3.8", 0, None),
                (26, "Etima benoit", "SF", "PPG: 11.7, RPG: 4.2", 0, None),
                (27, "Levi", "PF", "PPG: 10.5, RPG: 6.5", 0, None),
                (28, "Alexandre Ngoua", "C", "PPG: 9.8, RPG: 7.2", 0, None),
                (29, "Alpha", "PG", "PPG: 12.4, APG: 4.8", 0, None),
                (30, "Joel AMB", "SG", "PPG: 11.9, RPG: 3.5", 0, None),
                (31, "Marcelino", "SF", "PPG: 10.8, RPG: 4.1", 0, None),
                (32, "Rodney", "PF", "PPG: 9.5, RPG: 5.8", 0, None)
            ]
            c.executemany("INSERT INTO players (id, name, position, stats, is_top12, team_id) VALUES (?, ?, ?, ?, ?, ?)", top_players + bottom_players)
        
        conn.commit()
        conn.close()

    def get_teams(self):
        """Retourne toutes les équipes"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id, name, logo_url FROM teams')
        teams = [{'id': row[0], 'name': row[1], 'logo_url': row[2]} for row in c.fetchall()]
        conn.close()
        return teams

    def get_available_players(self):
        """Retourne tous les joueurs disponibles"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # D'abord, récupérer les joueurs TOP 12 dans l'ordre spécifié
        top12_order = {
            'Ousmane': 1,
            'Isaac': 2,
            'Rodrigue': 3,
            'Paul': 4,
            'Joan': 5,
            'Leo': 6,
            'Felipe': 7,
            'Kevin': 8,
            'Charlin': 9,
            'Christo': 10,
            'Arfan': 11,
            'Assane': 12
        }
        
        c.execute('''
            SELECT id, name, position, stats, is_top12 
            FROM players 
            WHERE team_id IS NULL
            ORDER BY 
                CASE 
                    WHEN is_top12 = 1 THEN 0 
                    ELSE 1 
                END,
                CASE name
                    WHEN 'Ousmane' THEN 1
                    WHEN 'Isaac' THEN 2
                    WHEN 'Rodrigue' THEN 3
                    WHEN 'Paul' THEN 4
                    WHEN 'Joan' THEN 5
                    WHEN 'Leo' THEN 6
                    WHEN 'Felipe' THEN 7
                    WHEN 'Kevin' THEN 8
                    WHEN 'Charlin' THEN 9
                    WHEN 'Christo' THEN 10
                    WHEN 'Arfan' THEN 11
                    WHEN 'Assane' THEN 12
                    ELSE 100
                END,
                name
        ''')
        
        players = [{
            'id': row[0],
            'name': row[1],
            'position': row[2],
            'stats': row[3],
            'is_top12': bool(row[4])
        } for row in c.fetchall()]
        
        conn.close()
        return players

    def update_player_status(self, player_id, team_id):
        """Met à jour l'équipe d'un joueur"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('UPDATE players SET team_id = ? WHERE id = ?', (team_id, player_id))
        conn.commit()
        conn.close()

    def get_team_players(self, team_id):
        """Retourne tous les joueurs d'une équipe"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT id, name, position, stats, is_top12 
            FROM players 
            WHERE team_id = ?
            ORDER BY is_top12 DESC, name
        ''', (team_id,))
        players = [{
            'id': row[0],
            'name': row[1],
            'position': row[2],
            'stats': row[3],
            'is_top12': bool(row[4])
        } for row in c.fetchall()]
        conn.close()
        return players
