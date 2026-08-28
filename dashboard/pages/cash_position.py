"""
Cash Position Page - Cash position breakdown and forecast.
"""

import streamlit as st
from dashboard.components.cash_waterfall import render_cash_position_breakdown
from dashboard.components.cash_waterfall import render_cash_waterfall_card
from dashboard.utils.api_client import api_get


def render_cash_position():
    """Render the cash position page with breakdown and forecast."""
    
    st.markdown('<div class="section-header">Cash Position & Forecast</div>', unsafe_allow_html=True)
    
    # Fetch cash position
    with st.spinner("Loading cash position..."):
        from dashboard.utils.api_client import api_get
        cash_position = api_get("/cash/position")
    
    if not cash_position:
        st.info("No cash position data available. Run reconciliation first.")
        return
    
    # Render breakdown
    from dashboard.components.cash_waterfall import render_cash_position_breakdown
    render_cash_position_breakdown(cash_position)
    
    # Forecast
    st.markdown("### Forecast")
    from dashboard.components.forecast_chart import render_forecast_chart_card
    from dashboard.utils.api_client import api_get
    
    forecast = api_get("/cash/forecast", {"days": 30})
    if forecast:
        render_forecast_chart_card(forecast, title="30-Day Cash Flow Forecast")


if __name__ == "__main__":
    import streamlit as st
    from dashboard.pages.cash_position import render_cash_position
    render_cash_position()