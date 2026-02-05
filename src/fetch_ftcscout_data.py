import requests
import json

def fetch_meet_data(event_code, season=2025):
    """Fetch all match data for a given event from FTCScout GraphQL API."""
    url = "https://api.ftcscout.org/graphql"
    
    query = """
    query {
      eventByCode(code: "%s", season: %d) {
        matches {
          matchNum
          teams {
            teamNumber
            alliance
            surrogate
          }
          scores {
            ... on MatchScores2025 {
              red {
                totalPoints
                movementRp
                goalRp
                patternRp
              }
              blue {
                totalPoints
                movementRp
                goalRp
                patternRp
              }
            }
          }
        }
      }
    }
    """ % (event_code, season)
    
    response = requests.post(url, json={'query': query})
    if response.status_code == 200:
        data = response.json()
        return data['data']['eventByCode']['matches']
    else:
        print(f"Error fetching {event_code}: {response.status_code}")
        return []

def calculate_match_rp(match, team_num):
    """Calculate RP for a specific team in a match."""
    # Find which alliance the team is on
    alliance = None
    is_surrogate = False
    
    for team_data in match['teams']:
        if str(team_data['teamNumber']) == str(team_num):
            alliance = team_data['alliance']
            is_surrogate = team_data.get('surrogate', False)
            break
    
    if alliance is None:
        return 0, 0  # Team not in match
    
    if is_surrogate:
        return 0, 0  # Surrogates get 0 RP but still get score
    
    scores = match.get('scores')
    if not scores:
        return 0, 0
    
    alliance_data = scores['red'] if alliance == 'Red' else scores['blue']
    opp_alliance_data = scores['blue'] if alliance == 'Red' else scores['red']
    
    total_points = alliance_data['totalPoints']
    opp_points = opp_alliance_data['totalPoints']
    
    # Win/Loss/Tie RP
    if total_points > opp_points:
        base_rp = 3  # Win
    elif total_points == opp_points:
        base_rp = 1  # Tie
    else:
        base_rp = 0  # Loss
    
    # Bonus RPs
    bonus_rp = (alliance_data.get('movementRp', 0) + 
                alliance_data.get('goalRp', 0) + 
                alliance_data.get('patternRp', 0))
    
    total_rp = base_rp + bonus_rp
    
    return total_rp, total_points

def main():
    # Fetch data from all three meets
    meets = [
        ("USCANOEBM1", "M1"),
        ("USCANOEBM2", "M2"),
        ("USCANOEBM3", "M3")
    ]
    
    all_teams = set()
    team_performances = {}
    
    for event_code, meet_prefix in meets:
        print(f"Fetching {event_code}...")
        matches = fetch_meet_data(event_code)
        
        for match in matches:
            match_id = f"{meet_prefix}-Q{match['matchNum']}"
            
            # Collect all teams
            for team_data in match['teams']:
                team_num = str(team_data['teamNumber'])
                all_teams.add(team_num)
                
                if team_num not in team_performances:
                    team_performances[team_num] = []
                
                rp, score = calculate_match_rp(match, team_num)
                
                team_performances[team_num].append({
                    'match_id': match_id,
                    'rp': rp,
                    'score': score,
                    'surrogate': team_data.get('surrogate', False)
                })
    
    # Calculate rankings
    team_rankings = []
    for team_num in all_teams:
        performances = team_performances.get(team_num, [])
        
        # Sort by RP (desc), then score (desc) to get top 10
        performances.sort(key=lambda x: (x['rp'], x['score']), reverse=True)
        top_10 = performances[:10]
        
        total_rp = sum(p['rp'] for p in top_10)
        total_score = sum(p['score'] for p in performances)
        avg_score = total_score / len(performances) if performances else 0
        
        # Count W-L-T
        wins = sum(1 for p in performances if p['rp'] >= 3 and not p['surrogate'])
        losses = sum(1 for p in performances if p['rp'] == 0 and not p['surrogate'])
        ties = sum(1 for p in performances if p['rp'] == 1 and not p['surrogate'])
        
        team_rankings.append({
            'team': team_num,
            'total_rp': total_rp,
            'avg_score': avg_score,
            'matches': len(performances),
            'record': f"{wins}-{losses}-{ties}"
        })
    
    # Sort by total_rp (desc), then avg_score (desc)
    team_rankings.sort(key=lambda x: (x['total_rp'], x['avg_score']), reverse=True)
    
    # Return data instead of printing if needed, or save to file
    # Save to JSON for DataManager
    try:
        with open('ftcscout_data.json', 'w') as f:
            json.dump({
                'team_performances': team_performances,
                'team_rankings': team_rankings
            }, f, indent=2)
        print("Data saved to ftcscout_data.json")
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def update_live_data():
    """Callable function to update data from FTCScout."""
    return main()

if __name__ == "__main__":
    main()
