import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="G7 Population Dashboard", layout="wide")


# Function for data from api

def get_population_data(country_name):
    url = f"https://api.api-ninjas.com/v1/population?country={country_name}"
    headers = {"X-Api-Key": "rlwDsTI8EW3/doFNMJ7N4Q==0MsYuVlROHGjDRFD"} 
    response = requests.get(url, headers=headers)

    hist_df = pd.DataFrame()
    if response.status_code == 200:
        data = response.json()
        hist_df = pd.DataFrame(data.get("historical_population", []))

        if not hist_df.empty:
            hist_df = hist_df.set_index("year")
            hist_df.index = hist_df.index.astype(int)

            for col in ["migrants", "fertility_rate", "median_age", "urban_population_pct"]:
                if col not in hist_df.columns:
                    hist_df[col] = None
    return hist_df


def pearsonr_safe(x, y):
    x = pd.Series(x).dropna()
    y = pd.Series(y).dropna()
    if len(x) < 2 or len(y) < 2:
        return np.nan
    return np.corrcoef(x, y)[0, 1]



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


tab1, tab2, tab3, tab4 = st.tabs([
    "Population Trends", 
    "Migrants Over Time", 
    "Median Age", 
    "Correlation for Median Age"
])

with tab1:
    st.subheader("Population Trends of G7 Countries")
    fig_pop = go.Figure()
    for c in selected_countries:
        hist_df = get_population_data(c)
        if not hist_df.empty:
            mask = (hist_df.index >= year_range[0]) & (hist_df.index <= year_range[1])
            hist_df = hist_df.loc[mask]

            if not hist_df.empty:
                mode = "lines+markers" if (show_lines and show_points) else "lines" if show_lines else "markers"
                fig_pop.add_trace(go.Scatter(x=hist_df.index, y=hist_df["population"],
                                             mode=mode, name=c))

    fig_pop.update_layout(
        xaxis_title="Year",
        yaxis_title="Population",
        height=600,
        width=1100,
        template="plotly_white"
    )
    fig_pop.update_xaxes(dtick=5)
    st.plotly_chart(fig_pop, use_container_width=True)


with tab2:
    st.subheader("Migrants Over Time")
    fig_mig = go.Figure()
    for c in selected_countries:
        hist_df = get_population_data(c)
        if not hist_df.empty:
            mask = (hist_df.index >= year_range[0]) & (hist_df.index <= year_range[1])
            hist_df = hist_df.loc[mask]

            # 🔹 Exclude Italy, 1995
            if c == "Italy" and 1995 in hist_df.index:
                hist_df = hist_df.drop(index=1995)

            if "migrants" in hist_df.columns:
                fig_mig.add_trace(go.Scatter(
                    x=hist_df.index,
                    y=hist_df["migrants"],
                    mode="lines+markers",
                    name=c
                ))

    fig_mig.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Migrants",
        height=500,
        width=1100,
        template="plotly_white"
    )
    fig_mig.update_xaxes(dtick=5)
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
                mode = "lines+markers" if (show_lines and show_points) else "lines" if show_lines else "markers"
                fig_age.add_trace(go.Scatter(x=hist_df.index, y=hist_df["median_age"],
                                             mode=mode, name=c))

    fig_age.update_layout(
        xaxis_title="Year",
        yaxis_title="Median Age",
        height=600,
        width=1100,
        template="plotly_white"
    )
    fig_age.update_xaxes(dtick=5)
    st.plotly_chart(fig_age, use_container_width=True)


