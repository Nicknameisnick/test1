import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np

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
            hist_df.index = hist_df.index.astype(int)

            # Ensure optional columns always exist
            for col in ["migrants", "fertility_rate", "median_age"]:
                if col not in hist_df.columns:
                    hist_df[col] = None
    return hist_df


# -------------------------------
# Sidebar controls
# -------------------------------
st.sidebar.title("Controls")

year_range = st.sidebar.slider("Select Year Range", 1950, 2025, (1950, 2025))
select_all = st.sidebar.toggle("Select/Deselect All Countries", value=True)

countries = [
    "Canada", "France", "Germany", "Italy", "Japan",
    "United Kingdom", "United States of America"
]

if select_all:
    selected_countries = st.sidebar.multiselect("Select Countries", countries, default=countries)
else:
    selected_countries = st.sidebar.multiselect("Select Countries", countries, default=[])

show_lines = st.sidebar.checkbox("Show Lines", value=True)
show_points = st.sidebar.checkbox("Show Points", value=True)


# -------------------------------
# Tabs for different plots
# -------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Population Trends", "Migrants Over Time", "Median Age", "Correlations"])

with tab1:
    st.subheader("Population Trends of G7 Countries")
    fig_pop = go.Figure()
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
                fig_pop.add_trace(go.Scatter(x=hist_df.index, y=hist_df["population"],
                                             mode=mode, name=c))

    fig_pop.update_layout(
        xaxis_title="Year",
        yaxis_title="Population",
        height=600,
        width=1100,
        template="plotly_white"
    )
    st.plotly_chart(fig_pop, use_container_width=True)


with tab2:
    st.subheader("Migrants Over Time")
    fig_mig = go.Figure()
    data_found = False
    for c in selected_countries:
        hist_df = get_population_data(c)
        if not hist_df.empty:
            mask = (hist_df.index >= year_range[0]) & (hist_df.index <= year_range[1])
            hist_df = hist_df.loc[mask]

            if "migrants" in hist_df.columns and hist_df["migrants"].notna().any():
                data_found = True
                fig_mig.add_trace(go.Scatter(x=hist_df.index, y=hist_df["migrants"],
                                             mode="lines+markers", name=c))

    if data_found:
        fig_mig.update_layout(
            xaxis_title="Year",
            yaxis_title="Number of Migrants",
            height=500,
            width=1100,
            template="plotly_white"
        )
        st.plotly_chart(fig_mig, use_container_width=True)


with tab3:
    st.subheader("Median Age of G7 Countries")
    fig_age = go.Figure()
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
                fig_age.add_trace(go.Scatter(x=hist_df.index, y=hist_df["median_age"],
                                             mode=mode, name=c))

    fig_age.update_layout(
        xaxis_title="Year",
        yaxis_title="Median Age",
        height=600,
        width=1100,
        template="plotly_white"
    )
    st.plotly_chart(fig_age, use_container_width=True)


with tab4:
    st.subheader("Correlations")

    for c in selected_countries:
        hist_df = get_population_data(c)
        if hist_df.empty:
            continue

        mask = (hist_df.index >= year_range[0]) & (hist_df.index <= year_range[1])
        hist_df = hist_df.loc[mask]

        # Drop NA values for clean correlation
        df_clean1 = hist_df[["median_age", "fertility_rate"]].dropna()
        df_clean2 = hist_df[["median_age", "migrants"]].dropna()

        if not df_clean1.empty:
            r1 = np.corrcoef(df_clean1["median_age"], df_clean1["fertility_rate"])[0, 1]
            fig_corr1 = go.Figure(go.Scatter(
                x=df_clean1["median_age"], y=df_clean1["fertility_rate"],
                mode="markers", name=c
            ))
            fig_corr1.update_layout(
                title=f"{c}: Median Age vs Fertility Rate (R={r1:.2f})",
                xaxis_title="Median Age",
                yaxis_title="Fertility Rate",
                template="plotly_white"
            )
            st.plotly_chart(fig_corr1, use_container_width=True)

        if not df_clean2.empty:
            r2 = np.corrcoef(df_clean2["median_age"], df_clean2["migrants"])[0, 1]
            fig_corr2 = go.Figure(go.Scatter(
                x=df_clean2["median_age"], y=df_clean2["migrants"],
                mode="markers", name=c
            ))
            fig_corr2.update_layout(
                title=f"{c}: Median Age vs Migrants (R={r2:.2f})",
                xaxis_title="Median Age",
                yaxis_title="Migrants",
                template="plotly_white"
            )
            st.plotly_chart(fig_corr2, use_container_width=True)
