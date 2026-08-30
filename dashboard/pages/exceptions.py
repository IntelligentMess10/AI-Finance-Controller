"""
Exceptions Page - Tabbed exception queue with investigation actions.
"""

import streamlit as st
import pandas as pd
from dashboard.components.exception_queue import render_exception_queue
from dashboard.utils.api_client import api_get
from dashboard.components.exception_queue import render_exception_queue, render_exception_investigation_result
from dashboard.utils.api_client import api_get, api_post


def render_exceptions():
    """Render the exceptions page with tabbed queue and investigation actions."""
    
    # Initialize session state
    if 'investigation_result' not in st.session_state:
        st.session_state['investigation_result'] = None
    
    # Show cached investigation result (no API call on rerun)
    if st.session_state.get('investigation_result'):
        render_exception_investigation_result(st.session_state['investigation_result'])
        if st.button("← Back to Exception Queue", type="secondary"):
            st.session_state['investigation_result'] = None
            st.session_state['investigate_exc_id'] = None
            st.rerun()
        return
    
    # Create spinner container at the TOP before header
    spinner_container = st.container()
    
    st.markdown('<div class="section-header">Exception Queue</div>', unsafe_allow_html=True)
    
    # Fetch exceptions
    with st.spinner("Loading exceptions..."):
        exceptions = api_get("/exceptions/")
    
    if not exceptions:
        st.info("No exceptions found")
        return
    
    # Callback that calls API AND stores result
    def handle_investigate(exc_id):
        with spinner_container.spinner("Running AI investigation..."):  # Spinner shows at top
            resolution = api_post(f"/exceptions/{exc_id}/investigate")
        if resolution:
            st.session_state['investigation_result'] = resolution
            st.session_state['investigate_exc_id'] = exc_id
            st.rerun()
    
    # Delegate to component with callback
    render_exception_queue(exceptions, on_investigate=handle_investigate)


if __name__ == "__main__":
    import streamlit as st
    from dashboard.pages.Exceptions import render_exceptions
    render_exceptions()