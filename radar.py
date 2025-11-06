"""
Create an interactive radar chart comparison with player selection dropdowns
"""
import pandas as pd
import webbrowser
from soccer_api import SOCCERAPI

# Initialize API and load data
soccerapi = SOCCERAPI("players_data-2024_2025.csv")

# Get filtered data (adjust these parameters as needed)
df = soccerapi.get_data(
    min_goals=0,
    min_assists=0,
    comp=None,  # Or specify leagues: ['Premier League', 'La Liga']
    squad=None,  # Or specify squads: ['Manchester City', 'Real Madrid']
    age_range=(18, 35),
    min_minutes=500
)

# Get list of all players with their positions
player_list = []
for player in df['Player'].unique():
    pos = soccerapi.get_player_position(player)
    squad = df[df['Player'] == player]['Squad'].iloc[0]
    player_list.append({
        'name': player,
        'pos': pos if pos else 'Unknown',
        'squad': squad
    })

# Sort players alphabetically
player_list = sorted(player_list, key=lambda x: x['name'])
# Define position categories and stats
def get_position_category(pos):
    return {'FW': 'ATTACK', 'MF': 'ATTACK', 'DF': 'DEFENSE', 'GK': 'GOALKEEPER'}.get(pos, 'ATTACK')

# Add position category to each player
for player in player_list:
    player['category'] = get_position_category(player['pos'])

# Define stats based on position
stats_config = {
    'ATTACK': {
        'cols': ['Min', 'Gls', 'Ast', 'KP', 'PrgC'],
        'title': '⚡ Attacking Player Comparison'},
    'DEFENSE': {
        'cols': ['Min', 'Tkl', 'TklW', 'Blocks', 'Int', 'Clr'],
        'title': '🛡️ Defensive Player Comparison'},
    'GOALKEEPER': {
        'cols': ['Min', 'GA', 'Saves', 'Save%', 'CS'],
        'title': '🧤 Goalkeeper Comparison'}
}

# Display names for stats
stat_display_names = {
    'Min': 'Minutes Played',
    'Gls': 'Goals',
    'Ast': 'Assists',
    'KP': 'Key Passes',
    'PrgC': 'Progressive Carries',
    'Tkl': 'Tackles',
    'TklW': 'Tackles Won',
    'Blocks': 'Blocks',
    'Int': 'Interceptions',
    'Clr': 'Clearances',
    'GA': 'Goals Against',
    'Saves': 'Saves',
    'Save%': 'Save Percentage',
    'CS': 'Clean Sheets'
}

# Normalize data function
def normalize_dataframe(df_input, cols, scale_min=0, scale_max=100):
    normalized = df_input.copy()
    for col in cols:
        col_max, col_min = df_input[col].max(), df_input[col].min()
        if col_max != col_min:
            normalized[col] = ((df_input[col] - col_min) / (col_max - col_min)) * (scale_max - scale_min) + scale_min
        else:
            normalized[col] = scale_min
    return normalized

# Only need attacking stats
attack_stats = ['Min', 'Gls', 'Ast', 'KP', 'PrgC']
normalized_df = normalize_dataframe(df, attack_stats)

# Convert dataframes to JSON for JavaScript
df_json = df.to_json(orient='records')
normalized_df_json = normalized_df.to_json(orient='records')
player_list_json = str(player_list).replace("'", '"')

