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
    df["temperatur"] = pd.to_numeric(df["temperatur"])
    df_chart = df.pivot(
        index="created_at",
        columns="sensor_id",
        values="temperatur",
    )
    df_chart = df_chart.ffill().bfill()

    st.success("Daten erfolgreich geladen!")
    st.subheader("Temperaturverlauf")
    st.line_chart(df_chart)

    st.subheader("Systemstatus & Alarme")
    MIN_TEMPERATUR = 20.0
    latest_values = df_chart.iloc[-1]

    for sensor, temp in latest_values.items():
        if pd.isna(temp):
            continue

        if temp < MIN_TEMPERATUR:
            st.error(
                f"🚨 ALARM: Vorlauftemperatur an Sensor {sensor} kritisch niedrig! "
                f"Aktuell: {temp:.1f} °C"
            )
        else:
            st.success(f"✅ Sensor {sensor} im Normalbereich ({temp:.1f} °C).")

    with st.expander("Rohe Tabellendaten einsehen"):
        st.dataframe(df)
else:
    st.warning("Keine Daten gefunden oder Verbindungsfehler.")