import streamlit as st
from dashboard.pages.overview import render_overview
from dashboard.pages.reconciliation import render_reconciliation
from dashboard.pages.exceptions import render_exceptions
from dashboard.pages.cash_position import render_cash_position
from dashboard.pages.metrics import render_metrics
from dashboard.pages.probable_matches import render_probable_matches
from dashboard.styles.css import inject_css
from dashboard.utils.state import init_session_state


def main():
    st.set_page_config(
        page_title="AI Finance Controller",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    inject_css()
    init_session_state()
    
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem;">
        <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #00D4AA 0%, #00A3CC 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">💰</div>
        <div>
            <h1 style="margin: 0; font-size: 1.75rem;">AI Finance Controller</h1>
            <p style="margin: 0; color: #8B949E; font-size: 0.875rem;">Run the books and the cash position.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab_overview, tab_reconciliation, tab_probable, tab_exceptions, tab_cash, tab_metrics = st.tabs([
        "📊 Overview", "🔍 Reconciliation", "⚠️ Probable Matches", "⚠️ Exceptions", "💵 Cash Position", "📈 Metrics"
    ])
    
    with tab_overview:
        render_overview()
    
    with tab_reconciliation:
        render_reconciliation()
    
    with tab_probable:
        render_probable_matches()
    
    with tab_exceptions:
        render_exceptions()
    
    with tab_cash:
        render_cash_position()
    
    with tab_metrics:
        render_metrics()


if __name__ == "__main__":
    main()