"""
Forecast Chart Component.
"""

import streamlit as st
import pandas as pd
from typing import List, Optional, Dict, Any
from dashboard.utils.chart_helpers import create_forecast_chart, create_forecast_summary_chart
from dashboard.utils.formatters import format_inr
from dashboard.utils.chart_helpers import create_forecast_chart, create_forecast_summary_chart
from dashboard.utils.formatters import format_inr


def render_forecast_chart(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    key: str = "",
) -> None:
    """
    Render a forecast chart with inflows/outflows over time.
    
    Args:
        forecast_entries: List of dicts with keys: date, amount, horizon_days, event_name
        horizons: List of horizon days
        key: Unique key for Streamlit
    """
    if horizons is None:
        horizons = [7, 14, 30]
    
    fig = create_forecast_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True, key=key)


def render_forecast_summary(
    forecast_entries: List[dict],
    horizons: List[int] = None,
) -> None:
    """
    Render forecast summary with horizon bars.
    
    Args:
        forecast_entries: List of forecast entries
        horizons: List of horizon days
    """
    if not forecast_entries:
        st.info("No forecast data available")
        return
    
    fig = create_forecast_summary_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True)


def render_forecast_chart_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Cash Flow Forecast",
    key: str = "",
) -> None:
    """Render forecast chart in a card container."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_chart
    fig = create_forecast_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_summary_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Forecast Summary",
) -> None:
    """Render forecast summary with horizontal bars by horizon."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_summary_chart
    fig = create_forecast_summary_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_table(
    forecast_entries: List[dict],
    horizons: List[int] = None,
) -> None:
    """Render forecast entries as a table."""
    if not forecast_entries:
        st.info("No forecast data available")
        return
    
    df = pd.DataFrame(forecast_entries)
    if df.empty:
        st.info("No forecast data available")
        return
    
    if horizons is None:
        horizons = [7, 14, 30]
    
    # Format for display
    df_display = df.copy()
    df_display['amount_fmt'] = df['amount'].apply(lambda x: f"₹{x:,.2f}")
    df_display['date_fmt'] = pd.to_datetime(df['forecast_date']).dt.strftime('%d %b %Y')
    
    st.dataframe(
        df[['date_fmt', 'amount_fmt', 'event_name', 'horizon_days', 'frequency']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "forecast_date": "Date",
            "amount_fmt": "Amount",
            "event_name": "Event",
            "horizon_days": "Horizon (days)",
            "frequency": "Frequency",
        },
    )


def render_forecast_chart_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Cash Flow Forecast",
    key: str = "",
) -> None:
    """Render forecast chart in a card container."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_chart
    fig = create_forecast_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_summary_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Forecast Summary",
) -> None:
    """Render forecast summary with horizontal bars by horizon."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_summary_chart
    fig = create_forecast_summary_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_table(
    forecast_entries: List[dict],
    horizons: List[int] = None,
) -> None:
    """Render forecast entries as a table."""
    if not forecast_entries:
        st.info("No forecast data available")
        return
    
    df = pd.DataFrame(forecast_entries)
    if df.empty:
        st.info("No forecast data available")
        return
    
    if horizons is None:
        horizons = [7, 14, 30]
    
    # Format for display
    df_display = df.copy()
    df_display['amount_fmt'] = df['amount'].apply(lambda x: f"₹{x:,.2f}")
    df_display['date_fmt'] = pd.to_datetime(df['forecast_date']).dt.strftime('%d %b %Y')
    
    st.dataframe(
        df[['date_fmt', 'amount_fmt', 'event_name', 'horizon_days', 'frequency']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "forecast_date": "Date",
            "amount_fmt": "Amount",
            "event_name": "Event",
            "horizon_days": "Horizon (days)",
            "frequency": "Frequency",
        },
    )


