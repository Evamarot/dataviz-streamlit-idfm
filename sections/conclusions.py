# sections/conclusions.py
import streamlit as st

def render():
    st.header("3. The Bottom Line: Insights & What's Next")

    st.subheader("Key Findings:")
    st.success("""
    * **Frequency Isn't King:** Our central finding is that higher train/metro frequency **does not directly correlate** with higher measured pollution scores at the station level. Other factors seem much more important.
    * **Line Matters:** Certain lines consistently show higher average pollution scores across their stations (like **Metro 5, Metro 9**). This points towards line-specific characteristics (age, depth, ventilation, train technology) being significant drivers.
    """)

    st.subheader("Recommendations:")
    st.info("""
    Based on this analysis:
    1.  **Target the Top Lines:** Efforts to improve air quality (like ventilation upgrades or using trains with better braking systems) should prioritize the lines identified with the highest average pollution scores.
    2.  **Look Beyond Frequency:** Further studies should investigate station-specific factors like depth, overall ventilation capacity, and platform design, as these likely play a major role.
    3.  **Better Data Needed:** Moving towards more granular, real-time air quality sensors within stations would provide a much clearer picture than the current static or averaged scores.
    """)