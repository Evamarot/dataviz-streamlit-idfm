# utils/io.py
import streamlit as st
import pandas as pd
import requests
import zipfile
from io import BytesIO, StringIO

# --- Configuration ---
# Direct URLs for data download
AIR_QUALITY_URL = "https://www.data.gouv.fr/api/1/datasets/r/efb9ab99-4c52-4722-be5a-245c5322ab33"
GTFS_ZIP_URL = "https://www.data.gouv.fr/api/1/datasets/r/f9fff5b1-f9e4-4ec2-b8b3-8ad7005d869c"

@st.cache_data(show_spinner="Downloading and preparing data...")
def get_processed_data():
    """Main function: Downloads, caches, and processes the raw data."""
    air_df_raw, gtfs_data_raw = load_raw_data()
    from utils.prep import prepare_data
    processed_tables = prepare_data(air_df_raw, gtfs_data_raw)
    return processed_tables

def load_raw_data():
    """Downloads and loads the raw datasets from their URLs."""
    
    # --- Load Air Quality Data ---
    st.info("Downloading Air Quality Data...")
    try:
        response_air = requests.get(AIR_QUALITY_URL)
        response_air.raise_for_status()
        air_df_raw = pd.read_csv(StringIO(response_air.text), sep=';', encoding='utf-8')
        
        # Rename essential French columns to English for consistency
        air_df_raw.rename(columns={
            'Identifiant station': 'station_id',
            'Nom de la Station': 'station_name',
            'Nom de la ligne': 'line_name',
            'Niveau de pollution aux particules': 'pollution_level_text',
            'stop_lat': 'stop_lat_air',
            'stop_lon': 'stop_lon_air',
        }, inplace=True)
        # Keep other raw columns; they will be dropped in prep.py
    except Exception as e:
        st.error(f"Error loading air quality data: {e}")
        return pd.DataFrame(), {}

    # --- Load GTFS Data ---
    st.info("Downloading GTFS (Schedule) data...")
    try:
        response_gtfs = requests.get(GTFS_ZIP_URL)
        response_gtfs.raise_for_status()
        zip_file = zipfile.ZipFile(BytesIO(response_gtfs.content))
        
        # Read the four key GTFS files, suppressing DtypeWarnings
        gtfs_data_raw = {
            'stops': pd.read_csv(zip_file.open('stops.txt'), low_memory=False),
            'stop_times': pd.read_csv(zip_file.open('stop_times.txt'), low_memory=False),
            'trips': pd.read_csv(zip_file.open('trips.txt'), low_memory=False),
            'routes': pd.read_csv(zip_file.open('routes.txt'), low_memory=False)
        }
    except Exception as e:
        st.error(f"Error downloading or unzipping GTFS: {e}")
        gtfs_data_raw = {}

    return air_df_raw, gtfs_data_raw