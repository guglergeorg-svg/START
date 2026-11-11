import streamlit as st
import pandas as pd
from supabase import create_client, Client

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

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

# Daten aus Supabase abrufen
@st.cache_data(ttl=60) # Holt alle 60 Sekunden frische Daten
def load_data():
    # WICHTIG: "dein_tabellenname" anpassen!
    response = supabase.table("vorlauf_messungen").select("*").order("created_at", desc=True).limit(200).execute()
    return response.data

st.title("Vorlaufwächter Dashboard")

raw_data = load_data()

if raw_data:
    df = pd.DataFrame(raw_data)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df_chart = df.pivot(
        index="created_at",
        columns="sensor_id",
        values="temperatur",
    )

    st.success("Daten erfolgreich geladen!")
    st.subheader("Temperaturverlauf")
    st.line_chart(df_chart)

    with st.expander("Rohe Tabellendaten einsehen"):
        st.dataframe(df)
else:
    st.warning("Keine Daten gefunden oder Verbindungsfehler.")