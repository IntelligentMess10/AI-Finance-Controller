"""
Exception Queue Component - Tabbed queue with investigate actions.
"""

import streamlit as st
import pandas as pd
from typing import List, Optional, Dict, Any, Callable
from dashboard.utils.formatters import format_inr, format_inr_compact
from dashboard.utils.api_client import api_get
from dashboard.styles.theme import get_status_color, STATUS_COLORS
from dashboard.components.status_badge import render_status_badge_inline


def render_exception_queue(
    exceptions: List[dict],
    on_investigate: Callable[[int], None] = None,
    show_actions: bool = True,
) -> None:
    """
    Render tabbed exception queue with investigate actions.
    
    Args:
        exceptions: List of exception dicts
        on_investigate: Callback function(exc_id) when investigate clicked
        show_actions: Whether to show investigate buttons
    """
    if not exceptions:
        st.info("No exceptions found")
        return
    
    df = pd.DataFrame(exceptions)
    
    # Ensure required columns exist
    required_cols = ['id', 'transaction_id', 'type', 'severity', 'status', 'confidence', 'description']
    for col in required_cols:
        if col not in df.columns:
            df[col] = None
    
    # Format for display
    df['confidence_fmt'] = df['confidence'].apply(lambda x: f"{x:.0%}" if pd.notna(x) else "—")
    df['status_display'] = df['status'].apply(lambda x: x.replace('_', ' ').title())
    df['type_display'] = df['type'].str.replace('_', ' ').str.title()
    
    # tabs = st.tabs(["All", "Open", "Investigating", "Resolved", "Escalated", "Unresolved"])
    # statuses = ["All", "open", "investigating", "resolved", "escalated", "unresolved"]
    
    for tab, status in zip(st.tabs(["All", "Open", "Investigating", "Resolved", "Escalated", "Unresolved"]), 
                           ["All", "open", "investigating", "resolved", "escalated", "unresolved"]):
        with tab:
            if status == "All":
                filtered = df
            else:
                filtered = df[df['status'] == status]
            
            if len(filtered) > 0:
                render_exception_table(filtered)
            else:
                st.info(f"No {status} exceptions")
    
    # Investigation action
    if show_actions:
        open_exceptions = df[df['status'].isin(['open', 'investigating'])]
        if len(open_exceptions) > 0:
            st.markdown("---")
            selected = st.selectbox(
                "Select exception to investigate",
                options=open_exceptions['id'].tolist(),
                format_func=lambda x: f"Exception #{x} - {open_exceptions[open_exceptions['id']==x]['description'].values[0][:50]}",
            )
            if st.button("🔍 Investigate", type="primary"):
                if callable(on_investigate):
                    on_investigate(selected)


def render_exception_table(
    df: pd.DataFrame,
    on_investigate: Callable = None,
    show_actions: bool = False,
) -> None:
    """Render exception table with investigate actions."""
    if len(df) == 0:
        st.info("No exceptions found")
        return
    
    display_df = df.copy()
    display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{x:.0%}" if pd.notna(x) else "—")
    display_df['status'] = display_df['status'].apply(lambda x: x.replace('_', ' ').title())
    display_df['type'] = display_df['type'].str.replace('_', ' ').str.title()
    
    st.dataframe(
        display_df[['id', 'transaction_id', 'type', 'severity', 'status', 'confidence', 'description']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("Exc ID", width="small"),
            "transaction_id": st.column_config.NumberColumn("Txn ID", width="small"),
            "type": st.column_config.TextColumn("Type", width="medium"),
            "severity": st.column_config.TextColumn("Severity", width="small"),
            "status": st.column_config.TextColumn("Status", width="small"),
            "confidence": st.column_config.TextColumn("Confidence", width="small"),
            "description": st.column_config.TextColumn("Description", width="large"),
        },
    )
    
    if show_actions:
        open_exceptions = df[df['status'].isin(['open', 'investigating'])]
        if len(open_exceptions) > 0:
            selected = st.selectbox(
                "Select exception to investigate",
                options=open_exceptions['id'].tolist(),
                format_func=lambda x: f"Exception #{x} - {df[df['id']==x]['description'].values[0][:50]}",
                key="investigate_select"
            )
            if st.button("🔍 Investigate", type="primary"):
                st.session_state['investigate_exc_id'] = selected
                st.rerun()


