"""
Status badge component for displaying transaction/exception statuses.
"""

import streamlit as st
from typing import Optional

from dashboard.styles.theme import get_status_color, STATUS_COLORS


def render_status_badge(status: str, size: str = "normal") -> str:
    """
    Generate HTML for a status badge.
    
    Args:
        status: Status string (e.g., "matched", "probable_match", "exception")
        size: "small" or "normal"
        
    Returns:
        HTML string for the status badge
    """
    from dashboard.styles.theme import STATUS_COLORS, get_status_color
    
    status_lower = status.lower().replace(" ", "_")
    color = STATUS_COLORS.get(status.lower(), "#8B949E")
    
    # Format label
    label = status.replace("_", " ").title()
    
    padding = "0.2rem 0.5rem" if size == "small" else "0.25rem 0.75rem"
    font_size = "0.7rem" if size == "small" else "0.75rem"
    
    return f'''
    <span style="
        background: {STATUS_COLORS.get(status.lower(), "#8B949E")};
        color: #E6EDF3;
        padding: 0.2rem 0.5rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: capitalize;
        display: inline-block;
        white-space: nowrap;
    ">
        {status.replace("_", " ").title()}
    </span>'''


def render_status_badge(status: str, size: str = "normal") -> None:
    """
    Render a status badge using Streamlit markdown.
    
    Args:
        status: Status string (e.g., "matched", "probable_match", "exception")
        size: "small" or "normal"
    """
    from dashboard.styles.theme import STATUS_COLORS
    
    status_lower = status.lower().replace(" ", "_")
    color = STATUS_COLORS.get(status.lower(), "#8B949E")
    
    # Format label
    label = status.replace("_", " ").title()
    
    padding = "0.2rem 0.5rem" if size == "small" else "0.25rem 0.75rem"
    font_size = "0.7rem" if size == "small" else "0.75rem"
    
    st.markdown(f'''
    <span style="
        background: {STATUS_COLORS.get(status.lower(), "#8B949E")};
        color: #E6EDF3;
        padding: 0.2rem 0.5rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: capitalize;
        display: inline-block;
        white-space: nowrap;
    ">
        {status.replace("_", " ").title()}
    </span>''', unsafe_allow_html=True)


def render_status_badge_inline(status: str) -> str:
    """
    Return HTML string for a status badge (for use in tables/dataframes).
    """
    from dashboard.styles.theme import STATUS_COLORS
    
    color = STATUS_COLORS.get(status.lower(), "#8B949E")
    label = status.replace("_", " ").title()
    
    return f'''
    <span style="
        background: {STATUS_COLORS.get(status.lower(), "#8B949E")};
        color: #E6EDF3;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: capitalize;
        display: inline-block;
        white-space: nowrap;
    ">
        {status.replace("_", " ").title()}
    </span>'''


def render_status_badge_streamlit(status: str) -> None:
    """Render status badge using Streamlit markdown."""
    st.markdown(render_status_badge_inline(status), unsafe_allow_html=True)


def render_status_badge_inline(status: str) -> str:
    """Return HTML string for status badge."""
    from dashboard.styles.theme import STATUS_COLORS
    
    status_lower = status.lower().replace(" ", "_")
    color = STATUS_COLORS.get(status_lower, "#8B949E")
    label = status.replace("_", " ").title()
    
    return f'''
    <span style="
        background: {STATUS_COLORS.get(status.lower(), "#8B949E")};
        color: #E6EDF3;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: capitalize;
        display: inline-block;
        white-space: nowrap;
    ">
        {status.replace("_", " ").title()}
    </span>'''


def status_badge_html(status: str) -> str:
    """Generate HTML for status badge (for use in dataframes)."""
    from dashboard.styles.theme import STATUS_COLORS
    
    status_lower = status.lower().replace(" ", "_")
    color = STATUS_COLORS.get(status.lower(), "#8B949E")
    label = status.replace("_", " ").title()
    
    return f'<span style="background:{STATUS_COLORS.get(status.lower(), "#8B949E")}; color:#E6EDF3; padding:0.25rem 0.75rem; border-radius:9999px; font-size:0.75rem; font-weight:600; text-transform:capitalize; display:inline-block;">{status.replace("_", " ").title()}</span>'


def get_status_color(status: str) -> str:
    """Get color for a status string."""
    from dashboard.styles.theme import get_status_color
    return get_status_color(status)


def render_status_badge_simple(status: str) -> None:
    """Simple status badge using Streamlit's native components."""
    status_colors = {
        "matched": ("✅", "success"),
        "probable_match": ("⚠️", "warning"),
        "exception": ("❌", "error"),
        "unresolved": ("❓", "info"),
        "escalated": ("⚠️", "warning"),
        "open": ("🔵", "info"),
        "investigating": ("🔍", "info"),
        "resolved": ("✅", "success"),
        "escalated": ("⚠️", "warning"),
        "unresolved": ("❓", "info"),
    }
    
    icon, color = status_colors.get(status.lower().replace(" ", "_"), ("❓", "info"))
    st.markdown(f":{color}[{status.replace('_', ' ').title()}]")