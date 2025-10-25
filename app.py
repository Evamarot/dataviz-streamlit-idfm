# app.py
import streamlit as st
import pandas as pd
# Import data loading function
from utils.io import get_processed_data
# Import section rendering modules
from sections import intro, overview, deep_dives, conclusions
import re # Needed for splitting line names

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Air Quality & Transit - IDF",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- TITLE AND CAPTION ---
st.title("Air Quality in the Paris Transit Network: Frequency vs. Pollution")
st.caption("""
    Data Sources: 
    [Qualité de l’Air dans le réseau de transport francilien](https://www.data.gouv.fr/datasets/qualite-de-lair-dans-le-reseau-de-transport-francilien/) & 
    [Horaires prévus sur les lignes de transport en commun d'Ile-de-France (GTFS Datahub)](https://www.data.gouv.fr/datasets/horaires-prevus-sur-les-lignes-de-transport-en-commun-dile-de-france-gtfs-datahub/) 
    (data.gouv.fr) | Data Story by Eva MAROT (20220929)
""")

# --- DATA LOADING (Uses cached function) ---
processed_data = get_processed_data()
df_geo = processed_data.get('geo_table', pd.DataFrame())

# --- SIDEBAR CONTROLS (Filters) ---
with st.sidebar:
    st.header("Exploration Filters")
    # --- Line Selector ---
    if not df_geo.empty and 'line_name_list' in df_geo.columns:
        st.subheader("Filter by Transit Line")
        all_lines_raw = df_geo['line_name_list'].astype(str).str.split(', ').explode().dropna().unique().tolist()
        all_lines_cleaned = sorted([re.sub(r'^\s+|\s+$', '', line) for line in all_lines_raw if line])
        all_lines = ['All Lines'] + all_lines_cleaned
        selected_line = st.selectbox("Select Line(s) to Highlight", all_lines)
    else:
        selected_line = 'All Lines'
        if df_geo.empty: st.warning("Data not loaded.")
        else: st.warning("Column 'line_name_list' not found.")

    st.markdown("---")
    st.subheader("Analysis Metrics")
    selected_metric = st.selectbox( # Primarily for display context, not used for filtering visuals
        "Display Metric Context",
        ["Pollution Score (1=Low, 3=High)", "Average Passages Count"]
    )

# --- MAIN PANEL RENDERING ---
if not df_geo.empty:
    # --- DATA FILTERING LOGIC ---
    if selected_line != 'All Lines':
        if 'line_name_list' in df_geo.columns:
            df_geo_filtered = df_geo[
                df_geo['line_name_list'].astype(str).str.contains(selected_line, na=False, regex=False)
            ].copy()
        else:
            df_geo_filtered = df_geo.copy()

        # Pass filtered geo_table, but original aggregated tables for rankings
        filtered_data = {
            'geo_table': df_geo_filtered,
            'line_ranking_table': processed_data.get('line_ranking_table', pd.DataFrame()),
            'single_line_agg_table': processed_data.get('single_line_agg_table', pd.DataFrame())
        }
    else:
        # No filter applied
        filtered_data = processed_data
        df_geo_filtered = processed_data.get('geo_table', pd.DataFrame())

    # --- RENDER SECTIONS ---
    intro.render()
    st.markdown("---")
    overview.render(df_geo_filtered, selected_metric)
    st.markdown("---")
    deep_dives.render(filtered_data, selected_line)
    st.markdown("---")

    # --- DATA QUALITY AND CONCLUSION ---
    st.markdown("### Data Quality & Limitations")
    st.info("""
    * The pollution score is a quantification (1=Low, 3=High) based on official categorical measurements. It represents an average or snapshot, not real-time data.
    * Analysis focuses solely on underground stations, above-ground stations were excluded.
    * Transit frequency is based on scheduled GTFS data, not real-time traffic.
    * Station name matching between datasets relies on normalization and may have minor inaccuracies.
    * No missing values were imputed; stations with incomplete data were excluded from relevant analyses.
            """)
    conclusions.render()
else:
    st.error("Application failed to load or process necessary data. Please check data source links or network connection.")