import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="G7 Population Dashboard", layout="wide")

# -------------------------------
# Function to get population data
# -------------------------------
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
            hist_df.index = hist_df.index.astype(int)  # ✅ ensure year is int
    return hist_df


# -------------------------------
# Sidebar controls
# -------------------------------
st.sidebar.title("Controls")

# Year range slider
year_range = st.sidebar.slider("Select Year Range", 1950, 2025, (1970, 2020))

# Select all toggle
select_all = st.sidebar.toggle("Select/Deselect All Countries", value=True)

countries = [
    "Canada", "France", "Germany", "Italy", "Japan",
    "United Kingdom", "United States of America"
]

# Country multiselect (default all if toggle = True)
if select_all:
    selected_countries = st.sidebar.multiselect("Select Countries", countries, default=countries)
else:
    selected_countries = st.sidebar.multiselect("Select Countries", countries, default=[])

# Line and marker display options
show_lines = st.sidebar.checkbox("Show Lines", value=True)
show_points = st.sidebar.checkbox("Show Points", value=True)

# -------------------------------
# Main content
# -------------------------------
st.title("📊 G7 Population Dashboard")

st.markdown(
    """
    The **G7 (Group of Seven)** is an intergovernmental forum of seven of the world’s largest 
    advanced economies: **Canada, France, Germany, Italy, Japan, the United Kingdom, and the United States**.  
    These countries play a key role in global economic governance, trade policy, and international relations.  

    This dashboard shows the historical population growth of the G7 countries, allowing you to 
    explore trends and compare across nations.
    """
)

# Create plot
fig = go.Figure()

for c in selected_countries:
    hist_df = get_population_data(c)
    if not hist_df.empty:
        mask = (hist_df.index >= year_range[0]) & (hist_df.index <= year_range[1])
        hist_df = hist_df.loc[mask]

        if not hist_df.empty:
            mode = (
                "lines+markers"
                if (show_lines and show_points)
                else "lines"
                if show_lines
                else "markers"
            )

            fig.add_trace(
                go.Scatter(
                    x=hist_df.index,
                    y=hist_df["historical_population"],
                    mode=mode,
                    name=c,
                )
            )

fig.update_layout(
    title="Population Trends of G7 Countries",
    xaxis_title="Year",
    yaxis_title="Population",
    template="plotly_white",
    height=800,  # ✅ make graph bigger
    width=1200   # ✅ make graph bigger
)

st.plotly_chart(fig, use_container_width=True)








