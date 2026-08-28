"""
Exception Detail Component - Detailed view for exception investigation.
"""

import streamlit as st
from typing import Optional, Dict, Any
from dashboard.utils.formatters import format_inr, format_pct
from dashboard.utils.api_client import api_get
from dashboard.styles.theme import get_status_color, STATUS_COLORS
from dashboard.components.status_badge import render_status_badge_inline
from dashboard.components.evidence_panel import render_evidence_panel


def render_exception_detail(exception_data: dict) -> None:
    """Render detailed exception view with investigation actions."""
    exc = exception_data
    
    st.markdown(f'''
    <div style="
        background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
        border: 1px solid #2D333B;
        border-left: 4px solid {get_status_color(exc['status'])};
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: #E6EDF3;">Exception #{exc['id']}</h1>
            <span style="
                background: {get_status_color(exc['status'])};
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


def render_exception_evidence_detail(exception_data: dict) -> None:
    """
    Render detailed evidence view for an exception.
    Shows side-by-side Bank | Ledger | Processor records.
    """
    st.markdown('<div class="section-header">Exception Evidence</div>', unsafe_allow_html=True)
    
    # Get the canonical transaction for this exception
    txn_id = exception_data.get("transaction_id")
    
    # Build source records
    sources = {"BANK": {}, "LEDGER": {}, "PROCESSOR": {}}
    
    # Extract from metadata
    for k, v in exception_data.get("metadata", {}).items():
        kl = k.lower()
        if "bank" in kl:
            sources["BANK"][k] = v
        elif "ledger" in kl:
            sources["LEDGER"][k] = v
        elif "processor" in kl:
            sources["PROCESSOR"][k] = v
    
    # Also check evidence list
    for item in exception_data.get("evidence", []):
        il = item.lower()
        if "bank" in il:
            sources["BANK"]["evidence"] = item
        elif "ledger" in il:
            sources["LEDGER"]["evidence"] = item
        elif "processor" in il:
            sources["PROCESSOR"]["evidence"] = item
    
    # Render three columns
    from dashboard.styles.theme import SOURCE_COLORS
    
    cols = st.columns(3)
    for col, (src_key, color) in zip(st.columns(3), [
        ("BANK", SOURCE_COLORS.get("bank", "#58A6FF")),
        ("LEDGER", SOURCE_COLORS.get("ledger", "#00D4AA")),
        ("PROCESSOR", SOURCE_COLORS.get("processor", "#F0B429")),
    ]):
        with col:
            source_data = sources.get(src_key, {})
            
            st.markdown(f'''
            <div style="
                background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
                border: 1px solid #2D333B;
                border-left: 3px solid {color};
                border-radius: 8px;
                padding: 1rem;
                min-height: 300px;
            ">
                <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; color: {color}; margin-bottom: 1rem;">
                    {src_key}
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Render source data fields
            source_data = {"BANK": {}, "LEDGER": {}, "PROCESSOR": {}}[src_key]
            
            if source_data:
                for k, v in source_data.items():
                    if k.startswith("_"):
                        continue
                    st.markdown(f'''
                    <div style="margin: 0.5rem 0; padding: 0.5rem; background: #161B22; border-radius: 4px;">
                        <div style="font-size: 0.7rem; color: #8B949E; text-transform: uppercase;">{k}</div>
                        <div style="font-family: monospace; font-size: 0.85rem;">{v}</div>
                    </div>
                    ''', unsafe_allow_html=True)
            else:
                st.caption("No data available")


def render_exception_evidence_detail(exception_data: dict) -> None:
    """
    Main entry point for rendering exception evidence detail.
    Shows side-by-side Bank | Ledger | Processor records.
    """
    st.markdown('<div class="section-header">Exception Evidence</div>', unsafe_allow_html=True)
    
    # Get the canonical transaction for this exception
    txn_id = exception_data.get("transaction_id")
    
    # Build source records
    sources = {"BANK": {}, "LEDGER": {}, "PROCESSOR": {}}
    
    # Extract from metadata
    for k, v in exception_data.get("metadata", {}).items():
        kl = k.lower()
        if "bank" in kl:
            sources["BANK"][k] = v
        elif "ledger" in kl:
            sources["LEDGER"][k] = v
        elif "processor" in kl:
            sources["PROCESSOR"][k] = v
    
    # Also check evidence list
    for item in exception_data.get("evidence", []):
        il = item.lower()
        if "bank" in il:
            sources["BANK"]["evidence"] = item
        elif "ledger" in il:
            sources["LEDGER"]["evidence"] = item
        elif "processor" in il:
            sources["PROCESSOR"]["evidence"] = item
    
    # Render three columns
    from dashboard.styles.theme import SOURCE_COLORS
    
    cols = st.columns(3)
    for col, (src_key, color) in zip(st.columns(3), [
        ("BANK", SOURCE_COLORS.get("bank", "#58A6FF")),
        ("LEDGER", SOURCE_COLORS.get("ledger", "#00D4AA")),
        ("PROCESSOR", SOURCE_COLORS.get("processor", "#F0B429")),
    ]):
        with col:
            source_data = {"BANK": {}, "LEDGER": {}, "PROCESSOR": {}}[src_key]
            
            st.markdown(f'''
            <div style="
                background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
                border: 1px solid #2D333B;
                border-left: 3px solid {SOURCE_COLORS.get(src_key.lower(), "#8B949E")};
                border-radius: 8px;
                padding: 1rem;
                min-height: 300px;
            ">
                <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; color: {color}; margin-bottom: 1rem;">
                    {src_key}
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Display source data fields
            # ... render key-value pairs from source data