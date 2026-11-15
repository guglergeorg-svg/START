import streamlit as st
import pandas as pd
import numpy as np
import httpx
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

from google import genai
from google.genai import types
from postgrest.exceptions import APIError
from site_pages import render_site_footer
from supabase import Client, create_client

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .stApp {
        background: #0b1120;
        color: #e5e7eb;
    }

    #MainMenu,
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

    [class*="st-key-diagnostic_alert_kritisch_"] [data-testid="stAlert"],
    [class*="st-key-diagnostic_alert_kritisch_"] [data-testid="stAlert"] > div,
    [class*="st-key-diagnostic_alert_hygiene_alarm_"] [data-testid="stAlert"],
    [class*="st-key-diagnostic_alert_hygiene_alarm_"] [data-testid="stAlert"] > div {
        background-color: #991b1b !important;
        border-color: #7f1d1d !important;
    }

    [class*="st-key-diagnostic_alert_kritisch_"] [data-testid="stAlert"] *,
    [class*="st-key-diagnostic_alert_hygiene_alarm_"] [data-testid="stAlert"] * {
        color: #fff !important;
    }

    [class*="st-key-diagnostic_alert_kritisch_"] [data-testid="stAlert"] svg,
    [class*="st-key-diagnostic_alert_hygiene_alarm_"] [data-testid="stAlert"] svg {
        fill: #fff !important;
        stroke: #fff !important;
    }

    [class*="st-key-diagnostic_alert_warnung_"] [data-testid="stAlert"],
    [class*="st-key-diagnostic_alert_warnung_"] [data-testid="stAlert"] > div {
        background-color: #fffbeb !important;
        border-color: #fcd34d !important;
    }

    [class*="st-key-diagnostic_alert_warnung_"] [data-testid="stAlert"] * {
        color: #78350f !important;
    }

    [class*="st-key-diagnostic_alert_warnung_"] [data-testid="stAlert"] svg {
        fill: #b45309 !important;
        stroke: #b45309 !important;
    }

    [class*="st-key-diagnostic_alert_ok_"] [data-testid="stAlert"],
    [class*="st-key-diagnostic_alert_ok_"] [data-testid="stAlert"] > div {
        background-color: #ecfdf5 !important;
        border-color: #86efac !important;
    }

    [class*="st-key-diagnostic_alert_ok_"] [data-testid="stAlert"] * {
        color: #14532d !important;
    }

    [class*="st-key-diagnostic_alert_ok_"] [data-testid="stAlert"] svg {
        fill: #15803d !important;
        stroke: #15803d !important;
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

    [data-testid="stTabs"] [role="tablist"] {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.7rem;
        border-bottom: 0;
    }

    [data-testid="stTabs"] [role="tab"] {
        min-height: 3.5rem;
        justify-content: center;
        padding: 0.8rem 1rem;
        color: #365247;
        background: #fff;
        border: 1px solid #d7e1d9;
        border-radius: 14px;
        font-size: 0.95rem;
        font-weight: 700;
        text-align: center;
        white-space: normal;
        transition: background 120ms ease, border-color 120ms ease, transform 120ms ease;
    }

    [data-testid="stTabs"] [role="tab"]:hover {
        background: #edf7f0;
        border-color: #84b69a;
        transform: translateY(-1px);
    }

    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: #fff;
        background: #187b63;
        border-color: #187b63;
    }

    [data-testid="stTabs"] [role="tab"]:focus-visible {
        outline: 3px solid #a35400;
        outline-offset: 3px;
    }

    [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        display: none;
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

    @media (max-width: 768px) {
        .block-container {
            padding: 0.35rem 0.45rem 1.25rem;
        }

        h1 {
            font-size: clamp(1.35rem, 6vw, 1.8rem);
            line-height: 1.15;
            overflow-wrap: anywhere;
        }

        h2 {
            margin-top: 1rem;
            font-size: clamp(1.05rem, 4.8vw, 1.4rem);
            line-height: 1.25;
            overflow-wrap: anywhere;
        }

        h3 {
            font-size: clamp(0.98rem, 4.2vw, 1.2rem);
            line-height: 1.3;
            overflow-wrap: anywhere;
        }

        [data-testid="stHorizontalBlock"] {
            flex-direction: column;
            gap: 0.75rem;
        }

        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            width: 100% !important;
            min-width: 0;
            flex: 1 1 100% !important;
        }

        .st-key-kpi_grid [data-testid="stHorizontalBlock"] {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.55rem;
        }

        .st-key-kpi_grid [data-testid="column"] {
            width: 100% !important;
            min-width: 0;
            flex: initial !important;
        }

        [data-testid="stMetric"] {
            min-height: 88px;
            padding: 0.7rem 0.65rem;
            border-radius: 10px;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.72rem;
            line-height: 1.2;
        }

        [data-testid="stMetricValue"] {
            font-size: clamp(0.95rem, 4.2vw, 1.25rem);
            overflow-wrap: anywhere;
        }

        [data-testid="stTabs"] [role="tablist"] {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        [data-testid="stTabs"] [role="tab"] {
            min-width: 0;
            padding: 0.7rem 0.45rem;
            font-size: 0.82rem;
        }

        [data-testid="stPlotlyChart"],
        [data-testid="stPydeckChart"] {
            width: 100%;
            max-width: 100%;
        }

        [data-testid="stSidebar"] [data-testid="stSelectbox"],
        [data-testid="stSidebar"] [data-testid="stSlider"],
        [data-testid="stSidebar"] [data-testid="stToggle"] {
            width: 100%;
        }

        [data-testid="stTextArea"] textarea {
            font-size: 0.85rem;
        }

        .dashboard-header {
            align-items: flex-start;
            flex-direction: column;
            gap: 0.85rem;
            padding: 1rem;
            margin: 0.2rem 0 0.8rem;
        }

        .gateway-status {
            white-space: normal;
            flex-wrap: wrap;
            font-size: 0.78rem;
            padding: 0.55rem 0.75rem;
        }
    }

        :root {
            color-scheme: light;
            --ink: #172a27;
            --muted: #586a61;
            --line: #e4eae5;
            --paper: #f4f7f3;
            --green: #187b63;
        }

        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background: var(--paper);
            color: var(--ink);
            font-family: Inter, "Segoe UI", sans-serif;
        }

        .block-container {
            max-width: 1540px;
            padding: 1.45rem clamp(1rem, 3vw, 2.8rem) 3rem;
        }

        section[data-testid="stSidebar"] {
            background: #edf2ed;
            border-right: 1px solid #dfe7df;
        }

        section[data-testid="stSidebar"] > div {
            padding: 1.8rem 1.15rem 2rem;
        }

        section[data-testid="stSidebar"] [data-testid="stSelectbox"] {
            margin-bottom: 1.2rem;
        }

        section[data-testid="stSidebar"] hr {
            margin: 1.35rem 0;
            border-color: #dfe7df;
        }

        section[data-testid="stSidebar"] [data-testid="stToggle"] {
            margin-top: .65rem;
        }

        .st-key-mobile_location_picker {
            display: none;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: var(--ink);
        }

        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stCaptionContainer"] {
            color: var(--muted);
        }

        section[data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: #fff !important;
            border-color: #d7e1d9 !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="select"] *,
        section[data-testid="stSidebar"] [data-testid="stSlider"] *,
        section[data-testid="stSidebar"] [data-testid="stToggle"] * {
            color: var(--ink);
        }

        h1, h2, h3, h4 {
            color: var(--ink);
            letter-spacing: -0.035em;
        }

        main h1,
        main h2,
        main h3,
        main h4 {
            text-align: center;
        }

        h2 {
            margin-top: 1.8rem;
            font-size: 1.45rem;
        }

        h3 {
            font-size: 1.15rem;
        }

        .hero {
            position: relative;
            display: flex;
            min-height: 238px;
            align-items: center;
            justify-content: space-between;
            gap: 2rem;
            overflow: hidden;
            padding: clamp(1.5rem, 4vw, 3rem);
            margin: 0.3rem 0 1.2rem;
            color: #effaf3;
            background:
                radial-gradient(ellipse at 83% 45%, rgba(52, 211, 153, .2), transparent 34%),
                linear-gradient(112deg, #102d2a 0%, #163e37 54%, #155443 100%);
            border: 1px solid rgba(255, 255, 255, .1);
            border-radius: 24px;
            box-shadow: 0 22px 55px rgba(27, 68, 54, .14);
            isolation: isolate;
        }

        .hero::after {
            position: absolute;
            z-index: -1;
            inset: 0;
            content: "";
            opacity: .16;
            background-image: radial-gradient(rgba(220, 252, 231, .6) .7px, transparent .7px);
            background-size: 20px 20px;
            mask-image: linear-gradient(90deg, transparent 30%, #000 100%);
        }

        .hero-copy {
            position: relative;
            z-index: 1;
            max-width: 620px;
            text-align: center;
        }

        .hero-eyebrow {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: .55rem;
            margin-bottom: 1rem;
            color: #a7d9c2;
            font-size: .72rem;
            font-weight: 750;
            letter-spacing: .16em;
            text-transform: uppercase;
        }

        .hero-mark {
            display: grid;
            width: 1.65rem;
            height: 1.65rem;
            place-items: center;
            color: #b6f2d1;
            background: rgba(136, 220, 177, .12);
            border: 1px solid rgba(169, 236, 195, .25);
            border-radius: 8px;
            font-size: .9rem;
        }

        .hero h1 {
            margin: 0;
            color: #f5fbf7;
            font-size: clamp(2.05rem, 4vw, 3.25rem);
            font-weight: 620;
            letter-spacing: -.06em;
            line-height: 1.02;
        }

        .hero-building {
            margin: 1rem 0 0;
            color: #c2d8ce;
            font-size: 1rem;
        }

        .hero-building strong {
            color: #fff;
            font-weight: 620;
        }

        .hero-meta {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: .65rem;
            margin-top: 1.35rem;
            color: #afc8bb;
            font-size: .8rem;
        }

        .gateway-status {
            display: inline-flex;
            align-items: center;
            gap: .55rem;
            padding: .48rem .78rem;
            color: #c9f8dd;
            font-size: .76rem;
            font-weight: 650;
            background: rgba(125, 211, 158, .1);
            border: 1px solid rgba(157, 231, 183, .2);
            border-radius: 999px;
        }

        .gateway-dot {
            position: relative;
            width: .48rem;
            height: .48rem;
            background: #72e0a6;
            border-radius: 50%;
            box-shadow: 0 0 13px rgba(114, 224, 166, .8);
            animation: status-glow 2.4s ease-in-out infinite;
        }

        .hero-art {
            width: min(39%, 390px);
            min-width: 220px;
            height: auto;
            overflow: visible;
            opacity: .95;
        }

        .flow-line {
            fill: none;
            stroke-dasharray: 9 13;
            animation: flow 5s linear infinite;
        }

        .flow-line--slow {
            animation-duration: 8s;
            animation-direction: reverse;
        }

        .orbit {
            transform-origin: 180px 110px;
            animation: orbit 18s linear infinite;
        }

        @keyframes flow {
            to { stroke-dashoffset: -88; }
        }

        @keyframes orbit {
            to { transform: rotate(360deg); }
        }

        @keyframes status-glow {
            50% { box-shadow: 0 0 4px rgba(114, 224, 166, .45); }
        }

        [data-testid="stMetric"] {
            min-height: 132px;
            padding: 1.2rem 1.25rem;
            text-align: center;
            background: #fff;
            border: 1px solid var(--line);
            border-radius: 16px;
            box-shadow: 0 5px 18px rgba(32, 57, 43, .035);
            transition: transform 180ms ease, box-shadow 180ms ease;
        }

        [data-testid="stMetric"] > div {
            align-items: center;
        }

        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 28px rgba(32, 57, 43, .08);
        }

        [data-testid="stMetricLabel"] {
            color: var(--muted);
            font-size: .78rem;
            font-weight: 600;
        }

        [data-testid="stMetricValue"] {
            color: var(--ink);
            font-size: clamp(.9rem, 1.35vw, 1.35rem);
            font-weight: 680;
            letter-spacing: -.045em;
            line-height: 1.2;
            overflow-wrap: anywhere;
            white-space: normal;
        }

        [data-testid="stMetricLabel"] {
            font-size: .72rem;
            line-height: 1.25;
            overflow-wrap: anywhere;
            white-space: normal;
        }

        [data-testid="stMetricDelta"] {
            font-size: .74rem;
        }

        [data-testid="stLayoutWrapper"]:has(> .st-key-dashboard_intro) {
            position: sticky;
            top: 0;
            z-index: 0;
        }

        [data-testid="stTabs"] {
            position: relative;
            z-index: 1;
            margin-top: 1.4rem;
            background: var(--paper);
        }

        [data-testid="stTabs"] [role="tabpanel"] {
            padding-top: 1.25rem;
        }

        [data-testid="stTabs"] [role="tablist"] {
            gap: .55rem;
            border-bottom: 1px solid #e1e8e2;
        }

        [data-testid="stTabs"] [role="tab"] {
            min-height: 3rem;
            color: #687871;
            font-size: .87rem;
        }

        [data-testid="stTabs"] button[aria-selected="true"] {
            color: #176e59;
            border-bottom: 2px solid #24846a;
        }

        [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
            background-color: #24846a !important;
        }

        [data-testid="stAlert"] {
            border: 1px solid rgba(120, 140, 128, .18);
            border-radius: 14px;
            box-shadow: 0 3px 12px rgba(32, 57, 43, .035);
        }

        [data-testid="stPlotlyChart"],
        [data-testid="stPydeckChart"] {
            overflow: hidden;
            border: 1px solid var(--line);
            border-radius: 18px;
            box-shadow: 0 8px 26px rgba(32, 57, 43, .05);
        }

        [data-testid="stPlotlyChart"] {
            background: #fff;
        }

        [data-testid="stAlert"] {
            background: #fff;
        }

        [data-testid="stAlert"] [data-testid="stMarkdownContainer"],
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
            color: var(--ink);
        }

        .st-key-portfolio_loss_metric [data-testid="stMetricValue"] {
            font-size: clamp(1.6rem, 2.1vw, 2rem);
            font-weight: 760;
        }

        [data-testid="stPydeckChart"] {
            width: 100% !important;
            max-width: 100%;
            border-radius: 12px;
            background: #fff;
        }

        [data-baseweb="select"] > div,
        [data-testid="stTextArea"] textarea,
        [data-testid="stNumberInput"] input {
            background: #fff;
            border-color: #dce5de;
            border-radius: 10px;
        }

        [data-testid="stTextArea"] textarea,
        [data-testid="stNumberInput"] input {
            color: var(--ink);
        }

        [data-testid="stRadio"] label {
            color: var(--ink);
        }

        .stButton button {
            min-height: 2.8rem;
            border-radius: 10px;
            font-weight: 650;
            transition: transform 160ms ease, box-shadow 160ms ease;
        }

        .stButton button[kind="primary"] {
            background: #187b63;
            border-color: #187b63;
        }

        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 7px 16px rgba(24, 123, 99, .14);
        }

        :focus-visible {
            outline: 3px solid #a35400 !important;
            outline-offset: 3px !important;
            box-shadow: 0 0 0 2px #fff !important;
        }

        .site-footer a {
            color: #155e4b;
            text-decoration-thickness: 1px;
            text-underline-offset: 3px;
        }

        .site-footer a:hover {
            color: #0e4537;
        }

        .site-footer {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: .8rem 1.5rem;
            padding: 1.2rem 0 .4rem;
            margin-top: 2rem;
            color: #53635c;
            border-top: 1px solid #dfe7df;
            font-size: .82rem;
        }

        .site-footer nav {
            display: flex;
            flex-wrap: wrap;
            gap: 1.2rem;
        }

        .section-kicker {
            margin: .25rem 0 1.1rem;
            color: var(--muted);
            font-size: .86rem;
            text-align: center;
        }

        hr {
            border-color: #dfe7df;
        }

        @media (max-width: 900px) {
            .hero {
                min-height: 210px;
                padding: 1.6rem;
            }

            .hero-art {
                width: 34%;
                min-width: 175px;
                margin-right: -1rem;
            }
        }

        @media (max-width: 600px) {
            .block-container {
                padding: .7rem .75rem 1.5rem;
            }

            .hero {
                min-height: 0;
                padding: 1.35rem;
                border-radius: 18px;
            }

            .hero-art {
                display: none;
            }

            .hero h1 {
                font-size: 2.2rem;
            }

            .hero-meta {
                flex-wrap: wrap;
            }

            [data-testid="stMetric"] {
                min-height: 94px;
                padding: .75rem;
                border-radius: 12px;
            }

            [data-testid="stMetricLabel"] {
                font-size: .68rem;
            }
        }

        @media (max-width: 768px) {
            .st-key-mobile_location_picker {
                display: block;
                position: relative;
                z-index: 2;
                margin-bottom: .85rem;
                padding: .7rem .8rem .35rem;
                background: #fff;
                border: 1px solid #dfe7df;
                border-radius: 14px;
            }

            .st-key-mobile_location_picker [data-testid="stSelectbox"] {
                width: 100%;
                margin: 0;
            }

            .st-key-mobile_location_picker [data-baseweb="select"] > div {
                min-height: 48px;
                border-radius: 10px;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
                scroll-behavior: auto !important;
                animation-duration: .01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: .01ms !important;
            }
        }
        </style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_supabase_connection() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


