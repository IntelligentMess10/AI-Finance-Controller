"""
CSS injection utilities for Streamlit.
"""

from dashboard.styles.theme import generate_css


def inject_css() -> None:
    """Inject custom CSS into Streamlit."""
    import streamlit as st
    st.markdown(generate_css(), unsafe_allow_html=True)


def get_theme() -> dict:
    """Get the theme dictionary."""
    from dashboard.styles.theme import THEME
    return THEME


def get_status_color(status: str) -> str:
    """Get color for a status string."""
    from dashboard.styles.theme import get_status_color
    return get_status_color(status)


def get_source_color(source: str) -> str:
    """Get color for a source."""
    from dashboard.styles.theme import get_source_color
    return get_source_color(source)


def get_direction_color(direction: str) -> str:
    """Get color for transaction direction."""
    from dashboard.styles.theme import get_direction_color
    return get_direction_color(direction)