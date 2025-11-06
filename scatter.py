import pandas as pd
import plotly.express as px
import webbrowser

# === Load your dataset ===
# Make sure the CSV file is in: data/players_data.csv
df = pd.read_csv("data/players_data.csv")

# === Filter players like in your JavaScript version ===
df = df[(df["Min"] >= 500) & (df["Gls"] >= 5)]

# === Create scatter plot ===
fig = px.scatter(
    df,
    x="Gls",
    y="xG",
    color="Comp",
    hover_data=["Player", "Squad", "Age", "Ast"],
    title="⚽ Goals vs Expected Goals<br><sub>Players with ≥500 min & ≥5 goals</sub>",
)

# === Customize layout ===
fig.update_layout(
    height=650,
    plot_bgcolor="#fafafa",
    legend_title_text="League",
    xaxis_title="Goals (Gls)",
    yaxis_title="Expected Goals (xG)",
    font=dict(family="Segoe UI, sans-serif", size=14),
)

# === Save to HTML file ===
output_file = "soccer_analytics_plot.html"
fig.write_html(output_file, include_plotlyjs="cdn", full_html=True)

# === Automatically open in your default browser ===
webbrowser.open(output_file)

print(f"✅ Plot saved and opened: {output_file}")