@st.cache_data(ttl=60)
def load_prototype_measurements() -> pd.DataFrame:
    response = (
        init_supabase_connection()
        .table("vorlauf_messungen")
        .select("created_at,sensor_id,temperatur")
        .order("created_at", desc=True)
        .limit(1000)
        .execute()
    )
    measurements = pd.DataFrame(response.data)
    if measurements.empty:
        return pd.DataFrame(columns=["Timestamp", "sensor_id", "Temperatur_C"])

    required_columns = {"created_at", "sensor_id", "temperatur"}
    missing_columns = required_columns.difference(measurements.columns)
    if missing_columns:
        raise ValueError(
            "Die Supabase-Tabelle enthält nicht alle benötigten Spalten: "
            + ", ".join(sorted(missing_columns))
        )

    measurements["Timestamp"] = pd.to_datetime(
        measurements["created_at"],
        errors="coerce",
        utc=True,
    )
    measurements["sensor_id"] = measurements["sensor_id"].astype("string")
    measurements["Temperatur_C"] = pd.to_numeric(
        measurements["temperatur"],
        errors="coerce",
    )
    measurements = measurements.dropna(
        subset=["Timestamp", "sensor_id", "Temperatur_C"]
    )
    if measurements.empty:
        raise ValueError("Supabase enthält keine gültigen Temperaturmessungen.")

    return measurements[
        ["Timestamp", "sensor_id", "Temperatur_C"]
    ].sort_values("Timestamp")


