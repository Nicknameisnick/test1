import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="G7 Population Dashboard", layout="wide")

# Function to get population data
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
            hist_df.index = hist_df.index.astype(int)
            if "migrants" not in hist_df.columns:
                hist_df["migrants"] = None
    return hist_df


# Sidebar controls
st.sidebar.title("Controls")
year_range = st.sidebar.slider("Select Year Range", 1950, 2025, (1970, 2020))
select_all = st.sidebar.toggle("Select/Deselect All Countries", value=True)

countries = [
    "Canada", "France", "Germany", "Italy", "Japan",
    "United Kingdom", "United States of America"
]

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    countries,
    default=countries if select_all else []
)

show_lines = st.sidebar.checkbox("Show Lines", value=True)
show_points = st.sidebar.checkbox("Show Points", value=True)

# Main content
st.title("📊 G7 Population Dashboard")
st.markdown("""
The **G7 (Group of Seven)** is an intergovernmental forum of seven of the world’s largest 
advanced economies: **Canada, France, Germany, Italy, Japan, the United Kingdom, and the United States**.  
These countries play a key role in global economic governance, trade policy, and international relations.  

This dashboard shows **population growth** and **migration flows** of the G7 countries.
""")

# Population Trends
fig_pop = go.Figure()
for c in selected_countries:
    hist_df = get_population_data(c)
    if not hist_df.empty:
        mask = (hist_df.index >= year_range[0]) & (hist_df.index <= year_range[1])
        hist_df = hist_df.loc[mask]
        if not hist_df.empty:
            mode = (
                "lines+markers" if show_lines and show_points
                else "lines" if show_lines
                else "markers"
            )
            fig_pop.add_trace(go.Scatter(
                x=hist_df.index, y=hist_df["population"],
                mode=mode, name=c
            ))

fig_pop.update_layout(
    title="Population Trends of G7 Countries",
    xaxis_title="Year",
    yaxis_title="Population",
    height=600,
    width=1100,
    template="plotly_white"
)
st.plotly_chart(fig_pop, use_container_width=True)

# Migrants over time
fig_mig = go.Figure()
data_found = False
for c in selected_countries:
    hist_df = get_population_data(c)
    if not hist_df.empty:
        mask = (hist_df.index >= year_range[0]) & (hist_df.index <= year_range[1])
        hist_df = hist_df.loc[mask]
        if "migrants" in hist_df.columns and hist_df["migrants"].notna().any():
            data_found = True
            fig_mig.add_trace(go.Scatter(
                x=hist_df.index, y=hist_df["migrants"],
                mode="lines+markers", name=c
            ))

if data_found:
    fig_mig.update_layout(
        title="Migrants Over Time",
        xaxis_title="Year",
        yaxis_title="Number of Migrants",
        height=500,
        width=1100,
        template="plotly_white"
    )
    st.plotly_chart(fig_mig, use_container_width=True)
else:
    st.warning("⚠️ No migrants data available for the selected countries and years.")



