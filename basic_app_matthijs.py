import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ==============================
# API function
# ==============================
def get_population_data(country_name):
    url = f"https://api.api-ninjas.com/v1/population?country={country_name}"
    headers = {"X-Api-Key": "WXpLhqoFwtWNQK/4yBAnLQ==Dr4y3QC5e0OOcSpn"}
    response = requests.get(url, headers=headers)

    hist_df = pd.DataFrame()
    if response.status_code == 200:
        data = response.json()

        hist_df = pd.DataFrame(data.get("historical_population", []))
        if not hist_df.empty:
            hist_df = hist_df.set_index("year")
            hist_df.rename(columns={"population": "historical_population"}, inplace=True)

        forecast_df = pd.DataFrame(data.get("population_forecast", []))
        if not forecast_df.empty:
            forecast_df = forecast_df.set_index("year")
            forecast_df.rename(columns={"population": "population_forecast"}, inplace=True)

        top_level_fields = {
            k: v for k, v in data.items() if k not in ["historical_population", "population_forecast"]
        }
        for key, value in top_level_fields.items():
            hist_df[key] = value

        # clean columns
        for col in hist_df.columns:
            if "." in col:
                base_col = col.split(".")[0]
                hist_df[base_col] = hist_df[base_col].combine_first(hist_df[col])
                hist_df = hist_df.drop(columns=[col])

        key_cols = ["historical_population", "median_age", "fertility_rate", "rank"]
        hist_df = hist_df.dropna(subset=key_cols, how="all")
        hist_df = hist_df.sort_index()

    return hist_df


# ==============================
# Streamlit App
# ==============================
st.title("🌍 G7 Population Dashboard")
st.write("Interactieve analyse van historische populatiedata via de Ninja API.")

# G7 landen
countries = ["Canada", "France", "Germany", "Italy", "Japan", "United Kingdom", "United States of America"]

# Sliders voor jaarrange
year_min, year_max = 1960, 2025
year_range = st.slider("Selecteer een jaarrange:", year_min, year_max, (1980, 2020))

# Checkbox voor lijnen en punten
show_lines = st.checkbox("Toon lijngrafieken", value=True)
show_points = st.checkbox("Toon datapunten", value=False)

# Landen checkboxes
st.subheader("Selecteer landen:")
country_selection = {}
for c in countries:
    country_selection[c] = st.checkbox(c, value=True)  # alles standaard aan

# Plot maken
fig = go.Figure()
for c in countries:
    if country_selection[c]:  # alleen als checkbox aan staat
        hist_df = get_population_data(c)
        hist_df = hist_df.loc[hist_df.index.between(year_range[0], year_range[1])]

        mode = "lines+markers" if (show_lines and show_points) else "lines" if show_lines else "markers"
        fig.add_trace(go.Scatter(x=hist_df.index, y=hist_df["historical_population"], mode=mode, name=c))

fig.update_layout(
    title="📈 Populatie per land",
    xaxis_title="Jaar",
    yaxis_title="Populatie",
    template="plotly_white",
)

st.plotly_chart(fig, use_container_width=True)

st.success("✅ Dashboard geladen!")








