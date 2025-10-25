# utils/prep.py
import pandas as pd
import numpy as np
import unicodedata
import re

# --- Configuration ---
POLLUTION_SCORE_MAP = {
    'pollution faible': 1, 'pollution moyenne': 2, 'pollution élevée': 3,
    'faible': 1, 'moyen': 2, 'élevée': 3,
}

# --- Utility Functions ---
def normalize_station_name(name):
    """Standardizes station names for merging (lowercase, no accents/punctuation)."""
    if pd.isna(name): return name
    name = str(name).lower().strip()
    name = unicodedata.normalize('NFD', name)
    name = name.encode('ascii', 'ignore').decode('utf-8')
    name = re.sub(r'[^\w]', '', name).strip()
    return name

def join_unique_lines(series):
    """Aggregates unique line names into a comma-separated string."""
    return ', '.join(series.dropna().astype(str).unique())

def time_to_seconds(time_str):
    """Converts HH:MM:SS time string to total seconds from midnight."""
    try:
        h, m, s = map(int, str(time_str).split(':'))
        # Handle times beyond 24:00:00 if necessary, though modulo later fixes it
        return h * 3600 + m * 60 + s
    except:
        return np.nan

# --- Main Preparation Function ---
def prepare_data(air_df_raw, gtfs_data_raw):
    """Orchestrates the cleaning, transformation, and merging of data."""
    
    if air_df_raw.empty or not gtfs_data_raw or gtfs_data_raw['stops'].empty:
        # Return empty dict if raw data loading failed
        return {"geo_table": pd.DataFrame(), "line_ranking_table": pd.DataFrame(), "single_line_agg_table": pd.DataFrame()}

    df_air_processed = process_air_quality(air_df_raw)
    df_gtfs_processed = process_gtfs(gtfs_data_raw)

    # Merge processed dataframes
    df_merged = pd.merge(
        df_air_processed,
        df_gtfs_processed,
        on='station_name_clean',
        how='inner',
        suffixes=('_air', '_gtfs')
    )

    # Select and rename final columns for analysis/display
    COLS_TO_KEEP_FINAL = [
        'station_name_clean', 'station_name_air', 'lines_affected_air',
        'pollution_score_mean', 'avg_passages',
        'stop_lat', 'stop_lon', # Use averaged GTFS coordinates
    ]
    df_final = df_merged[[col for col in COLS_TO_KEEP_FINAL if col in df_merged.columns]].copy()
    
    df_final.rename(columns={
        'station_name_air': 'station_name',
        'lines_affected_air': 'line_name_list',
        'pollution_score_mean': 'pollution_score',
        'stop_lat': 'lat', 'stop_lon': 'lon',
    }, inplace=True)
    
    df_final = df_final.drop_duplicates(subset=['station_name']).copy()

    # Create aggregated tables for specific visualizations
    df_geo_table = df_final.copy()

    df_line_ranking_table = df_final.groupby('line_name_list').agg(
        pollution_score=('pollution_score', 'mean'),
        stations_count=('station_name', 'count')
    ).reset_index().sort_values(by='pollution_score', ascending=False).rename(columns={'line_name_list': 'line_name'})

    # Create Single Line Aggregation Table (for individual line ranking)
    df_for_single_line = df_final[['line_name_list', 'pollution_score', 'avg_passages']].copy()
    df_for_single_line['line_name_single'] = df_for_single_line['line_name_list'].str.split(', ')
    df_exploded = df_for_single_line.explode('line_name_single')
    df_exploded['line_name_single'] = df_exploded['line_name_single'].str.strip()
    
    df_single_line_agg = df_exploded.groupby('line_name_single').agg(
        avg_pollution=('pollution_score', 'mean'),
        avg_frequency=('avg_passages', 'mean'),
        stations_served=('line_name_single', 'count')
    ).reset_index().sort_values(by='avg_pollution', ascending=False)

    return {
        "geo_table": df_geo_table,
        "line_ranking_table": df_line_ranking_table, # Ranking by unique line combinations
        "single_line_agg_table": df_single_line_agg # Ranking by individual lines
    }

