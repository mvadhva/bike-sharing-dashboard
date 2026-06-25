from pathlib import Path
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go


def format_hour(hour):
    if hour == 0:
        return "12 AM"
    if hour < 12:
        return f"{hour} AM"
    if hour == 12:
        return "12 PM"
    return f"{hour - 12} PM"


def format_window(start_hour, window_size=3):
    end_hour = (start_hour + window_size - 1) % 24
    return f"{format_hour(start_hour)}–{format_hour(end_hour)}"


def format_number(value):
    return f"{value:,.0f}"


def make_kpi_card(title, value, note, background, border_color, value_color):
    return html.Div(
        [
            html.Div(
                title,
                style={
                    "fontSize": "14px",
                    "fontWeight": "700",
                    "color": "#334155",
                },
            ),
            html.Div(
                value,
                style={
                    "fontSize": "30px",
                    "fontWeight": "800",
                    "color": value_color,
                    "marginTop": "6px",
                    "lineHeight": "1.1",
                },
            ),
            html.Div(
                note,
                style={
                    "fontSize": "14px",
                    "color": "#64748b",
                    "marginTop": "4px",
                },
            ),
        ],
        style={
            "flex": "1",
            "padding": "12px",
            "backgroundColor": background,
            "border": f"1px solid {border_color}",
            "borderRadius": "16px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.04)",
            "minWidth": "180px",
        },
    )


# Load data
BASE_DIR = Path(__file__).resolve().parent
df = pd.read_csv(BASE_DIR / "hour.csv")

# Readable labels
df["season_name"] = df["season"].map(
    {
        1: "Spring",
        2: "Summer",
        3: "Fall",
        4: "Winter",
    }
)

df["weather_name"] = df["weathersit"].map(
    {
        1: "Clear/Few Clouds",
        2: "Mist/Cloudy",
        3: "Light Rain/Snow",
        4: "Heavy Rain/Snow",
    }
)

app = Dash(__name__)
server = app.server
app.title = "Bike Sharing Demand Explorer"

app.layout = html.Div(
    [
        html.H1("🚲 Bike Sharing Demand Explorer"),
        html.P("Find the best times to ride and avoid peak demand periods."),

        html.Div(
            [
                html.Div("Season", style={"fontWeight": "bold", "marginBottom": "8px"}),
                dcc.RadioItems(
                    id="season-selector",
                    options=[
                        {"label": "All Seasons", "value": "All"},
                        {"label": "🌸 Spring", "value": "Spring"},
                        {"label": "☀️ Summer", "value": "Summer"},
                        {"label": "🍂 Fall", "value": "Fall"},
                        {"label": "❄️ Winter", "value": "Winter"},
                    ],
                    value="All",
                    inline=True,
                    labelStyle={
                        "display": "inline-block",
                        "padding": "10px 16px",
                        "marginRight": "10px",
                        "marginBottom": "10px",
                        "border": "1px solid #ddd",
                        "borderRadius": "999px",
                        "backgroundColor": "#f8f8f8",
                        "cursor": "pointer",
                        "fontWeight": "600",
                    },
                    inputStyle={"marginRight": "6px"},
                ),
            ],
            style={"marginTop": "20px", "marginBottom": "20px"},
        ),

        html.Div(id="kpi-cards"),

      html.H3("🚲 When Should I Ride?"),

html.P(
    "Why this chart? A line chart was chosen because it effectively shows how bike rental demand changes throughout the day. It helps users identify peak and low-demand hours, making it easier to choose the best times to ride."
),

dcc.Graph(id="hourly-chart"),
html.H3("🗓️ When Is Demand Highest Across Seasons?"),

html.P(
    "Why this chart? A heatmap was selected because it allows users to compare bike rental demand across both seasons and hours of the day simultaneously. The color intensity makes high- and low-demand periods easy to identify."
),

dcc.Graph(id="heatmap-chart"),

        html.H3("🌦️ How Much Does Weather Reduce Demand?"),

html.P(
    "Why this chart? A bar chart was chosen because weather conditions are categorical variables. It clearly compares how each weather condition affects bike rental demand relative to clear weather."
),

dcc.Graph(id="weather-chart"),

        html.H3("Key Findings"),
        html.Ul(
            [
                html.Li("Lowest demand occurs in the early morning hours."),
                html.Li("Peak demand occurs around the evening commute."),
                html.Li("Fall and Summer show the strongest demand patterns."),
                html.Li("Heavy rain and snow reduce demand by the largest amount."),
                html.Li(
                    "Demand peaks during commuting hours (8 AM and 5–6 PM), "
                    "especially in Fall and Summer."
                ),
            ]
        ),

        html.H3("Limitations"),
        html.Ul(
            [
                html.Li("The data only covers Washington, D.C."),
                html.Li("The analysis is descriptive, not causal."),
                html.Li("External events and transit disruptions are not included."),
            ]
        ),
        html.Hr(),

html.H3("Project Links"),

html.P([
    "GitHub Repository: ",
    html.A(
        "https://github.com/mvadhva/bike-sharing-dashboard",
        href="https://github.com/mvadhva/bike-sharing-dashboard",
        target="_blank",
    )
]),

html.P([
    "Final Video: ",
    html.A(
        "watch video link",
        href="https://indiana-my.sharepoint.com/:v:/r/personal/mvadhva_iu_edu/Documents/Final%20video%20Project.webm?csf=1&web=1&e=OPi3NB&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D",
        target="_blank",
    )
]),
    ],
    style={
        "width": "90%",
        "margin": "auto",
        "padding": "18px",
    },
)