@st.cache_data(ttl=3600)
def load_innsbruck_weather(start_date: str, end_date: str) -> pd.DataFrame:
    response = httpx.get(
        "https://archive-api.open-meteo.com/v1/archive",
        params={
            "latitude": 47.2692,
            "longitude": 11.4041,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": "temperature_2m",
            "timezone": "UTC",
        },
        timeout=20.0,
    )
    response.raise_for_status()
    payload = response.json()
    hourly = payload.get("hourly") if isinstance(payload, dict) else None
    if not isinstance(hourly, dict):
        raise ValueError("Open-Meteo hat keine stündlichen Wetterdaten geliefert.")

    timestamps = hourly.get("time")
    temperatures = hourly.get("temperature_2m")
    if (
        not isinstance(timestamps, list)
        or not isinstance(temperatures, list)
        or len(timestamps) != len(temperatures)
    ):
        raise ValueError("Die Open-Meteo-Wetterdaten haben ein ungültiges Format.")

    weather = pd.DataFrame({
        "Timestamp": pd.to_datetime(timestamps, errors="coerce", utc=True),
        "Aussen_C": pd.to_numeric(temperatures, errors="coerce"),
    }).dropna(subset=["Timestamp", "Aussen_C"])
    if weather.empty:
        raise ValueError("Open-Meteo hat keine gültigen Außentemperaturen geliefert.")

    return weather.sort_values("Timestamp")


