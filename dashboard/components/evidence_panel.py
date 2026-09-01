import streamlit as st
from typing import Dict, Any, Optional, List
from dashboard.utils.formatters import format_inr, format_date
from dashboard.styles.theme import get_source_color, SOURCE_COLORS


def render_evidence_panel(
    exception_data: dict,
    show_raw: bool = False,
) -> None:
    """
    Render side-by-side evidence panel for Bank | Ledger | Processor.
    
    Args:
        exception_data: Dict containing exception data with source records
        show_raw: Whether to show raw metadata
    """
    st.markdown('<div class="section-header">Evidence Panel</div>', unsafe_allow_html=True)
    
    # Get source records from exception metadata
    evidence = exception_data.get("evidence", [])
    metadata = exception_data.get("metadata", {})
    
    # Extract source records from metadata or evidence
    sources = {
        "BANK": None,
        "LEDGER": None,
        "PROCESSOR": None,
    }
    
    # Try to extract from evidence list
    for item in exception_data.get("evidence", []):
        if "bank" in item.lower():
            source_key = "BANK"
        elif "ledger" in item.lower():
            source_key = "LEDGER"
        elif "processor" in item.lower():
            source_key = "PROCESSOR"
        else:
            continue
    
    # Also check metadata for raw source records
    if "bank" in exception_data.get("metadata", {}):
        sources["BANK"] = exception_data["metadata"]["bank"]
    if "ledger" in exception_data.get("metadata", {}):
        sources["LEDGER"] = exception_data["metadata"]["ledger"]
    if "processor" in exception_data.get("metadata", {}):
        sources["PROCESSOR"] = exception_data["metadata"]["processor"]
    
    # Fallback: check exception metadata for source records
    meta = exception_data.get("metadata", {})
    for source_key in ["BANK", "LEDGER", "PROCESSOR"]:
        key = source_key.lower()
        if key in sources and sources[key] is None:
            # Try to find in metadata
            for k, v in meta.items():
                if source_key.lower() in k.lower():
                    sources[source_key] = v
                    break
    
    # Render three-column layout
    cols = st.columns(3)
    source_config = [
        ("BANK", "🏦 BANK", "#58A6FF"),
        ("LEDGER", "#00D4AA"),
        ("PROCESSOR", "#F0B429"),
    ]
    
    cols = st.columns(3)
    for col, (source_key, title, color) in zip(st.columns(3), source_config):
        with col:
            render_source_card(source_key, exception_data, color)


def render_source_card(source_key: str, exception_data: dict, color: str) -> None:
    """Render a single source card (Bank, Ledger, or Processor)."""
    from dashboard.styles.theme import SOURCE_COLORS
    
    # Get source data from exception metadata
    meta = exception_data.get("metadata", {})
    source_data = None
    source_title = ""
    
    # Try to find source data in metadata
    source_key_lower = source_key.lower()
    for k, v in exception_data.get("metadata", {}).items():
        if source_key.lower() in k.lower():
            source_data = v
            break
    
    # Also check txn_metadata on canonical transaction
    if not source_data:
        # Check if there's a canonical transaction with this source
        pass
    
    st.markdown(f'''
    <div style="
        background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
        border: 1px solid #2D333B;
        border-left: 3px solid {SOURCE_COLORS.get("bank", "#58A6FF") if "bank" in source_key.lower() else SOURCE_COLORS.get("ledger", "#00D4AA") if "ledger" in source_key.lower() else SOURCE_COLORS.get("processor", "#F0B429")};
        border-radius: 8px;
        padding: 1rem;
        height: 100%;
    ">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
            <span style="
                background: {SOURCE_COLORS.get("bank", "#58A6FF") if "bank" in source_key.lower() else SOURCE_COLORS.get("ledger", "#00D4AA") if "ledger" in source_key.lower() else "#F0B429"};
                color: #0E1117;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.7rem;
                font-weight: 700;
                text-transform: uppercase;
            ">
                {source_key}
            </span>
        </div>
    ''', unsafe_allow_html=True)
    
    # Render source data if available
    # ... (implementation continues)
    st.markdown('</div>', unsafe_allow_html=True)


