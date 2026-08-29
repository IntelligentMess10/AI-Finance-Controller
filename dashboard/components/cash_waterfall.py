'''
Cash Waterfall Chart Component.
'''

import streamlit as st
from typing import Optional
from dashboard.utils.chart_helpers import create_cash_waterfall_chart
from dashboard.utils.formatters import format_inr


def render_cash_waterfall(
    opening: float,
    confirmed_inflows: float,
    confirmed_outflows: float,
    pending_inflows: float = 0,
    pending_outflows: float = 0,
    bank_cash: Optional[float] = None,
    key: str = "cash_waterfall_main",
) -> None:
    """
    Render a cash position waterfall chart.
    
    Args:
        opening: Opening balance
        confirmed_inflows: Total confirmed inflows
        confirmed_outflows: Total confirmed outflows
        pending_inflows: Pending inflows
        pending_outflows: Pending outflows
        bank_cash: Actual bank cash (optional)
        key: Unique key for Streamlit
    """
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
        bank_cash=bank_cash,
    )
    
    st.plotly_chart(fig, use_container_width=True, key=key)


def render_cash_waterfall_card(
    opening: float,
    confirmed_inflows: float,
    confirmed_outflows: float,
    pending_inflows: float = 0,
    pending_outflows: float = 0,
    bank_cash: Optional[float] = None,
    title: str = "Cash Position Waterfall",
) -> None:
    """Render cash waterfall chart in a card container."""
    st.markdown(f'''
    <div style="
        background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
        border: 1px solid #2D333B;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    ">
        <h3 style="margin: 0 0 1rem 0; color: #E6EDF3; font-size: 1.125rem;">{title}</h3>
    ''', unsafe_allow_html=True)
    
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
        bank_cash=bank_cash,
    )
    st.plotly_chart(fig, use_container_width=True, key="cash_waterfall_card")
    st.markdown('</div>', unsafe_allow_html=True)


def render_cash_position_breakdown(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render detailed cash position breakdown with optional chart."""
    from dashboard.utils.formatters import format_inr
    
    if not cash_position:
        st.info("No cash position data available")
        return
    
    st.markdown('<div class="section-header">Cash Position Breakdown</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Detailed breakdown
        breakdown = [
            ("Opening Balance", cash_position['opening_balance'], "#58A6FF"),
            ("Confirmed Inflows", cash_position['confirmed_inflows'], "#00D4AA"),
            ("Confirmed Outflows", cash_position['confirmed_outflows'], "#FF6B6B"),
            ("Pending Inflows", cash_position.get('pending_inflows', 0), "#F0B429"),
            ("Pending Outflows", cash_position.get('pending_outflows', 0), "#F0B429"),
            ("Adjustments", cash_position.get('adjustments', 0), "#58A6FF"),
        ]
        
        for label, value, color in breakdown:
            st.markdown(f'''
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.75rem;
                margin-bottom: 0.5rem;
                background: #1E2329;
                border-left: 3px solid {color};
                border-radius: 4px;
            ">
                <span style="color: #E6EDF3;">{label}</span>
                <span style="color: {color}; font-weight: 600; font-family: 'JetBrains Mono', monospace;">₹{format_inr(float(value))}</span>
            </div>
            ''', unsafe_allow_html=True)
    
    with col2:
        # Summary metrics
        expected_cash = float(cash_position.get('expected_cash', 0))
        bank_cash = float(cash_position.get('bank_cash', 0))
        variance = float(cash_position.get('variance', 0))
        
        variance_color = "#00D4AA" if variance >= 0 else "#FF6B6B"
        
        st.markdown(f'''
        <div style="
            background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
            border: 1px solid #2D333B;
            border-radius: 8px;
            padding: 1.5rem;
        ">
            <div style="margin-bottom: 1rem;">
                <div style="color: #8B949E; font-size: 0.875rem; margin-bottom: 0.5rem;">Expected Cash</div>
                <div style="color: #58A6FF; font-size: 1.5rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">₹{format_inr(float(expected_cash))}</div>
            </div>
            <div style="margin-bottom: 1rem;">
                <div style="color: #8B949E; font-size: 0.875rem; margin-bottom: 0.5rem;">Bank Cash</div>
                <div style="color: #B3B1AD; font-size: 1.5rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">₹{format_inr(float(bank_cash))}</div>
            </div>
            <div style="padding-top: 1rem; border-top: 1px solid #2D333B;">
                <div style="color: #8B949E; font-size: 0.875rem; margin-bottom: 0.5rem;">Variance</div>
                <div style="color: {variance_color}; font-size: 1.5rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">₹{format_inr(float(variance))}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    if show_chart:
        st.markdown("---")
        render_cash_waterfall(
            opening=float(cash_position['opening_balance']),
            confirmed_inflows=float(cash_position['confirmed_inflows']),
            confirmed_outflows=float(cash_position['confirmed_outflows']),
            pending_inflows=float(cash_position.get('pending_inflows', 0)),
            pending_outflows=float(cash_position.get('pending_outflows', 0)),
            bank_cash=float(cash_position.get('bank_cash')) if cash_position.get('bank_cash') else None,
            key="cash_waterfall_breakdown",
        )