def pair_prototype_sensor_readings(measurements: pd.DataFrame) -> pd.DataFrame:
    empty = pd.DataFrame(
        columns=["Vorlauf_C", "Ruecklauf_C", "Spreizung_K"],
        index=pd.DatetimeIndex([], name="Timestamp"),
    )
    sensor_ids = sorted(measurements["sensor_id"].dropna().unique())
    if len(sensor_ids) < 2:
        return empty

    vorlauf = (
        measurements.loc[
            measurements["sensor_id"] == sensor_ids[0],
            ["Timestamp", "Temperatur_C"],
        ]
        .rename(columns={"Temperatur_C": "Vorlauf_C"})
        .sort_values("Timestamp")
    )
    ruecklauf = (
        measurements.loc[
            measurements["sensor_id"] == sensor_ids[1],
            ["Timestamp", "Temperatur_C"],
        ]
        .rename(columns={"Temperatur_C": "Ruecklauf_C"})
        .sort_values("Timestamp")
    )
    paired = pd.merge_asof(
        vorlauf,
        ruecklauf,
        on="Timestamp",
        direction="nearest",
        tolerance=pd.Timedelta(seconds=3),
    ).dropna(subset=["Ruecklauf_C"])
    if paired.empty:
        return empty

    paired["Spreizung_K"] = paired["Vorlauf_C"] - paired["Ruecklauf_C"]
    return (
        paired.set_index("Timestamp")[
            ["Vorlauf_C", "Ruecklauf_C", "Spreizung_K"]
        ]
        .sort_index()
    )


def analyze_heating_chart(df: pd.DataFrame) -> str:
    if df.empty:
        raise ValueError("Es liegen keine Heizungsdaten für die Analyse vor.")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("Die Heizungsdaten benötigen einen Zeitstempel-Index.")

    api_key = st.secrets["GEMINI_API_KEY"]
    if not api_key:
        raise ValueError("Der Gemini-API-Key ist leer.")

    recent_data = df.sort_index().tail(60)
    csv_data = recent_data.to_csv(
        index=True,
        index_label="Timestamp",
        float_format="%.1f",
    )
    system_instruction = (
        "Du bist ein erfahrener HKLS-Ingenieur. Analysiere die Zeitreihen "
        "für Vorlauf und Rücklauf auf Takten des Wärmeerzeugers, eine zu "
        "geringe Spreizung (Delta T) sowie plötzliche Temperaturabfälle und "
        "mögliche Sensorstörungen. Nutze ausschließlich die bereitgestellten "
        "Messwerte und erfinde keine Ursachen oder Messwerte. Antworte kurz, "
        "strukturiert und auf Deutsch mit genau diesen Abschnitten: "
        "Status, Beobachtung, Ursache & Maßnahme. Wenn die Daten für eine "
        "belastbare Diagnose nicht ausreichen, sage das ausdrücklich."
    )
    if any("vorläufig" in str(column).lower() for column in recent_data.columns):
        system_instruction += (
            " WICHTIG: Die Vorlauf-/Rücklauf-Sensorzuordnung ist nur beliebig "
            "und vorläufig; die Fühler sind noch nicht angeschlossen. "
            "Kennzeichne alle daraus abgeleiteten Befunde einschließlich "
            "Delta T als nicht verifiziert und stelle keine reale Anlagenstörung fest."
        )

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=25000),
    )
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=f"Heizungsdaten als CSV:\n{csv_data}",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
        ),
    )

    if not response.text or not response.text.strip():
        raise ValueError("Gemini hat keine textuelle Diagnose zurückgegeben.")
    return response.text.strip()


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
st.sidebar.title("🏢 HeatTrace")
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
    ("Maximilianstraße 12", 47.2742, 11.3881),
    ("Maria-Theresien-Straße 18", 47.2729, 11.4052),
    ("Innstraße 31", 47.2692, 11.4108),
    ("Amraser Straße 24", 47.2608, 11.4026),
    ("Leopoldstraße 16", 47.2587, 11.3914),
    ("Höttinger Gasse 9", 47.2619, 11.3785),
    ("Andreas-Hofer-Straße 22", 47.2714, 11.3738),
    ("Haller Straße 35", 47.2761, 11.3984),
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

prototype_location = {
    "scenario": "Supabase-Messungen",
    "building": "Prototypen Anlage",
    "source": "supabase",
}
available_locations = portfolio_locations + [prototype_location]


def sync_location_selection(widget_key: str) -> None:
    selected_index = st.session_state[widget_key]
    st.session_state["selected_location_index"] = selected_index
    st.session_state["sidebar_location_index"] = selected_index
    st.session_state["mobile_location_index"] = selected_index


st.session_state.setdefault("selected_location_index", 0)
st.session_state.setdefault(
    "sidebar_location_index",
    st.session_state["selected_location_index"],
)
st.session_state.setdefault(
    "mobile_location_index",
    st.session_state["selected_location_index"],
)

st.sidebar.selectbox(
    "Liegenschaft auswählen:",
    options=range(len(available_locations)),
    format_func=lambda index: available_locations[index]["building"],
    key="sidebar_location_index",
    on_change=sync_location_selection,
    args=("sidebar_location_index",),
)
selected_location = available_locations[st.session_state["selected_location_index"]]
selected_building = selected_location["scenario"]
is_supabase_prototype = selected_location.get("source") == "supabase"

if is_supabase_prototype:
    live_mode = False
    st.sidebar.caption("Datenquelle: Supabase · gespeicherte Messungen")
    try:
        df = load_prototype_measurements()
    except (KeyError, APIError, httpx.HTTPError, ValueError) as error:
        st.error(f"Supabase-Messungen konnten nicht geladen werden: {error}")
        st.stop()
    if df.empty:
        st.error("In Supabase wurden noch keine Messungen für die Prototypen Anlage gefunden.")
        st.stop()
    latest_by_sensor = (
        df.groupby("sensor_id", as_index=False)
        .tail(1)
        .sort_values("sensor_id")
    )
    sensor_assignments = {}
    for sensor_index, sensor_id in enumerate(sorted(df["sensor_id"].unique())):
        if sensor_index == 0:
            sensor_label = "Vorlauf (vorläufig)"
        elif sensor_index == 1:
            sensor_label = "Rücklauf (vorläufig)"
        else:
            sensor_label = f"Zusatzsensor {sensor_id}"
        sensor_assignments[sensor_id] = sensor_label
    df["Messstelle"] = df["sensor_id"].map(sensor_assignments)
    latest_by_sensor["Messstelle"] = latest_by_sensor["sensor_id"].map(
        sensor_assignments
    )
    assignment_summary = "; ".join(
        f"{label}: Sensor {sensor_id}"
        for sensor_id, label in sensor_assignments.items()
    )
    issues = [{
        "severity": "WARNUNG",
        "title": "Vorlauf/Rücklauf-Zuordnung ist nur vorläufig",
        "desc": (
            f"{assignment_summary}. "
            "Die Zuordnung erfolgt beliebig nach Sensor-ID und ist nicht "
            "fachlich bestätigt. Da die Fühler noch nicht angeschlossen sind, "
            "werden keine HKLS-Grenzwerte oder Einsparungen diagnostiziert."
        ),
        "action": (
            "Nach dem Anschluss die Sensorzuordnung vor Ort prüfen und "
            "bestätigen, bevor automatische Anlagenalarme aktiviert werden."
        ),
    }]
    loss_eur = 0
    ticket_body = ""
