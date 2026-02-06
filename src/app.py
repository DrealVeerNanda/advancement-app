import threading
import time
from src.fetch_ftcscout_data import update_live_data

# ... existing imports
from flask import Flask, render_template, request, jsonify
import json
from src.data_manager import DataManager
from src.ranking_calculator import RankingCalculator

app = Flask(__name__)
data_manager = DataManager()
ranking_calculator = RankingCalculator()

# Background Task for Live Updates
def background_data_fetch():
    while True:
        try:
            print("Fetching live data from FTCScout...")
            if update_live_data():
                print("Data updated successfully. Reloading DataManager...")
                data_manager.reload_ftc_data()
            else:
                print("No data verification or error during fetch.")
        except Exception as e:
            print(f"Error in background fetch: {e}")
        
        # specific interval (e.g., 5 minutes = 300 seconds)
        time.sleep(300)

# Start background thread (daemon so it dies when main app dies)
threading.Thread(target=background_data_fetch, daemon=True).start()

# In-memory storage for advancement inputs (awards, alliance selection)
advancement_state = {
    'alliance_selections': {}, 
    'detailed_alliances': {
        'alliance1': {'captain': None, 'pick1': None, 'pick2': None},
        'alliance2': {'captain': None, 'pick1': None, 'pick2': None},
        'alliance3': {'captain': None, 'pick1': None, 'pick2': None},
        'alliance4': {'captain': None, 'pick1': None, 'pick2': None}
    },
    'awards': {}, 
    'playoff_results': {} 
}

def save_advancement_state():
    """Save advancement state to a file."""
    try:
        with open('advancement_state.json', 'w') as f:
            json.dump(advancement_state, f, indent=4)
    except Exception as e:
        print(f"Error saving advancement state: {e}")

def load_advancement_state():
    """Load advancement state from a file."""
    global advancement_state
    try:
        with open('advancement_state.json', 'r') as f:
            loaded_data = json.load(f)
            # Merge loaded data with default structure to ensure keys exist
            for k, v in loaded_data.items():
                if k == 'detailed_alliances' and isinstance(v, dict):
                    # Ensure all alliances exist
                    for all_key_default in advancement_state['detailed_alliances']:
                         if all_key_default not in v:
                             v[all_key_default] = advancement_state['detailed_alliances'][all_key_default]
                advancement_state[k] = v
            
            # Ensure detailed_alliances exists if not in loaded data
            if 'detailed_alliances' not in advancement_state:
                 advancement_state['detailed_alliances'] = {
                    'alliance1': {'captain': None, 'pick1': None, 'pick2': None},
                    'alliance2': {'captain': None, 'pick1': None, 'pick2': None},
                    'alliance3': {'captain': None, 'pick1': None, 'pick2': None},
                    'alliance4': {'captain': None, 'pick1': None, 'pick2': None}
                }
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error loading advancement state: {e}")

# Load initial state
load_advancement_state()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/teams', methods=['GET'])
def get_teams():
    teams = data_manager.get_all_teams()
    ranked_teams = ranking_calculator.calculate_league_rankings(teams)
    
    result = []
    for t in ranked_teams:
        result.append({
            'rank': t.league_rank,
            'number': t.number,
            'name': t.name,
            'total_rp': t.total_rp,
            'matches_played': t.matches_played,
            'avg_score': round(t.avg_score, 2),
            'breakdown': getattr(t, 'match_breakdown', [])
        })
    return jsonify(result)

