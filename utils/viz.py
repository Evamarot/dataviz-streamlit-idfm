# utils/viz.py
import pandas as pd
import altair as alt
import streamlit as st
import pydeck as pdk

# Thème Altair personnalisé pour la cohérence
ALTAIR_THEME = {
    'config': {
        'view': {'stroke': 'transparent'},
        'axis': {'gridColor': '#e0e0e0'},
        'range': {'category': ['#E74C3C', '#F39C12', '#2ECC71', '#3498DB']}, 
        'header': {'titleFontSize': 16, 'labelFontSize': 12},
    }
}
alt.themes.register('custom_theme', lambda: ALTAIR_THEME)
alt.themes.enable('custom_theme')

def create_map_chart(df_geo: pd.DataFrame):
    """
    Creates an interactive map using Pydeck (st.pydeck_chart) with tooltips.
    """
    
    # 1. Prepare DataFrame (ensure numeric, drop NaNs)
    df_map = df_geo.copy()
    for col in ['lat', 'lon', 'pollution_score', 'avg_passages', 'station_name', 'line_name_list']:
        if col in ['lat', 'lon', 'pollution_score', 'avg_passages']:
            df_map[col] = pd.to_numeric(df_map[col], errors='coerce')
        else: # Ensure text columns are strings
             df_map[col] = df_map[col].astype(str)
    df_map.dropna(subset=['lat', 'lon', 'pollution_score', 'avg_passages'], inplace=True)

    if df_map.empty:
        st.warning("No valid station data to display on the map.")
        return

    # 2. Map score to RGBA color (Pydeck expects list/tuple of 4 values 0-255)
    def map_score_to_rgba(score):
        if score <= 1.5: return [46, 204, 113, 200]  # Green
        elif score <= 2.5: return [243, 156, 18, 200]  # Orange
        else: return [231, 76, 60, 200]   # Red
    df_map['color'] = df_map['pollution_score'].apply(map_score_to_rgba)

    # 3. Scale size (Pydeck uses radius in meters, needs careful scaling)
    min_freq, max_freq = df_map['avg_passages'].min(), df_map['avg_passages'].max()
    if max_freq > min_freq:
        # Scale radius roughly from 20m to 200m based on frequency
        df_map['radius'] = ((df_map['avg_passages'] - min_freq) / (max_freq - min_freq)) * 250 + 50
    else:
        df_map['radius'] = 100 # Default radius
    df_map['radius'] = df_map['radius'].fillna(20).astype(int)

    # 4. Define Pydeck Layer
    layer = pdk.Layer(
        "ScatterplotLayer",
        df_map,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius="radius",
        pickable=True,
        auto_highlight=True,
    )

    # 5. Set Initial View State
    view_state = pdk.ViewState(
        latitude=48.8566, longitude=2.3522, zoom=11, pitch=0,
    )

    # 6. Define Tooltip Content (HTML)
    tooltip = {
        "html": """
            <b>Station:</b> {station_name}<br/>
            <b>Lines Served:</b> {line_name_list}<br/>
            <b>Pollution Score:</b> {pollution_score}<br/>
            <b>Avg Frequency:</b> {avg_passages} pass/hr<br/>
            <i><small>(Lat: {lat}, Lon: {lon})</small></i>
        """,
         "style": {"backgroundColor": "steelblue", "color": "white"}
     }

    # 7. Render Pydeck Chart
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v9", # Common styles: light-v9, dark-v9, streets-v11, satellite-v9
        tooltip=tooltip
    ))

    # 8. Add Manual Legend (Pydeck layers don't auto-generate complex legends)
    st.markdown("""
        **Legend:**
        * <span style="display: inline-block; width: 12px; height: 12px; background-color: #2ECC71; border-radius: 50%;"></span> Low Pollution (Score ≤ 1.5)
        * <span style="display: inline-block; width: 12px; height: 12px; background-color: #F39C12; border-radius: 50%;"></span> Medium Pollution (1.5 < Score ≤ 2.5)
        * <span style="display: inline-block; width: 12px; height: 12px; background-color: #E74C3C; border-radius: 50%;"></span> High Pollution (Score > 2.5)
        * _Circle size indicates average traffic frequency._
        """, unsafe_allow_html=True)

def create_scatter_chart(df_geo: pd.DataFrame):
    """Creates the station-level correlation scatter plot."""
    df_geo['avg_passages'] = pd.to_numeric(df_geo['avg_passages'], errors='coerce')
    df_geo['pollution_score'] = pd.to_numeric(df_geo['pollution_score'], errors='coerce')
    df_geo.dropna(subset=['avg_passages', 'pollution_score'], inplace=True)

    color_scale = alt.Scale(domain=[1.0, 2.0, 3.0], range=['#2ECC71', '#F39C12', '#E74C3C'])
    
    chart = alt.Chart(df_geo).mark_circle(size=60, opacity=0.7).encode(
        x=alt.X('avg_passages:Q', title='Average Frequency (Passages/Hour)'),
        y=alt.Y('pollution_score:Q', title='Pollution Score (1=Low, 3=High)', scale=alt.Scale(domain=[0.5, 3.5])),
        tooltip=[
            alt.Tooltip('station_name:N', title='Station'),
            alt.Tooltip('line_name_list:N', title='Lines'),
            alt.Tooltip('pollution_score:Q', title='Pollution Score', format='.2f'),
            alt.Tooltip('avg_passages:Q', title='Avg Frequency', format='.1f')
        ],
        color=alt.Color('pollution_score:Q', scale=color_scale, legend=alt.Legend(title="Pollution Score")),
    ).properties(
        title="Correlation: Frequency vs. Pollution (by Station)"
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)

def create_histogram(df_geo: pd.DataFrame, column: str, title: str):
    """Creates a simple histogram for distribution."""
    chart = alt.Chart(df_geo).mark_bar().encode(
        x=alt.X(f'{column}:Q', bin=alt.Bin(maxbins=20), title=title),
        y=alt.Y('count()', title='Number of Stations'),
        tooltip=[alt.Tooltip(f'{column}:Q', bin=True), alt.Tooltip('count()', title='Stations')]
    ).properties(
        title=f"Distribution of Stations by {title}"
    )
    st.altair_chart(chart, use_container_width=True)

def create_single_line_ranking_chart(df_single_line_agg: pd.DataFrame, top_n=30):
    """Creates the horizontal bar chart ranking individual lines by pollution."""
    df_display = df_single_line_agg.head(top_n).copy()
    df_display['avg_pollution'] = pd.to_numeric(df_display['avg_pollution'], errors='coerce')
    df_display.dropna(subset=['avg_pollution'], inplace=True)
    
    chart = alt.Chart(df_display).mark_bar().encode(
        x=alt.X('avg_pollution:Q', title='Avg Pollution Score (1=Low, 3=High)', scale=alt.Scale(domain=[0, 3])),
        y=alt.Y('line_name_single:N', sort='-x', title='Transit Line'),
        tooltip=[
            alt.Tooltip('line_name_single:N', title='Line'),
            alt.Tooltip('avg_pollution:Q', title='Avg Pollution Score', format='.2f'),
            alt.Tooltip('avg_frequency:Q', title='Avg Frequency on Line', format='.1f'),
            alt.Tooltip('stations_served:Q', title='Stations Served')
        ],
        color=alt.condition(
            alt.datum.avg_pollution >= 2.0,
            alt.value('#E74C3C'), # Red
            alt.value('#F39C12')  # Orange
        )
    ).properties(
        title=f"Lines Ranked by Average Pollution Score"
    )
    st.altair_chart(chart, use_container_width=True)