# --- Air Quality Processing ---
def process_air_quality(air_df_raw):
    """Cleans, filters, and aggregates the raw air quality data."""
    air_df = air_df_raw.copy()

    # Drop unnecessary columns identified in the notebook
    cols_to_drop = [
        'Niveau de pollution', 'Incertitude', 'Recommandation de surveillance', 'Action(s) QAI en cours', 
        'Lien vers les mesures en direct', 'Durée des mesures', "Mesures d’amélioration mises en place ou prévues", 
        'point_geo', 'pollution_air', 'air', 'niveau', 'actions', 'niveau_pollution'
    ]
    air_df.drop(columns=[col for col in cols_to_drop if col in air_df.columns], inplace=True, errors='ignore')

    # Filter out above-ground stations
    air_df = air_df[air_df['pollution_level_text'] != "station aérienne"].copy()

    # Quantify pollution score
    air_df['pollution_score'] = air_df['pollution_level_text'].str.lower().map(POLLUTION_SCORE_MAP)
    air_df.dropna(subset=['pollution_score'], inplace=True)
    
    # Normalize station name for merging
    air_df['station_name_clean'] = air_df['station_name'].apply(normalize_station_name)

    # Aggregate by cleaned station name
    df_air_processed = air_df.groupby(['station_name_clean']).agg(
        pollution_score_mean=('pollution_score', 'mean'),
        lines_affected_air=('line_name', join_unique_lines),
        station_name_air=('station_name', 'first'), # Keep one original name
        station_id_list=('station_id', join_unique_lines), # Keep IDs for ref
        stop_lat_air=('stop_lat_air', 'mean'), # Average coords
        stop_lon_air=('stop_lon_air', 'mean')
    ).reset_index()
    
    return df_air_processed

# --- GTFS Processing ---
def process_gtfs(gtfs_data_raw):
    """Processes GTFS data to calculate average frequency per station."""
    df_stops = gtfs_data_raw['stops']
    df_stop_times = gtfs_data_raw['stop_times']
    df_trips = gtfs_data_raw['trips']
    df_routes = gtfs_data_raw['routes']

    # Link trips to routes for line names
    df_trips_routes = df_trips[['route_id', 'trip_id']].merge(
        df_routes[['route_id', 'route_short_name', 'route_long_name']], on='route_id', how='left'
    )
    df_trips_routes['line_name_clean'] = df_trips_routes['route_short_name'].fillna(df_trips_routes['route_long_name']).astype(str)
    df_trips_routes = df_trips_routes[['trip_id', 'line_name_clean']]

    # Calculate passages per stop per hour
    df_stop_times['arrival_time_sec'] = df_stop_times['arrival_time'].apply(time_to_seconds)
    df_stop_times.dropna(subset=['arrival_time_sec'], inplace=True)
    df_stop_times['hour'] = (df_stop_times['arrival_time_sec'] // 3600).astype(int) % 24
    
    df_frequency_raw = df_stop_times.merge(df_trips_routes, on='trip_id', how='left')
    df_frequency_raw.dropna(subset=['line_name_clean'], inplace=True)
    df_frequency = df_frequency_raw.groupby(['stop_id', 'line_name_clean', 'hour']).size().reset_index(name='passages_count')

    # Normalize stop names and merge frequency
    df_stops_clean = df_stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']].copy()
    df_stops_clean.rename(columns={'stop_name': 'station_name'}, inplace=True)
    df_stops_clean['station_name_clean'] = df_stops_clean['station_name'].apply(normalize_station_name)
    
    df_final_gtfs = df_frequency.merge(df_stops_clean, on='stop_id', how='left')

    # Aggregate by cleaned station name, averaging frequency and coordinates
    df_gtfs_processed = df_final_gtfs.groupby(['station_name_clean']).agg(
        stop_lat=('stop_lat', 'mean'), # Average coords
        stop_lon=('stop_lon', 'mean'),
        avg_passages=('passages_count', 'mean'),
        station_name_gtfs=('station_name', 'first') # Keep one original name
    ).reset_index()

    return df_gtfs_processed