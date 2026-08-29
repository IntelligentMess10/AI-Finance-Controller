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

    if st.session_state.get('investigate_exc_id'):
        exc_id = st.session_state['investigate_exc_id']
        
        # Call investigate API
        with st.spinner("Running AI investigation..."):
            resolution = api_post(f"/exceptions/{exc_id}/investigate")
        
        if resolution:
            render_exception_investigation_result(resolution)
            
            # Back button
            if st.button("← Back to Exception Queue", type="secondary"):
                st.session_state['investigate_exc_id'] = None
                st.rerun()
        else:
            st.error("Investigation failed")
            if st.button("← Back to Queue"):
                st.session_state['investigate_exc_id'] = None
                st.rerun()
        return 
    
    st.markdown('<div class="section-header">Exception Queue</div>', unsafe_allow_html=True)
    
    # Fetch exceptions
    with st.spinner("Loading exceptions..."):
        exceptions = api_get("/exceptions/")
    
    if not exceptions:
        st.info("No exceptions found")
        return
    
    # Delegate to component
    render_exception_queue(exceptions)


if __name__ == "__main__":
    import streamlit as st
    from dashboard.pages.exceptions import render_exceptions
    render_exceptions()