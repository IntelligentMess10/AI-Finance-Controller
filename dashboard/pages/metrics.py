"""
Metrics Page - Evaluation metrics with ground truth comparison.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dashboard.utils.api_client import api_get


def render_metrics():
    """Render the metrics page with ground truth comparison."""
    
    st.markdown('<div class="section-header">Evaluation Metrics</div>', unsafe_allow_html=True)
    
    # Fetch metrics
    with st.spinner("Loading metrics..."):
        from dashboard.utils.api_client import api_get
        metrics = api_get("/metrics/")
    
    if not metrics:
        st.info("No metrics available. Run reconciliation first.")
        return
    
    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Match Rate", f"{metrics.get('match_rate', 0):.1f}%")
    with col2:
        st.metric("Accuracy", f"{metrics.get('accuracy', 0):.1f}%")
    with col3:
        st.metric("False Match Rate", f"{metrics.get('false_match_rate', 0):.2f}%")
    with col4:
        st.metric("Processing Time", f"{metrics.get('processing_time_seconds', 0):.2f}s")
    
    # AI-specific metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("AI Resolution Rate", f"{metrics.get('ai_resolution_rate', 0):.1f}%")
    with col2:
        st.metric("AI Accuracy", f"{metrics.get('ai_accuracy', 0):.1f}%")
    
    # Exception resolution breakdown
    st.markdown("### Exception Resolution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Resolution breakdown pie chart
        resolved = metrics.get('exceptions_resolved', 0)
        escalated = metrics.get('exceptions_escalated', 0)
        unresolved = metrics.get('exceptions_unresolved', 0)
        
        if resolved + escalated + unresolved > 0:
            fig = px.pie(
                values=[resolved, escalated, unresolved], 
                names=["Resolved", "Escalated", "Unresolved"],
                color_discrete_map={
                    "Resolved": "#00D4AA",
                    "Escalated": "#F0B429",
                    "Unresolved": "#FF6B6B",
                },
                hole=0.5
            )
            fig.update_layout(
                plot_bgcolor='#0E1117',
                paper_bgcolor='#0E1117',
                font_color='#E6EDF3',
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No exception data available")
    
    with col2:
        # Additional metrics
        st.markdown("#### Summary")
        st.write(f"**Total Records:** {metrics.get('total_records', 0)}")
        st.write(f"**Matched Records:** {metrics.get('matched_records', 0)}")
        st.write(f"**Total Exceptions:** {metrics.get('exceptions_total', 0)}")
        st.write(f"**Cash Variance:** ₹{float(metrics.get('cash_variance', 0)):,.2f}")
        
        if metrics.get('total_records', 0) > 0:
            match_rate = metrics.get('match_rate', 0)
            if match_rate >= 90:
                st.success(f"✅ Match rate: {match_rate:.1f}% (Target: ≥90%)")
            else:
                st.warning(f"⚠️ Match rate: {match_rate:.1f}% (Target: ≥90%)")


if __name__ == "__main__":
    import streamlit as st
    from dashboard.pages.metrics import render_metrics
    render_metrics()