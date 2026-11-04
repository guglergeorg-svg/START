import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="HeatPulse AI | B2B Heizungs-Monitoring",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .stApp {
        background: #0b1120;
        color: #e5e7eb;
    }

    #MainMenu,
    footer,
    header[data-testid="stHeader"] {
        display: none !important;
    }

    .block-container {
        max-width: 1600px;
        padding-top: 0.65rem;
        padding-bottom: 2rem;
    }

    section[data-testid="stSidebar"] {
        background: #101827;
        border-right: 1px solid rgba(148, 163, 184, 0.12);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 2rem;
    }

    h1, h2, h3 {
        color: #f8fafc;
        letter-spacing: -0.025em;
    }

    h2 {
        margin-top: 1.4rem;
    }

    .dashboard-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
        padding: 1.5rem 1.75rem;
        margin: 0.5rem 0 1.25rem;
        background: linear-gradient(120deg, #121d30, #111827);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 18px;
    }

    .dashboard-eyebrow {
        margin-bottom: 0.45rem;
        color: #94a3b8;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
    }

    .dashboard-header h1 {
        margin: 0;
        font-size: clamp(1.7rem, 3vw, 2.3rem);
        line-height: 1.15;
    }

    .dashboard-building {
        margin: 0.45rem 0 0;
        color: #94a3b8;
        font-size: 0.95rem;
    }

    .gateway-status {
        display: inline-flex;
        align-items: center;
        gap: 0.65rem;
        padding: 0.7rem 0.95rem;
        white-space: nowrap;
        color: #d1fae5;
        font-size: 0.85rem;
        font-weight: 600;
        background: rgba(16, 185, 129, 0.09);
        border: 1px solid rgba(52, 211, 153, 0.2);
        border-radius: 999px;
    }

    .gateway-dot {
        width: 0.55rem;
        height: 0.55rem;
        background: #34d399;
        border-radius: 50%;
        box-shadow: 0 0 12px rgba(52, 211, 153, 0.55);
    }

    [data-testid="stMetric"] {
        min-height: 108px;
        padding: 1rem 1.1rem;
        background: linear-gradient(145deg, #1e2030, #161824);
        border: 1px solid #2e3248;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.18);
    }

    [data-testid="stMetricLabel"] {
        color: #94a3b8;
        font-size: 0.82rem;
    }

    [data-testid="stMetricValue"] {
        color: #f8fafc;
        font-weight: 650;
    }

    [data-testid="stAlert"] {
        border-radius: 14px;
        border: 1px solid rgba(148, 163, 184, 0.16);
    }

    [data-testid="stPlotlyChart"] {
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 16px;
    }

    [data-testid="stPydeckChart"] {
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 16px;
    }

    [data-testid="stTabs"] button {
        font-weight: 600;
    }

    [data-testid="stTabs"] [role="tablist"] {
        gap: 0.4rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.16);
    }

    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #a5b4fc;
        border-bottom-color: #818cf8;
    }

    .section-kicker {
        margin: 0.35rem 0 0.9rem;
        color: #94a3b8;
        font-size: 0.86rem;
    }

    [data-baseweb="select"] > div,
    [data-testid="stTextArea"] textarea {
        background: #0f172a;
        border-color: rgba(148, 163, 184, 0.22);
        border-radius: 10px;
    }

    [data-testid="stTextArea"] textarea {
        color: #e2e8f0;
    }

    .stButton button {
        min-height: 2.8rem;
        border-radius: 10px;
        font-weight: 600;
        transition: transform 120ms ease, filter 120ms ease;
    }

    .stButton button:hover {
        filter: brightness(1.08);
        transform: translateY(-1px);
    }

    hr {
        border-color: rgba(148, 163, 184, 0.14);
    }

    @media (max-width: 700px) {
        .block-container {
            padding: 1rem 1rem 2rem;
        }

        .dashboard-header {
            align-items: flex-start;
            flex-direction: column;
            padding: 1.25rem;
        }

        .gateway-status {
            white-space: normal;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- 1. REALISTISCHE HKLS-DATENGENERIERUNG ---
@st.cache_data
def generate_hvac_data(scenario: str, hours: int = 72):
    np.random.seed(42)
    end_time = datetime.now().replace(minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(hours=hours)
    timestamps = pd.date_range(start=start_time, end=end_time, freq="5min")
    n = len(timestamps)
    
    # Zeit-Faktoren für Tag/Nacht-Rhythmus
    hours_float = timestamps.hour + timestamps.minute / 60.0
    
    # Realistische Außentemperatur (Tirol im Spätherbst: 2°C nachts bis 11°C tagsüber)
    t_out = 6.5 - 4.5 * np.cos(2 * np.pi * (hours_float - 4) / 24) + np.random.normal(0, 0.3, n)
    
    # Ideale Heizkurve (Vorlauf soll bei Kälte steigen)
    t_vl_ideal = 55 - 1.2 * t_out
    
    if scenario == "Hydraulischer Kurzschluss (Objekt Anichstraße 14)":
        # Vorlauf hoch, Rücklauf fast gleich hoch (Spreizung < 3K -> kein Brennwerteffekt!)
        t_vl = t_vl_ideal + 8 + np.random.normal(0, 0.5, n)
        t_rl = t_vl - np.random.uniform(1.8, 3.2, n) # Viel zu geringe Spreizung!
        t_ww = 58 + np.random.normal(0, 0.6, n)
        
    elif scenario == "Kesseltakten & Defekte Nachtabsenkung (Objekt Museumstraße 22)":
        # Starkes Schwingen alle 15-20 Minuten + keine Absenkung nachts
        takt_signal = 9 * np.sin(2 * np.pi * np.arange(n) / 4) # Alle 20 Min ein Peak
        t_vl = 62 + takt_signal + np.random.normal(0, 0.8, n)
        t_rl = 46 + 0.5 * takt_signal + np.random.normal(0, 0.6, n)
        t_ww = 57 + np.random.normal(0, 0.5, n)
        
    elif scenario == "Legionellen-Risiko / Speicherfehler (Objekt Höttinger Au 8)":
        # Normale Heizung, aber Warmwasser fällt dauerhaft unter 50°C (ÖNORM B 5019 Verstoß)
        t_vl = t_vl_ideal + np.random.normal(0, 0.5, n)
        t_rl = t_vl - 14 + np.random.normal(0, 0.5, n)
        t_ww = 46.5 - 2.5 * np.sin(2 * np.pi * (hours_float - 8) / 24) + np.random.normal(0, 0.4, n)
        
    else: # "Optimaler Betrieb (Objekt Rennweg 5)"
        # Nachtabsenkung zwischen 22:00 und 05:00 Uhr + saubere 15K Spreizung
        night_drop = np.where((hours_float >= 22) | (hours_float <= 5), -8.0, 0.0)
        t_vl = t_vl_ideal + night_drop + np.random.normal(0, 0.4, n)
        t_rl = t_vl - 15.0 + np.random.normal(0, 0.4, n)
        t_ww = 58.5 + np.random.normal(0, 0.4, n)

    df = pd.DataFrame({
        "Timestamp": timestamps,
        "Aussen_C": np.round(t_out, 1),
        "Vorlauf_C": np.round(t_vl, 1),
        "Ruecklauf_C": np.round(t_rl, 1),
        "Warmwasser_C": np.round(t_ww, 1)
    })
    df["Spreizung_K"] = np.round(df["Vorlauf_C"] - df["Ruecklauf_C"], 1)
    return df

# --- 2. AUTOMATISCHE HKLS-FEHLERDIAGNOSE ENGINE ---
def diagnose_system(df: pd.DataFrame):
    avg_dt = df["Spreizung_K"].mean()
    avg_rl = df["Ruecklauf_C"].mean()
    min_ww = df["Warmwasser_C"].min()
    avg_ww = df["Warmwasser_C"].mean()
    
    # Kesseltakten erkennen über Standardabweichung der Differenzen von Punkt zu Punkt
    vl_diffs = df["Vorlauf_C"].diff().abs()
    cycling_index = (vl_diffs > 6.0).sum() # Wie oft springt VL in 5 Min um mehr als 6K?

    issues = []
    loss_eur_month = 0
    ticket_text = ""

    # Check 1: Hydraulischer Kurzschluss / Brennwertverlust
    if avg_dt < 5.0:
        loss_eur_month += 380
        issues.append({
            "severity": "KRITISCH",
            "title": f"Hydraulischer Kurzschluss / Zu geringe Spreizung (Ø ΔT = {avg_dt:.1f} K)",
            "desc": f"Die Rücklauftemperatur liegt im Schnitt bei {avg_rl:.1f} °C (über dem Taupunkt von ~55 °C bei Erdgas). Der Brennwerteffekt fällt komplett aus, die Umwälzpumpe fördert ein massives Überströmen.",
            "action": "Überströmventil prüfen, Pumpenförderhöhe reduzieren und Strangregulierventile abgleichen."
        })
        ticket_text += f"- HYDRAULIK: Systemspreizung beträgt nur {avg_dt:.1f} K (Rücklauf Ø {avg_rl:.1f} °C). Bitte Überströmventil im Hauptverteiler und Differenzdruckregler prüfen.\n"

    # Check 2: Kesseltakten
    if cycling_index > 40:
        loss_eur_month += 290
        issues.append({
            "severity": "WARNUNG",
            "title": f"Starkes Kesseltakten & Fehlende Nachtabsenkung ({cycling_index} Brennerstarts in 72h)",
            "desc": "Der Wärmeerzeuger schaltet im 15-Minuten-Takt ein und aus. Zudem erfolgt zwischen 22:00 und 05:00 Uhr keine Vorlaufabsenkung. Hoher Verschleiß an Zündelektroden/Kompressor.",
            "action": "Brennerhysterese an der Regelung vergrößern, Mindestpausenzeit erhöhen und Zeitprogramm für Nachtabsenkung aktivieren."
        })
        ticket_text += f"- REGELUNG: Massives Takten ({cycling_index} Zyklen/72h) sowie fehlende Nachtabsenkung detektiert. Bitte Hysterese und Heizzeitenprogramm am Kesselregler korrigieren.\n"

    # Check 3: Legionellen / ÖNORM B 5019
    if avg_ww < 52.0 or min_ww < 48.0:
        loss_eur_month += 150
        issues.append({
            "severity": "HYGIENE-ALARM",
            "title": f"Akutes Legionellen-Risiko gemäß ÖNORM B 5019 (Warmwasser Ø {avg_ww:.1f} °C)",
            "desc": f"Die Warmwassertemperatur am Speicheraustritt unterschreitet dauerhaft die geforderten 55 °C (Minimum: {min_ww:.1f} °C). Haftungsrisiko für die Hausverwaltung!",
            "action": "Speicherladepumpe, 3-Wege-Umschaltventil und Temperaturfühler im Boiler prüfen."
        })
        ticket_text += f"- HYGIENE / ÖNORM B 5019: Warmwasser erreicht nur Ø {avg_ww:.1f} °C (Min: {min_ww:.1f} °C). Bitte Speicherladung und Zirkulationsstrang umgehend prüfen.\n"

    if not issues:
        issues.append({
            "severity": "OK",
            "title": "Anlage läuft im energetischen Optimum",
            "desc": f"Spreizung stabil bei Ø {avg_dt:.1f} K, Nachtabsenkung aktiv, Warmwasserhygiene (> 55 °C) durchgehend gewährleistet.",
            "action": "Kein Eingriff erforderlich."
        })

    return issues, loss_eur_month, ticket_text

# --- SIDEBAR: OBJEKTAUSWAHL & LIVE-PITCH-SIMULATOR ---
st.sidebar.title("🏢 HeatPulse AI")
st.sidebar.caption("Plug-&-Play Heizkeller-Intelligenz für Hausverwaltungen")

portfolio_locations = [
    {
        "scenario": "Hydraulischer Kurzschluss (Objekt Anichstraße 14)",
        "building": "Anichstraße 14",
        "latitude": 47.2654,
        "longitude": 11.3927,
    },
    {
        "scenario": "Kesseltakten & Defekte Nachtabsenkung (Objekt Museumstraße 22)",
        "building": "Museumstraße 22",
        "latitude": 47.2672,
        "longitude": 11.3975,
    },
    {
        "scenario": "Legionellen-Risiko / Speicherfehler (Objekt Höttinger Au 8)",
        "building": "Höttinger Au 8",
        "latitude": 47.2685,
        "longitude": 11.3812,
    },
    {
        "scenario": "Optimaler Betrieb (Objekt Rennweg 5)",
        "building": "Rennweg 5",
        "latitude": 47.2705,
        "longitude": 11.3955,
    },
]

demo_optimal_locations = [
    ("Demoanlage 01 · Optimal", 47.2742, 11.3881),
    ("Demoanlage 02 · Optimal", 47.2729, 11.4052),
    ("Demoanlage 03 · Optimal", 47.2692, 11.4108),
    ("Demoanlage 04 · Optimal", 47.2608, 11.4026),
    ("Demoanlage 05 · Optimal", 47.2587, 11.3914),
    ("Demoanlage 06 · Optimal", 47.2619, 11.3785),
    ("Demoanlage 07 · Optimal", 47.2714, 11.3738),
    ("Demoanlage 08 · Optimal", 47.2761, 11.3984),
]
portfolio_locations.extend(
    {
        "scenario": f"Optimaler Betrieb ({name})",
        "building": name,
        "latitude": latitude,
        "longitude": longitude,
    }
    for name, latitude, longitude in demo_optimal_locations
)

selected_location = st.sidebar.selectbox(
    "Liegenschaft auswählen:",
    portfolio_locations,
    format_func=lambda location: location["building"],
)
selected_building = selected_location["scenario"]

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Live-Sensor-Demo (Pitch-Modus)")
live_mode = st.sidebar.toggle("ESP32 Live-Eingriff simulieren", value=False)

df = generate_hvac_data(selected_building)

if live_mode:
    st.sidebar.info("Simuliere Echtzeit-Werte vom ESP32-Sensor am Rohr:")
    sim_vl = st.sidebar.slider("Vorlauftemperatur Sensor (°C)", 30.0, 85.0, 68.0, 0.5)
    sim_rl = st.sidebar.slider("Rücklauftemperatur Sensor (°C)", 25.0, 80.0, 66.0, 0.5)
    sim_ww = st.sidebar.slider("Warmwasser Sensor (°C)", 35.0, 70.0, 58.0, 0.5)
    
    # Überschreibe die letzten 12 Datenpunkte (letzte Stunde) mit den Live-Werten für sofortigen Effekt
    df.loc[df.index[-12:], "Vorlauf_C"] = sim_vl
    df.loc[df.index[-12:], "Ruecklauf_C"] = sim_rl
    df.loc[df.index[-12:], "Warmwasser_C"] = sim_ww
    df.loc[df.index[-12:], "Spreizung_K"] = round(sim_vl - sim_rl, 1)

# Diagnose ausführen
issues, loss_eur, ticket_body = diagnose_system(df.tail(36 if live_mode else len(df)))

status_style = {
    "KRITISCH": ("Kritisch", [239, 68, 68]),
    "HYGIENE-ALARM": ("Hygiene-Alarm", [239, 68, 68]),
    "WARNUNG": ("Warnung", [249, 115, 22]),
    "OK": ("Optimal", [34, 197, 94]),
}
portfolio_rows = []
for location in portfolio_locations:
    portfolio_data = generate_hvac_data(location["scenario"])
    portfolio_issues, portfolio_loss, _ = diagnose_system(portfolio_data)
    issue_severity = max(
        (issue["severity"] for issue in portfolio_issues),
        key=lambda severity: {
            "KRITISCH": 4,
            "HYGIENE-ALARM": 3,
            "WARNUNG": 2,
            "OK": 1,
        }.get(severity, 0),
    )
    status_label, marker_color = status_style[issue_severity]
    portfolio_rows.append({
        "Objekt": location["building"],
        "Adresse": f"{location['building']}, Innsbruck",
        "Status": status_label,
        "Verlust / Monat (€)": portfolio_loss,
        "Verlust": f"€ {portfolio_loss:,} / Monat",
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "color_r": marker_color[0],
        "color_g": marker_color[1],
        "color_b": marker_color[2],
    })
portfolio_df = pd.DataFrame(portfolio_rows)

# --- HAUPTBEREICH: HEADER & KPI CARDS ---
building_name = selected_location["building"]
st.markdown(
    f"""
    <div class="dashboard-header">
        <div>
            <div class="dashboard-eyebrow">HEATPULSE AI · ANLAGENÜBERSICHT</div>
            <h1>Heizhaus-Monitor</h1>
            <p class="dashboard-building">{building_name}</p>
        </div>
        <div class="gateway-status">
            <span class="gateway-dot"></span>
            <span>Gateway online</span>
            <span>· LTE-M -74 dBm</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(f"Letztes Datenpaket · {df['Timestamp'].iloc[-1].strftime('%H:%M:%S')} Uhr")

col1, col2, col3, col4, col5 = st.columns(5)
latest = df.iloc[-1]

col1.metric("Vorlauf (T_VL)", f"{latest['Vorlauf_C']} °C", f"{latest['Vorlauf_C'] - df['Vorlauf_C'].iloc[-15]:.1f} °C (1h)")
col2.metric("Rücklauf (T_RL)", f"{latest['Ruecklauf_C']} °C", f"{latest['Ruecklauf_C'] - df['Ruecklauf_C'].iloc[-15]:.1f} °C (1h)", delta_color="inverse")
col3.metric("Spreizung (ΔT)", f"{latest['Spreizung_K']} K", "Ziel: 12-15 K" if latest['Spreizung_K'] < 8 else "Optimal", delta_color="normal" if latest['Spreizung_K'] >= 10 else "inverse")
col4.metric("Warmwasser (T_WW)", f"{latest['Warmwasser_C']} °C", "ÖNORM B 5019 OK" if latest['Warmwasser_C'] >= 55 else "Unter 55 °C!", delta_color="normal" if latest['Warmwasser_C'] >= 55 else "inverse")
col5.metric("Erkannter Mehrverbrauch", f"€ {loss_eur} / Monat", f"€ {loss_eur * 6} / Heizsaison" if loss_eur > 0 else "0 € Verlust", delta_color="inverse")

# --- DETAILANSICHTEN ---
portfolio_tab, diagnosis_tab, telemetry_tab = st.tabs([
    "🗺️ Portfolio-Leitstelle Innsbruck",
    "🚨 KI-Diagnose & Wartungs-Ticket",
    "📈 Live-Telemetrie & Hydraulik",
])

with diagnosis_tab:
    left_col, right_col = st.columns([1.5, 1], gap="large")

    with left_col:
        st.subheader("Automatische HKLS-Anlagendiagnose")
        st.markdown(
            '<p class="section-kicker">Erkannte Abweichungen und empfohlene Maßnahmen</p>',
            unsafe_allow_html=True,
        )
        for issue in issues:
            message = (
                f"**[{issue['severity']}] {issue['title']}**\n\n"
                f"{issue['desc']}\n\n"
                f"👉 **Empfohlene Maßnahme:** {issue['action']}"
            )
            if issue["severity"] in {"KRITISCH", "HYGIENE-ALARM"}:
                st.error(message)
            elif issue["severity"] == "WARNUNG":
                st.warning(message)
            else:
                st.success(message)

    with right_col:
        st.subheader("1-Click Installateur-Ticket")
        st.markdown(
            '<p class="section-kicker">Auftragsentwurf direkt aus der Diagnose</p>',
            unsafe_allow_html=True,
        )
        if loss_eur > 0:
            default_ticket = (
                f"An: Kundendienst HKLS-Partnerbetrieb\n"
                f"Objekt: {building_name}, 6020 Innsbruck\n\n"
                f"Automatische Störungsmeldung durch HeatPulse-Sensorik:\n"
                f"{ticket_body}\n"
                f"Geschätzter Energieverlust aktuell: ca. {loss_eur} EUR/Monat.\n"
                f"Bitte um Terminvorschlag zur Behebung."
            )
            st.text_area(
                "Fertiger Auftragsentwurf für die Hausverwaltung:",
                value=default_ticket,
                height=180,
            )
            if st.button(
                "🚀 Auftrag direkt an Installateur senden",
                width="stretch",
                type="primary",
            ):
                st.toast(
                    "Auftrag erfolgreich samt Temperaturprotokoll an HKLS-Partner versendet!",
                    icon="✅",
                )
        else:
            st.info("Kein Wartungsticket erforderlich. Anlage arbeitet innerhalb aller Grenzwerte.")

        st.markdown("#### Amortisations-Benchmark")
        investment_cost = st.number_input(
            "Geschätzte Maßnahmenkosten (€)",
            min_value=0,
            step=250,
            value=0,
            key="investment_cost",
        )
        st.metric("Einsparpotenzial pro Heizsaison", f"€ {loss_eur * 6:,}")
        if investment_cost > 0 and loss_eur > 0:
            st.caption(
                f"Geschätzte Amortisation: "
                f"{investment_cost / loss_eur:.1f} Monate bei € {loss_eur:,} "
                "Einsparpotenzial pro Monat."
            )
        elif loss_eur > 0:
            st.caption("Maßnahmenkosten eintragen, um die Amortisationszeit zu schätzen.")
        else:
            st.caption("Bei aktuellem Anlagenstatus ist kein Einsparpotenzial diagnostiziert.")

with telemetry_tab:
    st.subheader("Thermodynamischer Zeitverlauf")
    st.markdown(
        '<p class="section-kicker">Vorlauf, Rücklauf, Warmwasser und Systemspreizung · letzte 72 Stunden</p>',
        unsafe_allow_html=True,
    )

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.7, 0.3],
        subplot_titles=(
            "Systemtemperaturen (Vorlauf, Rücklauf, Warmwasser)",
            "Systemspreizung ΔT (K) & Außentemperatur (°C)",
        ),
    )

    # Obere Grafik: VL, RL, WW
    fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["Vorlauf_C"], name="Vorlauf (T_VL)", line=dict(color="#FF4B4B", width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["Ruecklauf_C"], name="Rücklauf (T_RL)", line=dict(color="#3B82F6", width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["Warmwasser_C"], name="Warmwasser (T_WW)", line=dict(color="#F59E0B", width=2, dash="dot")), row=1, col=1)

    fig.add_hline(
        y=55,
        line_dash="dash",
        line_color="#64748b",
        annotation_text="55°C Referenz",
        row=1,
        col=1,
    )

    # Untere Grafik: Spreizung & Außentemperatur
    fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["Spreizung_K"], name="Spreizung ΔT (K)", fill="tozeroy", line=dict(color="#10B981", width=1.5)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["Aussen_C"], name="Außentemp. (°C)", line=dict(color="#9CA3AF", width=1.5)), row=2, col=1)

    fig.update_layout(
        height=550,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=55, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(color="#cbd5e1"),
    )
    fig.update_xaxes(gridcolor="rgba(148, 163, 184, 0.12)", zerolinecolor="rgba(148, 163, 184, 0.12)")
    fig.update_yaxes(gridcolor="rgba(148, 163, 184, 0.12)", zerolinecolor="rgba(148, 163, 184, 0.12)")
    st.plotly_chart(fig, width="stretch")

with portfolio_tab:
    st.subheader("Portfolio-Leitstelle Innsbruck")
    st.markdown(
        f"""
        <p class="section-kicker">
            {len(portfolio_df)} Anlagen · {len(demo_optimal_locations)} simulierte Demoanlagen mit optimalem Profil.
            Marker und Gebäudestatus sind farblich codiert.
        </p>
        <div style="display:flex;flex-wrap:wrap;gap:0.65rem;margin:0.4rem 0 1rem;">
            <span style="display:inline-flex;align-items:center;gap:0.45rem;padding:0.4rem 0.7rem;border:1px solid rgba(239,68,68,.3);border-radius:999px;background:rgba(239,68,68,.1);color:#fecaca;font-size:.82rem;">
                <span style="width:.55rem;height:.55rem;border-radius:50%;background:#ef4444;"></span>
                Rot · Kritisch / Hygiene-Alarm
            </span>
            <span style="display:inline-flex;align-items:center;gap:0.45rem;padding:0.4rem 0.7rem;border:1px solid rgba(249,115,22,.3);border-radius:999px;background:rgba(249,115,22,.1);color:#fed7aa;font-size:.82rem;">
                <span style="width:.55rem;height:.55rem;border-radius:50%;background:#f97316;"></span>
                Orange · Warnung
            </span>
            <span style="display:inline-flex;align-items:center;gap:0.45rem;padding:0.4rem 0.7rem;border:1px solid rgba(34,197,94,.3);border-radius:999px;background:rgba(34,197,94,.1);color:#bbf7d0;font-size:.82rem;">
                <span style="width:.55rem;height:.55rem;border-radius:50%;background:#22c55e;"></span>
                Grün · Optimal
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    map_col, table_col = st.columns([1.1, 1], gap="large")

    with map_col:
        import pydeck as pdk

        marker_layer = pdk.Layer(
            "ScatterplotLayer",
            data=portfolio_df,
            get_position="[longitude, latitude]",
            get_fill_color="[color_r, color_g, color_b, 220]",
            get_line_color="[255, 255, 255, 180]",
            get_radius=100,
            radius_min_pixels=8,
            radius_max_pixels=18,
            line_width_min_pixels=1,
            stroked=True,
            pickable=True,
        )
        portfolio_map = pdk.Deck(
            layers=[marker_layer],
            initial_view_state=pdk.ViewState(
                latitude=47.2675,
                longitude=11.3915,
                zoom=12.5,
                pitch=0,
            ),
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
            tooltip={
                "html": (
                    "<b>{Objekt}</b><br/>"
                    "{Adresse}<br/>"
                    "Status: {Status}<br/>"
                    "Verlust: {Verlust}"
                ),
                "style": {
                    "backgroundColor": "#161824",
                    "color": "#f8fafc",
                    "border": "1px solid #2e3248",
                },
            },
        )
        st.pydeck_chart(portfolio_map, width="stretch", height=430)

    with table_col:
        st.markdown("#### Objektübersicht")
        st.dataframe(
            portfolio_df[["Objekt", "Status", "Verlust / Monat (€)"]],
            hide_index=True,
            width="stretch",
            column_config={
                "Objekt": st.column_config.TextColumn("Liegenschaft"),
                "Status": st.column_config.TextColumn("Anlagenstatus"),
                "Verlust / Monat (€)": st.column_config.NumberColumn(
                    "Verlust / Monat",
                    format="€ %d",
                ),
            },
        )
        st.metric(
            "Portfolio-Verlust pro Monat",
            f"€ {int(portfolio_df['Verlust / Monat (€)'].sum()):,}",
        )