@app.route('/api/matches', methods=['POST'])
def add_match():
    data = request.json
    try:
        data_manager.add_tournament_match(
            data['match_id'],
            data['r1'], data['r2'], data['b1'], data['b2'],
            int(data['rs']), int(data['bs']),
            int(data['rrp']), int(data['brp'])
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/matches/<category>', methods=['GET'])
def get_matches(category):
    # category: 'all', 'meet1', 'meet2', 'meet3', 'tournament'
    all_matches = data_manager.matches
    filtered = []
    
    for m in all_matches:
        include = False
        if category == 'all':
            include = True
        elif category == 'tournament':
            include = (m.match_type == 'TOURNAMENT')
        elif category == 'meet1':
            include = m.match_id.startswith('M1-')
        elif category == 'meet2':
            include = m.match_id.startswith('M2-')
        elif category == 'meet3':
            include = m.match_id.startswith('M3-')
            
        if include:
            filtered.append({
                'id': m.match_id,
                'r1': m.red_alliance[0],
                'r2': m.red_alliance[1],
                'b1': m.blue_alliance[0],
                'b2': m.blue_alliance[1],
                'rs': m.red_score,
                'bs': m.blue_score,
                'rrp': m.red_rp,
                'brp': m.blue_rp
            })
            
    return jsonify(filtered)

@app.route('/api/meets/<meet_id>', methods=['GET'])
def get_meet_matches(meet_id):
    """Serve meet match data from FTCScout JSON."""
    try:
        with open('meets_data.json', 'r') as f:
            meets_data = json.load(f)
    except:
        return jsonify([])
    
    return jsonify(meets_data.get(meet_id, []))

@app.route('/api/matches/<match_id>', methods=['DELETE'])
def delete_match(match_id):
    data_manager.delete_match(match_id)
    return jsonify({'success': True})

@app.route('/api/reset', methods=['POST'])
def reset_scenario():
    data_manager.clear_tournament_matches()
    advancement_state['alliance_selections'].clear()
    advancement_state['detailed_alliances'] = {
        'alliance1': {'captain': None, 'pick1': None, 'pick2': None},
        'alliance2': {'captain': None, 'pick1': None, 'pick2': None},
        'alliance3': {'captain': None, 'pick1': None, 'pick2': None},
        'alliance4': {'captain': None, 'pick1': None, 'pick2': None}
    }
    advancement_state['awards'].clear()
    advancement_state['playoff_results'].clear()
    save_advancement_state()
    return jsonify({'success': True})

@app.route('/api/alliance_selection', methods=['GET', 'POST'])
def handle_alliance_selection():
    if request.method == 'GET':
        return jsonify(advancement_state.get('detailed_alliances', {}))
    
    if request.method == 'POST':
        data = request.json
        advancement_state['detailed_alliances'] = data
        
        # NOTE: User requested this be completely random/irrelevant to advancement points.
        # So we do NOT update 'alliance_selections' here anymore.
        
        save_advancement_state()
        return jsonify({'success': True})

@app.route('/api/advancement', methods=['POST'])
def update_advancement():
    data = request.json
    action = data.get('action')
    team = data.get('team')
    
    if action == 'add':
        selection = data.get('selection')
        pts = int(selection.split('(')[1].strip(')'))
        
        if "Alliance" in selection and "Captain" in selection:
            # Legacy handling - ignored in favor of drag-n-drop if used
            rank = int(selection.split(' ')[1])
            advancement_state['alliance_selections'][team] = rank
        elif "Winning Alliance" in selection:
            advancement_state['playoff_results'][team] = pts
        elif "Finalist Alliance" in selection:
            advancement_state['playoff_results'][team] = pts
        else:
            current = advancement_state['awards'].get(team, 0)
            advancement_state['awards'][team] = current + pts
        
        save_advancement_state()
            
    return jsonify({'success': True})

@app.route('/api/advancement_calc', methods=['GET'])
def get_advancement():
    teams = data_manager.get_all_teams()
    ranked_teams = ranking_calculator.calculate_league_rankings(teams)
    
    final_teams = ranking_calculator.calculate_advancement_points(
        ranked_teams,
        advancement_state['alliance_selections'],
        advancement_state['awards'],
        advancement_state['playoff_results']
    )
    
    result = []
    for i, t in enumerate(final_teams):
        qual_pts = max(2, 17 - t.league_rank)
        alliance_pts = 0
        if t.number in advancement_state['alliance_selections']:
            alliance_pts = 21 - advancement_state['alliance_selections'][t.number]
            
        award_pts = advancement_state['awards'].get(t.number, 0)
        play_pts = advancement_state['playoff_results'].get(t.number, 0)
        
        result.append({
            'rank': i + 1,
            'number': t.number,
            'name': t.name,
            'qual_pts': qual_pts,
            'alliance_pts': alliance_pts,
            'award_pts': award_pts,
            'playoff_pts': play_pts,
            'total_ap': t.advancement_points
        })
        
    return jsonify(result)

@app.route('/api/rankings/hypothetical', methods=['POST'])
def calculate_hypothetical():
    data = request.json
    hypothetical_matches = data.get('matches', [])
    
    # Get all teams with hypothetical matches applied (cloned, non-destructive)
    teams = data_manager.get_all_teams_with_hypothetical(hypothetical_matches)
    
    # Calculate league rankings based on these teams
    ranked_teams = ranking_calculator.calculate_league_rankings(teams)
    
    # Calculate advancement points if needed, or just return rankings
    # Providing advancement context too since that's the end goal
    final_teams = ranking_calculator.calculate_advancement_points(
        ranked_teams,
        advancement_state['alliance_selections'],
        advancement_state['awards'],
        advancement_state['playoff_results']
    )
    
    result = []
    for t in final_teams:
        result.append({
            'rank': t.league_rank,
            'number': t.number,
            'name': t.name,
            'total_rp': t.total_rp,
            'matches_played': t.matches_played,
            'avg_score': round(t.avg_score, 2),
            'advancement_points': t.advancement_points,
            'breakdown': getattr(t, 'match_breakdown', [])
        })
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)
