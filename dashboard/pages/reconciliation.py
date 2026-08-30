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
    
    # Initialize pagination state
    if 'match_page' not in st.session_state:
        st.session_state['match_page'] = 1
    if 'match_page_size' not in st.session_state:
        st.session_state['match_page_size'] = 100
    
    # Fetch matches (paginated)
    with st.spinner("Loading reconciliation results..."):
        from dashboard.utils.api_client import get_api_client
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
    
    # Apply filters (client-side on current page)
    filtered = df[
        (df['status'].isin(status_filter) if status_filter else True) &
        (df['method'].isin(method_filter) if method_filter else True) &
        (df['score'] >= min_score)
    ]
    
    # Pagination controls
    st.markdown("### Pagination")
    pcol1, pcol2, pcol3, pcol4, pcol5 = st.columns([1.5, 1, 1.5, 1, 1])

    with pcol1:
        st.caption(f"**Total:** {total} matches")

    with pcol2:
        if st.button("← Previous", disabled=(page <= 1), use_container_width=True):
            st.session_state['match_page'] = max(1, page - 1)
            st.rerun()

    with pcol3:
        page_options = list(range(1, total_pages + 1)) if total_pages > 0 else [1]
        selected_page = st.selectbox(
            "Page",
            options=page_options,
            index=page - 1 if page in page_options else 0,
            label_visibility="collapsed",
            key="match_page_selector"
        )
        if selected_page != page:
            st.session_state['match_page'] = selected_page
            st.rerun()

    with pcol4:
        if st.button("Next →", disabled=(page >= total_pages), use_container_width=True):
            st.session_state['match_page'] = min(total_pages, page + 1)
            st.rerun()

    with pcol5:
        page_size = st.selectbox(
            "Per page",
            options=[50, 100, 200, 500],
            index=[50, 100, 200, 500].index(limit) if limit in [50, 100, 200, 500] else 1,
            key="match_page_size_selector"
        )
        if page_size != st.session_state['match_page_size']:
            st.session_state['match_page_size'] = page_size
            st.session_state['match_page'] = 1
            st.rerun()
    
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