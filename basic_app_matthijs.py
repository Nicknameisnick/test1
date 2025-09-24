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

        # --- Scatterplot 1: Median Age vs Fertility Rate ---
        df1 = df_all[["median_age", "fertility_rate", "country"]].dropna()
        fig1 = go.Figure()
        for c in df1["country"].unique():
            sub = df1[df1["country"] == c]
            fig1.add_trace(go.Scatter(
                x=sub["median_age"], y=sub["fertility_rate"],
                mode="markers", name=c
            ))

        fig1.update_layout(
            title="Median Age vs Fertility Rate",
            xaxis_title="Median Age",
            yaxis_title="Fertility Rate",
            template="plotly_white",
            height=600
        )
        st.plotly_chart(fig1, use_container_width=True)

        # R values per country
        r_values1 = []
        for c in df1["country"].unique():
            sub = df1[df1["country"] == c]
            if len(sub) > 1:
                r = np.corrcoef(sub["median_age"], sub["fertility_rate"])[0, 1]
                r_values1.append({"Country": c, "R (Median Age vs Fertility Rate)": round(r, 2)})
        st.dataframe(pd.DataFrame(r_values1).set_index("Country"))

        # --- Scatterplot 2: Median Age vs Migrants ---
        df2 = df_all[["median_age", "migrants", "country"]].dropna()
        fig2 = go.Figure()
        for c in df2["country"].unique():
            sub = df2[df2["country"] == c]
            fig2.add_trace(go.Scatter(
                x=sub["median_age"], y=sub["migrants"],
                mode="markers", name=c
