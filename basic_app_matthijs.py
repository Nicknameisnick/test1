import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

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
            # Convert population to millions for display
            y_millions = hist_df["population"] / 1_000_000
            fig_pop.add_trace(go.Scatter(
                x=hist_df.index,
                y=y_millions,
                mode=mode,
                name=c,
                hovertemplate=(
                    "Year: %{x}<br>" +
                    "Population: %{y:.1f}M<br>" +
                    f"Country: {c}<extra></extra>"
                )
            ))

fig_pop.update_layout(
    title="Population Trends of G7 Countries",
    xaxis_title="Year",
    yaxis_title="Population (millions)",
    height=700,  # make it bigger
    width=1200,
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
            y_millions = hist_df["migrants"] / 1_000_000  # convert to millions
            fig_mig.add_trace(go.Scatter(
                x=hist_df.index,
                y=y_millions,
                mode="lines+markers",
                name=c,
                hovertemplate=(
                    "Year: %{x}<br>" +
                    "Migrants: %{y:.1f}M<br>" +
                    f"Country: {c}<extra></extra>"
                )
            ))

if data_found:
    fig_mig.update_layout(
        title="Migrants Over Time",
        xaxis_title="Year",
        yaxis_title="Migrants (millions)",
        height=700,  # bigger chart
        width=1200,
        template="plotly_white"
    )
    st.plotly_chart(fig_mig, use_container_width=True)
else:
    st.warning("⚠️ No migrants data available for the selected countries and years.")



