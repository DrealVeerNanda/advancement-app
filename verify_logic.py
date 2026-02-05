from src.data_manager import DataManager
from src.ranking_calculator import RankingCalculator

dm = DataManager()
teams = dm.get_all_teams()
ranked = RankingCalculator.calculate_league_rankings(teams)

print("--- RANKINGS ---")
for t in ranked:
    print(f"Rank {t.league_rank}: {t.number} - RP: {t.total_rp}")
    if t.number == "25627":
        print("Breakdown for 25627:")
        for m in t.match_breakdown:
            print(f"  {m['match_id']}: RP {m['rp']}, Score {m['score']}, Counted {m['is_counted']}")
