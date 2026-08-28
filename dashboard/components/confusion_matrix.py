"""
Confusion Matrix Component - Visualization of match accuracy.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from typing import Optional
from dashboard.utils.chart_helpers import create_confusion_matrix_chart
from dashboard.utils.formatters import format_pct


def render_confusion_matrix_chart(
    tp: int,
    fp: int,
    fn: int,
    tn: int,
    title: str = "Confusion Matrix",
    height: int = 300,
) -> None:
    """Render confusion matrix heatmap."""
    fig = create_confusion_matrix_chart(tp, fp, fn, tn)
    fig.update_layout(title=title, height=height)
    st.plotly_chart(fig, use_container_width=True)


def render_confusion_matrix_from_counts(
    tp: int,
    fp: int,
    fn: int,
    tn: int,
    title: str = "Confusion Matrix",
    height: int = 300,
) -> None:
    """Render confusion matrix from counts."""
    from dashboard.utils.chart_helpers import create_confusion_matrix_chart
    
    fig = create_confusion_matrix_chart(tp, fp, fn, tn)
    st.plotly_chart(fig, use_container_width=True)


def render_confusion_matrix_card(
    tp: int,
    fp: int,
    fn: int,
    tn: int,
    title: str = "Confusion Matrix",
) -> None:
    """Render confusion matrix in a card container."""
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
    
    from dashboard.utils.chart_helpers import create_confusion_matrix_chart
    fig = create_confusion_matrix_chart(tp, fp, fn, tn)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_confusion_matrix_from_metrics(
    tp: int,
    fp: int,
    fn: int,
    tn: int,
    title: str = "Confusion Matrix",
) -> None:
    """Render confusion matrix from TP, FP, FN, TN counts."""
    from dashboard.utils.chart_helpers import create_confusion_matrix_chart
    
    fig = create_confusion_matrix_chart(tp, fp, fn, tn)
    
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
    
    fig = create_confusion_matrix_chart(tp, fp, fn, tn)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_confusion_matrix_metrics(
    tp: int,
    fp: int,
    fn: int,
    tn: int,
) -> None:
    """Render confusion matrix with derived metrics."""
    total = tp + fp + fn + tn
    if total == 0:
        st.info("No data available for confusion matrix")
        return
    
    accuracy = (tp + tn) / (tp + fp + fn + tn) if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
    false_match_rate = fp / (tp + fp) if (tp + fp) > 0 else 0
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        from dashboard.utils.chart_helpers import create_confusion_matrix_chart
        fig = create_confusion_matrix_chart(tp, fp, fn, tn)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Metrics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Accuracy", f"{(tp + fn + fp + tn - fp - fn) / (tp + fp + fn + tn) * 100:.1f}%")
            st.metric("Precision", f"{tp / (tp + fp) * 100:.1f}%" if (tp + fp) > 0 else "0%")
        with col2:
            st.metric("Recall", f"{tp / (tp + fn) * 100:.1f}%" if (tp + fn) > 0 else "0%")
            st.metric("F1 Score", f"{2 * tp / (2 * tp + fp + fn) * 100:.1f}%" if (2 * tp + fp + fn) > 0 else "0%")
        
        st.markdown("---")
        st.metric("False Match Rate", f"{fp / (tp + fp) * 100:.2f}%" if (tp + fp) > 0 else "0%")


def render_confusion_matrix_card(
    tp: int,
    fp: int,
    fn: int,
    tn: int,
    title: str = "Confusion Matrix",
) -> None:
    """Render confusion matrix in a card with metrics."""
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
    
    from dashboard.utils.chart_helpers import create_confusion_matrix_chart
    fig = create_confusion_matrix_chart(tp, fp, fn, tn)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show metrics
    total = tp + fp + fn + tn
    if total > 0:
        accuracy = (tp + tn) / (tp + fp + fn + tn)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
        false_match_rate = fp / (tp + fp) if (tp + fp) > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Accuracy", f"{(tp + tn) / (tp + fp + fn + tn) * 100:.1f}%")
        with col2:
            st.metric("Precision", f"{precision * 100:.1f}%")
        with col3:
            st.metric("Recall", f"{recall * 100:.1f}%")
        with col4:
            st.metric("F1 Score", f"{f1 * 100:.1f}%")
        
        st.metric("False Match Rate", f"{fp / (tp + fp) * 100:.2f}%" if (tp + fp) > 0 else "0%")


def render_confusion_matrix_card(
    tp: int,
    fp: int,
    fn: int,
    tn: int,
    title: str = "Confusion Matrix",
) -> None:
    """Render confusion matrix in a card with metrics."""
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
    
    from dashboard.utils.chart_helpers import create_confusion_matrix_chart
    fig = create_confusion_matrix_chart(tp, fp, fn, tn)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show metrics
    total = tp + fp + fn + tn
    if total > 0:
        accuracy = (tp + tn) / (tp + fp + fn + tn)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
        false_match_rate = fp / (tp + fp) if (tp + fp) > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Accuracy", f"{accuracy * 100:.1f}%")
        with col2:
            st.metric("Precision", f"{precision * 100:.1f}%")
        with col3:
            st.metric("Recall", f"{recall * 100:.1f}%")
        with col4:
            st.metric("F1 Score", f"{f1 * 100:.1f}%")
        
        st.metric("False Match Rate", f"{fp / (tp + fp) * 100:.2f}%" if (tp + fp) > 0 else "0%")


def render_confusion_matrix_card(
    tp: int,
    fp: int,
    fn: int,
    tn: int,
    title: str = "Confusion Matrix",
) -> None:
    """Render confusion matrix in a card with metrics."""
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
    
    from dashboard.utils.chart_helpers import create_confusion_matrix_chart
    fig = create_confusion_matrix_chart(tp, fp, fn, tn)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show metrics
    total = tp + fp + fn + tn
    if total > 0:
        accuracy = (tp + tn) / (tp + fp + fn + tn)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
        false_match_rate = fp / (tp + fp) if (tp + fp) > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Accuracy", f"{accuracy * 100:.1f}%")
        with col2:
            st.metric("Precision", f"{precision * 100:.1f}%")
        with col3:
            st.metric("Recall", f"{recall * 100:.1f}%")
        with col4:
            st.metric("F1 Score", f"{f1 * 100:.1f}%")
        
        st.metric("False Match Rate", f"{fp / (tp + fp) * 100:.2f}%" if (tp + fp) > 0 else "0%")


def render_confusion_matrix_card(
    tp: int,
    fp: int,
    fn: int,
    tn: int,
    title: str = "Confusion Matrix",
) -> None:
    """Render confusion matrix in a card with metrics."""
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
    
    from dashboard.utils.chart_helpers import create_confusion_matrix_chart
    fig = create_confusion_matrix_chart(tp, fp, fn, tn)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show metrics
    total = tp + fp + fn + tn
    if total > 0:
        accuracy = (tp + tn) / (tp + fp + fn + tn)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
        false_match_rate = fp / (tp + fp) if (tp + fp) > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Accuracy", f"{accuracy * 100:.1f}%")
        with col2:
            st.metric("Precision", f"{precision * 100:.1f}%")
        with col3:
            st.metric("Recall", f"{recall * 100:.1f}%")
        with col4:
            st.metric("F1 Score", f"{f1 * 100:.1f}%")
        
        st.metric("False Match Rate", f"{fp / (tp + fp) * 100:.2f}%" if (tp + fp) > 0 else "0%")


def render_confusion_matrix_card(
    tp: int,
    fp: int,
    fn: int,
    tn: int,
    title: str = "Confusion Matrix",
) -> None:
    """Render confusion matrix in a card with metrics."""
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
    
    from dashboard.utils.chart_helpers import create_confusion_matrix_chart
    fig = create_confusion_matrix_chart(tp, fp, fn, tn)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show metrics
    total = tp + fp + fn + tn
    if total > 0:
        accuracy = (tp + tn) / (tp + fp + fn + tn)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
        false_match_rate = fp / (tp + fp) if (tp + fp) > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Accuracy", f"{accuracy * 100:.1f}%")
        with col2:
            st.metric("Precision", f"{precision * 100:.1f}%")
        with col3:
            st.metric("Recall", f"{recall * 100:.1f}%")
        with col4:
            st.metric("F1 Score", f"{f1 * 100:.1f}%")
        
        st.metric("False Match Rate", f"{fp / (tp + fp) * 100:.2f}%" if (tp + fp) > 0 else "0%")


def render_confusion_matrix_card(
    tp: int,
    fp: int,
    fn: int,
    tn: int,
    title: str = "Confusion Matrix",
) -> None:
    """Render confusion matrix in a card with metrics."""
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
    
    from dashboard.utils.chart_helpers import create_confusion_matrix_chart
    fig = create_confusion_matrix_chart(tp, fp, fn, tn)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show metrics
    total = tp + fp + fn + tn
    if total > 0:
        accuracy = (tp + tn) / (tp + fp + fn + tn)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
        false_match_rate = fp / (tp + fp) if (tp + fp) > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Accuracy", f"{accuracy * 100:.1f}%")
        with col2:
            st.metric("Precision", f"{precision * 100:.1f}%")
        with col3:
            st.metric("Recall", f"{recall * 100:.1f}%")
        with col4:
            st.metric("F1 Score", f"{f1 * 100:.1f}%")
        
        st.metric("False Match Rate", f"{fp / (tp + fp) * 100:.2f}%" if (tp + fp) > 0 else "0%")


def render_confusion_matrix_card(
    tp: int,
    fp: int,
    fn: int,
    tn: int,
    title: str = "Confusion Matrix",
) -> None:
    """Render confusion matrix in a card with metrics."""
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
    
    from dashboard.utils.chart_helpers import create_confusion_matrix_chart
    fig = create_confusion_matrix_chart(tp, fp, fn, tn)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show metrics
    total = tp + fp + fn + tn
    if total > 0:
        accuracy = (tp + tn) / (tp + fp + fn + tn)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
        false_match_rate = fp / (tp + fp) if (tp + fp) > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Accuracy", f"{accuracy * 100:.1f}%")
        with col2:
            st.metric("Precision", f"{precision * 100:.1f}%")
        with col3:
            st.metric("Recall", f"{recall * 100:.1f}%")
        with col4:
            st.metric("F1 Score", f"{f1 * 100:.1f}%")
        
        st.metric("False Match Rate", f"{fp / (tp + fp) * 100:.2f}%" if (tp + fp) > 0 else "0%")