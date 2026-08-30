"""
Reconciliation Page - View and filter reconciliation matches.
"""

import streamlit as st
import pandas as pd
from dashboard.utils.api_client import get_api_client
from dashboard.utils.formatters import format_inr


def render_reconciliation():
    """Render the reconciliation page with filterable match table."""
    
    # Initialize pagination state
    if 'match_page' not in st.session_state:
        st.session_state['match_page'] = 1
    if 'match_page_size' not in st.session_state:
        st.session_state['match_page_size'] = 100
    
    st.markdown('<div class="section-header">Reconciliation Results</div>', unsafe_allow_html=True)
    
    # Callback functions for pagination buttons (execute BEFORE rerun)
    def go_previous():
        new_page = max(1, st.session_state['match_page'] - 1)
        st.session_state['match_page'] = new_page
        st.session_state['match_page_selector'] = new_page
    
    def go_next(total_pages):
        new_page = min(total_pages, st.session_state['match_page'] + 1)
        st.session_state['match_page'] = new_page
        st.session_state['match_page_selector'] = new_page
    
    def go_to_page():
        st.session_state['match_page'] = st.session_state['match_page_selector']
    
    def change_page_size():
        st.session_state['match_page_size'] = st.session_state['match_page_size_selector']
        st.session_state['match_page'] = 1
    
    # Fetch matches (paginated) - FIRST to get real total_pages
    with st.spinner("Loading reconciliation results..."):
        client = get_api_client()
        result = client.get_matches_paginated(
            page=st.session_state['match_page'],
            limit=st.session_state['match_page_size']
        )
    
    if not result or not result.get('items'):
        st.info("No matches found. Run reconciliation first.")
        return
    
    matches = result['items']
    total = result.get('total', len(matches))
    page = result.get('page', 1)
    limit = result.get('limit', st.session_state['match_page_size'])
    total_pages = (total + limit - 1) // limit
    
    df = pd.DataFrame(matches)
    
    if df.empty:
        st.info("No matches found")
        return
    
    # Format for display
    df['score_fmt'] = df['score'].apply(lambda x: f"{x:.2%}")
    df['status_fmt'] = df['status'].str.replace('_', ' ').str.title()
    df['method_fmt'] = df['method'].str.replace('_', ' ').str.title()
    
    # Filters - MOVED ABOVE PAGINATION
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
    
    # Pagination controls - render AFTER fetch with correct total_pages
    st.markdown("### Pagination")
    
    pcol1, pcol2, pcol3, pcol4, pcol5 = st.columns([1.5, 1, 1.5, 1, 1])
    
    with pcol1:
        st.caption(f"**Total:** {total} matches")
    
    with pcol2:
        st.button(
            "← Previous", 
            disabled=(page <= 1), 
            use_container_width=True,
            on_click=go_previous
        )
    
    with pcol3:
        page_options = list(range(1, total_pages + 1)) if total_pages > 0 else [1]
        st.selectbox(
            "Page",
            options=page_options,
            index=page - 1 if page in page_options else 0,
            label_visibility="collapsed",
            key="match_page_selector",
            on_change=go_to_page
        )
    
    with pcol4:
        st.button(
            "Next →", 
            disabled=(page >= total_pages), 
            use_container_width=True,
            on_click=lambda: go_next(total_pages)
        )
    
    with pcol5:
        st.selectbox(
            "",
            options=[50, 100, 200, 500],
            index=[50, 100, 200, 500].index(limit) if limit in [50, 100, 200, 500] else 1,
            label_visibility="collapsed",
            key="match_page_size_selector",
            on_change=change_page_size
        )
    
    st.caption("Pagination")
    st.caption("Per page")
    
    # Display table
    st.dataframe(
        filtered[['id', 'canonical_transaction_id', 'matched_transaction_id', 'score_fmt', 'method', 'status']],
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
    
    st.caption(f"Showing {len(filtered)} of {len(matches)} matches on page {page}/{total_pages} (Total: {total})")


if __name__ == "__main__":
    import streamlit as st
    from dashboard.pages.reconciliation import render_reconciliation
    render_reconciliation()