import requests
import json

def fetch_meet_matches(event_code, season=2025):
    """Fetch full structured match data for a specific meet."""
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
    if response.status_code != 200:
        return []
    
    data = response.json()
    matches_raw = data['data']['eventByCode']['matches']
   
    # Process each match
    structured_matches = []
    for match in matches_raw:
        red_teams = []
        blue_teams = []
        
        for team in match['teams']:
            if team['alliance'] == 'Red':
                red_teams.append(str(team['teamNumber']))
            else:
                blue_teams.append(str(team['teamNumber']))
        
        scores = match.get('scores')
        if not scores:
            continue
            
        red_score = scores['red']['totalPoints']
        blue_score = scores['blue']['totalPoints']
        
        # Calculate RPs
        red_rp = scores['red'].get('movementRp', 0) + scores['red'].get('goalRp', 0) + scores['red'].get('patternRp', 0)
        blue_rp = scores['blue'].get('movementRp', 0) + scores['blue'].get('goalRp', 0) + scores['blue'].get('patternRp', 0)
        
        # Add win/loss/tie RP
        if red_score > blue_score:
            red_rp += 3
        elif blue_score > red_score:
            blue_rp += 3
        else:
            red_rp += 1
            blue_rp += 1
        
        structured_matches.append({
            'match_num': match['matchNum'],
            'red': red_teams,
            'blue': blue_teams,
            'red_score': red_score,
            'blue_score': blue_score,
            'red_rp': red_rp,
            'blue_rp': blue_rp
        })
    
    # Sort by match number
    structured_matches.sort(key=lambda x: x['match_num'])
    return structured_matches

def main():
    meets_data = {}
    
    for event_code, meet_key in [('USCANOEBM1', 'meet1'), ('USCANOEBM2', 'meet2'), ('USCANOEBM3', 'meet3')]:
        print(f"Fetching {event_code}...")
        matches = fetch_meet_matches(event_code)
        meets_data[meet_key] = matches
    
    with open('meets_data.json', 'w') as f:
        json.dump(meets_data, f, indent=2)
    
    print("Saved meets_data.json")

if __name__ == "__main__":
    main()