# Create the HTML with embedded JavaScript
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>⚽ Attacking Players Radar Comparison</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        h1 {{
            color: #2d6a4f;
            text-align: center;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        .controls {{
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        .player-select {{
            flex: 1;
            min-width: 300px;
            max-width: 400px;
            position: relative;
        }}
        label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2d6a4f;
        }}
        input {{
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            background: white;
            transition: border-color 0.3s;
            box-sizing: border-box;
        }}
        input:focus {{
            outline: none;
            border-color: #2d6a4f;
            box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.1);
        }}
        .suggestions {{
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 2px solid #2d6a4f;
            border-top: none;
            border-radius: 0 0 8px 8px;
            max-height: 300px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
        }}
        .suggestion-item {{
            padding: 12px;
            cursor: pointer;
            border-bottom: 1px solid #eee;
        }}
        .suggestion-item:hover {{
            background: #e8f5e9;
        }}
        .suggestion-item:last-child {{
            border-bottom: none;
        }}
        .player-info {{
            font-size: 12px;
            color: #666;
            margin-top: 2px;
        }}
        #plotDiv {{
            width: 100%;
            height: 650px;
        }}
        .info {{
            background: #e8f5e9;
            border: 2px solid #4caf50;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
            color: #2d6a4f;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ Attacking Players Radar Comparison</h1>
        <div class="subtitle">Compare attacking stats for forwards and midfielders</div>
        
        <div class="controls">
            <div class="player-select">
                <label for="player1">🔍 Search Player 1:</label>
                <input type="text" id="player1" placeholder="Type to search for a player..." autocomplete="off">
                <div id="suggestions1" class="suggestions"></div>
            </div>
            <div class="player-select">
                <label for="player2">🔍 Search Player 2:</label>
                <input type="text" id="player2" placeholder="Type to search for a player..." autocomplete="off">
                <div id="suggestions2" class="suggestions"></div>
            </div>
        </div>
        
        <div id="message"></div>
        <div id="plotDiv"></div>
    </div>

    <script>
        // Data from Python
        const playerData = {df_json};
        const normalizedData = {normalized_df_json};
        const playerList = {player_list_json};
        
        // Attacking stats configuration
        const statCols = ['Min', 'Gls', 'Ast', 'KP', 'PrgC'];
        const displayNames = ['Minutes Played', 'Goals', 'Assists', 'Key Passes', 'Progressive Carries'];
        
        // Selected players
        let selectedPlayer1 = '';
        let selectedPlayer2 = '';
        
        // Get input elements
        const player1Input = document.getElementById('player1');
        const player2Input = document.getElementById('player2');
        const suggestions1 = document.getElementById('suggestions1');
        const suggestions2 = document.getElementById('suggestions2');
        
        function showMessage(text) {{
            const messageDiv = document.getElementById('message');
            messageDiv.innerHTML = `<div class="info">${{text}}</div>`;
        }}
        
        function filterPlayers(searchText) {{
            if (!searchText) return playerList;
            const lower = searchText.toLowerCase();
            return playerList.filter(player => 
                player.name.toLowerCase().includes(lower) ||
                player.squad.toLowerCase().includes(lower)
            );
        }}
        
        function showSuggestions(inputElement, suggestionsElement, searchText) {{
            const filtered = filterPlayers(searchText);
            
            if (filtered.length === 0 || !searchText) {{
                suggestionsElement.style.display = 'none';
                return;
            }}
            
            suggestionsElement.innerHTML = filtered.slice(0, 10).map(player => `
                <div class="suggestion-item" data-player="${{player.name}}">
                    <div>${{player.name}}</div>
                    <div class="player-info">${{player.squad}} • ${{player.pos}}</div>
                </div>
            `).join('');
            
            suggestionsElement.style.display = 'block';
            
            // Add click handlers
            suggestionsElement.querySelectorAll('.suggestion-item').forEach(item => {{
                item.addEventListener('click', () => {{
                    const playerName = item.getAttribute('data-player');
                    inputElement.value = playerName;
                    suggestionsElement.style.display = 'none';
                    
                    if (inputElement === player1Input) {{
                        selectedPlayer1 = playerName;
                    }} else {{
                        selectedPlayer2 = playerName;
                    }}
                    
                    updateChart();
                }});
            }});
        }}
        
        function updateChart() {{
            const selectedPlayers = [selectedPlayer1, selectedPlayer2].filter(p => p);
            
            if (selectedPlayers.length === 0) {{
                showMessage('🔍 Please search and select at least one player to see the comparison');
                document.getElementById('plotDiv').innerHTML = '';
                return;
            }}
            
            // Clear message
            document.getElementById('message').innerHTML = '';
            
            // Create traces
            const traces = selectedPlayers.map(playerName => {{
                const normRow = normalizedData.find(row => row.Player === playerName);
                const actualRow = playerData.find(row => row.Player === playerName);
                
                if (!normRow || !actualRow) return null;
                
                const normValues = statCols.map(col => normRow[col]);
                const actualValues = statCols.map(col => actualRow[col]);
                const hoverText = displayNames.map((name, i) => 
                    `${{name}}: ${{actualValues[i].toFixed(1)}}`
                );
                
                return {{
                    type: 'scatterpolar',
                    r: normValues,
                    theta: displayNames,
                    fill: 'toself',
                    name: playerName,
                    hovertext: hoverText,
                    hoverinfo: 'text+name'
                }};
            }}).filter(t => t !== null);
            
            // Layout
            const layout = {{
                polar: {{
                    radialaxis: {{
                        visible: true,
                        range: [0, 100],
                        ticksuffix: '%'
                    }}
                }},
                showlegend: true,
                title: '⚡ Attacking Player Comparison',
                height: 650,
                font: {{
                    family: 'Segoe UI, sans-serif',
                    size: 14
                }}
            }};
            
            // Plot
            Plotly.newPlot('plotDiv', traces, layout, {{responsive: true}});
        }}
        
        // Event listeners for player 1
        player1Input.addEventListener('input', (e) => {{
            showSuggestions(player1Input, suggestions1, e.target.value);
            // Clear selection if user types something different
            if (e.target.value !== selectedPlayer1) {{
                selectedPlayer1 = '';
                updateChart();
            }}
        }});
        
        player1Input.addEventListener('focus', (e) => {{
            if (e.target.value) {{
                showSuggestions(player1Input, suggestions1, e.target.value);
            }}
        }});
        
        // Event listeners for player 2
        player2Input.addEventListener('input', (e) => {{
            showSuggestions(player2Input, suggestions2, e.target.value);
            // Clear selection if user types something different
            if (e.target.value !== selectedPlayer2) {{
                selectedPlayer2 = '';
                updateChart();
            }}
        }});
        
        player2Input.addEventListener('focus', (e) => {{
            if (e.target.value) {{
                showSuggestions(player2Input, suggestions2, e.target.value);
            }}
        }});
        
        // Close suggestions when clicking outside
        document.addEventListener('click', (e) => {{
            if (!e.target.closest('.player-select')) {{
                suggestions1.style.display = 'none';
                suggestions2.style.display = 'none';
            }}
        }});
        
        // Initial message
        showMessage('🔍 Please search and select at least one player to see the comparison');
    </script>
</body>
</html>
"""

# Save and open
output_file = "attacking_players_radar.html"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

# Automatically open in browser
webbrowser.open(output_file)

print(f"✅ Interactive attacking players radar chart opened in browser!")
print(f"   File saved: {output_file}")
print(f"   Total attacking players available: {len(player_list)}")