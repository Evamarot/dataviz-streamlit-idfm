# sections/overview.py
import streamlit as st
import pandas as pd
from utils.viz import create_histogram
import numpy as np 

def render(df_geo_filtered, selected_metric):
    st.header("1. Network Overview: A First Look at the Numbers")

    # Calculate KPIs
    if not df_geo_filtered.empty:
        total_stations = df_geo_filtered.shape[0]
        avg_pollution = df_geo_filtered['pollution_score'].mean()
        avg_frequency = df_geo_filtered['avg_passages'].mean()
        high_pollution_count = df_geo_filtered[df_geo_filtered['pollution_score'] >= 2.5].shape[0]
    else:
        total_stations, avg_pollution, avg_frequency, high_pollution_count = 0, np.nan, np.nan, 0

    st.markdown("Here's a snapshot of the **319 underground stations** successfully matched between air quality and traffic data:")

    # Display KPIs with Tooltips
    c1, c2, c3 = st.columns(3)
    c1.metric("Stations Analyzed", f"{total_stations}",
              help="Number of matched underground stations in the current filter.")
    c2.metric("Avg Pollution Score", f"{avg_pollution:.2f}" if not np.isnan(avg_pollution) else "N/A",
              delta=f"{high_pollution_count} stations (High Pollution)", delta_color="inverse",
              help="Average quantified score (1=Low, 3=High). Scores > 2.5 are flagged as 'High'.")
    c3.metric("Avg Frequency (Passages/Hr)", f"{avg_frequency:.1f}" if not np.isnan(avg_frequency) else "N/A",
              help="Average scheduled train/metro passages per hour across these stations.")

    st.markdown("---")
    st.subheader("Distribution: How do stations rank on pollution?")
    st.markdown("Most stations fall into the 'Low' (Score 1.0) or 'Medium' (Score 2.0) categories based on the available measurements.")

    if not df_geo_filtered.empty and 'pollution_score' in df_geo_filtered.columns:
        create_histogram(df_geo_filtered, 'pollution_score', 'Pollution Score')
        st.caption("This histogram shows the count of stations for each pollution score level. Notice the peaks around 1.0 and 2.0, with fewer stations scoring higher.")
    else:
        st.warning("No stations match the selected line filter to display distribution.")