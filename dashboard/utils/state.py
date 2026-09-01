import streamlit as st


def init_session_state() -> None:
    """Initialize session state variables."""
    if "investigate_exc_id" not in st.session_state:
        st.session_state["investigate_exc_id"] = None
    
    if "view_evidence_id" not in st.session_state:
        st.session_state["view_evidence_id"] = None
    
    if "view_txn_id" not in st.session_state:
        st.session_state["view_txn_id"] = None
    
    if "investigate_exc_id" not in st.session_state:
        st.session_state["investigate_exc_id"] = None
    
    if "view_evidence_id" not in st.session_state:
        st.session_state["view_evidence_id"] = None
    
    if "view_txn_id" not in st.session_state:
        st.session_state["view_txn_id"] = None
    
    if "run_reconciliation" not in st.session_state:
        st.session_state["run_reconciliation"] = False