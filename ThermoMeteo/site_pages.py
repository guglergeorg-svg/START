import streamlit as st


def render_site_footer() -> None:
    st.html(
        """
        <footer class="site-footer">
            <span>HeatPulse AI · Heizungs-Monitoring</span>
            <nav aria-label="Rechtliche Informationen">
                <a href="/impressum">Impressum</a>
                <a href="/datenschutz">Datenschutzerklärung</a>
            </nav>
        </footer>
        """
    )