else:
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

    issues, loss_eur, ticket_body = diagnose_system(
        df.tail(36 if live_mode else len(df))
    )

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

with st.container(key="mobile_location_picker"):
    st.selectbox(
        "Anlage wechseln",
        options=range(len(available_locations)),
        format_func=lambda index: available_locations[index]["building"],
        key="mobile_location_index",
        on_change=sync_location_selection,
        args=("mobile_location_index",),
    )

# --- DETAILANSICHTEN ---
portfolio_tab, details_tab, diagnosis_tab, telemetry_tab = st.tabs([
    "Portfolio-Leitstelle",
    "Anlagendetails",
    "KI-Diagnose",
    "Live-Telemetrie",
])

# --- ANLAGENDETAILS: HEADER & KPI CARDS ---
building_name = selected_location["building"]
latest_update = df["Timestamp"].iloc[-1].strftime("%d.%m.%Y %H:%M")
if is_supabase_prototype:
    connection_label = "Supabase-Daten geladen"
    connection_detail = f"{df['sensor_id'].nunique()} Sensoren"
    update_timezone = " UTC"
    update_label = "Letzte Messung"
else:
    connection_label = "Gateway online"
    connection_detail = "LTE-M · −74 dBm"
    update_timezone = ""
    update_label = "Aktualisiert"

with details_tab.container(key="dashboard_intro"):
    st.markdown(
        f"""
    <div class="hero">
        <div class="hero-copy">
            <div class="hero-eyebrow"><span class="hero-mark">✳</span> HEATTRACE <span>·</span> ENERGIE-MONITORING</div>
            <h1>Wärme im<br>Gleichgewicht.</h1>
            <p class="hero-building">Anlagenübersicht für <strong>{building_name}</strong></p>
            <div class="hero-meta">
                <span class="gateway-status"><span class="gateway-dot"></span> {connection_label}</span>
                <span>{connection_detail}</span>
                <span>·</span>
                <span>{update_label} {latest_update}{update_timezone}</span>
            </div>
        </div>
        <svg class="hero-art" viewBox="0 0 390 220" role="img" aria-label="Animierte Visualisierung des Heizkreislaufs">
            <defs>
                <linearGradient id="pipe" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#b9f4d0" stop-opacity=".85"/>
                    <stop offset="100%" stop-color="#50cba0" stop-opacity=".25"/>
                </linearGradient>
                <radialGradient id="core">
                    <stop offset="0%" stop-color="#bdf7d4" stop-opacity=".32"/>
                    <stop offset="100%" stop-color="#bdf7d4" stop-opacity="0"/>
                </radialGradient>
            </defs>
            <circle cx="180" cy="110" r="95" fill="url(#core)"/>
            <g fill="none" stroke="url(#pipe)" stroke-width="1.2" opacity=".7">
                <path d="M22 65h68a18 18 0 0 1 18 18v12a18 18 0 0 0 18 18h111a18 18 0 0 0 18-18V74a18 18 0 0 1 18-18h93"/>
                <path d="M22 152h43a18 18 0 0 0 18-18v-9a18 18 0 0 1 18-18h35a18 18 0 0 1 18 18v13a18 18 0 0 0 18 18h135a18 18 0 0 0 18-18v-9a18 18 0 0 1 18-18h25"/>
                <path d="M70 31v21a18 18 0 0 0 18 18h23m205 99v-24a18 18 0 0 0-18-18h-27"/>
            </g>
            <g fill="none" stroke="#d4ffe3" stroke-width="2.4" stroke-linecap="round">
                <path class="flow-line" d="M22 65h68a18 18 0 0 1 18 18v12a18 18 0 0 0 18 18h111a18 18 0 0 0 18-18V74a18 18 0 0 1 18-18h93"/>
                <path class="flow-line flow-line--slow" d="M22 152h43a18 18 0 0 0 18-18v-9a18 18 0 0 1 18-18h35a18 18 0 0 1 18 18v13a18 18 0 0 0 18 18h135a18 18 0 0 0 18-18v-9a18 18 0 0 1 18-18h25"/>
            </g>
            <g class="orbit" fill="none" stroke="#baf4d1" stroke-opacity=".38" stroke-width="1">
                <circle cx="180" cy="110" r="61" stroke-dasharray="2 7"/>
                <circle cx="180" cy="49" r="3" fill="#baf4d1" stroke="none"/>
            </g>
            <circle cx="180" cy="110" r="30" fill="#d3ffe2" fill-opacity=".08" stroke="#c6f7d8" stroke-opacity=".65"/>
            <path d="M183 87c-11 0-17 9-17 18 0 11 14 25 14 25s17-16 17-26c0-9-6-17-14-17Zm0 24a6 6 0 1 1 0-12 6 6 0 0 1 0 12Z" fill="#c6f7d8"/>
            <circle cx="93" cy="65" r="3" fill="#f3c984"/>
            <circle cx="318" cy="152" r="3" fill="#f3c984"/>
        </svg>
    </div>
    """,
        unsafe_allow_html=True,
    )

    with st.container(key="kpi_grid"):
        if is_supabase_prototype:
            prototype_metrics = [
                (row.Messstelle, f"{row.Temperatur_C:.1f} °C")
                for row in latest_by_sensor.itertuples(index=False)
            ]
            prototype_metrics.extend([
                ("Sensoren", str(df["sensor_id"].nunique())),
                ("Messpunkte", f"{len(df):,}"),
            ])
            metric_columns = st.columns(len(prototype_metrics))
            for column, (label, value) in zip(metric_columns, prototype_metrics):
                column.metric(label, value)
        else:
            latest = df.iloc[-1]
            col1, col2, col3, col4, col5 = st.columns(5)

            col1.metric("Vorlauf", f"{latest['Vorlauf_C']} °C", f"{latest['Vorlauf_C'] - df['Vorlauf_C'].iloc[-15]:.1f} °C (1h)")
            col2.metric("Rücklauf", f"{latest['Ruecklauf_C']} °C", f"{latest['Ruecklauf_C'] - df['Ruecklauf_C'].iloc[-15]:.1f} °C (1h)", delta_color="inverse")
            col3.metric("Spreizung", f"{latest['Spreizung_K']} K", "Ziel: 12-15 K" if latest['Spreizung_K'] < 8 else "Optimal", delta_color="normal" if latest['Spreizung_K'] >= 10 else "inverse")
            col4.metric("Warmwasser", f"{latest['Warmwasser_C']} °C", "Hygiene OK" if latest['Warmwasser_C'] >= 55 else "Zu niedrig!", delta_color="normal" if latest['Warmwasser_C'] >= 55 else "inverse")
            col5.metric("Mehrverbrauch", f"€ {loss_eur} / Mo.", f"6 Mon. €{loss_eur * 6:,}" if loss_eur > 0 else "Kein Verlust", delta_color="inverse")

    if is_supabase_prototype:
        st.subheader("Letzte Supabase-Messungen")
        recent_measurements = (
            df.sort_values("Timestamp", ascending=False)
            .head(20)
            .rename(columns={
                "Timestamp": "Zeitpunkt",
                "Messstelle": "Vorläufige Messstelle",
                "sensor_id": "Sensor-ID",
                "Temperatur_C": "Temperatur (°C)",
            })
        )
        st.dataframe(recent_measurements, width="stretch", hide_index=True)

