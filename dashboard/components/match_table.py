"""
Match Table Component - Filterable, sortable reconciliation results table.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from dashboard.utils.formatters import format_inr, format_pct
from dashboard.styles.theme import STATUS_COLORS, get_status_color


def render_match_table(
    matches: List[dict],
    on_select: callable = None,
    show_actions: bool = True,
    key_prefix: str = "",
) -> Optional[int]:
    """
    Render a filterable, sortable match table with selection.
    
    Args:
        matches: List of match dictionaries
        on_select: Callback function(match_id) when row selected
        show_actions: Whether to show action buttons
        
    Returns:
        Selected match ID or None
    """
    if not matches:
        st.info("No matches found")
        return None
    
    df = pd.DataFrame(matches)
    
    if len(df) == 0:
        st.info("No matches found")
        return None
    
    # Format for display
    df = df.copy()
    df['score_fmt'] = df['score'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "—")
    df['status_fmt'] = df['status'].apply(lambda x: x.replace('_', ' ').title())
    df['method_fmt'] = df['method'].str.replace('_', ' ').str.title()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.multiselect(
            "Status",
            options=df['status'].unique().tolist(),
            default=df['status'].unique().tolist(),
            key="match_status_filter"
        )
    with col2:
        method_filter = st.multiselect(
            "Method",
            options=df['method'].unique().tolist(),
            default=df['method'].unique().tolist(),
            key="match_method_filter"
        )
    with col3:
        min_score = st.slider("Min Score", 0.0, 1.0, 0.0, 0.05, key="min_score_filter")
    
    # Apply filters
    filtered = df.copy()
    if status_filter:
        filtered = filtered[filtered['status'].isin(status_filter)]
    if method_filter:
        filtered = filtered[filtered['method'].isin(method_filter)]
    if min_score > 0:
        filtered = filtered[filtered['score'] >= min_score]
    
    if len(filtered) == 0:
        st.info("No matches match the current filters")
        return None
    
    # Prepare display dataframe
    display_df = filtered.copy()
    display_df['score_fmt'] = filtered['score'].apply(lambda x: f"{x:.2%}")
    display_df['status_fmt'] = filtered['status'].str.replace('_', ' ').str.title()
    display_df['method_fmt'] = filtered['method'].str.replace('_', ' ').str.title()
    
    if 'amount' in filtered.columns:
        filtered['amount_fmt'] = filtered['amount'].apply(
            lambda x: f"₹{x:,.2f}" if pd.notna(x) else "—"
        )
    
    # Display table
    display_df = filtered.copy()
    display_df['score_fmt'] = filtered['score'].apply(lambda x: f"{x:.2%}")
    display_df['status_fmt'] = filtered['status'].str.replace('_', ' ').str.title()
    display_df['method_fmt'] = filtered['method'].str.replace('_', ' ').str.title()
    
    if 'amount' in filtered.columns:
        filtered['amount_fmt'] = filtered['amount'].apply(
            lambda x: f"₹{x:,.2f}" if pd.notna(x) else "—"
        )
    
    # Display columns
    display_cols = ['id', 'canonical_transaction_id', 'matched_transaction_id', 'score_fmt', 'method_fmt', 'status_fmt']
    if 'amount_fmt' in filtered.columns:
        display_cols = display_cols + ['amount_fmt']
    
    # Configure column display
    column_config = {
        "id": st.column_config.NumberColumn("Match ID", width="small"),
        "canonical_transaction_id": st.column_config.NumberColumn("Txn A", width="small"),
        "matched_transaction_id": st.column_config.NumberColumn("Txn B", width="small"),
        "score_fmt": st.column_config.TextColumn("Score", width="small"),
        "method_fmt": st.column_config.TextColumn("Method", width="medium"),
        "status_fmt": st.column_config.TextColumn("Status", width="small"),
    }
    
    if 'amount_fmt' in filtered.columns:
        st.dataframe(
            filtered[['id', 'canonical_transaction_id', 'matched_transaction_id', 'score_fmt', 'method_fmt', 'status_fmt']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": "Match ID",
                "canonical_transaction_id": "Txn A",
                "matched_transaction_id": "Txn B",
                "score_fmt": "Score",
                "method_fmt": "Method",
                "status_fmt": "Status",
            },
        )
    else:
        st.dataframe(
            filtered[['id', 'canonical_transaction_id', 'matched_transaction_id', 'score_fmt', 'method_fmt', 'status_fmt']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": "Match ID",
                "canonical_transaction_id": "Txn A",
                "matched_transaction_id": "Txn B",
                "score_fmt": "Score",
                "method_fmt": "Method",
                "status_fmt": "Status",
            },
        )
    
    st.caption(f"Showing {len(filtered)} of {len(matches)} matches")
    
    return None


def render_match_table_simple(matches: List[dict]) -> Optional[int]:
    """Simple match table without filters."""
    if not matches:
        st.info("No matches found")
        return None
    
    df = pd.DataFrame(matches)
    df['score_fmt'] = df['score'].apply(lambda x: f"{x:.2%}")
    df['status_fmt'] = df['status'].str.replace('_', ' ').str.title()
    df['method_fmt'] = df['method'].str.replace('_', ' ').str.title()
    
    st.dataframe(
        df[['id', 'canonical_transaction_id', 'matched_transaction_id', 'score_fmt', 'method_fmt', 'status_fmt']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": "Match ID",
            "canonical_transaction_id": "Txn A",
            "matched_transaction_id": "Txn B",
            "score_fmt": "Score",
            "method_fmt": "Method",
            "status_fmt": "Status",
        },
    )
    
    return None


def render_match_card(match: dict) -> None:
    """Render a single match as a card."""
    from dashboard.styles.theme import STATUS_COLORS, get_status_color
    from dashboard.utils.formatters import format_inr
    
    color = STATUS_COLORS.get(match['status'], '#8B949E')
    
    st.markdown(f'''
    <div style="
        background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
        border: 1px solid #2D333B;
        border-left: 4px solid {STATUS_COLORS.get(match['status'], '#8B949E')};
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-weight: 600;">Match #{match['id']}</span>
            <span style="background: {STATUS_COLORS.get(match['status'], '#8B949E')}; color: #E6EDF3; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; text-transform: capitalize;">
                {match['status'].replace('_', ' ').title()}
            </span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; font-size: 0.875rem; color: #8B949E;">
            <div><strong>Score:</strong> {match['score']:.2%}</div>
            <div><strong>Method:</strong> {match['method'].replace('_', ' ').title()}</div>
            <div><strong>Txn A:</strong> #{match['canonical_transaction_id']} ↔ #{match['matched_transaction_id']}</div>
        </div>
        <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #E6EDF3;">
            <strong>Evidence:</strong> {', '.join(match.get('evidence', []))}
        </div>
    </div>
    ''', unsafe_allow_html=True)