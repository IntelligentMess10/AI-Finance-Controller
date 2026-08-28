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
    
    # Confusion Matrix
    st.markdown("### Ground Truth Comparison")
    
    # This would need actual confusion matrix data from backend
    # For now, show placeholder
    st.info("Ground truth comparison requires running evaluation against ground truth data.")
    
    # Exception resolution breakdown
    st.markdown("### Exception Resolution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Resolution breakdown pie chart
        import plotly.express as px
        
        # Placeholder data - would come from API
        exc_data = {
            "Status": ["Resolved", "Escalated", "Unresolved"],
            "Count": [5, 2, 3]
        }
        df = pd.DataFrame(exc_data)
        
        import plotly.express as px
        fig = px.pie(
            values=[5, 2, 3], 
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


if __name__ == "__main__":
    import streamlit as st
    from dashboard.pages.metrics import render_metrics
    render_metrics()