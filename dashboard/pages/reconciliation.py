import streamlit as st
import pandas as pd
from dashboard.utils.api_client import get_api_client, api_post
from dashboard.utils.formatters import format_inr


def render_reconciliation():
    """Render the reconciliation page with filterable match table."""
    
    # Initialize pagination state
    if 'match_page' not in st.session_state:
        st.session_state['match_page'] = 1
    if 'match_page_size' not in st.session_state:
        st.session_state['match_page_size'] = 100
    
    # Check if reconciliation should be triggered
    if st.session_state.get('run_reconciliation'):
        st.session_state['run_reconciliation'] = False  # Clear flag immediately
        with st.spinner("Running reconciliation... This may take a moment."):
            try:
                result = api_post("/reconciliation/run", json_data={"force_rerun": True})
                if result:
                    st.success("Reconciliation completed successfully!")
                else:
                    st.error("Reconciliation failed. Please check the logs.")
            except Exception as e:
                st.error(f"Reconciliation failed: {str(e)}")
            st.rerun()
    
    st.markdown('<div class="section-header">Reconciliation Results</div>', unsafe_allow_html=True)
    
    # Initialize pagination state
    if 'match_page' not in st.session_state:
        st.session_state['match_page'] = 1
    if 'match_page_size' not in st.session_state:
        st.session_state['match_page_size'] = 100
    
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
    
    # Filters - FIRST to capture filter state
    st.markdown("### Filters")
    col1, col2, col3 = st.columns(3)
    
    # These will be updated after fetch
    if 'match_status_filter' not in st.session_state:
        st.session_state['match_status_filter'] = ['matched', 'probable_match']
    if 'match_method_filter' not in st.session_state:
        st.session_state['match_method_filter'] = []
    
    with col1:
        status_options = ['matched', 'probable_match', 'duplicate', 'missing_counterparty']
        status_filter = st.multiselect(
            "Status", 
            options=status_options, 
            default=st.session_state.get('match_status_filter', status_options), 
            key="match_status_filter"
        )
    
    with col2:
        method_options = ['processor_fee_match', 'date_mismatch', 'strong_amount_counterparty_date', 'rounding_difference', 'fuzzy_weighted']
        method_filter = st.multiselect(
            "Method", 
            options=method_options, 
            default=st.session_state.get('match_method_filter', method_options), 
            key="match_method_filter"
        )
    
    with col3:
        min_score = st.slider("Min Score", 0.0, 1.0, 0.0, 0.05, key="min_score_filter")
    
    # Determine filter values for API (pass first selected if single, None if multiple/all)
    api_status = status_filter[0] if len(status_filter) == 1 else None
    api_method = method_filter[0] if len(method_filter) == 1 else None
    api_min_score = min_score if min_score > 0 else None
    
    # Fetch matches (paginated) with server-side filters
    with st.spinner("Loading reconciliation results..."):
        client = get_api_client()
        result = client.get_matches_paginated(
            page=st.session_state['match_page'],
            limit=st.session_state['match_page_size'],
            status=api_status,
            method=api_method,
            min_score=api_min_score,
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
    
    # Format for display (handle None values for exceptions)
    df['score_fmt'] = df['score'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "—")
    df['status_fmt'] = df['status'].apply(lambda x: x.replace('_', ' ').title() if pd.notna(x) else "—")
    df['method_fmt'] = df['method'].apply(lambda x: x.replace('_', ' ').title() if pd.notna(x) else "—")
    
    # Apply additional client-side filters (method, min_score, status) since backend only filters by status
    filtered = df[
        (df['method'].isin(method_filter) if method_filter else True) &
        (df['score'] >= min_score) &
        (df['status'].isin(status_filter) if status_filter else True)
    ]
    
    # Pagination controls
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