def render_exception_card(exc: dict) -> None:
    """Render a single exception as a card."""
    from dashboard.styles.theme import STATUS_COLORS
    from dashboard.utils.formatters import format_inr
    
    color = STATUS_COLORS.get(exc['status'], '#8B949E')
    
    st.markdown(f'''
    <div style="
        background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
        border: 1px solid #2D333B;
        border-left: 4px solid {STATUS_COLORS.get(exc['status'], '#8B949E')};
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-weight: 600;">Exception #{exc['id']}</span>
            <span style="background: {STATUS_COLORS.get(exc['status'], '#8B949E')}; color: #E6EDF3; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; text-transform: capitalize;">
                {exc['status'].replace('_', ' ').title()}
            </span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #8B949E; margin-bottom: 0.5rem;">
            <span>Type: {exc['type'].replace('_', ' ').title()}</span>
            <span>Severity: {exc['severity'].title()}</span>
            <span>Confidence: {exc.get('confidence', 0):.0%}</span>
        </div>
        <div style="color: #E6EDF3; font-size: 0.875rem; margin-top: 0.5rem;">
            {exc.get('description', 'No description')[:100]}...
        </div>
    </div>
    ''', unsafe_allow_html=True)


def render_exception_detail(exception_data: dict) -> None:
    """Render detailed exception view with investigation actions."""
    from dashboard.styles.theme import STATUS_COLORS, get_status_color
    from dashboard.components.status_badge import render_status_badge_inline
    from dashboard.utils.formatters import format_inr
    
    exc = exception_data
    
    st.markdown(f'''
    <div style="
        background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
        border: 1px solid #2D333B;
        border-left: 4px solid {STATUS_COLORS.get(exc['status'], '#8B949E')};
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: #E6EDF3;">Exception #{exc['id']}</h1>
            <span style="
                background: {STATUS_COLORS.get(exc['status'], '#8B949E')};
                color: #E6EDF3;
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: capitalize;
            ">
                {exc['status'].replace('_', ' ').title()}
            </span>
        </div>
        <div style="display: flex; gap: 1.5rem; margin: 1rem 0; font-size: 0.875rem; color: #8B949E;">
            <span><strong>Type:</strong> {exc['type'].replace('_', ' ').title()}</span>
            <span><strong>Severity:</strong> {exc['severity'].title()}</span>
            <span><strong>Confidence:</strong> {exc.get('confidence', 0):.0%}</span>
        </div>
        <div style="color: #E6EDF3; margin-top: 1rem;">
            {exc.get('description', 'No description available')}
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔍 Investigate", key=f"investigate_{exc['id']}", type="primary", use_container_width=True):
            st.session_state['investigate_exc_id'] = exc['id']
            st.rerun()
    with col2:
        if st.button("📋 View Evidence", key=f"evidence_{exc['id']}", use_container_width=True):
            st.session_state['view_evidence_id'] = exc['id']
            st.rerun()
    with col3:
        if st.button("📋 View Transaction", key=f"txn_{exc['id']}", use_container_width=True):
            st.session_state['view_txn_id'] = exc['id']
            st.rerun()


def render_exception_list(exceptions: list) -> None:
    """Render a list of exception cards."""
    if not exceptions:
        st.info("No exceptions found")
        return
    
    for exc in exceptions:
        render_exception_card(exc)


def render_exception_detail(exception_data: dict) -> None:
    """Render detailed exception view with investigation actions."""
    from dashboard.styles.theme import STATUS_COLORS, get_status_color
    from dashboard.components.status_badge import render_status_badge_inline
    from dashboard.utils.formatters import format_inr
    
    exc = exception_data
    
    st.markdown(f'''
    <div style="
        background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
        border: 1px solid #2D333B;
        border-left: 4px solid {STATUS_COLORS.get(exc['status'], '#8B949E')};
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: #E6EDF3;">Exception #{exc['id']}</h1>
            <span style="
                background: {STATUS_COLORS.get(exc['status'], '#8B949E')};
                color: #E6EDF3;
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: capitalize;
            ">
                {exc['status'].replace('_', ' ').title()}
            </span>
        </div>
        <div style="display: flex; gap: 1.5rem; margin: 1rem 0; font-size: 0.875rem; color: #8B949E;">
            <span><strong>Type:</strong> {exc['type'].replace('_', ' ').title()}</span>
            <span><strong>Severity:</strong> {exc['severity'].title()}</span>
            <span><strong>Confidence:</strong> {exc.get('confidence', 0):.0%}</span>
        </div>
        <div style="color: #E6EDF3; margin-top: 1rem;">
            {exc.get('description', 'No description available')}
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔍 Investigate", key=f"investigate_{exc['id']}", type="primary", use_container_width=True):
            st.session_state['investigate_exc_id'] = exc['id']
            st.rerun()
    with col2:
        if st.button("📋 View Evidence", key=f"evidence_{exc['id']}", use_container_width=True):
            st.session_state['view_evidence_id'] = exc['id']
            st.rerun()
    with col3:
        if st.button("📋 View Transaction", key=f"txn_{exc['id']}", use_container_width=True):
            st.session_state['view_txn_id'] = exc['id']
            st.rerun()


def render_exception_list(exceptions: list) -> None:
    """Render a list of exception cards."""
    if not exceptions:
        st.info("No exceptions found")
        return
    
    for exc in exceptions:
        render_exception_card(exc)


def render_exception_investigation_result(resolution: dict) -> None:
    """Render AI investigation result."""
    from dashboard.styles.theme import STATUS_COLORS, get_status_color
    from dashboard.components.status_badge import render_status_badge_inline
    
    st.markdown(f'''
    <div style="
        background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
        border: 1px solid #2D333B;
        border-left: 4px solid {STATUS_COLORS.get(resolution['status'], '#8B949E')};
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: #E6EDF3;">Investigation Result</h3>
            <span style="
                background: {STATUS_COLORS.get(resolution['status'], '#8B949E')};
                color: #E6EDF3;
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: capitalize;
            ">
                {resolution['status'].replace('_', ' ').title()}
            </span>
        </div>
        <div style="display: flex; gap: 1.5rem; margin: 1rem 0; font-size: 0.875rem; color: #8B949E;">
            <span><strong>Classification:</strong> {resolution['classification'].replace('_', ' ').title()}</span>
            <span><strong>Confidence:</strong> {float(resolution['confidence']):.0%}</span>
        </div>
        <div style="color: #E6EDF3; margin-top: 1rem;">
            {resolution['explanation']}
        </div>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #2D333B;">
            <strong>Evidence:</strong>
            <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                {''.join(f'<li>{e}</li>' for e in resolution.get('evidence', []))}
            </ul>
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #2D333B;">
                <strong>Recommended Action:</strong> {resolution.get('recommended_action', 'No action specified')}
            </div>
        </div>
    ''', unsafe_allow_html=True)


# def render_exception_queue(exceptions: list, on_investigate=None) -> None:
#     """Render full exception queue with tabs and actions."""
#     st.markdown('<div class="section-header">Exception Queue</div>', unsafe_allow_html=True)
    
#     if not exceptions:
#         st.info("No exceptions found")
#         return
    
#     df = pd.DataFrame(exceptions)
#     df['confidence_fmt'] = df['confidence'].apply(lambda x: f"{x:.0%}" if pd.notna(x) else "—")
#     df['status_display'] = df['status'].apply(lambda x: x.replace('_', ' ').title())
#     df['type_display'] = df['type'].str.replace('_', ' ').str.title()
    
#     tabs = st.tabs(["All", "Open", "Investigating", "Resolved", "Escalated", "Unresolved"])
#     statuses = ["All", "open", "investigating", "resolved", "escalated", "unresolved"]
    
#     for tab, status in zip(tabs, statuses):
#         with tab:
#             if status == "All":
#                 filtered = df
#             else:
#                 filtered = df[df['status'] == status]
            
#             if len(filtered) == 0:
#                 st.info(f"No {status} exceptions")
#                 continue
            
#             display_df = filtered.copy()
#             display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{x:.0%}" if pd.notna(x) else "—")
#             display_df['status'] = display_df['status'].apply(lambda x: x.replace('_', ' ').title())
#             display_df['type'] = display_df['type'].str.replace('_', ' ').str.title()
            
#             st.dataframe(
#                 display_df[['id', 'transaction_id', 'type', 'severity', 'status', 'confidence', 'description']],
#                 use_container_width=True,
#                 hide_index=True,
#                 column_config={
#                     "id": st.column_config.NumberColumn("Exc ID", width="small"),
#                     "transaction_id": st.column_config.NumberColumn("Txn ID", width="small"),
#                     "type": st.column_config.TextColumn("Type", width="medium"),
#                     "severity": st.column_config.TextColumn("Severity", width="small"),
#                     "status": st.column_config.TextColumn("Status", width="small"),
#                     "confidence": st.column_config.TextColumn("Confidence", width="small"),
#                     "description": st.column_config.TextColumn("Description", width="large"),
#                 }
#             )
            
#             if status in ["All", "open", "investigating"]:
#                 open_exc = filtered[filtered['status'].isin(['open', 'investigating'])]
#                 if len(open_exc) > 0:
#                     selected = st.selectbox(
#                         "Select exception to investigate",
#                         options=open_exc['id'].tolist(),
#                         format_func=lambda x: f"Exception #{x} - {filtered[filtered['id']==x]['description'].values[0][:50]}",
#                         key=f"select_{status}"
#                     )
#                     if st.button("🔍 Investigate", key=f"investigate_{status}", type="primary"):
#                         if callable(on_investigate):
#                             on_investigate(selected)
#                         else:
#                             st.session_state['investigate_exc_id'] = selected
#                             st.rerun()