@app.callback(
    Output("kpi-cards", "children"),
    Output("hourly-chart", "figure"),
    Input("season-selector", "value"),
)
def update_dashboard(selected_season):
    filtered_df = df.copy()

    if selected_season != "All":
        filtered_df = filtered_df[filtered_df["season_name"] == selected_season]

    hourly = (
        filtered_df.groupby("hr", as_index=False)["cnt"]
        .mean()
        .sort_values("hr")
    )

    hourly_values = hourly["cnt"].tolist()

    window_stats = []
    for start in range(24):
        vals = [hourly_values[(start + i) % 24] for i in range(3)]
        window_stats.append((start, sum(vals) / 3))

    best_start, best_avg = min(window_stats, key=lambda x: x[1])
    peak_start, peak_avg = max(window_stats, key=lambda x: x[1])

    best_window = format_window(best_start)
    peak_window = format_window(peak_start)

    season_totals = (
        df.groupby("season_name")["cnt"]
        .sum()
        .sort_values(ascending=False)
    )
    most_active_season = season_totals.index[0]
    most_active_total = season_totals.iloc[0]

    kpi_cards = html.Div(
        [
            make_kpi_card(
                "Most Active Season",
                most_active_season,
                f"{format_number(most_active_total)} total rentals",
                background="#f8fbff",
                border_color="#dbeafe",
                value_color="#2563eb",
            ),
            make_kpi_card(
                "Best Riding Window",
                best_window,
                f"Avg demand: {format_number(best_avg)}",
                background="#f7fff7",
                border_color="#d9f2d9",
                value_color="#2ca02c",
            ),
            make_kpi_card(
                "Peak Demand Window",
                peak_window,
                f"Avg demand: {format_number(peak_avg)}",
                background="#fff7f7",
                border_color="#f2d9d9",
                value_color="#d62728",
            ),
        ],
        style={
            "display": "flex",
            "gap": "16px",
            "flexWrap": "wrap",
            "marginBottom": "18px",
        },
    )

    fig = px.line(
        hourly,
        x="hr",
        y="cnt",
        markers=True,
        labels={"hr": "Hour of Day", "cnt": "Average Rentals"},
    )

    fig.update_layout(
        title=None,
        template="plotly_white",
        xaxis=dict(dtick=1),
        xaxis_title="Hour of Day",
        yaxis_title="Average Rentals",
        margin=dict(l=60, r=30, t=40, b=60),
    )

    fig.update_traces(line=dict(width=3), marker=dict(size=8))

    fig.add_annotation(
        x=(best_start + 1) % 24,
        y=float(best_avg),
        text="Lowest 3-hour window",
        showarrow=True,
        arrowhead=2,
        yshift=20,
    )

    fig.add_annotation(
        x=(peak_start + 1) % 24,
        y=float(peak_avg),
        text="Highest 3-hour window",
        showarrow=True,
        arrowhead=2,
        yshift=20,
    )

    return kpi_cards, fig


