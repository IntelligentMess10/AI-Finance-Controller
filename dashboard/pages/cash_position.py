"""
Cash Position Page - Cash position breakdown and forecast.
"""

import streamlit as st
from dashboard.components.cash_waterfall import render_cash_position_breakdown
from dashboard.components.cash_waterfall import render_cash_waterfall_card
from dashboard.utils.api_client import api_get, api_post


def render_cash_position():
    """Render the cash position page with breakdown and forecast."""
    
    st.markdown('<div class="section-header">Cash Position & Forecast</div>', unsafe_allow_html=True)
    
    with st.spinner("Loading cash position..."):
        cash_position = api_get("/cash/position")
        if cash_position is None:
            st.info("No cash position exists yet. Creating one from the latest reconciliation data...")
            cash_position = api_post("/cash/position/calculate")
    
    if not cash_position:
        st.info("No cash position data available. Run reconciliation first.")
        return
    
    # Render breakdown
    render_cash_position_breakdown(cash_position)
    
    # Forecast - 30-day chart
    st.markdown("### Cash Flow Forecast")
    from dashboard.components.forecast_chart import render_forecast_chart_card
    
    forecast = api_get("/cash/forecast", {"days": 30})
    if forecast:
        render_forecast_chart_card(forecast, title="30-Day Cash Flow Forecast")
    
    # Forecast Summary - 7/14/30 day horizons
    st.markdown("### Forecast Summary by Horizon")
    from dashboard.components.forecast_chart import render_forecast_summary_card
    
    if forecast:
        render_forecast_summary_card(forecast, title="Forecast Summary (7/14/30 Days)")


if __name__ == "__main__":
    import streamlit as st
    from dashboard.pages.cash_position import render_cash_position
    render_cash_position()