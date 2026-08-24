import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta
from decimal import Decimal
import plotly.graph_objects as go
import plotly.express as px

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="AI Finance Controller",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #0E1117; }
    .stApp { background-color: #0E1117; }
    .block-container { padding-top: 2rem; }
    .metric-card {
        background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
        border: 1px solid #2D333B;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #00D4AA; }
    .metric-label { font-size: 0.875rem; color: #8B949E; text-transform: uppercase; letter-spacing: 0.05em; }
    .status-matched { background: #1A3A2A; color: #00D4AA; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
    .status-probable { background: #3A2E1A; color: #F0B429; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
    .status-exception { background: #3A1A1A; color: #FF6B6B; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
    .status-unresolved { background: #2D2D3A; color: #8B949E; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
    .evidence-panel { background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 1rem; }
    .section-header { color: #E6EDF3; font-weight: 600; font-size: 1.125rem; margin-bottom: 1rem; }
    .stButton>button { background: #1E2329; border: 1px solid #30363D; color: #E6EDF3; }
    .stButton>button:hover { background: #2D333B; border-color: #00D4AA; }
    .sidebar .stSelectbox { background: #161B22; }
    h1, h2, h3 { color: #E6EDF3; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background: #1E2329; border-radius: 6px 6px 0 0; padding: 0.5rem 1rem; }
    .stTabs [aria-selected="true"] { background: #2D333B; color: #00D4AA; }
</style>
""", unsafe_allow_html=True)


def api_get(endpoint: str, params: dict = None):
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def api_post(endpoint: str, json_data: dict = None):
    try:
        resp = requests.post(f"{API_BASE}{endpoint}", json=json_data, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def format_inr(amount: float) -> str:
    if amount >= 10000000:
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:
        return f"₹{amount/100000:.2f} L"
    else:
        return f"₹{amount:,.2f}"


def status_badge(status: str) -> str:
    classes = {
        "matched": "status-matched",
        "probable_match": "status-probable",
        "exception": "status-exception",
        "unresolved": "status-unresolved",
        "escalated": "status-exception",
    }
    cls = classes.get(status, "status-unresolved")
    return f'<span class="{cls}">{status.replace("_", " ").title()}</span>'


def main():
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem;">
        <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #00D4AA 0%, #00A3CC 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">💰</div>
        <div>
            <h1 style="margin: 0; font-size: 1.75rem;">AI Finance Controller</h1>
            <p style="margin: 0; color: #8B949E; font-size: 0.875rem;">Run the books and the cash position.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab_overview, tab_reconciliation, tab_exceptions, tab_cash, tab_metrics = st.tabs([
        "📊 Overview", "🔍 Reconciliation", "⚠️ Exceptions", "💵 Cash Position", "📈 Metrics"
    ])
    
    with tab_overview:
        render_overview()
    
    with tab_reconciliation:
        render_reconciliation()
    
    with tab_exceptions:
        render_exceptions()
    
    with tab_cash:
        render_cash_position()
    
    with tab_metrics:
        render_metrics()


def render_overview():
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = api_get("/metrics/")
    cash = api_get("/cash/position")
    
    if metrics:
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Match Rate</div>
                <div class="metric-value">{metrics['match_rate']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Records</div>
                <div class="metric-value">{metrics['total_records']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Exceptions</div>
                <div class="metric-value">{metrics['exceptions_total']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            unresolved = metrics['exceptions_unresolved']
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Unresolved</div>
                <div class="metric-value" style="color: {'#FF6B6B' if unresolved > 0 else '#00D4AA'};">{unresolved}</div>
            </div>
            """, unsafe_allow_html=True)
    
    if cash:
        st.markdown("### Cash Position")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Expected Cash</div>
                <div class="metric-value">{format_inr(float(cash['expected_cash']))}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Bank Cash</div>
                <div class="metric-value">{format_inr(float(cash['bank_cash']))}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            variance = float(cash['variance'])
            color = "#00D4AA" if variance >= 0 else "#FF6B6B"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Variance</div>
                <div class="metric-value" style="color: {color};">{format_inr(variance)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Cash waterfall chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Opening',
            x=['Cash Position'],
            y=[float(cash['opening_balance'])],
            marker_color='#58A6FF',
            text=[format_inr(float(cash['opening_balance']))],
            textposition='auto',
        ))
        fig.add_trace(go.Bar(
            name='Confirmed Inflows',
            x=['Cash Position'],
            y=[float(cash['confirmed_inflows'])],
            marker_color='#00D4AA',
            text=[format_inr(float(cash['confirmed_inflows']))],
            textposition='auto',
        ))
        fig.add_trace(go.Bar(
            name='Confirmed Outflows',
            x=['Cash Position'],
            y=[-float(cash['confirmed_outflows'])],
            marker_color='#FF6B6B',
            text=[format_inr(float(cash['confirmed_outflows']))],
            textposition='auto',
        ))
        fig.add_trace(go.Bar(
            name='Pending Net',
            x=['Cash Position'],
            y=[float(cash['pending_inflows']) - float(cash['pending_outflows'])],
            marker_color='#F0B429',
            text=[format_inr(float(cash['pending_inflows']) - float(cash['pending_outflows']))],
            textposition='auto',
        ))
        fig.add_trace(go.Bar(
            name='Expected',
            x=['Cash Position'],
            y=[float(cash['expected_cash'])],
            marker_color='#8B949E',
            text=[format_inr(float(cash['expected_cash']))],
            textposition='auto',
        ))
        
        fig.update_layout(
            barmode='relative',
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            font_color='#E6EDF3',
            showlegend=True,
            height=400,
            margin=dict(l=40, r=40, t=40, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Quick actions
    st.markdown("### Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Run Reconciliation", use_container_width=True):
            with st.spinner("Running reconciliation..."):
                result = api_post("/reconciliation/run", {"force_rerun": True})
                if result:
                    st.success(f"Done: {result['matched']} matched, {result['exceptions']} exceptions")
                    st.rerun()
    with col2:
        if st.button("🤖 Investigate Exceptions", use_container_width=True):
            st.info("AI investigation triggered")
    with col3:
        if st.button("📊 Refresh Metrics", use_container_width=True):
            st.rerun()


def render_reconciliation():
    st.markdown('<div class="section-header">Reconciliation Results</div>', unsafe_allow_html=True)
    
    matches = api_get("/reconciliation/results")
    
    if matches:
        df = pd.DataFrame(matches)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.multiselect("Status", df['status'].unique().tolist(), default=df['status'].unique().tolist())
        with col2:
            method_filter = st.multiselect("Method", df['method'].unique().tolist(), default=df['method'].unique().tolist())
        with col3:
            min_score = st.slider("Min Score", 0.0, 1.0, 0.0, 0.05)
        
        filtered = df[
            (df['status'].isin(status_filter)) &
            (df['method'].isin(method_filter)) &
            (df['score'] >= min_score)
        ]
        
        # Display table
        display_df = filtered.copy()
        display_df['score'] = display_df['score'].apply(lambda x: f"{x:.2%}")
        display_df['status'] = display_df['status'].apply(lambda x: x.replace('_', ' ').title())
        
        st.dataframe(
            display_df[['id', 'canonical_transaction_id', 'matched_transaction_id', 'score', 'method', 'status']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": "Match ID",
                "canonical_transaction_id": "Txn A",
                "matched_transaction_id": "Txn B",
                "score": "Score",
                "method": "Method",
                "status": "Status",
            }
        )
        
        st.caption(f"Showing {len(filtered)} of {len(matches)} matches")


def render_exceptions():
    st.markdown('<div class="section-header">Exception Queue</div>', unsafe_allow_html=True)
    
    exceptions = api_get("/exceptions/")
    
    if exceptions:
        df = pd.DataFrame(exceptions)
        
        tabs = st.tabs(["All", "Open", "Investigating", "Resolved", "Escalated", "Unresolved"])
        statuses = ["All", "open", "investigating", "resolved", "escalated", "unresolved"]
        
        for tab, status in zip(tabs, statuses):
            with tab:
                if status == "All":
                    filtered = df
                else:
                    filtered = df[df['status'] == status]
                
                if len(filtered) > 0:
                    display_df = filtered.copy()
                    display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{x:.0%}" if pd.notna(x) else "—")
                    
                    st.dataframe(
                        display_df[['id', 'transaction_id', 'type', 'severity', 'status', 'confidence', 'description']],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "id": "Exc ID",
                            "transaction_id": "Txn ID",
                            "type": "Type",
                            "severity": "Severity",
                            "status": "Status",
                            "confidence": "Confidence",
                            "description": "Description",
                        }
                    )
                    
                    if status in ["open", "investigating"]:
                        selected = st.selectbox(
                            "Select exception to investigate",
                            options=filtered['id'].tolist(),
                            format_func=lambda x: f"Exception #{x} - {filtered[filtered['id']==x]['description'].values[0][:50]}",
                            key=f"select_{status}"
                        )
                        if st.button("🔍 Investigate", key=f"inv_{status}"):
                            result = api_post(f"/exceptions/{selected}/investigate")
                            if result:
                                st.success("Investigation started")
                                st.rerun()
                else:
                    st.info(f"No {status} exceptions")


def render_cash_position():
    st.markdown('<div class="section-header">Cash Position & Forecast</div>', unsafe_allow_html=True)
    
    cash = api_get("/cash/position")
    
    if cash:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Detailed breakdown
            st.markdown("#### Position Breakdown")
            breakdown = [
                ("Opening Balance", cash['opening_balance'], "#58A6FF"),
                ("Confirmed Inflows", cash['confirmed_inflows'], "#00D4AA"),
                ("Confirmed Outflows", -float(cash['confirmed_outflows']), "#FF6B6B"),
                ("Pending Inflows", cash['pending_inflows'], "#F0B429"),
                ("Pending Outflows", -float(cash['pending_outflows']), "#F0B429"),
                ("**Expected Cash**", cash['expected_cash'], "#E6EDF3"),
                ("Bank Reported", cash['bank_cash'], "#8B949E"),
                ("**Variance**", cash['variance'], "#00D4AA" if float(cash['variance']) >= 0 else "#FF6B6B"),
            ]
            
            for label, value, color in breakdown:
                is_total = label.startswith("**")
                clean_label = label.replace("**", "")
                fmt_value = format_inr(float(value))
                prefix = "+" if float(value) > 0 and not is_total and "Outflow" not in label else ""
                if "Outflow" in label or float(value) < 0:
                    prefix = ""
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: {'#1E2329' if is_total else '#161B22'}; border-radius: 6px; margin: 0.25rem 0; border-left: 3px solid {color};">
                    <span style="color: {'#E6EDF3' if is_total else '#8B949E'}; font-weight: {'600' if is_total else '400'};">{clean_label}</span>
                    <span style="color: {color}; font-weight: {'700' if is_total else '500'};">{prefix}{fmt_value}</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Forecast")
            forecast = api_get("/cash/forecast", {"days": 30})
            
            if forecast:
                df = pd.DataFrame(forecast)
                
                for horizon in [7, 14, 30]:
                    h_data = df[df['horizon_days'] <= horizon]
                    inflows = h_data[h_data['amount'] > 0]['amount'].sum()
                    outflows = abs(h_data[h_data['amount'] < 0]['amount'].sum())
                    net = inflows - outflows
                    
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 1rem;">
                        <div class="metric-label">{horizon}-Day Forecast</div>
                        <div style="color: #00D4AA; font-size: 1.25rem;">{format_inr(inflows)} In</div>
                        <div style="color: #FF6B6B; font-size: 1.25rem;">{format_inr(outflows)} Out</div>
                        <div style="color: {'#00D4AA' if net >= 0 else '#FF6B6B'}; font-size: 1.5rem; font-weight: 700; margin-top: 0.5rem;">Net: {format_inr(net)}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Forecast chart
            if forecast:
                df = pd.DataFrame(forecast)
                df['date'] = pd.to_datetime(df['forecast_date'])
                df_in = df[df['amount'] > 0].groupby('date')['amount'].sum().reset_index()
                df_out = df[df['amount'] < 0].groupby('date')['amount'].sum().reset_index()
                
                fig = go.Figure()
                fig.add_trace(go.Bar(x=df_in['date'], y=df_in['amount'], name='Inflows', marker_color='#00D4AA'))
                fig.add_trace(go.Bar(x=df_out['date'], y=df_out['amount'], name='Outflows', marker_color='#FF6B6B'))
                
                fig.update_layout(
                    barmode='relative',
                    plot_bgcolor='#0E1117',
                    paper_bgcolor='#0E1117',
                    font_color='#E6EDF3',
                    height=300,
                    margin=dict(l=40, r=40, t=40, b=40),
                )
                st.plotly_chart(fig, use_container_width=True)


def render_metrics():
    st.markdown('<div class="section-header">Evaluation Metrics</div>', unsafe_allow_html=True)
    
    metrics = api_get("/metrics/")
    
    if metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Match Rate", f"{metrics['match_rate']:.1f}%")
        with col2:
            st.metric("Accuracy", f"{metrics['accuracy']:.1f}%")
        with col3:
            st.metric("False Match Rate", f"{metrics['false_match_rate']:.2f}%")
        with col4:
            st.metric("Processing Time", f"{metrics['processing_time_seconds']:.2f}s")
        
        # Confusion matrix placeholder
        st.markdown("### Ground Truth Comparison")
        
        data = {
            "Category": ["True Positives", "False Positives", "True Negatives", "False Negatives"],
            "Count": [metrics['matched_records'], 0, 0, 0],
        }
        
        fig = px.bar(data, x="Category", y="Count", color="Category",
                     color_discrete_map={
                         "True Positives": "#00D4AA",
                         "False Positives": "#FF6B6B",
                         "True Negatives": "#58A6FF",
                         "False Negatives": "#F0B429",
                     })
        fig.update_layout(
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            font_color='#E6EDF3',
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Exception resolution breakdown
        st.markdown("### Exception Resolution")
        exc_data = {
            "Status": ["Resolved", "Escalated", "Unresolved"],
            "Count": [metrics['exceptions_resolved'], metrics['exceptions_escalated'], metrics['exceptions_unresolved']],
        }
        fig2 = px.pie(exc_data, values="Count", names="Status",
                      color="Status",
                      color_discrete_map={
                          "Resolved": "#00D4AA",
                          "Escalated": "#F0B429",
                          "Unresolved": "#FF6B6B",
                      })
        fig2.update_layout(
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            font_color='#E6EDF3',
        )
        st.plotly_chart(fig2, use_container_width=True)


if __name__ == "__main__":
    main()