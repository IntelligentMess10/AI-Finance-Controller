"""
Overview Page - Main dashboard view with KPIs and quick actions.
"""

import streamlit as st
from dashboard.components.kpi_card import render_kpi_row_simple
from dashboard.components.cash_waterfall import render_cash_waterfall_card
from dashboard.components.exception_queue import render_exception_queue
from dashboard.utils.api_client import api_get
from dashboard.utils.formatters import format_inr


def render_overview():
    """Render the main overview page with KPIs and key metrics."""
    
    # Fetch data
    metrics = api_get("/metrics/")
    cash = api_get("/cash/position")
    
    # KPI Row
    if metrics:
        kpi_metrics = [
            {"label": "Match Rate", "value": f"{metrics.get('match_rate', 0):.1f}%", "delta": f"{metrics.get('match_rate', 0) - 90:.1f}%", "delta_type": "normal"},
            {"label": "Total Records", "value": str(metrics.get('total_records', 0))},
            {"label": "Exceptions", "value": str(metrics.get('exceptions_total', 0))},
            {"label": "Unresolved", "value": str(metrics.get('exceptions_unresolved', 0)), "delta_type": "inverse" if metrics.get('exceptions_unresolved', 0) > 0 else "normal"},
        ]
        render_kpi_row_simple(metrics=[
            {"label": m["label"], "value": m["value"], "delta": m.get("delta"), "delta_type": m.get("delta_type", "normal")}
            for m in kpi_metrics
        ])
    
    # Cash Waterfall
    if cash:
        render_cash_waterfall_card(
            opening=cash['opening_balance'],
            confirmed_inflows=cash['confirmed_inflows'],
            confirmed_outflows=cash['confirmed_outflows'],
            pending_inflows=cash['pending_inflows'],
            pending_outflows=cash['pending_outflows'],
            title="Cash Position Waterfall"
        )
    
    # Quick Actions
    st.markdown("### Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Run Reconciliation", use_container_width=True, type="primary"):
            st.session_state['run_reconciliation'] = True
            st.rerun()
    with col2:
        if st.button("🤖 Investigate Exceptions", use_container_width=True):
            st.info("Navigate to Exceptions page to investigate")
    with col3:
        if st.button("📊 Refresh Metrics", use_container_width=True):
            st.rerun()


if __name__ == "__main__":
    import streamlit as st
    from dashboard.pages.Overview import render_overview
    render_overview()