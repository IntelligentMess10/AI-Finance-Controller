import streamlit as st
from typing import Optional
from dashboard.utils.chart_helpers import create_resolution_pie_chart
from dashboard.utils.chart_helpers import create_resolution_pie_chart
from dashboard.utils.chart_helpers import create_resolution_breakdown_chart


def render_resolution_pie_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
    height: int = 350,
) -> None:
    """Render a pie chart showing exception resolution breakdown."""
    fig = create_resolution_pie_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)


def render_resolution_pie_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
    height: int = 350,
) -> None:
    """Render a pie chart showing exception resolution breakdown."""
    fig = create_resolution_pie_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)


def render_resolution_pie_chart_card(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
) -> None:
    """Render resolution pie chart in a card container."""
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
    
    from dashboard.utils.chart_helpers import create_resolution_pie_chart
    fig = create_resolution_pie_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_resolution_breakdown_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
) -> None:
    """Create horizontal bar chart for resolution breakdown."""
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
    
    from dashboard.utils.chart_helpers import create_resolution_breakdown_chart
    fig = create_resolution_breakdown_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)


def render_resolution_pie_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
    height: int = 350,
) -> None:
    """Render a pie chart showing exception resolution breakdown."""
    fig = create_resolution_pie_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)


def render_resolution_pie_chart_card(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
) -> None:
    """Render resolution pie chart in a card container."""
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
    
    from dashboard.utils.chart_helpers import create_resolution_pie_chart
    fig = create_resolution_pie_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_resolution_breakdown_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
) -> None:
    """Create horizontal bar chart for resolution breakdown."""
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
    
    from dashboard.utils.chart_helpers import create_resolution_breakdown_chart
    fig = create_resolution_breakdown_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)


def render_resolution_pie_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
    height: int = 350,
) -> None:
    """Render a pie chart showing exception resolution breakdown."""
    fig = create_resolution_pie_chart(resolved, escalated, unresolved)
    fig.update_layout(title=title, height=height)
    st.plotly_chart(fig, use_container_width=True)


def render_resolution_pie_chart_card(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
) -> None:
    """Render resolution pie chart in a card container."""
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
    
    from dashboard.utils.chart_helpers import create_resolution_pie_chart
    fig = create_resolution_pie_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_resolution_breakdown_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
) -> None:
    """Create horizontal bar chart for resolution breakdown."""
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
    
    from dashboard.utils.chart_helpers import create_resolution_breakdown_chart
    fig = create_resolution_breakdown_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)


def render_resolution_pie_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
    height: int = 350,
) -> None:
    """Render a pie chart showing exception resolution breakdown."""
    fig = create_resolution_pie_chart(resolved, escalated, unresolved)
    fig.update_layout(title=title, height=height)
    st.plotly_chart(fig, use_container_width=True)


def render_resolution_pie_chart_card(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
) -> None:
    """Render resolution pie chart in a card container."""
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
    
    from dashboard.utils.chart_helpers import create_resolution_pie_chart
    fig = create_resolution_pie_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_resolution_breakdown_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
) -> None:
    """Create horizontal bar chart for resolution breakdown."""
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
    
    from dashboard.utils.chart_helpers import create_resolution_breakdown_chart
    fig = create_resolution_breakdown_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)


def render_resolution_pie_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
    height: int = 350,
) -> None:
    """Render a pie chart showing exception resolution breakdown."""
    fig = create_resolution_pie_chart(resolved, escalated, unresolved)
    fig.update_layout(title=title, height=height)
    st.plotly_chart(fig, use_container_width=True)


def render_resolution_pie_chart_card(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
) -> None:
    """Render resolution pie chart in a card container."""
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
    
    from dashboard.utils.chart_helpers import create_resolution_pie_chart
    fig = create_resolution_pie_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_resolution_breakdown_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
) -> None:
    """Create horizontal bar chart for resolution breakdown."""
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
    
    from dashboard.utils.chart_helpers import create_resolution_breakdown_chart
    fig = create_resolution_breakdown_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)


def render_resolution_pie_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
    height: int = 350,
) -> None:
    """Render a pie chart showing exception resolution breakdown."""
    fig = create_resolution_pie_chart(resolved, escalated, unresolved)
    fig.update_layout(title=title, height=height)
    st.plotly_chart(fig, use_container_width=True)


def render_resolution_pie_chart_card(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
) -> None:
    """Render resolution pie chart in a card container."""
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
    
    from dashboard.utils.chart_helpers import create_resolution_pie_chart
    fig = create_resolution_pie_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_resolution_breakdown_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
) -> None:
    """Create horizontal bar chart for resolution breakdown."""
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
    
    from dashboard.utils.chart_helpers import create_resolution_breakdown_chart
    fig = create_resolution_breakdown_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)


def render_resolution_pie_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
    height: int = 350,
) -> None:
    """Render a pie chart showing exception resolution breakdown."""
    fig = create_resolution_pie_chart(resolved, escalated, unresolved)
    fig.update_layout(title=title, height=height)
    st.plotly_chart(fig, use_container_width=True)


def render_resolution_pie_chart_card(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
) -> None:
    """Render resolution pie chart in a card container."""
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
    
    from dashboard.utils.chart_helpers import create_resolution_pie_chart
    fig = create_resolution_pie_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_resolution_breakdown_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
) -> None:
    """Create horizontal bar chart for resolution breakdown."""
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
    
    from dashboard.utils.chart_helpers import create_resolution_breakdown_chart
    fig = create_resolution_breakdown_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)


def render_resolution_pie_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
    height: int = 350,
) -> None:
    """Render a pie chart showing exception resolution breakdown."""
    fig = create_resolution_pie_chart(resolved, escalated, unresolved)
    fig.update_layout(title=title, height=height)
    st.plotly_chart(fig, use_container_width=True)


def render_resolution_pie_chart_card(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
) -> None:
    """Render resolution pie chart in a card container."""
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
    
    from dashboard.utils.chart_helpers import create_resolution_pie_chart
    fig = create_resolution_pie_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_resolution_breakdown_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
    title: str = "Exception Resolution Breakdown",
) -> None:
    """Create horizontal bar chart for resolution breakdown."""
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
    
    from dashboard.utils.chart_helpers import create_resolution_breakdown_chart
    fig = create_resolution_breakdown_chart(resolved, escalated, unresolved)
    st.plotly_chart(fig, use_container_width=True)