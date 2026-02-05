from typing import List, Dict, Tuple
from src.data_manager import Team, Match

class RankingCalculator:
    @staticmethod
    def calculate_league_rankings(teams: List[Team]) -> List[Team]:
        """
        Calculates League Rankings using FTCScout data + Tournament matches.
        Rule: Rank = Sum of (Top 10 RPs from League Meets + Top 5 RPs from Tournament).
        """
        for team in teams:
            # Get league meet performances from FTCScout data
            league_performances = []
            if hasattr(team, '_ftc_performances'):
                league_performances = team._ftc_performances.copy()
            
            # Get tournament performances from team.matches
            tournament_performances = []
            for match in team.matches:
                if match.match_type == "TOURNAMENT":
                    # Determine which alliance this team was on
                    if team.number in match.red_alliance:
                        rp = match.red_rp
                        score = match.red_score
                    else:
                        rp = match.blue_rp
                        score = match.blue_score
                    
                    tournament_performances.append({
                        'match_id': match.match_id,
                        'rp': rp,
                        'score': score,
                        'is_surrogate': False,
                        'is_tournament': True
                    })
            
            # Sort league performances by RP (desc), then score (desc)
            league_sorted = sorted(league_performances, key=lambda x: (x['rp'], x['score']), reverse=True)
            top_10_league = league_sorted[:10]
            
            # Sort tournament performances by RP (desc), then score (desc)
            tournament_sorted = sorted(tournament_performances, key=lambda x: (x['rp'], x['score']), reverse=True)
            top_5_tournament = tournament_sorted[:5]
            
            # Calculate total RP from top 10 league + top 5 tournament
            league_rp = sum(p['rp'] for p in top_10_league)
            tournament_rp = sum(p['rp'] for p in top_5_tournament)
            team.total_rp = league_rp + tournament_rp
            
            # Track IDs of counted matches for UI highlighting
            top_10_league_ids = set(p['match_id'] for p in top_10_league)
            top_5_tournament_ids = set(p['match_id'] for p in top_5_tournament)
            
            # Calculate stats
            all_performances = league_performances + tournament_performances
            team.matches_played = len(all_performances)
            total_score = sum(p['score'] for p in all_performances)
            team.avg_score = total_score / team.matches_played if team.matches_played > 0 else 0
            
            # Build breakdown for UI - sort alphabetically for display
            all_performances_sorted = sorted(all_performances, key=lambda x: x['match_id'])
            
            breakdown = []
            for p in all_performances_sorted:
                is_tournament = p.get('is_tournament', False)
                if is_tournament:
                    is_counted = p['match_id'] in top_5_tournament_ids
                else:
                    is_counted = p['match_id'] in top_10_league_ids
                    
                breakdown.append({
                    'match_id': p['match_id'],
                    'rp': p['rp'],
                    'score': p['score'],
                    'is_counted': is_counted,
                    'is_surrogate': p.get('is_surrogate', False),
                    'is_tournament': is_tournament
                })
            
            team.match_breakdown = breakdown
        
        # Sort teams: Total RP (Desc), then Avg Score (Desc)
        sorted_teams = sorted(teams, key=lambda t: (t.total_rp, t.avg_score), reverse=True)
        
        # Assign Ranks
        for i, team in enumerate(sorted_teams):
            team.league_rank = i + 1
            
        return sorted_teams

    @staticmethod
    def calculate_advancement_points(teams: List[Team], 
                                     alliance_selections: Dict[str, int], 
                                     awards: Dict[str, int],
                                     playoff_results: Dict[str, int]) -> List[Team]:
        for team in teams:
            points = 0
            qual_pts = max(2, 17 - team.league_rank)
            points += qual_pts
            if team.number in alliance_selections:
                alliance_num = alliance_selections[team.number]
                points += (21 - alliance_num)
            if team.number in awards:
                points += awards[team.number]
            if team.number in playoff_results:
                points += playoff_results[team.number]
            team.advancement_points = points
            
        sorted_by_ap = sorted(teams, key=lambda t: t.advancement_points, reverse=True)
        return sorted_by_ap
