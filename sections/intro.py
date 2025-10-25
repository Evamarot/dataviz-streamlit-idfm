# sections/intro.py
import streamlit as st

def render():
    st.header("Context: Air Quality in the Paris Transit Network")
    st.markdown("""
        Ever wondered about the air you breathe underground? Air quality in subway and RER systems is a key public health topic, especially concerning fine particles (PM). 
        This dashboard digs into the data, comparing **official pollution measurements** from stations across the Île-de-France network with the **calculated train/metro frequency** based on published schedules (GTFS). 

        Our main question: **Does more traffic automatically mean worse air quality in a station?**

        We're using data from 
        [**Qualité de l’Air dans le réseau de transport francilien**](https://www.data.gouv.fr/datasets/qualite-de-lair-dans-le-reseau-de-transport-francilien/) (Air Quality) and 
        [**Horaires prévus sur les lignes de transport en commun d'Ile-de-France (GTFS Datahub)**](https://www.data.gouv.fr/datasets/horaires-prevus-sur-les-lignes-de-transport-en-commun-dile-de-france-gtfs-datahub/) (Schedules), 
        provided by Île-de-France Mobilités via data.gouv.fr.
    """)
    st.subheader("My Data Story Arc:")
    st.markdown("""
        1.  **The Big Picture:** What's the average air quality score, and how are stations distributed across pollution levels? (Overview & KPIs)
        2.  **Digging Deeper:** Where are the pollution hotspots geographically? Which specific lines tend to have higher pollution? Crucially, is there a direct link between a station's traffic volume and its pollution score? (Deep Dive)
        3.  **The Bottom Line:** What did we find, and what could be done about it? (Conclusion & Recommendations)
    """)