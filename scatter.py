import pandas as pd
import plotly.graph_objects as go
import webbrowser

# === Load your dataset ===
df = pd.read_csv("players_data-2024_2025.csv")

# === Filter players ===
df = df[(df["Min"] >= 500) & (df["Gls"] >= 5)]

# Rename leagues
df['League'] = df['Comp'].map({
    'eng Premier League': 'Premier League',
    'es La Liga': 'La Liga',
    'it Serie A': 'Serie A',
    'de Bundesliga': 'Bundesliga',
    'fr Ligue 1': 'Ligue 1'
})

league_colors = {
    'Premier League': '#9B4DB8',
    'La Liga': '#FF4C4C',
    'Serie A': '#0086D4',
    'Bundesliga': '#B00020',
    'Ligue 1': '#0B3A78',
}

# === Create figure ===
fig = go.Figure()

# Add traces for each league
for league in df['League'].unique():
    league_data = df[df['League'] == league]

    fig.add_trace(go.Scatter(
        x=league_data['Gls'],
        y=league_data['xG'],
        mode='markers',
        name=league,
        marker=dict(
            color=league_colors[league],
            size=10,
            line=dict(width=1, color='white'),
            opacity=0.8
        ),
        hovertemplate=(
            '<b>%{customdata[0]}</b><br>' +
            'Team: %{customdata[1]}<br>' +
            'Age: %{customdata[2]}<br>' +
            'Goals: %{x}<br>' +
            'xG: %{y:.2f}<br>' +
            'Assists: %{customdata[3]}<br>' +
            '<extra></extra>'
        ),
        customdata=league_data[['Player', 'Squad', 'Age', 'Ast']].values,
        showlegend=False
    ))

# Add reference line (Goals = xG)
fig.add_shape(
    type="line",
    x0=df["Gls"].min(),
    y0=df["Gls"].min(),
    x1=df["Gls"].max(),
    y1=df["Gls"].max(),
    line=dict(color="rgba(0,0,0,0.2)", width=2, dash="dash"),
)

fig.update_layout(
    title={
        'text': "⚽ Goals vs Expected Goals<br><sub>Players with ≥500 min & ≥5 goals</sub>",
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis_title="Goals (Gls)",
    yaxis_title="Expected Goals (xG)",
    plot_bgcolor="#f9f9f9",
    paper_bgcolor="#f0f2f5",
    font=dict(family="Segoe UI, sans-serif", size=14),
    margin=dict(l=80, r=40, t=120, b=80),
    hovermode='closest',
    xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
    yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
    showlegend=False,
    height=1000
)

# === Create custom HTML with legend OUTSIDE the plot ===
output_file = "soccer_analytics_plot.html"

plotly_html = fig.to_html(
    include_plotlyjs="cdn",
    full_html=False,
    config={"responsive": True, "displayModeBar": True, "displaylogo": False}
)

custom_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: 'Segoe UI', sans-serif;
            background: #f0f2f5;
        }}
        .plot-container {{
            width: 95%;
            max-width: 1200px;
            margin: 0 auto;
            height: 1000px;
        }}
        .custom-legend {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 30px;
            padding: 15px 25px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin: 20px auto;
            max-width: 900px;
            flex-wrap: wrap;
            transition: all 0.3s ease;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 15px;
            font-weight: 600;
            cursor: default;
        }}
        .legend-item:hover {{
            transform: scale(1.05);
        }}
        .legend-color {{
            width: 18px;
            height: 18px;
            border-radius: 50%;
            border: 1px solid white;
        }}
    </style>
</head>
<body>
    <div class="plot-container">
        {plotly_html}
    </div>

    <div class="custom-legend">
        <div class="legend-item"><div class="legend-color" style="background-color: #9B4DB8;"></div><span>Premier League</span></div>
        <div class="legend-item"><div class="legend-color" style="background-color: #FF4C4C;"></div><span>La Liga</span></div>
        <div class="legend-item"><div class="legend-color" style="background-color: #0086D4;"></div><span>Serie A</span></div>
        <div class="legend-item"><div class="legend-color" style="background-color: #B00020;"></div><span>Bundesliga</span></div>
        <div class="legend-item"><div class="legend-color" style="background-color: #0B3A78;"></div><span>Ligue 1</span></div>
    </div>
</body>
</html>
"""

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(custom_html)

webbrowser.open(output_file)
print(f"✅ Plot saved and opened: {output_file}")
