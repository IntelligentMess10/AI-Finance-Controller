"""
Reconciliation Page - View and filter reconciliation matches.
"""

import streamlit as st
import pandas as pd
from dashboard.components.match_table import render_match_table
from dashboard.utils.api_client import api_get
from dashboard.utils.formatters import format_inr


def render_reconciliation():
    """Render the reconciliation page with filterable match table."""
    
    st.markdown('<div class="section-header">Reconciliation Results</div>', unsafe_allow_html=True)
    
    # Fetch matches
    with st.spinner("Loading reconciliation results..."):
        matches = api_get("/reconciliation/results")
    
    if not matches:
        st.info("No matches found. Run reconciliation first.")
        return
    
    df = pd.DataFrame(matches)
    
    if df.empty:
        st.info("No matches found")
        return
    
    # Format for display
    df['score_fmt'] = df['score'].apply(lambda x: f"{x:.2%}")
    df['status_fmt'] = df['status'].str.replace('_', ' ').str.title()
    df['method_fmt'] = df['method'].str.replace('_', ' ').str.title()
    # df['amount_fmt'] = df['amount'].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) else "—")
    
    # Filters
    st.markdown("### Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_options = df['status'].unique().tolist()
        status_filter = st.multiselect("Status", options=status_options, default=status_options, key="match_status_filter")
    
    with col2:
        method_options = df['method'].unique().tolist()
        method_filter = st.multiselect("Method", options=method_options, default=method_options, key="method_filter")
    
    with col3:
        min_score = st.slider("Min Score", 0.0, 1.0, 0.0, 0.05, key="min_score_filter")
    
    # Apply filters
    filtered = df[
        (df['status'].isin(status_filter) if status_filter else True) &
        (df['method'].isin(method_filter) if method_filter else True) &
        (df['score'] >= min_score)
    ]
    
    # Display table
    st.dataframe(
        df[['id', 'canonical_transaction_id', 'matched_transaction_id', 'score_fmt', 'method', 'status']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": "Match ID",
            "canonical_transaction_id": "Txn A",
            "matched_transaction_id": "Txn B",
            "score": "Score",
            "method": "Method",
            "status": "Status",
        },
    )
    
    st.caption(f"Showing {len(filtered)} of {len(matches)} matches")


if __name__ == "__main__":
    import streamlit as st
    from dashboard.pages.reconciliation import render_reconciliation
    render_reconciliation()