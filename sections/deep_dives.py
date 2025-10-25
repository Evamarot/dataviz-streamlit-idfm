# sections/deep_dives.py
import streamlit as st
import pandas as pd
from utils.viz import create_map_chart, create_single_line_ranking_chart, create_scatter_chart

# --- Function to map score to text ---
def map_score_to_text(score):
    if score == 1.0: return "Low"
    elif 1.0 < score < 2.0: return "Low to Medium"
    elif score == 2.0: return "Medium"
    elif 2.0 < score < 3.0: return "Medium to High"
    elif score == 3.0: return "High"
    else: return f"Score {score:.1f}"

# --- Function for styling ---
def style_pollution_level(level):
    color = 'white'; background_color = 'transparent'
    if level == "Low": background_color = '#2ECC71'
    elif level in ["Low to Medium", "Medium"]: background_color = '#F39C12'
    elif level in ["Medium to High", "High"]: background_color = '#E74C3C'
    else: color = 'black'
    return f'background-color: {background_color}; color: {color}'

# --- Main Render Function ---
def render(filtered_data, selected_line):
    # Retrieve data tables
    df_geo = filtered_data.get('geo_table', pd.DataFrame())
    df_single_line_agg = filtered_data.get('single_line_agg_table', pd.DataFrame())

    st.header("2. Deep Dive: Data Exploration & Line Performance")

    # --- Section 1: Map view ---
    st.subheader("2.1. Where are the Pollution Hotspots?")
    st.markdown("Map showing station locations. **Color** indicates pollution score (Red=High), **Size** indicates average traffic frequency. Hover for details.")
    if not df_geo.empty:
        create_map_chart(df_geo)
        # ANALYSIS TEXT FOR MAP:
        st.caption("Looking at the map, higher pollution stations (orange/red) don't seem tightly clustered in one area. Also, notice how station traffic (circle size) doesn't visually align perfectly with pollution level (color).")
    else:
        st.warning(f"No station data found to display map (Filter: {selected_line})")
    st.markdown("---")

    # --- Section 2: Single Line Pollution Ranking ---
    st.subheader("2.2. Which Lines Have the Highest Average Pollution?")
    st.markdown("Let's rank individual transport lines by their *average* pollution score across all stations they serve. This might reveal line-specific issues.")
    if not df_single_line_agg.empty:
        create_single_line_ranking_chart(df_single_line_agg, top_n=20) # Show Top 20 for brevity
        top_lines = df_single_line_agg['line_name_single'].head(3).tolist()
        st.caption(f"Interesting! Lines like **{', '.join(top_lines)}** emerge with the highest average scores. This suggests factors specific to these lines (perhaps their depth, ventilation, train type?) could be influential.")
    else:
        st.error("Single line aggregation data unavailable.")
    st.markdown("---")

    # --- Section 3: Scatter Plot Correlation ---
    st.subheader("2.3. Does Higher Station Traffic Mean Higher Pollution?")
    st.markdown("Here's the direct test: comparing each station's average traffic frequency (X-axis) against its pollution score (Y-axis). If frequency were the main driver, we'd expect points rising from bottom-left to top-right.")
    if not df_geo.empty:
        create_scatter_chart(df_geo)
        st.caption("The scatter plot shows **no clear correlation**. Stations with high frequency can have low or high pollution, and vice-versa. This strongly suggests that traffic volume alone isn't the primary factor determining a station's pollution score.")
    else:
        st.warning(f"No station data found to display correlation (Filter: {selected_line})")
    st.markdown("---")

    # --- Section 4: Data explorer ---
    st.subheader("2.4. Data Explorer : Dig into the Station Details")
    st.markdown("Explore, sort, and search the final merged data for all **319** matched underground stations.")

    if not df_geo.empty:
        # Select columns relevant for the explorer
        columns_to_show = [
            'station_name', 'line_name_list', 'pollution_score',
            'avg_passages', 'lat', 'lon'
        ]
        # Ensure only existing columns are selected
        display_df = df_geo[[col for col in columns_to_show if col in df_geo.columns]].copy()

        # Create the textual pollution level column
        if 'pollution_score' in display_df.columns:
            display_df['Pollution Level'] = display_df['pollution_score'].apply(map_score_to_text)
        else:
            display_df['Pollution Level'] = 'N/A' # Handle missing score column

        # Rename columns for display
        display_df.rename(columns={
            'station_name': 'Station',
            'line_name_list': 'Lines Served',
            'avg_passages': 'Avg Freq (Pass/Hr)',
            'lat': 'Latitude',
            'lon': 'Longitude'
        }, inplace=True)

        # Define final column order for display
        final_columns_order = [
            'Station', 'Lines Served', 'Pollution Level',
            'Avg Freq (Pass/Hr)', 'Latitude', 'Longitude', 'pollution_score' # Keep score for styling reference
        ]
        # Filter again to ensure order exists
        display_df = display_df[[col for col in final_columns_order if col in display_df.columns]]

        # Apply styling using Pandas Styler
        styled_df = display_df.style
        if 'Pollution Level' in display_df.columns:
             styled_df = styled_df.apply(lambda col: col.map(style_pollution_level), subset=['Pollution Level'])

        # Display the styled DataFrame
        st.dataframe(
            styled_df,
            width='stretch', # Replaces use_container_width=True
            height=400,
            column_config={
                # Configure numeric columns
                "Avg Freq (Pass/Hr)": st.column_config.NumberColumn(format="%.1f"),
                "Latitude": st.column_config.NumberColumn(format="%.4f"),
                "Longitude": st.column_config.NumberColumn(format="%.4f"),
                # Hide the original numeric score column from display
                "pollution_score": None,
            }
        )
    else:
        st.warning("No data available to display in the table for the selected filter.")
