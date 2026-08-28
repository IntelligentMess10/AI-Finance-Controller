"""
KPI Card component for displaying key metrics.
"""

import streamlit as st
from typing import Optional
from dashboard.utils.formatters import format_inr, format_pct


def render_kpi_card(
    label: str,
    value: str,
    delta: str = None,
    delta_type: str = "normal",
    help_text: str = None,
) -> None:
    """
    Render a KPI metric card.
    
    Args:
        label: Label for the metric
        value: Main value to display
        delta: Optional delta/change indicator
        delta_type: "normal" (green for positive), "inverse" (red for negative), "off" (no color)
        help_text: Optional tooltip text
    """
    delta_color = "normal"
    if delta and delta.startswith("-"):
        delta_type = "inverse"
    elif delta and delta.startswith("+"):
        delta_type = "normal"
    else:
        delta_type = "normal"
    
    st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_type,
        help=help_text,
    )


def render_kpi_card(
    label: str,
    value: str,
    delta: str = None,
    delta_type: str = "normal",
    help_text: str = None,
    card_class: str = "kpi-card",
) -> None:
    """
    Render a custom KPI card using Streamlit metric with custom styling.
    
    Args:
        label: Label for the metric
        value: Main value to display
        delta: Optional delta/change indicator
        delta_type: "normal" (green for positive), "inverse" (red for negative), "off" (no color)
        help_text: Optional tooltip text
    """
    st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_type,
    )


def render_kpi_row(labels: list, values: list, deltas: list = None, help_texts: list = None):
    """
    Render a row of KPI cards.
    
    Args:
        labels: List of labels
        values: List of values
        deltas: Optional list of delta strings
        help_texts: Optional list of help texts
    """
    cols = st.columns(len(labels))
    
    for i, label in enumerate(labels):
        with cols[i]:
            value = values[i] if i < len(values) else "—"
            delta = deltas[i] if deltas and i < len(deltas) else None
            help_text = help_texts[i] if help_texts and i < len(help_texts) else None
            
            st.metric(
                label=label,
                value=value,
                delta=help_text if delta is None else None,
                delta_color="normal",
            )
            # Custom delta display would need HTML


def render_kpi_row(
    metrics: list,
    columns: int = 4,
) -> None:
    """
    Render a row of KPI cards.
    
    Args:
        metrics: List of dicts with keys: label, value, delta (optional), delta_type (optional)
        columns: Number of columns
    """
    cols = st.columns(min(len(metrics), 4))
    
    for i, metric in enumerate(metrics):
        with cols[i % columns]:
            label = metric.get("label", "")
            value = metric.get("value", "—")
            delta = metric.get("delta")
            delta_type = metric.get("delta_type", "normal")
            help_text = metric.get("help")
            
            st.metric(
                label=label,
                value=value,
                delta=metric.get("delta"),
                delta_color=metric.get("delta_type", "normal"),
                help=metric.get("help"),
            )


def render_kpi_grid(metrics: list, cols: int = 4):
    """
    Render a grid of KPI cards.
    
    Args:
        metrics: List of dicts with keys: label, value, delta (optional), delta_type (optional)
        cols: Number of columns
    """
    cols = st.columns(min(len(metrics), 4))
    
    for i, metric in enumerate(metrics):
        with cols[i % 4]:
            label = metric.get("label", "")
            value = metric.get("value", "—")
            delta = metric.get("delta")
            delta_type = metric.get("delta_type", "normal")
            help_text = metric.get("help")
            
            st.metric(
                label=label,
                value=value,
                delta=delta,
                delta_color=delta_type,
            )
            if metric.get("help"):
                st.caption(metric["help"])


def render_kpi_row_simple(metrics: list):
    """
    Render a simple row of KPI metrics using Streamlit's metric.
    
    Args:
        metrics: List of dicts with keys: label, value, delta (optional), delta_color (optional)
    """
    cols = st.columns(len(metrics))
    
    for i, metric in enumerate(metrics):
        with cols[i]:
            label = metric.get("label", "")
            value = metric.get("value", "—")
            delta = metric.get("delta")
            delta_color = metric.get("delta_color", "normal")
            
            st.metric(
                label=metric.get("label", ""),
                value=metric.get("value", "—"),
                delta=metric.get("delta"),
                delta_color=metric.get("delta_color", "normal"),
            )