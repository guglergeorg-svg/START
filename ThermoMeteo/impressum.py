import streamlit as st

from site_pages import render_site_footer

st.markdown(
    """
    <style>
    :root { color-scheme: light; }
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background: #f4f7f3;
        color: #172a27;
    }
    .block-container {
        max-width: 900px;
        padding: 2rem clamp(1rem, 4vw, 3rem) 3rem;
    }
    h1, h2, h3 { color: #172a27; letter-spacing: -.03em; }
    [data-testid="stMarkdownContainer"] a { color: #155e4b; }
    :focus-visible {
        outline: 3px solid #a35400 !important;
        outline-offset: 3px !important;
        box-shadow: 0 0 0 2px #fff !important;
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
    .site-footer nav { display: flex; flex-wrap: wrap; gap: 1.2rem; }
    .site-footer a { color: #155e4b; text-underline-offset: 3px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Impressum")
st.warning(
    "Muster mit Platzhaltern: vor Veröffentlichung mit den tatsächlichen "
    "Betreiber- und Unternehmensdaten vervollständigen und rechtlich prüfen."
)

st.header("Medieninhaber und Diensteanbieter")
st.markdown(
    """
- **Vollständiger Name / Firma:** [VOLLSTÄNDIGEN NAMEN ODER FIRMA EINTRAGEN]
- **Rechtsform:** [RECHTSFORM EINTRAGEN, FALLS ZUTREFFEND]
- **Ladungsfähige Anschrift in Österreich:** [STRASSE, HAUSNUMMER, PLZ, ORT, ÖSTERREICH]
- **E-Mail:** [GESCHÄFTLICHE E-MAIL-ADRESSE]
- **Telefon:** [TELEFONNUMMER]
- **Unternehmensgegenstand:** [UNTERNEHMENSGEGENSTAND BESCHREIBEN]
- **UID-Nummer:** [UID-NUMMER EINTRAGEN ODER „NICHT VORHANDEN“ BESTÄTIGEN]
- **Mitgliedschaft:** [ZUSTÄNDIGE WIRTSCHAFTSKAMMER / FACHGRUPPE ODER „KEINE“ BESTÄTIGEN]
- **Aufsichtsbehörde:** [ZUSTÄNDIGE BEZIRKSHAUPTMANNSCHAFT ODER MAGISTRAT]
- **Berufsrechtliche Vorschriften:** [ZUTREFFENDE GEWERBEORDNUNG / BERUFSRECHT EINTRAGEN]
  – abrufbar unter [RIS – Rechtsinformationssystem des Bundes](https://www.ris.bka.gv.at).
"""
)

st.header("Offenlegung nach § 25 Mediengesetz")
st.markdown(
    """
- **Medieninhaber:** [VOLLSTÄNDIGEN NAMEN ODER FIRMA EINTRAGEN]
- **Unternehmensgegenstand:** [UNTERNEHMENSGEGENSTAND EINTRAGEN]
- **Blattlinie / grundlegende Richtung des Mediums:** [ZWECK UND GRUNDLEGENDE AUSRICHTUNG DER WEBSITE BESCHREIBEN]
- **Sitz:** [ORT IN ÖSTERREICH]
"""
)

st.header("Haftungshinweis")
st.write(
    "Die Inhalte dieser Demo dienen der technischen Veranschaulichung. "
    "Die dargestellten Messwerte, Diagnosen, Einsparungen und Gebäude sind "
    "teilweise simuliert und ersetzen keine fachliche Prüfung vor Ort."
)

render_site_footer()
