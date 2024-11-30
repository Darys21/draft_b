import random

class Draft:
    def __init__(self, database):
        self.db = database
        self.picks = []
        self.team_order = []
        self.teams = []
        self.current_round = 1
        self.teams_in_current_round = []

    def initialize_draft(self):
        """Initialise le draft avec un ordre aléatoire des équipes"""
        teams = self.db.get_teams()
        team_ids = [team['id'] for team in teams]
        # Mélanger l'ordre initial des équipes
        random.shuffle(team_ids)
        self.team_order = team_ids
        self.teams = team_ids
        # Copier l'ordre pour le premier round
        self.teams_in_current_round = team_ids.copy()
        self.picks = []
        self.current_round = 1

    def get_current_team_id(self):
        """Retourne l'ID de l'équipe qui doit faire son pick"""
        if not self.teams_in_current_round:
            # Si toutes les équipes ont fait leur pick dans ce round,
            # commencer un nouveau round avec un ordre aléatoire
            self.current_round += 1
            self.teams_in_current_round = self.team_order.copy()
            random.shuffle(self.teams_in_current_round)

        if self.teams_in_current_round:
            return self.teams_in_current_round[0]
        return None

    def get_current_team(self):
        """Retourne l'ID de l'équipe actuelle"""
        if not self.teams_in_current_round:
            # Si toutes les équipes ont fait leur pick dans ce round,
            # commencer un nouveau round
            self.current_round += 1
            self.teams_in_current_round = self.team_order.copy()
            random.shuffle(self.teams_in_current_round)
        
        if self.teams_in_current_round:
            return self.teams_in_current_round[0]
        return None

    def get_next_team(self):
        """Retourne l'ID de la prochaine équipe"""
        if not self.teams_in_current_round:
            # Si le round actuel est terminé, regarder le prochain round
            next_round_teams = self.team_order.copy()
            random.shuffle(next_round_teams)
            return next_round_teams[0] if next_round_teams else None
            
        if len(self.teams_in_current_round) > 1:
            return self.teams_in_current_round[1]
        else:
            # Si c'est le dernier pick du round, prendre la première équipe du prochain round
            next_round_teams = self.team_order.copy()
            random.shuffle(next_round_teams)
            return next_round_teams[0]

    def make_pick(self, team_id, player_id):
        """Fait un pick pour une équipe"""
        # Vérifier que c'est bien le tour de cette équipe
        if team_id != self.get_current_team():
            return False

        # Vérifier que le joueur est disponible
        available_players = self.db.get_available_players()
        if not any(p['id'] == int(player_id) for p in available_players):
            return False

        # Faire le pick
        self.picks.append({
            'team_id': team_id,
            'player_id': int(player_id),
            'round': self.current_round
        })

        # Mettre à jour le statut du joueur dans la base de données
        self.db.update_player_status(int(player_id), team_id)

        # Retirer l'équipe qui vient de faire son pick de la liste du round actuel
        self.teams_in_current_round.pop(0)

        return True

    def get_picks_for_team(self, team_id):
        """Retourne tous les picks d'une équipe"""
        return [pick for pick in self.picks if pick['team_id'] == team_id]

    def get_teams_order(self):
        """Retourne l'ordre actuel des équipes"""
        return self.teams_in_current_round