with diagnosis_tab:
    left_col, right_col = st.columns([1.5, 1], gap="large")

    with left_col:
        st.header("Live-KI-Heizungsanalyse")
        st.markdown(
            '<p class="section-kicker">Analyse der aktuellen Vorlauf- und Rücklauf-Zeitreihen</p>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Beim Klick werden die letzten 60 Messpunkte an Google Gemini "
            "(gemini-3.8-flash) zur Analyse gesendet."
        )
        analysis_key = (
            f"heating_ai_analysis_{st.session_state['selected_location_index']}"
        )
        analysis_clicked = st.button(
            "🔍 Heizdiagramm mit KI analysieren",
            type="primary",
            width="stretch",
            key=f"analyze_heating_chart_{st.session_state['selected_location_index']}",
        )
        if analysis_clicked:
            st.session_state.pop(analysis_key, None)
            try:
                with st.spinner("Die aktuellen Heizungsdaten werden analysiert …"):
                    if is_supabase_prototype:
                        analysis_df = pair_prototype_sensor_readings(df)
                        if analysis_df.empty:
                            raise ValueError(
                                "Für Vorlauf und Rücklauf wurden keine zeitlich "
                                "passenden Sensorpaare gefunden."
                            )
                        analysis_df = analysis_df.rename(columns={
                            "Vorlauf_C": "Vorlauf_C (vorläufig)",
                            "Ruecklauf_C": "Ruecklauf_C (vorläufig)",
                            "Spreizung_K": "Spreizung_K (vorläufig)",
                        })
                    else:
                        analysis_df = df.set_index("Timestamp")[
                            [
                                "Vorlauf_C",
                                "Ruecklauf_C",
                                "Warmwasser_C",
                                "Spreizung_K",
                            ]
                        ]
                    st.session_state[analysis_key] = analyze_heating_chart(
                        analysis_df
                    )
            except Exception as error:
                st.error(f"Die KI-Analyse ist fehlgeschlagen: {error}")

        analysis_result = st.session_state.get(analysis_key)
        if analysis_result:
            st.markdown("#### Diagnoseergebnis")
            st.markdown(analysis_result)
        elif not analysis_clicked:
            st.info(
                "Klicken Sie auf „Heizdiagramm mit KI analysieren“, um die "
                "aktuellen Live-Sensordaten auszuwerten."
            )

    with right_col:
        st.header(
            "Datenzuordnung"
            if is_supabase_prototype
            else "Installateur-Ticket"
        )
        st.markdown(
            (
                '<p class="section-kicker">Benötigte Sensor-Metadaten</p>'
                if is_supabase_prototype
                else '<p class="section-kicker">Auftragsentwurf direkt aus der Diagnose</p>'
            ),
            unsafe_allow_html=True,
        )
        if is_supabase_prototype:
            st.info(
                f"Vorläufige Zuordnung: {assignment_summary}. "
                "Die Fühler sind noch nicht angeschlossen; die Bezeichnungen "
                "sind daher keine bestätigten Vorlauf-/Rücklaufmessungen. "
                "Automatische HKLS-Alarme bleiben deaktiviert."
            )
        elif loss_eur > 0:
            default_ticket = (
                f"An: Kundendienst HKLS-Partnerbetrieb\n"
                f"Objekt: {building_name}, 6020 Innsbruck\n\n"
                f"Automatische Störungsmeldung durch HeatTrace-Sensorik:\n"
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
                "Auftragstext im Demo-Modus prüfen",
                width="stretch",
                type="primary",
            ):
                st.toast(
                    "Demo: Der Entwurf wurde nicht an einen Installateur gesendet.",
                    icon="ℹ️",
                )
        else:
            st.info("Kein Wartungsticket erforderlich. Anlage arbeitet innerhalb aller Grenzwerte.")

        if not is_supabase_prototype:
            st.markdown("### Amortisations-Benchmark")
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
    period_options = [
        "Gesamter Zeitraum",
        "Letzte 24 Stunden",
        "Letzte 7 Tage",
        "Letzte 30 Tage",
        "Benutzerdefiniert",
    ]
    selected_period = st.selectbox(
        "Diagramm-Zeitraum",
        period_options,
        key="telemetry_period",
    )
    chart_df = df
    latest_timestamp = df["Timestamp"].max()

    if selected_period == "Benutzerdefiniert":
        available_start = df["Timestamp"].min().date()
        available_end = latest_timestamp.date()
        selected_dates = st.date_input(
            "Von–bis",
            value=(available_start, available_end),
            min_value=available_start,
            max_value=available_end,
            format="DD.MM.YYYY",
            key="telemetry_custom_dates",
        )
        if (
            isinstance(selected_dates, tuple)
            and len(selected_dates) == 2
            and all(selected_dates)
        ):
            start_date, end_date = selected_dates
            if start_date <= end_date:
                measurement_dates = df["Timestamp"].dt.date
                chart_df = df[
                    (measurement_dates >= start_date)
                    & (measurement_dates <= end_date)
                ]
            else:
                chart_df = df.iloc[0:0]
                st.info("Das Startdatum muss vor oder am Enddatum liegen.")
        else:
            chart_df = df.iloc[0:0]
            st.info("Bitte wählen Sie ein Start- und Enddatum aus.")
    elif selected_period != "Gesamter Zeitraum":
        period_durations = {
            "Letzte 24 Stunden": pd.Timedelta(hours=24),
            "Letzte 7 Tage": pd.Timedelta(days=7),
            "Letzte 30 Tage": pd.Timedelta(days=30),
        }
        cutoff = latest_timestamp - period_durations[selected_period]
        chart_df = df[df["Timestamp"] >= cutoff]

    if chart_df.empty:
        st.info("Für den gewählten Zeitraum liegen keine Messungen vor.")

    prototype_sensor_ids = (
        sorted(df["sensor_id"].unique()) if is_supabase_prototype else []
    )
    curve_scope = "prototype" if is_supabase_prototype else "demo"
    if is_supabase_prototype:
        curve_options = [
            (sensor_assignments[sensor_id], f"sensor_{sensor_id}")
            for sensor_id in prototype_sensor_ids
        ]
        curve_options.extend([
            ("Spreizung ΔT (vorläufig)", "spread"),
            ("Außentemperatur Innsbruck", "weather"),
        ])
    else:
        curve_options = [
            ("Vorlauf", "vorlauf"),
            ("Rücklauf", "ruecklauf"),
            ("Warmwasser", "warmwasser"),
            ("Spreizung ΔT", "spread"),
            ("Außentemperatur", "weather"),
        ]

    st.markdown("**Anzuzeigende Kurven**")
    curve_columns = st.columns(min(3, len(curve_options)))
    show_curves = {}
    for curve_index, (curve_label, curve_key) in enumerate(curve_options):
        with curve_columns[curve_index % len(curve_columns)]:
            show_curves[curve_key] = st.checkbox(
                curve_label,
                value=True,
                key=f"telemetry_curve_{curve_scope}_{curve_key}",
            )
    if not any(show_curves.values()):
        st.info("Bitte wählen Sie mindestens eine Kurve aus.")

    if is_supabase_prototype:
        weather_chart_df = pd.DataFrame(columns=["Timestamp", "Aussen_C"])
        if show_curves["weather"] and not chart_df.empty:
            try:
                weather_df = load_innsbruck_weather(
                    chart_df["Timestamp"].min().date().isoformat(),
                    chart_df["Timestamp"].max().date().isoformat(),
                )
                chart_start = chart_df["Timestamp"].min()
                chart_end = chart_df["Timestamp"].max()
                weather_chart_df = weather_df[
                    weather_df["Timestamp"].between(
                        chart_start.floor("h") - pd.Timedelta(hours=1),
                        chart_end.ceil("h") + pd.Timedelta(hours=1),
                    )
                ]
            except (httpx.HTTPError, ValueError) as error:
                st.warning(
                    f"Innsbrucker Außentemperaturen konnten nicht geladen werden: {error}"
                )

        st.header("Supabase-Temperaturverlauf")
        st.markdown(
            '<p class="section-kicker">Originalmessungen aus Supabase · Spreizung vorläufig · stündliche Innsbruck-Wetterdaten von Open-Meteo</p>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Außentemperatur: historische Wettermodell-Daten für Innsbruck "
            "(ca. 47,27° N, 11,40° E), keine lokale Sensor- oder Live-Messung."
        )
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            row_heights=[0.7, 0.3],
            specs=[[{}], [{"secondary_y": True}]],
            subplot_titles=(
                "Temperaturen · vorläufige Sensorzuordnung",
                "Spreizung ΔT (K) · vorläufig und Außentemperatur (°C)",
            ),
        )
        sensor_colors = ["#b42318", "#1d4ed8", "#b45309", "#047857", "#475569"]
        for sensor_index, (sensor_id, sensor_data) in enumerate(
            chart_df.groupby("sensor_id", sort=True)
        ):
            if not show_curves[f"sensor_{sensor_id}"]:
                continue
            fig.add_trace(
                go.Scatter(
                    x=sensor_data["Timestamp"],
                    y=sensor_data["Temperatur_C"],
                    name=sensor_assignments[sensor_id],
                    mode="lines",
                    line=dict(
                        color=sensor_colors[sensor_index % len(sensor_colors)],
                        width=2,
                    ),
                ),
                row=1,
                col=1,
            )

        if show_curves["spread"] and len(prototype_sensor_ids) >= 2:
            spread_df = pair_prototype_sensor_readings(df).reset_index()
            if not chart_df.empty and not spread_df.empty:
                spread_df = spread_df.loc[
                    spread_df["Timestamp"].between(
                        chart_df["Timestamp"].min(),
                        chart_df["Timestamp"].max(),
                    )
                ]
            else:
                spread_df = spread_df.iloc[0:0]

            if spread_df.empty:
                st.info(
                    "Für den gewählten Zeitraum gibt es keine zeitlich passenden "
                    "Messpaare für die Spreizung."
                )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=spread_df["Timestamp"],
                        y=spread_df["Spreizung_K"],
                        name="Spreizung ΔT (K, vorläufig)",
                        mode="lines",
                        line=dict(color="#047857", width=2),
                    ),
                    row=2,
                    col=1,
                    secondary_y=False,
                )
        elif show_curves["spread"]:
            st.info("Für die Spreizung werden mindestens zwei Sensoren benötigt.")

        if show_curves["weather"] and not weather_chart_df.empty:
            fig.add_trace(
                go.Scatter(
                    x=weather_chart_df["Timestamp"],
                    y=weather_chart_df["Aussen_C"],
                    name="Außentemperatur Innsbruck (°C)",
                    mode="lines",
                    line=dict(color="#475569", width=1.5, dash="dot"),
                ),
                row=2,
                col=1,
                secondary_y=True,
            )
            fig.update_xaxes(
                range=[chart_df["Timestamp"].min(), chart_df["Timestamp"].max()]
            )
        elif show_curves["weather"]:
            st.info("Für den ausgewählten Zeitraum liegen keine Innsbruck-Wetterdaten vor.")

        fig.update_yaxes(title_text="Temperatur (°C)", row=1, col=1)
        fig.update_yaxes(title_text="ΔT (K)", row=2, col=1, secondary_y=False)
        fig.update_yaxes(title_text="Außentemperatur (°C)", row=2, col=1, secondary_y=True)
        chart_alt = (
            "Supabase-Temperaturmessungen, vorläufige Spreizung und "
            "historische Außentemperatur in Innsbruck über "
            f"{len(chart_df)} Messpunkte"
        )
    else:
        st.header("Thermodynamischer Zeitverlauf")
        st.markdown(
            '<p class="section-kicker">Vorlauf, Rücklauf, Warmwasser und Systemspreizung · Zeitraum über die Auswahl einstellbar</p>',
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

        if show_curves["vorlauf"]:
            fig.add_trace(go.Scatter(x=chart_df["Timestamp"], y=chart_df["Vorlauf_C"], name="Vorlauf (T_VL)", line=dict(color="#b42318", width=2)), row=1, col=1)
        if show_curves["ruecklauf"]:
            fig.add_trace(go.Scatter(x=chart_df["Timestamp"], y=chart_df["Ruecklauf_C"], name="Rücklauf (T_RL)", line=dict(color="#1d4ed8", width=2)), row=1, col=1)
        if show_curves["warmwasser"]:
            fig.add_trace(go.Scatter(x=chart_df["Timestamp"], y=chart_df["Warmwasser_C"], name="Warmwasser (T_WW)", line=dict(color="#b45309", width=2, dash="dot")), row=1, col=1)

            fig.add_hline(
                y=55,
                line_dash="dash",
                line_color="#64748b",
                annotation_text="55°C Referenz",
                row=1,
                col=1,
            )

        if show_curves["spread"]:
            fig.add_trace(go.Scatter(x=chart_df["Timestamp"], y=chart_df["Spreizung_K"], name="Spreizung ΔT (K)", fill="tozeroy", fillcolor="rgba(4, 120, 87, 0.12)", line=dict(color="#047857", width=1.5)), row=2, col=1)
        if show_curves["weather"]:
            fig.add_trace(go.Scatter(x=chart_df["Timestamp"], y=chart_df["Aussen_C"], name="Außentemp. (°C)", line=dict(color="#475569", width=1.5)), row=2, col=1)
        chart_alt = (
            "Temperaturverlauf von Vorlauf, Rücklauf, Warmwasser, "
            "Spreizung und Außentemperatur"
        )

    fig.update_layout(
        height=550,
        autosize=True,
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=95, b=35),
        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor="#dce5de",
            font=dict(color="#172a27"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.18,
            xanchor="left",
            x=0,
            entrywidthmode="fraction",
            entrywidth=0.24,
            font=dict(color="#334155", size=12),
        ),
        font=dict(color="#334155", family='Inter, "Segoe UI", sans-serif'),
    )
    fig.update_xaxes(
        gridcolor="#e2e8f0",
        zerolinecolor="#cbd5e1",
        tickfont=dict(color="#475569"),
    )
    fig.update_yaxes(
        gridcolor="#e2e8f0",
        zerolinecolor="#cbd5e1",
        tickfont=dict(color="#475569"),
    )
    st.plotly_chart(
        fig,
        width="stretch",
        config={"responsive": True},
        theme=None,
        alt=chart_alt,
    )

