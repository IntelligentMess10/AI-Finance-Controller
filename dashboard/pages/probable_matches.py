import streamlit as st
from datetime import datetime
from dashboard.utils.api_client import api_get, api_post


def render_probable_matches():
    """Render the probable matches page with tabs and auto-resolve functionality."""
    
    st.markdown('<div class="section-header">Probable Matches</div>', unsafe_allow_html=True)
    
    # Auto-resolve button
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### Probable Matches Queue")
    with col3:
        if st.button("🤖 Auto-Resolve All", type="primary", use_container_width=True):
            with st.spinner("Running AI investigation on all probable matches..."):
                result = api_post("/reconciliation/auto-resolve-probable")
            
            if result:
                st.success(f"Auto-resolve complete: {result.get('resolved', 0)} resolved, {result.get('escalated', 0)} escalated")
                st.rerun()
            else:
                st.error("Auto-resolve failed. Check logs for details.")
    
    # Fetch probable matches
    with st.spinner("Loading probable matches..."):
        # Try different statuses
        all_matches = []
        for status in ["probable_match", "escalated", "resolved"]:
            result = api_get("/reconciliation/probable-matches", params={"status": status, "limit": 500})
            if result and result.get("items"):
                for item in result["items"]:
                    item["_status_filter"] = status
                    all_matches.append(item)
    
    if not all_matches:
        st.info("No probable matches found. Run reconciliation to generate probable matches.")
        return
    
    # Convert to DataFrame
    import pandas as pd
    df = pd.DataFrame(all_matches)
    
    # Format for display
    if 'score' in df.columns:
        df['score_fmt'] = df['score'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "—")
    if 'status' in df.columns:
        df['status_display'] = df['status'].apply(lambda x: x.replace('_', ' ').title())
    if 'method' in df.columns:
        df['method_display'] = df['method'].str.replace('_', ' ').str.title()
    
    # Tabs
    tabs = st.tabs(["📋 All", "✅ Resolved", "⚠️ Escalated"])
    statuses = ["all", "resolved", "escalated"]
    
    for tab, status in zip(tabs, statuses):
        with tab:
            if status == "all":
                filtered = df
            else:
                filtered = df[df['status'] == status] if 'status' in df.columns else pd.DataFrame()
            
            if len(filtered) > 0:
                render_probable_match_queue(filtered)
            else:
                status_label = status.replace('_', ' ').title()
                st.info(f"No {status_label} probable matches found")


def render_probable_match_queue(df):
    """Render probable match queue with action buttons."""
    import pandas as pd
    
    # Display table
    display_cols = ['id', 'canonical_transaction_id', 'matched_transaction_id', 'score_fmt', 'method', 'status_display']
    available_cols = [c for c in ['id', 'canonical_transaction_id', 'matched_transaction_id', 'score_fmt', 'method', 'status_display'] if c in df.columns]
    
    if not available_cols:
        st.info("No data to display")
        return
    
    st.dataframe(
        df[available_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": "Match ID",
            "canonical_transaction_id": "Txn A",
            "matched_transaction_id": "Txn B",
            "score_fmt": "Score",
            "method": "Method",
            "status_display": "Status",
        },
    )
    
    # Action buttons for individual matches
    if len(df) > 0:
        st.markdown("---")
        st.markdown("### Actions")
        
        # Select a match for detailed view or manual investigation
        match_ids = df['id'].tolist()
        if match_ids:
            selected_id = st.selectbox(
                "Select match for details",
                options=match_ids,
                format_func=lambda x: f"Match #{x} - {df[df['id']==x]['method'].values[0] if len(df[df['id']==x]) > 0 else ''}"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔍 View Details", use_container_width=True):
                    st.session_state['selected_probable_match'] = selected_id
                    st.rerun()
            with col2:
                if st.button("🤖 Investigate", type="primary", use_container_width=True):
                    st.session_state['investigate_probable_match'] = selected_id
                    st.rerun()


if __name__ == "__main__":
    import streamlit as st
    from dashboard.pages.Probable_Matches import render_probable_matches
    render_probable_matches()