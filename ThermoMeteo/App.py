import streamlit as st

st.set_page_config(
    page_title="HeatPulse AI | Heizungs-Monitoring",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

dashboard_page = st.Page(
    "dashboard.py",
    title="HeatPulse AI",
    url_path="",
    default=True,
)
impressum_page = st.Page(
    "impressum.py",
    title="Impressum",
    url_path="impressum",
)
datenschutz_page = st.Page(
    "datenschutz.py",
    title="Datenschutzerklärung",
    url_path="datenschutz",
)

current_page = st.navigation(
    [dashboard_page, impressum_page, datenschutz_page],
    position="hidden",
)
current_page.run()