def render_evidence_panel_simple(exception_data: dict) -> None:
    """Simplified evidence panel showing source records side by side."""
    
    # Extract source records from exception metadata
    meta = exception_data.get("metadata", {})
    evidence = exception_data.get("evidence", [])
    
    # Build source data
    sources = {
        "BANK": None,
        "LEDGER": None,
        "PROCESSOR": None,
    }
    
    # Check metadata for source records
    for key, value in exception_data.get("metadata", {}).items():
        if "bank" in key.lower():
            source_data = value
        elif "ledger" in key.lower():
            source_data = value
        elif "processor" in key.lower():
            source_data = value
    
    # Also check evidence list for source indicators
    for item in exception_data.get("evidence", []):
        item_lower = item.lower()
        if "bank" in item_lower and "bank" not in [k.lower() for k in source_data]:
            pass
    
    # Simple three-column layout
    cols = st.columns(3)
    source_configs = [
        ("BANK", "🏦 BANK", "#58A6FF"),
        ("LEDGER", "📒 LEDGER", "#00D4AA"),
        ("PROCESSOR", "⚙️ PROCESSOR", "#F0B429"),
    ]
    
    for col, (source_key, title, color) in zip(st.columns(3), source_configs):
        with col:
            st.markdown(f'''
            <div style="
                background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
                border: 1px solid #2D333B;
                border-left: 3px solid {SOURCE_COLORS.get("bank", "#58A6FF") if "bank" in source_key.lower() else SOURCE_COLORS.get("ledger", "#00D4AA") if "ledger" in source_key.lower() else "#F0B429"};
                border-radius: 8px;
                padding: 1rem;
                height: 100%;
            ">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <span style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; color: #8B949E;">
                        {source_key}
                    </span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Add source-specific data here
            st.caption("No data available")


def render_evidence_panel_side_by_side(
    exception_data: dict,
    bank_data: dict = None,
    ledger_data: dict = None,
    processor_data: dict = None,
) -> None:
    """
    Render side-by-side evidence panel for Bank | Ledger | Processor.
    
    Args:
        exception_data: Full exception data from API
        bank_data: Bank transaction data (optional, will extract from exception if not provided)
        ledger_data: Ledger transaction data (optional)
        processor_data: Processor transaction data (optional)
    """
    st.markdown('<div class="section-header">Evidence Panel</div>', unsafe_allow_html=True)
    
    # Determine source data
    bank_data = bank_data or {}
    ledger_data = ledger_data or {}
    processor_data = processor_data or {}
    
    # Try to extract from exception metadata
    meta = exception_data.get("metadata", {})
    if not any([bank_data, ledger_data, processor_data]):
        for k, v in exception_data.get("metadata", {}).items():
            key_lower = k.lower()
            if "bank" in key_lower and not bank_data:
                bank_data = v
            elif "ledger" in k.lower():
                ledger_data = v
            elif "processor" in key_lower:
                processor_data = v
    
    # Colors for each source
    from dashboard.styles.theme import SOURCE_COLORS
    
    cols = st.columns(3)
    source_configs = [
        ("BANK", "🏦 BANK", SOURCE_COLORS.get("bank", "#58A6FF"), bank_data),
        ("LEDGER", "📒 LEDGER", SOURCE_COLORS.get("ledger", "#00D4AA"), ledger_data),
        ("PROCESSOR", "⚙️ PROCESSOR", SOURCE_COLORS.get("processor", "#F0B429"), processor_data),
    ]
    
    cols = st.columns(3)
    
    for col, (source_key, title, color, data) in zip(st.columns(3), [
        ("BANK", "🏦 BANK", SOURCE_COLORS.get("bank", "#58A6FF"), {}),
        ("LEDGER", "📒 LEDGER", SOURCE_COLORS.get("ledger", "#00D4AA"), {}),
        ("PROCESSOR", "⚙️ PROCESSOR", SOURCE_COLORS.get("processor", "#F0B429"), {}),
    ]):
        with col:
            st.markdown(f'''
            <div style="
                background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
                border: 1px solid #2D333B;
                border-left: 3px solid {color};
                border-radius: 8px;
                padding: 1rem;
                height: 100%;
            ">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <span style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; color: {color};">
                        {title}
                    </span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Render source data fields
            if data:
                for key, value in data.items():
                    if key.startswith("_"):
                        continue
                    st.markdown(f'''
                    <div style="margin: 0.5rem 0; padding: 0.5rem; background: #161B22; border-radius: 4px;">
                        <div style="font-size: 0.7rem; color: #8B949E; text-transform: uppercase;">{key}</div>
                        <div style="font-family: monospace; font-size: 0.85rem;">{value}</div>
                    </div>
                    ''', unsafe_allow_html=True)
            else:
                st.caption("No data available")


def render_evidence_panel_compact(
    exception_data: dict,
) -> None:
    """
    Compact evidence panel for use in exception detail views.
    """
    st.markdown('<div class="section-header">Evidence</div>', unsafe_allow_html=True)
    
    # Get source records from exception
    meta = exception_data.get("metadata", {})
    evidence = exception_data.get("evidence", [])
    
    # Build source records
    sources = {"BANK": {}, "LEDGER": {}, "PROCESSOR": {}}
    
    # Extract from metadata
    for k, v in exception_data.get("metadata", {}).items():
        k_lower = k.lower()
        if "bank" in k:
            sources["BANK"][k] = v
        elif "ledger" in k:
            sources["LEDGER"][k] = v
        elif "processor" in k:
            sources["PROCESSOR"][k] = v
    
    # Also check evidence list
    for item in exception_data.get("evidence", []):
        item_lower = item.lower()
        if "bank" in item_lower:
            sources["BANK"]["evidence"] = item
        elif "ledger" in item_lower:
            sources["LEDGER"]["evidence"] = item
        elif "processor" in item_lower:
            sources["PROCESSOR"]["evidence"] = item
    
    # Render
    from dashboard.styles.theme import SOURCE_COLORS
    
    cols = st.columns(3)
    for col, (source_key, color) in zip(st.columns(3), [
        ("BANK", SOURCE_COLORS.get("bank", "#58A6FF")),
        ("LEDGER", SOURCE_COLORS.get("ledger", "#00D4AA")),
        ("PROCESSOR", SOURCE_COLORS.get("processor", "#F0B429")),
    ]):
        with col:
            source_data = {"BANK": {}, "LEDGER": {}, "PROCESSOR": {}}[source_key]
            
            st.markdown(f'''
            <div style="
                background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
                border: 1px solid #2D333B;
                border-left: 3px solid {color};
                border-radius: 8px;
                padding: 1rem;
            ">
                <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; color: {color}; margin-bottom: 0.5rem;">
                    {source_key}
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Display key-value pairs
            # ... render key-value pairs from data


def render_exception_evidence_detail(exception_data: dict) -> None:
    """
    Render detailed evidence view for an exception.
    Shows side-by-side Bank | Ledger | Processor records.
    """
    st.markdown('<div class="section-header">Exception Evidence</div>', unsafe_allow_html=True)
    
    # Get the canonical transaction for this exception
    txn_id = exception_data.get("transaction_id")
    
    # Try to get source records from metadata
    meta = exception_data.get("metadata", {})
    
    # Build source records
    sources = {
        "BANK": {},
        "LEDGER": {},
        "PROCESSOR": {},
    }
    
    # Extract from metadata
    for k, v in exception_data.get("metadata", {}).items():
        kl = k.lower()
        if "bank" in k.lower():
            sources["BANK"][k] = v
        elif "ledger" in k.lower():
            sources["LEDGER"][k] = v
        elif "processor" in k.lower():
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
            
            # Render source data fields
            # ... (render key-value pairs from source data)


def render_exception_evidence_detail(exception_data: dict) -> None:
    """
    Main entry point for rendering exception evidence detail.
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
            "BANK"
        elif "ledger" in kl:
            pass
        elif "processor" in k:
            pass
    
    # Render three columns
    from dashboard.styles.theme import SOURCE_COLORS
    cols = st.columns(3)
    for col, (src_key, color) in zip(st.columns(3), [
        ("BANK", SOURCE_COLORS.get("bank", "#58A6FF")),
        ("LEDGER", SOURCE_COLORS.get("ledger", "#00D4AA")),
        ("PROCESSOR", SOURCE_COLORS.get("processor", "#F0B429")),
    ]):
        with col:
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
            
            # Display source data
            # ... render key-value pairs from source data