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
        if not hist_df.empty and "year" in hist_df.columns:
            hist_df = hist_df.set_index("year")
            hist_df.rename(columns={"population": "historical_population"}, inplace=True)

            # ✅ zet index naar int
            hist_df.index = hist_df.index.astype(int)

    return hist_df


# ==============================
# Streamlit App
# ==============================
st.title("🌍 G7 Population Dashboard")
st.write("Interactieve analyse van historische populatiedata via de Ninja API.")

# G7 landen
countries = ["Canada", "France", "Germany", "Italy", "Japan", "United Kingdom", "United States of America"]

# Sidebar controls
st.sidebar.header("⚙️ Instellingen")

# Sliders voor jaarrange
year_min, year_max = 1960, 2025
year_range = st.sidebar.slider("Selecteer een jaarrange:", year_min, year_max, (1980, 2020))

# Checkbox voor lijnen en punten
show_lines = st.sidebar.checkbox("Toon lijngrafieken", value=True)
show_points = st.sidebar.checkbox("Toon datapunten", value=False)

# Selecteer alles / deselecteer alles
st.sidebar.subheader("Landen selectie")
select_all = st.sidebar.checkbox("Alles selecteren", value=True)

country_selection = {}
for c in countries:
    country_selection[c] = st.sidebar.checkbox(c, value=select_all)

# ==============================
# Plot maken
# ==============================
fig = go.Figure()

for c in countries:
    if country_selection[c]:  # alleen geselecteerde landen
        hist_df = get_population_data(c)

        if not hist_df.empty:  # ✅ check om errors te voorkomen
            hist_df = hist_df.loc[hist_df.index.between(year_range[0], year_range[1])]

            mode = "lines+markers" if (show_lines and show_points) else "lines" if show_lines else "markers"
            fig.add_trace(
                go.Scatter(
                    x=hist_df.index,
                    y=hist_df["historical_population"],
                    mode=mode,
                    name=c,
                )
            )

fig.update_layout(
    title="📈 Populatie per land",
    xaxis_title="Jaar",
    yaxis_title="Populatie",
    template="plotly_white",
)

st.plotly_chart(fig, use_container_width=True)