with tab4:
    st.subheader("Correlations Across G7 Countries")

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
        
        # Median Age vs Fertility
        df1 = df_all[["median_age", "fertility_rate", "country"]].dropna()
        fig1 = go.Figure()
        r_values1, r_list = [], []
        for c in df1["country"].unique():
            sub = df1[df1["country"] == c]
            fig1.add_trace(go.Scatter(x=sub["median_age"], y=sub["fertility_rate"],
                                      mode="markers", name=c))
            r = pearsonr_safe(sub["median_age"], sub["fertility_rate"])
            if not np.isnan(r): r_list.append(r)
            r_values1.append({"Country": c, "R (Median Age vs Fertility Rate)": round(r, 2) if not np.isnan(r) else np.nan})

        # 🔹 Add trendline for overall data
        if len(df1) > 1:
            m, b = np.polyfit(df1["median_age"], df1["fertility_rate"], 1)
            fig1.add_trace(go.Scatter(
                x=df1["median_age"],
                y=m * df1["median_age"] + b,
                mode="lines",
                name="Trendline",
                line=dict(color="black", dash="dash")
            ))

        overall_r1 = np.nanmean(r_list) if r_list else np.nan
        r_values1.append({"Country": "Overall", "R (Median Age vs Fertility Rate)": round(overall_r1, 2) if not np.isnan(overall_r1) else np.nan})

        fig1.update_layout(title="Median Age vs Fertility Rate", xaxis_title="Median Age", yaxis_title="Fertility Rate", template="plotly_white", height=600)
        st.plotly_chart(fig1, use_container_width=True)
        st.dataframe(pd.DataFrame(r_values1).set_index("Country"), use_container_width=True)

        # Median Age vs Migrants
        df2 = df_all[["median_age", "migrants", "country"]].dropna()
        fig2 = go.Figure()
        r_values2, r_list = [], []
        for c in df2["country"].unique():
            sub = df2[df2["country"] == c]
            fig2.add_trace(go.Scatter(x=sub["median_age"], y=sub["migrants"], mode="markers", name=c))
            r = pearsonr_safe(sub["median_age"], sub["migrants"])
            if not np.isnan(r): r_list.append(r)
            r_values2.append({"Country": c, "R (Median Age vs Migrants)": round(r, 2) if not np.isnan(r) else np.nan})

        if len(df2) > 1:
            m, b = np.polyfit(df2["median_age"], df2["migrants"], 1)
            fig2.add_trace(go.Scatter(
                x=df2["median_age"],
                y=m * df2["median_age"] + b,
                mode="lines",
                name="Trendline",
                line=dict(color="black", dash="dash")
            ))

        overall_r2 = np.nanmean(r_list) if r_list else np.nan
        r_values2.append({"Country": "Overall", "R (Median Age vs Migrants)": round(overall_r2, 2) if not np.isnan(overall_r2) else np.nan})

        fig2.update_layout(title="Median Age vs Migrants", xaxis_title="Median Age", yaxis_title="Migrants", template="plotly_white", height=600)
        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(pd.DataFrame(r_values2).set_index("Country"), use_container_width=True)

        # Median Age vs Urban Population %
        df3 = df_all[["median_age", "urban_population_pct", "country"]].dropna()
        fig3 = go.Figure()
        r_values3, r_list = [], []
        for c in df3["country"].unique():
            sub = df3[df3["country"] == c]
            fig3.add_trace(go.Scatter(x=sub["median_age"], y=sub["urban_population_pct"], mode="markers", name=c))
            r = pearsonr_safe(sub["median_age"], sub["urban_population_pct"])
            if not np.isnan(r): r_list.append(r)
            r_values3.append({"Country": c, "R (Median Age vs Urban Pop. %)": round(r, 2) if not np.isnan(r) else np.nan})

        if len(df3) > 1:
            m, b = np.polyfit(df3["median_age"], df3["urban_population_pct"], 1)
            fig3.add_trace(go.Scatter(
                x=df3["median_age"],
                y=m * df3["median_age"] + b,
                mode="lines",
                name="Trendline",
                line=dict(color="black", dash="dash")
            ))

        overall_r3 = np.nanmean(r_list) if r_list else np.nan
        r_values3.append({"Country": "Overall", "R (Median Age vs Urban Pop. %)": round(overall_r3, 2) if not np.isnan(overall_r3) else np.nan})

        fig3.update_layout(title="Median Age vs Urban Population %", xaxis_title="Median Age", yaxis_title="Urban Population (%)", template="plotly_white", height=600)
        st.plotly_chart(fig3, use_container_width=True)
        st.dataframe(pd.DataFrame(r_values3).set_index("Country"), use_container_width=True)

    else:
        st.info("No countries selected. Please select at least one country to view data.")
