"""
Exceptions Page - Tabbed exception queue with investigation actions.
"""

import streamlit as st
import pandas as pd
from dashboard.components.exception_queue import render_exception_queue
from dashboard.utils.api_client import api_get


def render_exceptions():
    """Render the exceptions page with tabbed queue and investigation actions."""
    
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