@app.callback(
    Output("heatmap-chart", "figure"),
    Input("season-selector", "value"),
)
def update_heatmap(selected_season):
    filtered_df = df.copy()

    if selected_season != "All":
        filtered_df = filtered_df[filtered_df["season_name"] == selected_season]

    heatmap_df = (
        filtered_df.groupby(["season_name", "hr"], as_index=False)["cnt"]
        .mean()
    )

    if selected_season == "All":
        row_order = ["Spring", "Summer", "Fall", "Winter"]
    else:
        row_order = [selected_season]

    heatmap_pivot = (
        heatmap_df.pivot(index="season_name", columns="hr", values="cnt")
        .reindex(row_order)
    )

    heatmap_hours = list(heatmap_pivot.columns)
    heatmap_labels = [format_hour(int(h)) for h in heatmap_hours]

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_pivot.values,
            x=heatmap_labels,
            y=heatmap_pivot.index.tolist(),
            colorscale="YlOrRd",
            colorbar=dict(title="Avg rentals"),
            hovertemplate=(
                "Season=%{y}<br>"
                "Hour=%{x}<br>"
                "Avg rentals=%{z:.0f}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=None,
        template="plotly_white",
        xaxis_title="Hour of Day",
        yaxis_title="Season",
        height=450,
        margin=dict(l=60, r=30, t=40, b=60),
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=heatmap_labels[::2],
        ticktext=heatmap_labels[::2],
    )

    fig.update_yaxes(autorange="reversed")

    return fig


@app.callback(
    Output("weather-chart", "figure"),
    Input("season-selector", "value"),
)
def update_weather_chart(selected_season):
    filtered_df = df.copy()

    if selected_season != "All":
        filtered_df = filtered_df[filtered_df["season_name"] == selected_season]

    weather_order = [
        "Clear/Few Clouds",
        "Mist/Cloudy",
        "Light Rain/Snow",
        "Heavy Rain/Snow",
    ]

    weather = (
        filtered_df.groupby("weather_name")["cnt"]
        .mean()
        .reindex(weather_order)
        .reset_index()
    )

    clear_avg = weather.loc[
        weather["weather_name"] == "Clear/Few Clouds", "cnt"
    ].dropna().mean()

    if pd.isna(clear_avg) or clear_avg == 0:
        clear_avg = df.loc[
            df["weather_name"] == "Clear/Few Clouds", "cnt"
        ].mean()

    if pd.isna(clear_avg) or clear_avg == 0:
        clear_avg = 1

    weather["change_pct"] = ((weather["cnt"] / clear_avg) - 1) * 100

    bar_colors = ["#2ca02c", "#f4a261", "#e76f51", "#d62728"]

    fig = go.Figure(
        data=go.Bar(
            x=weather["weather_name"],
            y=weather["change_pct"],
            marker_color=bar_colors,
            text=[
                f"{v:.0f}%" if pd.notna(v) else ""
                for v in weather["change_pct"]
            ],
            textposition="auto",
            cliponaxis=False,
            customdata=weather["cnt"],
            hovertemplate=(
                "Weather=%{x}<br>"
                "Avg rentals=%{customdata:.0f}<br>"
                "Change vs clear=%{y:.0f}%<extra></extra>"
            ),
        )
    )

    fig.add_hline(y=0, line_dash="dash", line_color="gray")

    valid_weather = weather.dropna(subset=["change_pct"])
    if not valid_weather.empty:
        worst_row = valid_weather.loc[valid_weather["change_pct"].idxmin()]
        fig.add_annotation(
            x=worst_row["weather_name"],
            y=worst_row["change_pct"],
            text="Largest drop",
            showarrow=True,
            arrowhead=2,
            yshift=-25,
        )

    fig.update_layout(
        title=None,
        template="plotly_white",
        xaxis_title="Weather Condition",
        yaxis_title="Demand change vs clear weather (%)",
        margin=dict(l=60, r=30, t=40, b=60),
        showlegend=False,
    )

    fig.update_yaxes(ticksuffix="%")

    return fig


if __name__ == "__main__":
    app.run(debug=False)