def render_forecast_chart_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Cash Flow Forecast",
    key: str = "",
) -> None:
    """Render forecast chart in a card container."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_chart
    fig = create_forecast_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_summary_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Forecast Summary",
) -> None:
    """Render forecast summary with horizontal bars by horizon."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_summary_chart
    fig = create_forecast_summary_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_table(
    forecast_entries: List[dict],
    horizons: List[int] = None,
) -> None:
    """Render forecast entries as a table."""
    if not forecast_entries:
        st.info("No forecast data available")
        return
    
    df = pd.DataFrame(forecast_entries)
    if df.empty:
        st.info("No forecast data available")
        return
    
    if horizons is None:
        horizons = [7, 14, 30]
    
    # Format for display
    df_display = df.copy()
    df_display['amount_fmt'] = df['amount'].apply(lambda x: f"₹{x:,.2f}")
    df_display['date_fmt'] = pd.to_datetime(df['forecast_date']).dt.strftime('%d %b %Y')
    
    st.dataframe(
        df[['date_fmt', 'amount_fmt', 'event_name', 'horizon_days', 'frequency']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "forecast_date": "Date",
            "amount_fmt": "Amount",
            "event_name": "Event",
            "horizon_days": "Horizon (days)",
            "frequency": "Frequency",
        },
    )


def render_forecast_chart_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Cash Flow Forecast",
    key: str = "",
) -> None:
    """Render forecast chart in a card container."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_chart
    fig = create_forecast_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_summary_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Forecast Summary",
) -> None:
    """Render forecast summary with horizontal bars by horizon."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_summary_chart
    fig = create_forecast_summary_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_table(
    forecast_entries: List[dict],
    horizons: List[int] = None,
) -> None:
    """Render forecast entries as a table."""
    if not forecast_entries:
        st.info("No forecast data available")
        return
    
    df = pd.DataFrame(forecast_entries)
    if df.empty:
        st.info("No forecast data available")
        return
    
    if horizons is None:
        horizons = [7, 14, 30]
    
    # Format for display
    df_display = df.copy()
    df_display['amount_fmt'] = df['amount'].apply(lambda x: f"₹{x:,.2f}")
    df_display['date_fmt'] = pd.to_datetime(df['forecast_date']).dt.strftime('%d %b %Y')
    
    st.dataframe(
        df[['date_fmt', 'amount_fmt', 'event_name', 'horizon_days', 'frequency']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "forecast_date": "Date",
            "amount_fmt": "Amount",
            "event_name": "Event",
            "horizon_days": "Horizon (days)",
            "frequency": "Frequency",
        },
    )


def render_forecast_chart_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Cash Flow Forecast",
    key: str = "",
) -> None:
    """Render forecast chart in a card container."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_chart
    fig = create_forecast_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_summary_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Forecast Summary",
) -> None:
    """Render forecast summary with horizontal bars by horizon."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_summary_chart
    fig = create_forecast_summary_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_table(
    forecast_entries: List[dict],
    horizons: List[int] = None,
) -> None:
    """Render forecast entries as a table."""
    if not forecast_entries:
        st.info("No forecast data available")
        return
    
    df = pd.DataFrame(forecast_entries)
    if df.empty:
        st.info("No forecast data available")
        return
    
    if horizons is None:
        horizons = [7, 14, 30]
    
    # Format for display
    df_display = df.copy()
    df_display['amount_fmt'] = df['amount'].apply(lambda x: f"₹{x:,.2f}")
    df_display['date_fmt'] = pd.to_datetime(df['forecast_date']).dt.strftime('%d %b %Y')
    
    st.dataframe(
        df[['date_fmt', 'amount_fmt', 'event_name', 'horizon_days', 'frequency']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "forecast_date": "Date",
            "amount_fmt": "Amount",
            "event_name": "Event",
            "horizon_days": "Horizon (days)",
            "frequency": "Frequency",
        },
    )


