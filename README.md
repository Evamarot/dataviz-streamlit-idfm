# Streamlit Data Story: Air Quality vs. Transit Frequency in Paris Underground

**Author:** Eva MAROT (ID: 20220929)
**Project:** Individual Student Project : Streamlit Dashboard

## 📊 Project Overview

This interactive dashboard explores the relationship between **air quality** and **transit frequency** within the underground stations of the Paris public transport network (Île-de-France).

Built with Streamlit, the application aims to answer the question: **Does higher train/metro traffic correlate with poorer air quality in stations?**

---

## 💾 Data Sources

The analysis relies on two primary open datasets provided by Île-de-France Mobilités (IDFM) via the French open data portal data.gouv.fr:

1.  **Air Quality Data:**
    * Dataset: [**Qualité de l’Air dans le réseau de transport francilien**](https://www.data.gouv.fr/datasets/qualite-de-lair-dans-le-reseau-de-transport-francilien/)
    * Description: Provides quantified pollution scores (Low=1, Medium=2, High=3) derived from official categorical measurements for underground stations.
2.  **Transit Data (GTFS):**
    * Dataset: [**Horaires prévus sur les lignes de transport en commun d'Ile-de-France (GTFS Datahub)**](https://www.data.gouv.fr/datasets/horaires-prevus-sur-les-lignes-de-transport-en-commun-dile-de-france-gtfs-datahub/)
    * Description: Contains detailed schedule information (stops, times, routes, trips) used to calculate the average hourly transit frequency per station.

**Reproducibility:** The application automatically downloads the latest versions of these datasets on the first run and uses Streamlit's caching (`@st.cache_data`) for subsequent loads, ensuring performance and reproducibility without bundling large files.

---

## ✨ Key Features & Visualizations

* **KPI Overview:** High-level metrics showing the average pollution score, average frequency, and count of high-pollution stations across the network.
* **Interactive Map:** Geographical distribution of stations using Pydeck, colored by pollution score and sized by average frequency, with tooltips on hover.
* **Line Ranking:** Bar chart ranking individual transport lines by their average pollution score across served stations.
* **Correlation Scatter Plot:** Visualization exploring the relationship between individual station frequency and pollution score.
* **Data Explorer:** An interactive table allowing users to sort, search, and explore the final merged dataset for all 319 matched stations.
* **Sidebar Filter:** Allows users to filter the map and KPIs by specific transit lines.

---

## 💡 Key Findings

The analysis reveals several key insights:

1.  **Weak Correlation:** There is no strong, direct correlation between a station's average transit frequency and its measured pollution score. High-traffic stations do not necessarily have the highest pollution, and vice-versa.
2.  **Line-Specific Factors:** Certain lines (ex: Metro 5, Metro 9) consistently show higher average pollution scores, suggesting that factors like line age, depth, ventilation systems, or train braking technology might be more influential than just traffic volume.
3.  **Distribution:** Most underground stations fall into the "Low" (Score ≈ 1) or "Medium" (Score ≈ 2) pollution categories, with only a smaller number classified as "High" (Score > 2.5).

---

## 🚀 Setup and Running Instructions

**Prerequisites:**
* Python 3.8+

**Steps:**

1.  **Clone the Repository (Optional):**
    ```bash
    git clone [YOUR REPO URL]
    cd MonProjetStreamlit_IDFM
    ```
2.  **Install Dependencies:**
    Install the required libraries using `pip`:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the Streamlit Application:**
    Navigate to the project's root directory in your terminal and run:
    ```bash
    streamlit run app.py
    ```
    The application will open automatically in your web browser. The initial run will take slightly longer as it downloads and processes the data for the first time.

---

## ⚠️ Data Quality & Limitations

* **Pollution Score:** The score is a quantification (1=Low, 3=High) based on official *categorical* measurements. It represents an average or snapshot, not real-time data.
* **Scope:** Analysis focuses solely on *underground* stations; above-ground stations were explicitly filtered out.
* **Frequency Data:** Transit frequency is calculated based on *scheduled* GTFS data, not real-time train movements.
* **Station Matching:** Merging datasets relies on normalized station names, which might introduce minor inaccuracies for complex or ambiguously named stations.