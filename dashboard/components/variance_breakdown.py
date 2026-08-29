"""
Variance Breakdown Component - Detailed variance analysis with drill-down.
"""

import streamlit as st
from typing import Optional, Dict, Any
from dashboard.utils.formatters import format_inr
from dashboard.styles.theme import get_status_color
from dashboard.utils.chart_helpers import create_variance_breakdown_chart


def render_variance_breakdown(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render detailed variance breakdown with drill-down."""
    if not cash_position:
        st.info("No cash position data available")
        return
    
    st.markdown('<div class="section-header">Variance Breakdown</div>', unsafe_allow_html=True)
    
    # Calculate variance components
    expected_cash = float(cash_position.get('expected_cash', 0))
    bank_cash = float(cash_position.get('bank_cash', 0))
    variance = float(cash_position.get('variance', 0))
    
    confirmed_inflows = float(cash_position.get('confirmed_inflows', 0))
    confirmed_outflows = float(cash_position.get('confirmed_outflows', 0))
    pending_inflows = float(cash_position.get('pending_inflows', 0))
    pending_outflows = float(cash_position.get('pending_outflows', 0))
    adjustments = float(cash_position.get('adjustments', 0))
    
    variance_components = {
        "Confirmed Inflows": confirmed_inflows,
        "Confirmed Outflows": -confirmed_outflows,
        "Pending Inflows": pending_inflows,
        "Pending Outflows": -pending_outflows,
        "Adjustments": adjustments,
    }
    
    st.markdown('<div class="section-header">Variance Breakdown</div>', unsafe_allow_html=True)
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Expected Cash", format_inr(expected_cash))
    with col2:
        st.metric("Bank Cash", format_inr(bank_cash))
    with col3:
        variance_color = "normal" if variance >= 0 else "inverse"
        st.metric("Variance", format_inr(variance), delta=f"{variance:,.0f}", delta_color="normal" if variance >= 0 else "inverse")
    with col4:
        st.metric("Variance %", f"{(variance/expected_cash*100):.1f}%" if expected_cash != 0 else "N/A")
    
    # Detailed breakdown
    st.markdown("### Variance Components")
    
    components = [
        ("Confirmed Inflows", confirmed_inflows, "#00D4AA"),
        ("Confirmed Outflows", -confirmed_outflows, "#FF6B6B"),
        ("Pending Inflows", pending_inflows, "#F0B429"),
        ("Pending Outflows", -pending_outflows, "#F0B429"),
        ("Adjustments", adjustments, "#58A6FF"),
    ]
    
    col1, col2 = st.columns(2)
    for i, (label, value, color) in enumerate(variance_components):
        with [st.columns(2)[0], st.columns(2)[1]][i % 2]:
            st.markdown(f'''
            <div style="
                background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
                border: 1px solid #2D333B;
                border-left: 3px solid {color};
                border-radius: 8px;
                padding: 1rem;
                margin: 0.5rem 0;
            ">
                <div style="color: #8B949E; font-size: 0.875rem; margin-bottom: 0.5rem;">{label}</div>
                <div style="color: {color}; font-size: 1.5rem; font-weight: 700; font-family: monospace;">{format_inr(value)}</div>
            </div>
            ''', unsafe_allow_html=True)
    
    if show_chart:
        from dashboard.utils.chart_helpers import create_variance_breakdown_chart
        fig = create_variance_breakdown_chart(
            expected_cash=0,  # placeholder
            confirmed_inflows=0,
            confirmed_outflows=0,
            pending_inflows=0,
            pending_outflows=0,
            adjustments=0,
        )
        st.plotly_chart(fig, use_container_width=True)


def render_variance_breakdown_card(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render variance breakdown in a card."""
    st.markdown(f'''
    <div style="
        background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
        border: 1px solid #2D333B;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    ">
        <h3 style="margin: 0 0 1rem 0; color: #E6EDF3; font-size: 1.125rem;">Variance Breakdown</h3>
    ''', unsafe_allow_html=True)
    
    from dashboard.utils.formatters import format_inr
    from dashboard.styles.theme import STATUS_COLORS
    
    confirmed_inflows = float(cash_position.get('confirmed_inflows', 0))
    confirmed_outflows = float(cash_position.get('confirmed_outflows', 0))
    pending_inflows = float(cash_position.get('pending_inflows', 0))
    pending_outflows = float(cash_position.get('pending_outflows', 0))
    adjustments = float(cash_position.get('adjustments', 0))
    
    variance_components = {
        "Confirmed Inflows": confirmed_inflows,
        "Confirmed Outflows": -confirmed_outflows,
        "Pending Inflows": pending_inflows,
        "Pending Outflows": -pending_outflows,
        "Adjustments": adjustments,
    }
    
    for label, value in variance_components.items():
        color = "#00D4AA" if value >= 0 else "#FF6B6B"
        is_negative = value < 0
        prefix = "-" if value < 0 else "+"
        formatted_value = format_inr(abs(value))
        
        st.markdown(f'''
        <div style="display: flex; justify-content: space-between; padding: 0.75rem; background: #1E2329; border-radius: 6px; margin: 0.5rem 0; border-left: 3px solid {"#00D4AA" if value >= 0 else "#FF6B6B"};">
            <span style="color: #8B949E;">{label}</div>
            <div style="color: {"#00D4AA" if value >= 0 else "#FF6B6B"}; font-weight: 600; font-family: monospace;">{"-" if value < 0 else "+"}{format_inr(abs(value))}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    if show_chart:
        from dashboard.utils.chart_helpers import create_variance_breakdown_chart
        fig = create_variance_breakdown_chart(
            expected_cash=0,
            confirmed_inflows=confirmed_inflows,
            confirmed_outflows=confirmed_outflows,
            pending_inflows=pending_inflows,
            pending_outflows=pending_outflows,
            adjustments=adjustments,
        )
        st.plotly_chart(fig, use_container_width=True)