def render_forecast_chart_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Cash Flow Forecast",
    key: str = "",
) -> None:
    """Render forecast chart in a card container."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_chart
    fig = create_forecast_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_summary_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Forecast Summary",
) -> None:
    """Render forecast summary with horizontal bars by horizon."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_summary_chart
    fig = create_forecast_summary_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_table(
    forecast_entries: List[dict],
    horizons: List[int] = None,
) -> None:
    """Render forecast entries as a table."""
    if not forecast_entries:
        st.info("No forecast data available")
        return
    
    df = pd.DataFrame(forecast_entries)
    if df.empty:
        st.info("No forecast data available")
        return
    
    if horizons is None:
        horizons = [7, 14, 30]
    
    # Format for display
    df_display = df.copy()
    df_display['amount_fmt'] = df['amount'].apply(lambda x: f"₹{x:,.2f}")
    df_display['date_fmt'] = pd.to_datetime(df['forecast_date']).dt.strftime('%d %b %Y')
    
    st.dataframe(
        df[['date_fmt', 'amount_fmt', 'event_name', 'horizon_days', 'frequency']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "forecast_date": "Date",
            "amount_fmt": "Amount",
            "event_name": "Event",
            "horizon_days": "Horizon (days)",
            "frequency": "Frequency",
        },
    )


def render_forecast_chart_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Cash Flow Forecast",
    key: str = "",
) -> None:
    """Render forecast chart in a card container."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_chart
    fig = create_forecast_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_summary_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Forecast Summary",
) -> None:
    """Render forecast summary with horizontal bars by horizon."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_summary_chart
    fig = create_forecast_summary_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_table(
    forecast_entries: List[dict],
    horizons: List[int] = None,
) -> None:
    """Render forecast entries as a table."""
    if not forecast_entries:
        st.info("No forecast data available")
        return
    
    df = pd.DataFrame(forecast_entries)
    if df.empty:
        st.info("No forecast data available")
        return
    
    if horizons is None:
        horizons = [7, 14, 30]
    
    # Format for display
    df_display = df.copy()
    df_display['amount_fmt'] = df['amount'].apply(lambda x: f"₹{x:,.2f}")
    df_display['date_fmt'] = pd.to_datetime(df['forecast_date']).dt.strftime('%d %b %Y')
    
    st.dataframe(
        df[['date_fmt', 'amount_fmt', 'event_name', 'horizon_days', 'frequency']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "forecast_date": "Date",
            "amount_fmt": "Amount",
            "event_name": "Event",
            "horizon_days": "Horizon (days)",
            "frequency": "Frequency",
        },
    )


def render_forecast_chart_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Cash Flow Forecast",
    key: str = "",
) -> None:
    """Render forecast chart in a card container."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_chart
    fig = create_forecast_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_summary_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Forecast Summary",
) -> None:
    """Render forecast summary with horizontal bars by horizon."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_summary_chart
    fig = create_forecast_summary_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_table(
    forecast_entries: List[dict],
    horizons: List[int] = None,
) -> None:
    """Render forecast entries as a table."""
    if not forecast_entries:
        st.info("No forecast data available")
        return
    
    df = pd.DataFrame(forecast_entries)
    if df.empty:
        st.info("No forecast data available")
        return
    
    if horizons is None:
        horizons = [7, 14, 30]
    
    # Format for display
    df_display = df.copy()
    df_display['amount_fmt'] = df['amount'].apply(lambda x: f"₹{x:,.2f}")
    df_display['date_fmt'] = pd.to_datetime(df['forecast_date']).dt.strftime('%d %b %Y')
    
    st.dataframe(
        df[['date_fmt', 'amount_fmt', 'event_name', 'horizon_days', 'frequency']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "forecast_date": "Date",
            "amount_fmt": "Amount",
            "event_name": "Event",
            "horizon_days": "Horizon (days)",
            "frequency": "Frequency",
        },
    )