with portfolio_tab:
    st.header("Portfolio-Leitstelle Innsbruck")
    st.markdown(
        f"""
        <p class="section-kicker">
            {len(portfolio_df)} Anlagen · {len(demo_optimal_locations)} simulierte Beispielobjekte mit optimalem Profil.
            Marker und Gebäudestatus sind farblich codiert.
        </p>
        <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:0.65rem;margin:0.4rem 0 1rem;">
            <span style="display:inline-flex;align-items:center;gap:0.45rem;padding:0.4rem 0.7rem;border:1px solid rgba(239,68,68,.3);border-radius:999px;background:rgba(239,68,68,.1);color:#9f2525;font-size:.82rem;">
                <span style="width:.55rem;height:.55rem;border-radius:50%;background:#ef4444;"></span>
                Rot · Kritisch / Hygiene-Alarm
            </span>
            <span style="display:inline-flex;align-items:center;gap:0.45rem;padding:0.4rem 0.7rem;border:1px solid rgba(249,115,22,.3);border-radius:999px;background:rgba(249,115,22,.1);color:#9a4611;font-size:.82rem;">
                <span style="width:.55rem;height:.55rem;border-radius:50%;background:#f97316;"></span>
                Orange · Warnung
            </span>
            <span style="display:inline-flex;align-items:center;gap:0.45rem;padding:0.4rem 0.7rem;border:1px solid rgba(34,197,94,.3);border-radius:999px;background:rgba(34,197,94,.1);color:#17643e;font-size:.82rem;">
                <span style="width:.55rem;height:.55rem;border-radius:50%;background:#22c55e;"></span>
                Grün · Optimal
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    portfolio_loss = int(portfolio_df["Verlust / Monat (€)"].sum())
    attention_count = int(portfolio_df["Status"].ne("Optimal").sum())
    loss_col, assets_col, attention_col = st.columns([1.2, 1, 1], gap="medium")
    with loss_col:
        with st.container(key="portfolio_loss_metric"):
            st.metric("Portfolio-Verlust pro Monat", f"€ {portfolio_loss:,}")
    assets_col.metric("Anlagen im Portfolio", len(portfolio_df))
    attention_col.metric(
        "Anlagen mit Handlungsbedarf",
        attention_count,
        f"von {len(portfolio_df)} Anlagen",
        delta_color="inverse",
    )
    st.markdown("### Portfolio-Karte")
    if not st.session_state.get("external_map_consent", False):
        with st.container(border=True):
            st.markdown("#### Innsbruck auf der Karte entdecken")
            st.write(
                "Die interaktive Karte verwendet den Kartendienst CARTO. "
                "Beim Laden wird eine Verbindung zu CARTO hergestellt; dabei "
                "werden Ihre IP-Adresse und technische Verbindungsdaten "
                "übermittelt. Kartenkacheln für den sichtbaren Kartenausschnitt "
                "werden von CARTO geladen."
            )
            if st.button(
                "Externe Karte laden (CARTO)",
                key="load_external_map",
                type="primary",
                width="stretch",
            ):
                st.session_state["external_map_consent"] = True
                st.rerun()
    else:
        import pydeck as pdk

        if st.button(
            "Externe Karte ausblenden / Einwilligung zurückziehen",
            key="revoke_external_map_consent",
        ):
            st.session_state["external_map_consent"] = False
            st.rerun()

        marker_layer = pdk.Layer(
            "ScatterplotLayer",
            data=portfolio_df,
            get_position="[longitude, latitude]",
            get_fill_color="[color_r, color_g, color_b, 220]",
            get_line_color="[255, 255, 255, 220]",
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
            map_style=(
                "https://basemaps.cartocdn.com/gl/"
                "positron-gl-style/style.json"
            ),
            tooltip={
                "html": (
                    "<b>{Objekt}</b><br/>"
                    "{Adresse}<br/>"
                    "Status: {Status}<br/>"
                    "Verlust: {Verlust}"
                ),
                "style": {
                    "backgroundColor": "#ffffff",
                    "color": "#172a27",
                    "border": "1px solid #dfe7df",
                },
            },
        )
        st.pydeck_chart(
            portfolio_map,
            width="stretch",
            height=620,
            key="portfolio_map",
        )

render_site_footer()
