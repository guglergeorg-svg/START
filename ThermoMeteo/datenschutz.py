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

st.title("Datenschutzerklärung")
st.warning(
    "Muster mit Betreiber-Platzhaltern: Hosting, Aufbewahrungsfristen, "
    "Kontaktangaben und tatsächliche Serverkonfiguration vor Veröffentlichung "
    "ergänzen. Diese Vorlage ist keine Rechtsberatung."
)

st.header("1. Verantwortlicher")
st.markdown(
    """
**[VOLLSTÄNDIGER NAME / FIRMA]**  
[LADUNGSFÄHIGE ANSCHRIFT IN ÖSTERREICH]  
E-Mail: [DATENSCHUTZ- ODER KONTAKT-E-MAIL]  
Telefon: [TELEFONNUMMER]
"""
)

st.header("2. Betrieb der Website und Server-Logfiles")
st.markdown(
    """
Beim Aufruf verarbeitet der Webserver technisch erforderliche Verbindungsdaten,
die Ihr Browser übermittelt. Dazu können insbesondere IP-Adresse, Zeitpunkt,
aufgerufene Ressource, Referrer, Browser-/Betriebssysteminformationen und
Statuscodes gehören. Diese Daten werden zur sicheren Bereitstellung,
Fehleranalyse und Abwehr von Missbrauch verarbeitet.

- **Rechtsgrundlage:** Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an
  einem sicheren und funktionsfähigen Betrieb).
- **Berechtigtes Interesse:** [SICHERHEITS- UND BETRIEBSZWECKE KONKRETISIEREN].
- **Hosting-Anbieter / Auftragsverarbeiter:** [HOSTER, SITZ UND KONTAKTDATEN].
- **Speicherort / mögliche Drittlandübermittlungen:** [RECHENZENTRUM UND
  TRANSFERGARANTIEN, FALLS ZUTREFFEND].
- **Aufbewahrungsdauer der Logs:** [TATSÄCHLICHE FRIST DES HOSTERS EINTRAGEN].
"""
)

st.header("3. App-Eingaben und Kontaktaufnahme")
st.markdown(
    """
Diese Demo enthält kein Kontaktformular und übermittelt keine Wartungsaufträge
an Installationsbetriebe. Der Wartungstext ist ein Entwurf im Streamlit-Widget;
Eingaben werden zur Anzeige und Verarbeitung an den Server dieser Anwendung
übertragen. Die Sensorwerte, Beispielobjekte und Diagnosen dienen in dieser
Version der Simulation. Bitte keine echten personenbezogenen Daten oder
vertraulichen Informationen eingeben.

Falls Sie uns außerhalb der App per E-Mail oder Telefon kontaktieren, verwenden
wir die von Ihnen mitgeteilten Daten ausschließlich zur Bearbeitung Ihrer
Anfrage und bewahren sie nur so lange auf, wie dies für deren Erledigung sowie
allfällige gesetzliche Pflichten erforderlich ist. Rechtsgrundlage ist Art. 6
Abs. 1 lit. b DSGVO, sofern die Anfrage vorvertraglich oder vertraglich erfolgt,
ansonsten Art. 6 Abs. 1 lit. f DSGVO (Bearbeitung und Beantwortung von Anfragen).
**[KONKRETE FRISTEN UND WEITERE KONTAKTWEGE ERGÄNZEN.]**
"""
)

st.header("4. Cookies, lokale Speicherung und Analyse")
st.markdown(
    """
Der Anwendungscode bindet keine Analyse-, Marketing- oder Pixel-Skripte ein und
verwendet kein eigenes LocalStorage oder SessionStorage. Es werden keine
externen Karten-, Schrift- oder Video-Inhalte automatisch geladen. Die
Portfolioansicht wird lokal aus den in der Anwendung vorhandenen Beispieldaten
gezeichnet. Die Übermittlung der Streamlit-Nutzungsstatistik ist über
`browser.gatherUsageStats = false` deaktiviert. Streamlit oder die
Hosting-Umgebung können für Sitzung,
Sicherheit und Betrieb technisch notwendige Cookies oder vergleichbare
Speichermechanismen verwenden; die konkrete Konfiguration ist beim Betreiber /
Hoster zu prüfen und hier zu dokumentieren.

In dieser Codeversion sind keine optionalen Tracking-Technologien eingebaut;
deshalb gibt es keinen Marketing- oder Analyse-Consent-Banner. Werden solche
Technologien künftig ergänzt, müssen sie bis zu einer wirksamen Einwilligung
blockiert bleiben und eine gleichwertige Ablehnungsoption erhalten.
"""
)

st.header("5. Empfänger und Drittanbieter")
st.markdown(
    """
Die Anwendung bindet keine externen Karten-, Font-, Video- oder Trackingdienste
ein. Die bisherigen Kartendaten wurden durch eine lokale Koordinatenansicht
ersetzt. **[HOSTER, E-MAIL-ANBIETER, SUPPORTDIENSTE UND SONSTIGE EMPFÄNGER
VOLLSTÄNDIG ERGÄNZEN; AUFTRAGSVERARBEITUNGSVERTRÄGE UND DRITTLANDTRANSFERS
PRÜFEN.]**
"""
)

st.header("6. HTTPS und Datensicherheit")
st.write(
    "Produktivbetrieb muss ausschließlich über HTTPS erfolgen. TLS wird üblicherweise "
    "am Reverse Proxy bzw. Hosting-Provider eingerichtet; der Anwendungscode allein "
    "erzwingt HTTPS nicht. Betreiber müssen HTTPS, sichere Proxy-Header und "
    "Zugriffsschutz vor Veröffentlichung verifizieren."
)

st.header("7. Ihre Rechte")
st.markdown(
    """
Im Rahmen der gesetzlichen Voraussetzungen haben Sie das Recht auf Auskunft,
Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit
sowie Widerspruch gegen Verarbeitungen auf Grundlage berechtigter Interessen.
Eine erteilte Einwilligung können Sie jederzeit mit Wirkung für die Zukunft
widerrufen. Zur Ausübung Ihrer Rechte kontaktieren Sie den oben genannten
Verantwortlichen.

Sie haben außerdem das Recht auf Beschwerde bei der österreichischen
**[Datenschutzbehörde](https://www.dsb.gv.at/)**. Bitte prüfen Sie die aktuellen
Kontaktdaten und Einreichungswege auf der Website der Behörde.
"""
)

st.header("8. Änderungen")
st.write(
    "Diese Erklärung ist mit dem tatsächlichen Funktionsumfang und der "
    "Hosting-Konfiguration abzugleichen und bei Änderungen zu aktualisieren. "
    "Stand: [DATUM EINTRAGEN]."
)

render_site_footer()