def render_forecast_chart_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Cash Flow Forecast",
    key: str = "",
) -> None:
    """Render forecast chart in a card container."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_chart
    fig = create_forecast_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_summary_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Forecast Summary",
) -> None:
    """Render forecast summary with horizontal bars by horizon."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_summary_chart
    fig = create_forecast_summary_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_table(
    forecast_entries: List[dict],
    horizons: List[int] = None,
) -> None:
    """Render forecast entries as a table."""
    if not forecast_entries:
        st.info("No forecast data available")
        return
    
    df = pd.DataFrame(forecast_entries)
    if df.empty:
        st.info("No forecast data available")
        return
    
    if horizons is None:
        horizons = [7, 14, 30]
    
    # Format for display
    df_display = df.copy()
    df_display['amount_fmt'] = df['amount'].apply(lambda x: f"₹{x:,.2f}")
    df_display['date_fmt'] = pd.to_datetime(df['forecast_date']).dt.strftime('%d %b %Y')
    
    st.dataframe(
        df[['date_fmt', 'amount_fmt', 'event_name', 'horizon_days', 'frequency']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "forecast_date": "Date",
            "amount_fmt": "Amount",
            "event_name": "Event",
            "horizon_days": "Horizon (days)",
            "frequency": "Frequency",
        },
    )


def render_forecast_chart_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Cash Flow Forecast",
    key: str = "",
) -> None:
    """Render forecast chart in a card container."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_chart
    fig = create_forecast_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_summary_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Forecast Summary",
) -> None:
    """Render forecast summary with horizontal bars by horizon."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_summary_chart
    fig = create_forecast_summary_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_table(
    forecast_entries: List[dict],
    horizons: List[int] = None,
) -> None:
    """Render forecast entries as a table."""
    if not forecast_entries:
        st.info("No forecast data available")
        return
    
    df = pd.DataFrame(forecast_entries)
    if df.empty:
        st.info("No forecast data available")
        return
    
    if horizons is None:
        horizons = [7, 14, 30]
    
    # Format for display
    df_display = df.copy()
    df_display['amount_fmt'] = df['amount'].apply(lambda x: f"₹{x:,.2f}")
    df_display['date_fmt'] = pd.to_datetime(df['forecast_date']).dt.strftime('%d %b %Y')
    
    st.dataframe(
        df[['date_fmt', 'amount_fmt', 'event_name', 'horizon_days', 'frequency']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "forecast_date": "Date",
            "amount_fmt": "Amount",
            "event_name": "Event",
            "horizon_days": "Horizon (days)",
            "frequency": "Frequency",
        },
    )


def render_forecast_chart_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Cash Flow Forecast",
    key: str = "",
) -> None:
    """Render forecast chart in a card container."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_chart
    fig = create_forecast_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_summary_card(
    forecast_entries: List[dict],
    horizons: List[int] = None,
    title: str = "Forecast Summary",
) -> None:
    """Render forecast summary with horizontal bars by horizon."""
    if not horizons:
        horizons = [7, 14, 30]
    
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
    
    from dashboard.utils.chart_helpers import create_forecast_summary_chart
    fig = create_forecast_summary_chart(forecast_entries, horizons)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_table(
    forecast_entries: List[dict],
    horizons: List[int] = None,
) -> None:
    """Render forecast entries as a table."""
    if not forecast_entries:
        st.info("No forecast data available")
        return
    
    df = pd.DataFrame(forecast_entries)
    if df.empty:
        st.info("No forecast data available")
        return
    
    if horizons is None:
        horizons = [7, 14, 30]
    
    # Format for display
    df_display = df.copy()
    df_display['amount_fmt'] = df['amount'].apply(lambda x: f"₹{x:,.2f}")
    df_display['date_fmt'] = pd.to_datetime(df['forecast_date']).dt.strftime('%d %b %Y')
    
    st.dataframe(
        df[['date_fmt', 'amount_fmt', 'event_name', 'horizon_days', 'frequency']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "forecast_date": "Date",
            "amount_fmt": "Amount",
            "event_name": "Event",
            "horizon_days": "Horizon (days)",
            "frequency": "Frequency",
        },
    )