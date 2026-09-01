"""
Probable Match Queue Component - Reusable component for rendering probable match queues.
"""

import streamlit as st
import pandas as pd
from typing import List, Optional, Dict, Any, Callable
from dashboard.utils.api_client import api_post


def render_probable_match_queue(
    matches: List[dict],
    on_investigate: Callable[[int], None] = None,
    show_auto_resolve: bool = True,
) -> None:
    """
    Render probable match queue with investigate actions.
    
    Args:
        matches: List of probable match dicts
        on_investigate: Callback function(match_id) when investigate clicked
        show_auto_resolve: Whether to show auto-resolve button
    """
    if not matches:
        st.info("No probable matches found")
        return
    
    df = pd.DataFrame(matches)
    
    # Format for display
    if 'score' in df.columns:
        df['score_fmt'] = df['score'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "—")
    if 'status' in df.columns:
        df['status_display'] = df['status'].apply(lambda x: x.replace('_', ' ').title())
    if 'method' in df.columns:
        df['method_display'] = df['method'].str.replace('_', ' ').str.title()
    
    # Auto-resolve button
    if show_auto_resolve:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### Probable Matches")
        with col2:
            if st.button("🤖 Auto-Resolve All", type="primary", use_container_width=True):
                # This will be handled by the parent page
                pass
    
    # Tabs for different statuses
    tabs = st.tabs(["📋 All", "✅ Resolved", "⚠️ Escalated"])
    statuses = ["all", "resolved", "escalated"]
    
    for tab, status in zip(tabs, statuses):
        with tab:
            if status == "all":
                filtered = matches
            else:
                filtered = [m for m in matches if m.get('status', '').lower() == status]
            
            if filtered:
                render_probable_match_table(filtered)
            else:
                status_label = status.replace('_', ' ').title()
                st.info(f"No {status_label} probable matches found")
    
    # Investigation action for individual matches
    if matches:
        st.markdown("---")
        st.markdown("### Quick Actions")
        
        open_matches = [m for m in matches if m.get('status', '').lower() in ['probable_match', 'probable']]
        if open_matches:
            selected = st.selectbox(
                "Select match to investigate",
                options=[m['id'] for m in open_matches],
                format_func=lambda x: f"Match #{x} - {next((m['method'] for m in open_matches if m['id'] == x), '')}",
                key="investigate_select"
            )
            if st.button("🔍 Investigate", type="primary", use_container_width=True):
                # This would trigger investigation - to be implemented by parent
                st.session_state['investigate_probable_match'] = selected
                st.rerun()


def render_probable_match_table(matches: List[dict]) -> None:
    """Render a table of probable matches."""
    if not matches:
        st.info("No matches to display")
        return
    
    df = pd.DataFrame(matches)
    
    # Format for display
    if 'score' in df.columns:
        df['score_fmt'] = df['score'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "—")
    if 'status' in df.columns:
        df['status_display'] = df['status'].apply(lambda x: x.replace('_', ' ').title())
    if 'method' in df.columns:
        df['method_display'] = df['method'].str.replace('_', ' ').str.title()
    
    display_cols = []
    for col in ['id', 'canonical_transaction_id', 'matched_transaction_id', 'score_fmt', 'method_display', 'status_display']:
        if col in df.columns or col.replace('_display', '').replace('_fmt', '') in df.columns:
            display_cols.append(col)
    
    # Map display columns to actual columns
    actual_cols = []
    for col in display_cols:
        if col in df.columns:
            actual_cols.append(col)
        elif col.replace('_display', '').replace('_fmt', '') in df.columns:
            actual_cols.append(col.replace('_display', '').replace('_fmt', ''))
    
    if actual_cols:
        st.dataframe(
            df[actual_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": "Match ID",
                "canonical_transaction_id": "Txn A",
                "matched_transaction_id": "Txn B",
                "score_fmt": "Score",
                "method_display": "Method",
                "status_display": "Status",
            },
        )


def render_probable_match_detail(match: dict) -> None:
    """Render detailed view of a probable match."""
    st.markdown(f"### Match #{match.get('id', 'N/A')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Match Details**")
        st.write(f"**Score:** {match.get('score', 0):.2%}")
        st.write(f"**Method:** {match.get('method', 'N/A').replace('_', ' ').title()}")
        st.write(f"**Status:** {match.get('status', 'N/A').replace('_', ' ').title()}")
        
        if match.get('evidence'):
            st.write("**Evidence:**")
            for e in match['evidence']:
                st.write(f"• {e}")
    
    with col2:
        st.write("**Resolution**")
        if match.get('resolution_summary'):
            st.write(match['resolution_summary'])
        if match.get('resolved_at'):
            st.write(f"Resolved at: {match['resolved_at']}")


if __name__ == "__main__":
    import streamlit as st
    from dashboard.components.probable_match_queue import render_probable_match_queue
    render_probable_match_queue([])