import re
import json
from typing import List, Dict, Optional

class Match:
    def __init__(self, match_id: str, red_alliance: List[str], blue_alliance: List[str], 
                 red_score: int, blue_score: int, red_rp: int, blue_rp: int, 
                 match_type: str = "MEET", surrogates: List[str] = None):
        self.match_id = match_id
        self.red_alliance = red_alliance
        self.blue_alliance = blue_alliance
        self.red_score = red_score
        self.blue_score = blue_score
        self.red_rp = red_rp
        self.blue_rp = blue_rp
        self.match_type = match_type
        self.surrogates = surrogates if surrogates else []

class Team:
    def __init__(self, number: str, name: str, location: str):
        self.number = number
        self.name = name
        self.location = location
        self.matches: List[Match] = []
        self._ftc_performances: List[Dict] = []
        self.total_rp = 0
        self.avg_score = 0
        self.league_rank = 0
        self.advancement_points = 0
        
    def add_match(self, match: Match):
        self.matches.append(match)
        
    def remove_match(self, match_id: str):
        self.matches = [m for m in self.matches if m.match_id != match_id]

    def clone(self):
        """Create a deep copy of the team - sufficient for hypothetical calculations."""
        new_team = Team(self.number, self.name, self.location)
        # Shallow copy matches list, but since we only append new matches for hypothetical, 
        # sharing the old match objects is fine
        new_team.matches = self.matches.copy()
        
        # Deep copy this list of dicts
        new_team._ftc_performances = [p.copy() for p in self._ftc_performances]
            
        new_team.total_rp = self.total_rp
        new_team.avg_score = self.avg_score
        new_team.league_rank = self.league_rank
        new_team.advancement_points = self.advancement_points
        return new_team

class DataManager:
    def __init__(self):
        self.teams: Dict[str, Team] = {}
        self.matches: List[Match] = []
        self._initialize_teams()
        self._load_ftcscout_data()
        self._load_tournament_data()

    def reload_ftc_data(self):
        """Reloads the FTC scout data from file."""
        self._load_ftcscout_data()
        
    def _initialize_teams(self):
        team_data = [
            ("5214", '"B.R.O." (Bot Resources Operation)', "Dublin, CA, USA"),
            ("11920", "QLS RaD Team", "Dublin, CA, USA"),
            ("14259", "TURBΩ V8", "Pleasanton, CA, USA"),
            ("14770", "Control+Q", "Dublin, CA, USA"),
            ("23212", "Dublin Robotics Cybirds", "Dublin, CA, USA"),
            ("23279", "Turbotrons", " Pleasanton, CA, USA"),
            ("23304", "Cyber Knights", "Dublin, CA, USA"),
            ("25627", "Robowarriors", "Fremont, CA, USA"),
            ("25810", "Cerberus", "Pleasanton, CA, USA"),
            ("26891", "Tech Titans", "Fremont, CA, USA"),
            ("30450", "Sharp Face Robotics", "Dublin, CA, USA"),
            ("30473", "Duck", "Dublin, CA, USA"),
            ("30474", "Quantum Sparks", "Dublin, CA, USA"),
            ("32098", "Robo Raptors", "Pleasanton, CA, USA"),
        ]
        for num, name, loc in team_data:
            self.teams[num] = Team(num, name, loc)

    def _load_ftcscout_data(self):
        """Load real match data from FTCScout API fetch results."""
        try:
            with open('ftcscout_data.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print("Warning: ftcscout_data.json not found. Run fetch_ftcscout_data.py first")
            return
        
        team_performances = data['team_performances']
        
        for team_num, performances in team_performances.items():
            if team_num in self.teams:
                self.teams[team_num]._ftc_performances = []
                for perf in performances:
                    self.teams[team_num]._ftc_performances.append({
                        'match_id': perf['match_id'],
                        'rp': perf['rp'],
                        'score': perf['score'],
                        'is_surrogate': perf['surrogate']
                    })

    def _save_tournament_data(self):
        """Save tournament matches to a file."""
        tournament_matches = [m for m in self.matches if m.match_type == "TOURNAMENT"]
        data = []
        for m in tournament_matches:
            data.append({
                'match_id': m.match_id,
                'red_alliance': m.red_alliance,
                'blue_alliance': m.blue_alliance,
                'red_score': m.red_score,
                'blue_score': m.blue_score,
                'red_rp': m.red_rp,
                'blue_rp': m.blue_rp
            })
        
        try:
            with open('tournament_matches.json', 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving tournament data: {e}")

    def _load_tournament_data(self):
        """Load tournament matches from a file."""
        try:
            with open('tournament_matches.json', 'r') as f:
                data = json.load(f)
                for item in data:
                    self.add_tournament_match(
                        item['match_id'],
                        item['red_alliance'][0], item['red_alliance'][1],
                        item['blue_alliance'][0], item['blue_alliance'][1],
                        item['red_score'], item['blue_score'],
                        item['red_rp'], item['blue_rp'],
                        save=False # Don't trigger another save while loading
                    )
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error loading tournament data: {e}")

    def add_tournament_match(self, match_id, r1, r2, b1, b2, rs, bs, rrp, brp, save=True):
        match = Match(match_id, [r1, r2], [b1, b2], rs, bs, rrp, brp, match_type="TOURNAMENT")
        self.matches.append(match)
        for team_num in [r1, r2, b1, b2]:
            if team_num in self.teams:
                self.teams[team_num].add_match(match)
        
        if save:
            self._save_tournament_data()

    def delete_match(self, match_id):
        self.matches = [m for m in self.matches if m.match_id != match_id]
        for team in self.teams.values():
            team.remove_match(match_id)
        self._save_tournament_data()
            
    def clear_tournament_matches(self):
        ids_to_remove = [m.match_id for m in self.matches if m.match_type == "TOURNAMENT"]
        for mid in ids_to_remove:
            self.matches = [m for m in self.matches if m.match_id != mid]
            for team in self.teams.values():
                team.remove_match(mid)
        self._save_tournament_data()

    def get_team_matches(self, team_num: str) -> List[Match]:
        if team_num in self.teams:
            return self.teams[team_num].matches
        return []

    def get_all_teams(self) -> List[Team]:
        return list(self.teams.values())
        
    def get_all_teams_with_hypothetical(self, hypothetical_matches: List[Dict]) -> List[Team]:
        """
        Returns a list of teams with hypothetical matches applied.
        Does NOT modify the actual state.
        """
        # Clone all teams
        temp_teams = {t_id: team.clone() for t_id, team in self.teams.items()}
        
        # Apply hypothetical matches
        for m_data in hypothetical_matches:
            # Create a temporary match object
            # format expected: {match_id, r1, r2, b1, b2, rs, bs, rrp, brp}
            match = Match(
                m_data['match_id'],
                [m_data['r1'], m_data['r2']],
                [m_data['b1'], m_data['b2']],
                m_data['rs'], m_data['bs'],
                m_data['rrp'], m_data['brp'],
                match_type="TOURNAMENT"
            )
            
            # Add to cloned teams
            for team_num in [m_data['r1'], m_data['r2'], m_data['b1'], m_data['b2']]:
                if team_num in temp_teams:
                    temp_teams[team_num].add_match(match)
                    
        return list(temp_teams.values())
    
    def get_tournament_matches(self) -> List[Dict]:
        return [m for m in self.matches if m.match_type == "TOURNAMENT"]
