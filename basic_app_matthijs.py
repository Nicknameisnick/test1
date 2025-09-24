import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="G7 Population Dashboard", layout="wide")

# Function to get population data

def get_population_data(country_name):
    url = f"https://api.api-ninjas.com/v1/population?country={country_name}"
    headers = {"X-Api-Key": "ctncIeEoDtS4xty3k/0f2A==gruY3Np8xYnobhv5"} 
    response = requests.get(url, headers=headers)

    hist_df = pd.DataFrame()
    if response.status_code == 200:
        data = response.json()
        hist_df = pd.DataFrame(data.get("historical_population", []))

        if not hist_df.empty:
            hist_df = hist_df.set_index("year")
            hist_df.index = hist_df.index.astype(int)

            for col in ["migrants", "fertility_rate", "median_age"]:
                if col not in hist_df.columns:
                    hist_df[col] = None
    return hist_df

# Sidebar controls

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


# Tabs for different plots

tab1, tab2, tab3, tab4 = st.tabs(["Population Trends", "Migrants Over Time", "Median Age", "Correlation for Median Age"])

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
    st.subheader("Correlations Across G7 Countries")

    # Collect combined data
    combined_data = []
    for c in selected_countries:
        hist_df = get_population_data(c)
        if hist_df.empty:
            continue

        mask = (hist_df.index >= year_range[0]) & (hist_df.index <= year_range[1])
        hist_df = hist_df.loc[mask]

        hist_df["country"] = c
        combined_data.append(hist_df)

    if combined_data:
        df_all = pd.concat(combined_data)

        # ==============================
        # 1️⃣ Median Age vs Fertility Rate
        # ==============================
        df1 = df_all[["median_age", "fertility_rate", "country"]].dropna()
        fig1 = go.Figure()
        for c in df1["country"].unique():
            sub = df1[df1["country"] == c]
            fig1.add_trace(go.Scatter(x=sub["median_age"], y=sub["fertility_rate"],
                                      mode="markers", name=c))

        fig1.update_layout(
            title="Median Age vs Fertility Rate",
            xaxis_title="Median Age",
            yaxis_title="Fertility Rate",
            template="plotly_white",
            height=600
        )
        st.plotly_chart(fig1, use_container_width=True)

        # R values
        r_values1 = []
        for c in df1["country"].unique():
            sub = df1[df1["country"] == c]
            if len(sub) > 1:
                r = np.corrcoef(sub["median_age"], sub["fertility_rate"])[0, 1]
                r_values1.append({"Country": c, "R (Median Age vs Fertility Rate)": round(r, 2)})

        # Overall R
        overall_r1 = np.corrcoef(df1["median_age"], df1["fertility_rate"])[0, 1]
        r_values1.append({"Country": "Overall", "R (Median Age vs Fertility Rate)": round(overall_r1, 2)})

        st.dataframe(pd.DataFrame(r_values1).set_index("Country"), use_container_width=True)

        # ==============================
        # 2️⃣ Median Age vs Migrants
        # ==============================
        df2 = df_all[["median_age", "migrants", "country"]].dropna()
        fig2 = go.Figure()
        for c in df2["country"].unique():
            sub = df2[df2["country"] == c]
            fig2.add_trace(go.Scatter(x=sub["median_age"], y=sub["migrants"],
                                      mode="markers", name=c))

        fig2.update_layout(
            title="Median Age vs Migrants",
            xaxis_title="Median Age",
            yaxis_title="Migrants",
            template="plotly_white",
            height=600
        )
        st.plotly_chart(fig2, use_container_width=True)

        # R values
        r_values2 = []
        for c in df2["country"].unique():
            sub = df2[df2["country"] == c]
            if len(sub) > 1:
                r = np.corrcoef(sub["median_age"], sub["migrants"])[0, 1]
                r_values2.append({"Country": c, "R (Median Age vs Migrants)": round(r, 2)})

        # Overall R
        overall_r2 = np.corrcoef(df2["median_age"], df2["migrants"])[0, 1]
        r_values2.append({"Country": "Overall", "R (Median Age vs Migrants)": round(overall_r2, 2)})

        st.dataframe(pd.DataFrame(r_values2).set_index("Country"), use_container_width=True)

        # ==============================
        # 3️⃣ Median Age vs Urban Population %
        # ==============================
        df3 = df_all[["median_age", "urban_population_pct", "country"]].dropna()
        fig3 = go.Figure()
        for c in df3["country"].unique():
            sub = df3[df3["country"] == c]
            fig3.add_trace(go.Scatter(x=sub["median_age"], y=sub["urban_population_pct"],
                                      mode="markers", name=c))

        fig3.update_layout(
            title="Median Age vs Urban Population %",
            xaxis_title="Median Age",
            yaxis_title="Urban Population (%)",
            template="plotly_white",
            height=600
        )
        st.plotly_chart(fig3, use_container_width=True)

        # R values
        r_values3 = []
        for c in df3["country"].unique():
            sub = df3[df3["country"] == c]
            if len(sub) > 1:
                r = np.corrcoef(sub["median_age"], sub["urban_population_pct"])[0, 1]
                r_values3.append({"Country": c, "R (Median Age vs Urban Pop. %)": round(r, 2)})

        # Overall R
        overall_r3 = np.corrcoef(df3["median_age"], df3["urban_population_pct"])[0, 1]
        r_values3.append({"Country": "Overall", "R (Median Age vs Urban Pop. %)": round(overall_r3, 2)})

        st.dataframe(pd.DataFrame(r_values3).set_index("Country"), use_container_width=True)



