"""
Cash Waterfall Chart Component.
"""

import streamlit as st
from typing import Optional
from dashboard.utils.chart_helpers import create_cash_waterfall_chart, create_cash_waterfall_chart
from dashboard.utils.formatters import format_inr


def render_cash_waterfall(
    opening: float,
    confirmed_inflows: float,
    confirmed_outflows: float,
    pending_inflows: float = 0,
    pending_outflows: float = 0,
    bank_cash: Optional[float] = None,
    key: str = "",
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
    from dashboard.utils.chart_helpers import create_cash_waterfall_chart
    
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
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
    from dashboard.utils.chart_helpers import create_cash_waterfall_chart
    
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
    
    from dashboard.utils.chart_helpers import create_cash_waterfall_chart
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_cash_position_breakdown(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render detailed cash position breakdown with optional chart."""
    from dashboard.utils.formatters import format_inr
    from dashboard.styles.theme import STATUS_COLORS
    
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
            ("Confirmed Outflows", -float(cash_position['confirmed_outflows']), "#FF6B6B"),
            ("Pending Inflows", cash_position['pending_inflows'], "#F0B429"),
            ("Pending Outflows", -float(cash_position['pending_outflows']), "#F0B429"),
            ("**Expected Cash**", cash_position['expected_cash'], "#E6EDF3"),
            ("Bank Reported", cash_position['bank_cash'], "#8B949E"),
            ("**Variance**", cash_position['variance'], "#00D4AA" if float(cash_position['variance']) >= 0 else "#FF6B6B"),
        ]
        
        for label, value, color in breakdown:
            is_total = label.startswith("**")
            clean_label = label.replace("**", "")
            fmt_value = format_inr(float(value))
            prefix = "+" if float(value) > 0 and not is_total and "Outflow" not in label else ""
            if "Outflow" in label or float(value) < 0:
                prefix = ""
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: {'#1E2329' if is_total else '#161B22'}; border-radius: 6px; margin: 0.25rem 0; border-left: 3px solid {color};">
                <span style="color: {'#E6EDF3' if is_total else '#8B949E'}; font-weight: {'600' if is_total else '400'};">{clean_label}</span>
                <span style="color: {color}; font-weight: {'700' if is_total else '500'};">{prefix}{fmt_value}</span>
            </div>
            ''', unsafe_allow_html=True)
        
        if show_chart:
            st.markdown("---")
            from dashboard.utils.chart_helpers import create_cash_waterfall_chart
            fig = create_cash_waterfall_chart(
                opening=cash_position['opening_balance'],
                inflows=cash_position['confirmed_inflows'],
                outflows=cash_position['confirmed_outflows'],
                pending_in=cash_position.get('pending_inflows', 0),
                pending_out=cash_position.get('pending_outflows', 0),
            )
            st.plotly_chart(fig, use_container_width=True)


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
    
    from dashboard.utils.chart_helpers import create_cash_waterfall_chart
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_cash_position_breakdown(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render detailed cash position breakdown with optional chart."""
    from dashboard.utils.formatters import format_inr
    from dashboard.styles.theme import STATUS_COLORS
    
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
            ("Confirmed Outflows", -float(cash_position['confirmed_outflows']), "#FF6B6B"),
            ("Pending Inflows", cash_position['pending_inflows'], "#F0B429"),
            ("Pending Outflows", -float(cash_position['pending_outflows']), "#F0B429"),
            ("**Expected Cash**", cash_position['expected_cash'], "#E6EDF3"),
            ("Bank Reported", cash_position['bank_cash'], "#8B949E"),
            ("**Variance**", cash_position['variance'], "#00D4AA" if float(cash_position['variance']) >= 0 else "#FF6B6B"),
        ]
        
        for label, value, color in breakdown:
            is_total = label.startswith("**")
            clean_label = label.replace("**", "")
            fmt_value = format_inr(float(value))
            prefix = "+" if float(value) > 0 and not is_total and "Outflow" not in label else ""
            if "Outflow" in label or float(value) < 0:
                prefix = ""
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: {'#1E2329' if is_total else '#161B22'}; border-radius: 6px; margin: 0.25rem 0; border-left: 3px solid {color};">
                <span style="color: {'#E6EDF3' if is_total else '#8B949E'}; font-weight: {'600' if is_total else '400'};">{clean_label}</span>
                <span style="color: {color}; font-weight: {'700' if is_total else '500'};">{prefix}{fmt_value}</span>
            </div>
            ''', unsafe_allow_html=True)
        
        if show_chart:
            st.markdown("---")
            from dashboard.utils.chart_helpers import create_cash_waterfall_chart
            fig = create_cash_waterfall_chart(
                opening=cash_position['opening_balance'],
                inflows=cash_position['confirmed_inflows'],
                outflows=cash_position['confirmed_outflows'],
                pending_in=cash_position.get('pending_inflows', 0),
                pending_out=cash_position.get('pending_outflows', 0),
            )
            st.plotly_chart(fig, use_container_width=True)


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
    
    from dashboard.utils.chart_helpers import create_cash_waterfall_chart
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_cash_position_breakdown(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render detailed cash position breakdown with optional chart."""
    from dashboard.utils.formatters import format_inr
    from dashboard.styles.theme import STATUS_COLORS
    
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
            ("Confirmed Outflows", -float(cash_position['confirmed_outflows']), "#FF6B6B"),
            ("Pending Inflows", cash_position['pending_inflows'], "#F0B429"),
            ("Pending Outflows", -float(cash_position['pending_outflows']), "#F0B429"),
            ("**Expected Cash**", cash_position['expected_cash'], "#E6EDF3"),
            ("Bank Reported", cash_position['bank_cash'], "#8B949E"),
            ("**Variance**", cash_position['variance'], "#00D4AA" if float(cash_position['variance']) >= 0 else "#FF6B6B"),
        ]
        
        for label, value, color in breakdown:
            is_total = label.startswith("**")
            clean_label = label.replace("**", "")
            fmt_value = format_inr(float(value))
            prefix = "+" if float(value) > 0 and not is_total and "Outflow" not in label else ""
            if "Outflow" in label or float(value) < 0:
                prefix = ""
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: {'#1E2329' if is_total else '#161B22'}; border-radius: 6px; margin: 0.25rem 0; border-left: 3px solid {color};">
                <span style="color: {'#E6EDF3' if is_total else '#8B949E'}; font-weight: {'600' if is_total else '400'};">{clean_label}</span>
                <span style="color: {color}; font-weight: {'700' if is_total else '500'};">{prefix}{fmt_value}</span>
            </div>
            ''', unsafe_allow_html=True)
        
        if show_chart:
            st.markdown("---")
            from dashboard.utils.chart_helpers import create_cash_waterfall_chart
            fig = create_cash_waterfall_chart(
                opening=cash_position['opening_balance'],
                inflows=cash_position['confirmed_inflows'],
                outflows=cash_position['confirmed_outflows'],
                pending_in=cash_position.get('pending_inflows', 0),
                pending_out=cash_position.get('pending_outflows', 0),
            )
            st.plotly_chart(fig, use_container_width=True)


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
    
    from dashboard.utils.chart_helpers import create_cash_waterfall_chart
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_cash_position_breakdown(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render detailed cash position breakdown with optional chart."""
    from dashboard.utils.formatters import format_inr
    from dashboard.styles.theme import STATUS_COLORS
    
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
            ("Confirmed Outflows", -float(cash_position['confirmed_outflows']), "#FF6B6B"),
            ("Pending Inflows", cash_position['pending_inflows'], "#F0B429"),
            ("Pending Outflows", -float(cash_position['pending_outflows']), "#F0B429"),
            ("**Expected Cash**", cash_position['expected_cash'], "#E6EDF3"),
            ("Bank Reported", cash_position['bank_cash'], "#8B949E"),
            ("**Variance**", cash_position['variance'], "#00D4AA" if float(cash_position['variance']) >= 0 else "#FF6B6B"),
        ]
        
        for label, value, color in breakdown:
            is_total = label.startswith("**")
            clean_label = label.replace("**", "")
            fmt_value = format_inr(float(value))
            prefix = "+" if float(value) > 0 and not is_total and "Outflow" not in label else ""
            if "Outflow" in label or float(value) < 0:
                prefix = ""
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: {'#1E2329' if is_total else '#161B22'}; border-radius: 6px; margin: 0.25rem 0; border-left: 3px solid {color};">
                <span style="color: {'#E6EDF3' if is_total else '#8B949E'}; font-weight: {'600' if is_total else '400'};">{clean_label}</span>
                <span style="color: {color}; font-weight: {'700' if is_total else '500'};">{prefix}{fmt_value}</span>
            </div>
            ''', unsafe_allow_html=True)
        
        if show_chart:
            st.markdown("---")
            from dashboard.utils.chart_helpers import create_cash_waterfall_chart
            fig = create_cash_waterfall_chart(
                opening=cash_position['opening_balance'],
                inflows=cash_position['confirmed_inflows'],
                outflows=cash_position['confirmed_outflows'],
                pending_in=cash_position.get('pending_inflows', 0),
                pending_out=cash_position.get('pending_outflows', 0),
            )
            st.plotly_chart(fig, use_container_width=True)


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
    
    from dashboard.utils.chart_helpers import create_cash_waterfall_chart
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_cash_position_breakdown(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render detailed cash position breakdown with optional chart."""
    from dashboard.utils.formatters import format_inr
    from dashboard.styles.theme import STATUS_COLORS
    
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
            ("Confirmed Outflows", -float(cash_position['confirmed_outflows']), "#FF6B6B"),
            ("Pending Inflows", cash_position['pending_inflows'], "#F0B429"),
            ("Pending Outflows", -float(cash_position['pending_outflows']), "#F0B429"),
            ("**Expected Cash**", cash_position['expected_cash'], "#E6EDF3"),
            ("Bank Reported", cash_position['bank_cash'], "#8B949E"),
            ("**Variance**", cash_position['variance'], "#00D4AA" if float(cash_position['variance']) >= 0 else "#FF6B6B"),
        ]
        
        for label, value, color in breakdown:
            is_total = label.startswith("**")
            clean_label = label.replace("**", "")
            fmt_value = format_inr(float(value))
            prefix = "+" if float(value) > 0 and not is_total and "Outflow" not in label else ""
            if "Outflow" in label or float(value) < 0:
                prefix = ""
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: {'#1E2329' if is_total else '#161B22'}; border-radius: 6px; margin: 0.25rem 0; border-left: 3px solid {color};">
                <span style="color: {'#E6EDF3' if is_total else '#8B949E'}; font-weight: {'600' if is_total else '400'};">{clean_label}</span>
                <span style="color: {color}; font-weight: {'700' if is_total else '500'};">{prefix}{fmt_value}</span>
            </div>
            ''', unsafe_allow_html=True)
        
        if show_chart:
            st.markdown("---")
            from dashboard.utils.chart_helpers import create_cash_waterfall_chart
            fig = create_cash_waterfall_chart(
                opening=cash_position['opening_balance'],
                inflows=cash_position['confirmed_inflows'],
                outflows=cash_position['confirmed_outflows'],
                pending_in=cash_position.get('pending_inflows', 0),
                pending_out=cash_position.get('pending_outflows', 0),
            )
            st.plotly_chart(fig, use_container_width=True)


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
    
    from dashboard.utils.chart_helpers import create_cash_waterfall_chart
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_cash_position_breakdown(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render detailed cash position breakdown with optional chart."""
    from dashboard.utils.formatters import format_inr
    from dashboard.styles.theme import STATUS_COLORS
    
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
            ("Confirmed Outflows", -float(cash_position['confirmed_outflows']), "#FF6B6B"),
            ("Pending Inflows", cash_position['pending_inflows'], "#F0B429"),
            ("Pending Outflows", -float(cash_position['pending_outflows']), "#F0B429"),
            ("**Expected Cash**", cash_position['expected_cash'], "#E6EDF3"),
            ("Bank Reported", cash_position['bank_cash'], "#8B949E"),
            ("**Variance**", cash_position['variance'], "#00D4AA" if float(cash_position['variance']) >= 0 else "#FF6B6B"),
        ]
        
        for label, value, color in breakdown:
            is_total = label.startswith("**")
            clean_label = label.replace("**", "")
            fmt_value = format_inr(float(value))
            prefix = "+" if float(value) > 0 and not is_total and "Outflow" not in label else ""
            if "Outflow" in label or float(value) < 0:
                prefix = ""
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: {'#1E2329' if is_total else '#161B22'}; border-radius: 6px; margin: 0.25rem 0; border-left: 3px solid {color};">
                <span style="color: {'#E6EDF3' if is_total else '#8B949E'}; font-weight: {'600' if is_total else '400'};">{clean_label}</span>
                <span style="color: {color}; font-weight: {'700' if is_total else '500'};">{prefix}{fmt_value}</span>
            </div>
            ''', unsafe_allow_html=True)
        
        if show_chart:
            st.markdown("---")
            from dashboard.utils.chart_helpers import create_cash_waterfall_chart
            fig = create_cash_waterfall_chart(
                opening=cash_position['opening_balance'],
                inflows=cash_position['confirmed_inflows'],
                outflows=cash_position['confirmed_outflows'],
                pending_in=cash_position.get('pending_inflows', 0),
                pending_out=cash_position.get('pending_outflows', 0),
            )
            st.plotly_chart(fig, use_container_width=True)


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
    
    from dashboard.utils.chart_helpers import create_cash_waterfall_chart
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_cash_position_breakdown(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render detailed cash position breakdown with optional chart."""
    from dashboard.utils.formatters import format_inr
    from dashboard.styles.theme import STATUS_COLORS
    
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
            ("Confirmed Outflows", -float(cash_position['confirmed_outflows']), "#FF6B6B"),
            ("Pending Inflows", cash_position['pending_inflows'], "#F0B429"),
            ("Pending Outflows", -float(cash_position['pending_outflows']), "#F0B429"),
            ("**Expected Cash**", cash_position['expected_cash'], "#E6EDF3"),
            ("Bank Reported", cash_position['bank_cash'], "#8B949E"),
            ("**Variance**", cash_position['variance'], "#00D4AA" if float(cash_position['variance']) >= 0 else "#FF6B6B"),
        ]
        
        for label, value, color in breakdown:
            is_total = label.startswith("**")
            clean_label = label.replace("**", "")
            fmt_value = format_inr(float(value))
            prefix = "+" if float(value) > 0 and not is_total and "Outflow" not in label else ""
            if "Outflow" in label or float(value) < 0:
                prefix = ""
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: {'#1E2329' if is_total else '#161B22'}; border-radius: 6px; margin: 0.25rem 0; border-left: 3px solid {color};">
                <span style="color: {'#E6EDF3' if is_total else '#8B949E'}; font-weight: {'600' if is_total else '400'};">{clean_label}</span>
                <span style="color: {color}; font-weight: {'700' if is_total else '500'};">{prefix}{fmt_value}</span>
            </div>
            ''', unsafe_allow_html=True)
        
        if show_chart:
            st.markdown("---")
            from dashboard.utils.chart_helpers import create_cash_waterfall_chart
            fig = create_cash_waterfall_chart(
                opening=cash_position['opening_balance'],
                inflows=cash_position['confirmed_inflows'],
                outflows=cash_position['confirmed_outflows'],
                pending_in=cash_position.get('pending_inflows', 0),
                pending_out=cash_position.get('pending_outflows', 0),
            )
            st.plotly_chart(fig, use_container_width=True)


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
    
    from dashboard.utils.chart_helpers import create_cash_waterfall_chart
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_cash_position_breakdown(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render detailed cash position breakdown with optional chart."""
    from dashboard.utils.formatters import format_inr
    from dashboard.styles.theme import STATUS_COLORS
    
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
            ("Confirmed Outflows", -float(cash_position['confirmed_outflows']), "#FF6B6B"),
            ("Pending Inflows", cash_position['pending_inflows'], "#F0B429"),
            ("Pending Outflows", -float(cash_position['pending_outflows']), "#F0B429"),
            ("**Expected Cash**", cash_position['expected_cash'], "#E6EDF3"),
            ("Bank Reported", cash_position['bank_cash'], "#8B949E"),
            ("**Variance**", cash_position['variance'], "#00D4AA" if float(cash_position['variance']) >= 0 else "#FF6B6B"),
        ]
        
        for label, value, color in breakdown:
            is_total = label.startswith("**")
            clean_label = label.replace("**", "")
            fmt_value = format_inr(float(value))
            prefix = "+" if float(value) > 0 and not is_total and "Outflow" not in label else ""
            if "Outflow" in label or float(value) < 0:
                prefix = ""
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: {'#1E2329' if is_total else '#161B22'}; border-radius: 6px; margin: 0.25rem 0; border-left: 3px solid {color};">
                <span style="color: {'#E6EDF3' if is_total else '#8B949E'}; font-weight: {'600' if is_total else '400'};">{clean_label}</span>
                <span style="color: {color}; font-weight: {'700' if is_total else '500'};">{prefix}{fmt_value}</span>
            </div>
            ''', unsafe_allow_html=True)
        
        if show_chart:
            st.markdown("---")
            from dashboard.utils.chart_helpers import create_cash_waterfall_chart
            fig = create_cash_waterfall_chart(
                opening=cash_position['opening_balance'],
                inflows=cash_position['confirmed_inflows'],
                outflows=cash_position['confirmed_outflows'],
                pending_in=cash_position.get('pending_inflows', 0),
                pending_out=cash_position.get('pending_outflows', 0),
            )
            st.plotly_chart(fig, use_container_width=True)


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
    
    from dashboard.utils.chart_helpers import create_cash_waterfall_chart
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_cash_position_breakdown(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render detailed cash position breakdown with optional chart."""
    from dashboard.utils.formatters import format_inr
    from dashboard.styles.theme import STATUS_COLORS
    
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
            ("Confirmed Outflows", -float(cash_position['confirmed_outflows']), "#FF6B6B"),
            ("Pending Inflows", cash_position['pending_inflows'], "#F0B429"),
            ("Pending Outflows", -float(cash_position['pending_outflows']), "#F0B429"),
            ("**Expected Cash**", cash_position['expected_cash'], "#E6EDF3"),
            ("Bank Reported", cash_position['bank_cash'], "#8B949E"),
            ("**Variance**", cash_position['variance'], "#00D4AA" if float(cash_position['variance']) >= 0 else "#FF6B6B"),
        ]
        
        for label, value, color in breakdown:
            is_total = label.startswith("**")
            clean_label = label.replace("**", "")
            fmt_value = format_inr(float(value))
            prefix = "+" if float(value) > 0 and not is_total and "Outflow" not in label else ""
            if "Outflow" in label or float(value) < 0:
                prefix = ""
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: {'#1E2329' if is_total else '#161B22'}; border-radius: 6px; margin: 0.25rem 0; border-left: 3px solid {color};">
                <span style="color: {'#E6EDF3' if is_total else '#8B949E'}; font-weight: {'600' if is_total else '400'};">{clean_label}</span>
                <span style="color: {color}; font-weight: {'700' if is_total else '500'};">{prefix}{fmt_value}</span>
            </div>
            ''', unsafe_allow_html=True)
        
        if show_chart:
            st.markdown("---")
            from dashboard.utils.chart_helpers import create_cash_waterfall_chart
            fig = create_cash_waterfall_chart(
                opening=cash_position['opening_balance'],
                inflows=cash_position['confirmed_inflows'],
                outflows=cash_position['confirmed_outflows'],
                pending_in=cash_position.get('pending_inflows', 0),
                pending_out=cash_position.get('pending_outflows', 0),
            )
            st.plotly_chart(fig, use_container_width=True)


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
    
    from dashboard.utils.chart_helpers import create_cash_waterfall_chart
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_cash_position_breakdown(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render detailed cash position breakdown with optional chart."""
    from dashboard.utils.formatters import format_inr
    from dashboard.styles.theme import STATUS_COLORS
    
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
            ("Confirmed Outflows", -float(cash_position['confirmed_outflows']), "#FF6B6B"),
            ("Pending Inflows", cash_position['pending_inflows'], "#F0B429"),
            ("Pending Outflows", -float(cash_position['pending_outflows']), "#F0B429"),
            ("**Expected Cash**", cash_position['expected_cash'], "#E6EDF3"),
            ("Bank Reported", cash_position['bank_cash'], "#8B949E"),
            ("**Variance**", cash_position['variance'], "#00D4AA" if float(cash_position['variance']) >= 0 else "#FF6B6B"),
        ]
        
        for label, value, color in breakdown:
            is_total = label.startswith("**")
            clean_label = label.replace("**", "")
            fmt_value = format_inr(float(value))
            prefix = "+" if float(value) > 0 and not is_total and "Outflow" not in label else ""
            if "Outflow" in label or float(value) < 0:
                prefix = ""
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: {'#1E2329' if is_total else '#161B22'}; border-radius: 6px; margin: 0.25rem 0; border-left: 3px solid {color};">
                <span style="color: {'#E6EDF3' if is_total else '#8B949E'}; font-weight: {'600' if is_total else '400'};">{clean_label}</span>
                <span style="color: {color}; font-weight: {'700' if is_total else '500'};">{prefix}{fmt_value}</span>
            </div>
            ''', unsafe_allow_html=True)
        
        if show_chart:
            st.markdown("---")
            from dashboard.utils.chart_helpers import create_cash_waterfall_chart
            fig = create_cash_waterfall_chart(
                opening=cash_position['opening_balance'],
                inflows=cash_position['confirmed_inflows'],
                outflows=cash_position['confirmed_outflows'],
                pending_in=cash_position.get('pending_inflows', 0),
                pending_out=cash_position.get('pending_outflows', 0),
            )
            st.plotly_chart(fig, use_container_width=True)


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
    
    from dashboard.utils.chart_helpers import create_cash_waterfall_chart
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_cash_position_breakdown(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render detailed cash position breakdown with optional chart."""
    from dashboard.utils.formatters import format_inr
    from dashboard.styles.theme import STATUS_COLORS
    
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
            ("Confirmed Outflows", -float(cash_position['confirmed_outflows']), "#FF6B6B"),
            ("Pending Inflows", cash_position['pending_inflows'], "#F0B429"),
            ("Pending Outflows", -float(cash_position['pending_outflows']), "#F0B429"),
            ("**Expected Cash**", cash_position['expected_cash'], "#E6EDF3"),
            ("Bank Reported", cash_position['bank_cash'], "#8B949E"),
            ("**Variance**", cash_position['variance'], "#00D4AA" if float(cash_position['variance']) >= 0 else "#FF6B6B"),
        ]
        
        for label, value, color in breakdown:
            is_total = label.startswith("**")
            clean_label = label.replace("**", "")
            fmt_value = format_inr(float(value))
            prefix = "+" if float(value) > 0 and not is_total and "Outflow" not in label else ""
            if "Outflow" in label or float(value) < 0:
                prefix = ""
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: {'#1E2329' if is_total else '#161B22'}; border-radius: 6px; margin: 0.25rem 0; border-left: 3px solid {color};">
                <span style="color: {'#E6EDF3' if is_total else '#8B949E'}; font-weight: {'600' if is_total else '400'};">{clean_label}</span>
                <span style="color: {color}; font-weight: {'700' if is_total else '500'};">{prefix}{fmt_value}</span>
            </div>
            ''', unsafe_allow_html=True)
        
        if show_chart:
            st.markdown("---")
            from dashboard.utils.chart_helpers import create_cash_waterfall_chart
            fig = create_cash_waterfall_chart(
                opening=cash_position['opening_balance'],
                inflows=cash_position['confirmed_inflows'],
                outflows=cash_position['confirmed_outflows'],
                pending_in=cash_position.get('pending_inflows', 0),
                pending_out=cash_position.get('pending_outflows', 0),
            )
            st.plotly_chart(fig, use_container_width=True)


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
    
    from dashboard.utils.chart_helpers import create_cash_waterfall_chart
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_cash_position_breakdown(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render detailed cash position breakdown with optional chart."""
    from dashboard.utils.formatters import format_inr
    from dashboard.styles.theme import STATUS_COLORS
    
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
            ("Confirmed Outflows", -float(cash_position['confirmed_outflows']), "#FF6B6B"),
            ("Pending Inflows", cash_position['pending_inflows'], "#F0B429"),
            ("Pending Outflows", -float(cash_position['pending_outflows']), "#F0B429"),
            ("**Expected Cash**", cash_position['expected_cash'], "#E6EDF3"),
            ("Bank Reported", cash_position['bank_cash'], "#8B949E"),
            ("**Variance**", cash_position['variance'], "#00D4AA" if float(cash_position['variance']) >= 0 else "#FF6B6B"),
        ]
        
        for label, value, color in breakdown:
            is_total = label.startswith("**")
            clean_label = label.replace("**", "")
            fmt_value = format_inr(float(value))
            prefix = "+" if float(value) > 0 and not is_total and "Outflow" not in label else ""
            if "Outflow" in label or float(value) < 0:
                prefix = ""
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: {'#1E2329' if is_total else '#161B22'}; border-radius: 6px; margin: 0.25rem 0; border-left: 3px solid {color};">
                <span style="color: {'#E6EDF3' if is_total else '#8B949E'}; font-weight: {'600' if is_total else '400'};">{clean_label}</span>
                <span style="color: {color}; font-weight: {'700' if is_total else '500'};">{prefix}{fmt_value}</span>
            </div>
            ''', unsafe_allow_html=True)
        
        if show_chart:
            st.markdown("---")
            from dashboard.utils.chart_helpers import create_cash_waterfall_chart
            fig = create_cash_waterfall_chart(
                opening=cash_position['opening_balance'],
                inflows=cash_position['confirmed_inflows'],
                outflows=cash_position['confirmed_outflows'],
                pending_in=cash_position.get('pending_inflows', 0),
                pending_out=cash_position.get('pending_outflows', 0),
            )
            st.plotly_chart(fig, use_container_width=True)


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
    
    from dashboard.utils.chart_helpers import create_cash_waterfall_chart
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_cash_position_breakdown(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render detailed cash position breakdown with optional chart."""
    from dashboard.utils.formatters import format_inr
    from dashboard.styles.theme import STATUS_COLORS
    
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
            ("Confirmed Outflows", -float(cash_position['confirmed_outflows']), "#FF6B6B"),
            ("Pending Inflows", cash_position['pending_inflows'], "#F0B429"),
            ("Pending Outflows", -float(cash_position['pending_outflows']), "#F0B429"),
            ("**Expected Cash**", cash_position['expected_cash'], "#E6EDF3"),
            ("Bank Reported", cash_position['bank_cash'], "#8B949E"),
            ("**Variance**", cash_position['variance'], "#00D4AA" if float(cash_position['variance']) >= 0 else "#FF6B6B"),
        ]
        
        for label, value, color in breakdown:
            is_total = label.startswith("**")
            clean_label = label.replace("**", "")
            fmt_value = format_inr(float(value))
            prefix = "+" if float(value) > 0 and not is_total and "Outflow" not in label else ""
            if "Outflow" in label or float(value) < 0:
                prefix = ""
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: {'#1E2329' if is_total else '#161B22'}; border-radius: 6px; margin: 0.25rem 0; border-left: 3px solid {color};">
                <span style="color: {'#E6EDF3' if is_total else '#8B949E'}; font-weight: {'600' if is_total else '400'};">{clean_label}</span>
                <span style="color: {color}; font-weight: {'700' if is_total else '500'};">{prefix}{fmt_value}</span>
            </div>
            ''', unsafe_allow_html=True)
        
        if show_chart:
            st.markdown("---")
            from dashboard.utils.chart_helpers import create_cash_waterfall_chart
            fig = create_cash_waterfall_chart(
                opening=cash_position['opening_balance'],
                inflows=cash_position['confirmed_inflows'],
                outflows=cash_position['confirmed_outflows'],
                pending_in=cash_position.get('pending_inflows', 0),
                pending_out=cash_position.get('pending_outflows', 0),
            )
            st.plotly_chart(fig, use_container_width=True)


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
    
    from dashboard.utils.chart_helpers import create_cash_waterfall_chart
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_cash_position_breakdown(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render detailed cash position breakdown with optional chart."""
    from dashboard.utils.formatters import format_inr
    from dashboard.styles.theme import STATUS_COLORS
    
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
            ("Confirmed Outflows", -float(cash_position['confirmed_outflows']), "#FF6B6B"),
            ("Pending Inflows", cash_position['pending_inflows'], "#F0B429"),
            ("Pending Outflows", -float(cash_position['pending_outflows']), "#F0B429"),
            ("**Expected Cash**", cash_position['expected_cash'], "#E6EDF3"),
            ("Bank Reported", cash_position['bank_cash'], "#8B949E"),
            ("**Variance**", cash_position['variance'], "#00D4AA" if float(cash_position['variance']) >= 0 else "#FF6B6B"),
        ]
        
        for label, value, color in breakdown:
            is_total = label.startswith("**")
            clean_label = label.replace("**", "")
            fmt_value = format_inr(float(value))
            prefix = "+" if float(value) > 0 and not is_total and "Outflow" not in label else ""
            if "Outflow" in label or float(value) < 0:
                prefix = ""
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: {'#1E2329' if is_total else '#161B22'}; border-radius: 6px; margin: 0.25rem 0; border-left: 3px solid {color};">
                <span style="color: {'#E6EDF3' if is_total else '#8B949E'}; font-weight: {'600' if is_total else '400'};">{clean_label}</span>
                <span style="color: {color}; font-weight: {'700' if is_total else '500'};">{prefix}{fmt_value}</span>
            </div>
            ''', unsafe_allow_html=True)
        
        if show_chart:
            st.markdown("---")
            from dashboard.utils.chart_helpers import create_cash_waterfall_chart
            fig = create_cash_waterfall_chart(
                opening=cash_position['opening_balance'],
                inflows=cash_position['confirmed_inflows'],
                outflows=cash_position['confirmed_outflows'],
                pending_in=cash_position.get('pending_inflows', 0),
                pending_out=cash_position.get('pending_outflows', 0),
            )
            st.plotly_chart(fig, use_container_width=True)


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
    
    from dashboard.utils.chart_helpers import create_cash_waterfall_chart
    fig = create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_cash_position_breakdown(
    cash_position: dict,
    show_chart: bool = True,
) -> None:
    """Render detailed cash position breakdown with optional chart."""
    from dashboard.utils.formatters import format_inr
    from dashboard.styles.theme import STATUS_COLORS
    
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
            ("Confirmed Outflows", -float(cash_position['confirmed_outflows']), "#FF6B6B"),
            ("Pending Inflows", cash_position['pending_inflows'], "#F0B429"),
            ("Pending Outflows", -float(cash_position['pending_outflows']), "#F0B429"),
            ("**Expected Cash**", cash_position['expected_cash'], "#E6EDF3"),
            ("Bank Reported", cash_position['bank_cash'], "#8B949E"),
            ("**Variance**", cash_position['variance'], "#00D4AA" if float(cash_position['variance']) >= 0 else "#FF6B6B"),
        ]
        
        for label, value, color in breakdown:
            is_total = label.startswith("**")
            clean_label = label.replace("**", "")
            fmt_value = format_inr(float(value))
            prefix = "+" if float(value) > 0 and not is_total and "Outflow" not in label else ""
            if "Outflow" in label or float(value) < 0:
                prefix = ""
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: {'#1E2329' if is_total else '#161B22'}; border-radius: 6px; margin: 0.25rem 0; border-left: 3px solid {color};">
                <span style="color: {'#E6EDF3' if is_total else '#8B949E'}; font-weight: {'600' if is_total else '400'};">{clean_label}</span>
                <span style="color: {color}; font-weight: {'700' if is_total else '500'};">{prefix}{fmt_value}</span>
            </div>
            ''', unsafe_allow_html=True)
        
        if show_chart:
            st.markdown("---")
            from dashboard.utils.chart_helpers import create_cash_waterfall_chart
            fig = create_cash_waterfall_chart(
                opening=cash_position['opening_balance'],
                inflows=cash_position['confirmed_inflows'],
                outflows=cash_position['confirmed_outflows'],
                pending_in=cash_position.get('pending_inflows', 0),
                pending_out=cash_position.get('pending_outflows', 0),
            )
            st.plotly_chart(fig, use_container_width=True)