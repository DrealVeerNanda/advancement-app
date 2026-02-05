from nicegui import ui

# Team Data
teams_raw = {
    "5214": "B.R.O.", "11920": "QLS RaD Team", "14259": "TURBΩ V8",
    "14770": "Control+Q", "23212": "Dublin Robotics Cybirds", "23279": "Turbotrons",
    "23304": "Cyber Knights", "25627": "Robowarriors", "25810": "Cerberus",
    "26891": "Tech Titans", "30450": "Sharp Face Robotics", "30473": "Duck",
    "30474": "Quantum Sparks", "32098": "Robo Raptors"
}

# Initial state: everything starts at baseline
rows = []
for t_id, name in teams_raw.items():
    rows.append({
        'id': t_id,
        'team': f"{t_id} - {name}",
        'rank_num': 14,
        'rank_pts': 2,
        'alliance_pts': 0,
        'award_pts': 0,
        'total': 2,
        'style': 'background-color: #ffd1d1'
    })

def handle_cell_value_change(e):
    # e.args contains the updated row data
    row = e.args['data']
    
    # Recalculate Rank Points (2026 Scale: Rank 1 = 16pts, Rank 14 = 2pts)
    try:
        r_num = int(row['rank_num'])
        row['rank_pts'] = max(2, 16 - (r_num - 1))
    except:
        row['rank_pts'] = 2

    # Ensure other values are ints
    a_pts = int(row['alliance_pts'] or 0)
    aw_pts = int(row['award_pts'] or 0)
    
    # Update Total
    row['total'] = row['rank_pts'] + a_pts + aw_pts
    
    # Update styling and sort
    refresh_grid()

def refresh_grid():
    # Sort all rows by total
    sorted_rows = sorted(grid.options['rowData'], key=lambda x: x['total'], reverse=True)
    
    # Update styles based on new positions
    for i, row in enumerate(sorted_rows):
        row['style'] = 'background-color: #d1ffd1; font-weight: bold;' if i < 2 else 'background-color: #ffd1d1;'
    
    grid.options['rowData'] = sorted_rows
    grid.update()

# UI Layout
ui.query('body').style('background-color: #f0f2f5;')
ui.label('East Bay League Advancement: Live Worksheet').classes('text-h5 q-ma-md')
ui.label('Click any cell under Rank, Alliance, or Awards to edit. Table sorts automatically.').classes('q-ml-md text-grey-7')

grid = ui.aggrid({
    'columnDefs': [
        {'headerName': 'Team', 'field': 'team', 'width': 220, 'editable': False},
        {'headerName': 'Qual Rank (1-14)', 'field': 'rank_num', 'width': 130, 'editable': True},
        {'headerName': 'Qual Pts', 'field': 'rank_pts', 'width': 100, 'editable': False, 'cellStyle': {'color': '#666'}},
        {'headerName': 'Alliance Pts', 'field': 'alliance_pts', 'width': 120, 'editable': True},
        {'headerName': 'Award Pts', 'field': 'award_pts', 'width': 120, 'editable': True},
        {'headerName': 'TOTAL', 'field': 'total', 'width': 100, 'sort': 'desc', 'editable': False},
    ],
    'rowData': rows,
    'getRowStyle': ': params => params.data.style',
    'stopEditingWhenCellsLoseFocus': True,
}).classes('w-full h-auto shadow-lg').on('cellValueChanged', handle_cell_value_change)

ui.run(title="EBL Live Worksheet", port=8080)