import unittest
from src.data_manager import DataManager
from src.ranking_calculator import RankingCalculator

class TestAdvancement(unittest.TestCase):
    def test_initial_rankings(self):
        dm = DataManager()
        teams = dm.get_all_teams()
        
        # Calculate rankings based on Meetings 1-3
        ranked_teams = RankingCalculator.calculate_league_rankings(teams)
        
        print("\n--- Initial League Rankings (Top 10 Matches) ---")
        for t in ranked_teams:
            print(f"Rank {t.league_rank}: {t.number} - Total RP: {t.total_rp} (Matches: {t.matches_played})")
            
        # Verify a specific known team/stat if possible or just ensure no crashes
        self.assertTrue(len(ranked_teams) > 0)
        self.assertEqual(ranked_teams[0].league_rank, 1)

    def test_advancement_calculation(self):
        dm = DataManager()
        teams = dm.get_all_teams()
        ranked_teams = RankingCalculator.calculate_league_rankings(teams)
        
        # Simulate User Scenario:
        # Team 14259 is Rank X. 
        # Add "Inspire 1" to Team 14259.
        awards = {'14259': 60}
        alliance = {}
        playoff = {}
        
        final_teams = RankingCalculator.calculate_advancement_points(ranked_teams, alliance, awards, playoff)
        
        t14259 = next(t for t in final_teams if t.number == '14259')
        print(f"\nTeam 14259 AP with Inspire 1: {t14259.advancement_points}")
        
        # Base Points = (17 - Rank) clipped at 2
        base = max(2, 17 - t14259.league_rank)
        expected = base + 60
        self.assertEqual(t14259.advancement_points, expected)

if __name__ == '__main__':
    unittest.main()
