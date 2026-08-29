"""
Chart helpers and Plotly utilities for the dashboard.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from decimal import Decimal
from typing import List, Dict, Any, Optional, List
from dashboard.styles.theme import THEME, STATUS_COLORS, SOURCE_COLORS


# Common layout settings for all charts
BASE_LAYOUT = dict(
    plot_bgcolor="#0E1117",
    paper_bgcolor="#0E1117",
    font_color="#E6EDF3",
    font_family="'Inter', -apple-system, sans-serif",
    margin=dict(l=40, r=40, t=40, b=40),
    showlegend=True,
    legend=dict(
        bgcolor="#1E2329",
        bordercolor="#2D333B",
        borderwidth=1,
        font=dict(color="#E6EDF3", size=12),
    ),
    xaxis=dict(
        gridcolor="#2D333B",
        zerolinecolor="#2D333B",
        linecolor="#2D333B",
        tickfont=dict(color="#8B949E", size=11),
        title_font=dict(color="#E6EDF3", size=12),
    ),
    yaxis=dict(
        gridcolor="#2D333B",
        zerolinecolor="#2D333B",
        linecolor="#2D333B",
        tickfont=dict(color="#8B949E", size=11),
        title_font=dict(color="#E6EDF3", size=12),
    ),
    hoverlabel=dict(
        bgcolor="#1E2329",
        bordercolor="#2D333B",
        font=dict(color="#E6EDF3", size=12),
    ),
)


def apply_base_layout(fig: go.Figure, **overrides) -> go.Figure:
    """Apply base layout to a figure with optional overrides."""
    layout = BASE_LAYOUT.copy()
    layout.update(overrides)
    fig.update_layout(**layout)
    return fig


def create_waterfall_chart(
    opening: float,
    inflows: float,
    outflows: float,
    pending_in: float = 0,
    pending_out: float = 0,
    expected: float = None,
    bank_cash: float = None,
) -> go.Figure:
    """
    Create a cash position waterfall chart.
    
    Args:
        opening: Opening balance
        inflows: Confirmed inflows
        outflows: Confirmed outflows
        pending_in: Pending inflows
        pending_out: Pending outflows
        expected: Expected cash (calculated if not provided)
        bank_cash: Actual bank cash (optional)
    """
    fig = go.Figure()
    
    # Calculate values
    opening = float(opening)
    inflows = float(inflows)
    outflows = float(outflows)
    pending_in = float(pending_in)
    pending_out = float(pending_out)
    
    expected = (inflows - outflows) if inflows or outflows else 0
    
    fig = go.Figure()
    
    # Opening Balance
    fig.add_trace(go.Bar(
        name='Opening Balance',
        x=['Cash Position'],
        y=[opening],
        marker_color='#58A6FF',
        text=[f"₹{opening:,.0f}"],
        textposition='auto',
        textfont=dict(size=11, color='#E6EDF3'),
        width=0.6,
    ))
    
    # Confirmed Inflows
    if inflows > 0:
        fig.add_trace(go.Bar(
            name='Confirmed Inflows',
            x=['Cash Position'],
            y=[float(inflows)],
            marker_color='#00D4AA',
            text=[f"₹{inflows:,.0f}"],
            textposition='auto',
            textfont=dict(size=11, color='#E6EDF3'),
            width=0.6,
        ))
    
    # Confirmed Outflows
    if outflows > 0:
        fig.add_trace(go.Bar(
            name='Confirmed Outflows',
            x=['Cash Position'],
            y=[-float(outflows)],
            marker_color='#FF6B6B',
            text=[f"₹{float(outflows):,.0f}"],
            textposition='auto',
            textfont=dict(size=11, color='#E6EDF3'),
            width=0.6,
        ))
    
    # Pending Net
    pending_net = float(pending_in) - float(outflows) if pending_out else float(pending_in)
    if pending_in or pending_out:
        pending_net = float(pending_in) - float(pending_out)
        if pending_net != 0:
            fig.add_trace(go.Bar(
                name='Pending Net',
                x=['Cash Position'],
                y=[pending_net],
                marker_color='#F0B429',
                text=[f"₹{abs(pending_net):,.0f}"],
                textposition='auto',
                textfont=dict(size=11, color='#E6EDF3'),
                width=0.6,
            ))
    
    # Expected Cash
    expected = float(opening) + sum([
        float(inflows) if inflows else 0,
        -float(outflows) if outflows else 0,
    ])
    # Add pending if we want to show in expected
    # expected += (pending_in - pending_out) if we want to show expected with pending
    
    fig.add_trace(go.Bar(
        name='Expected Cash',
        x=['Cash Position'],
        y=[float(inflows) - float(outflows) + float(opening)],  # Simplified
        marker_color='#8B949E',
        text=[f"₹{float(inflows) - float(outflows) + float(opening):,.0f}"],
        textposition='auto',
        textfont=dict(size=11, color='#E6EDF3'),
        width=0.6,
    ))
    
    return apply_base_layout(
        go.Figure(),
        barmode='relative',
        title="Cash Position Waterfall",
        xaxis_title="",
        yaxis_title="Amount (₹)",
        height=400,
    )


def create_cash_waterfall_chart(
    opening: float,
    inflows: float = 0,
    outflows: float = 0,
    pending_in: float = 0,
    pending_out: float = 0,
    expected_cash: float = None,
    bank_cash: float = None,
) -> go.Figure:
    """Create a cash position waterfall chart."""
    fig = go.Figure()

    opening = float(opening or 0)
    inflows = float(inflows or 0)
    outflows = float(outflows or 0)
    pending_in = float(pending_in or 0)
    pending_out = float(pending_out or 0)

    fig.add_trace(go.Bar(
        name='Opening Balance',
        x=['Cash Position'],
        y=[opening],
        marker_color='#58A6FF',
        text=[f"₹{opening:,.0f}"],
        textposition='auto',
        textfont=dict(size=11, color='#E6EDF3'),
        width=0.6,
    ))

    if inflows > 0:
        fig.add_trace(go.Bar(
            name='Confirmed Inflows',
            x=['Cash Position'],
            y=[inflows],
            marker_color='#00D4AA',
            text=[f"₹{inflows:,.0f}"],
            textposition='auto',
            textfont=dict(size=11, color='#E6EDF3'),
            width=0.6,
        ))

    if outflows > 0:
        fig.add_trace(go.Bar(
            name='Confirmed Outflows',
            x=['Cash Position'],
            y=[-outflows],
            marker_color='#FF6B6B',
            text=[f"₹{outflows:,.0f}"],
            textposition='auto',
            textfont=dict(size=11, color='#E6EDF3'),
            width=0.6,
        ))

    pending_net = pending_in - pending_out
    if pending_net != 0:
        fig.add_trace(go.Bar(
            name='Pending Net',
            x=['Cash Position'],
            y=[pending_net],
            marker_color='#F0B429',
            text=[f"₹{abs(pending_net):,.0f}"],
            textposition='auto',
            textfont=dict(size=11, color='#E6EDF3'),
            width=0.6,
        ))

    expected_total = float(expected_cash) if expected_cash is not None else opening + inflows - outflows + pending_net
    fig.add_trace(go.Bar(
        name='Expected Cash',
        x=['Cash Position'],
        y=[expected_total],
        marker_color='#8B949E',
        text=[f"₹{expected_total:,.0f}"],
        textposition='auto',
        textfont=dict(size=11, color='#E6EDF3'),
        width=0.6,
    ))

    if bank_cash is not None:
        bank_cash = float(bank_cash)
        fig.add_trace(go.Bar(
            name='Bank Cash',
            x=['Cash Position'],
            y=[bank_cash],
            marker_color='#B3B1AD',
            text=[f"₹{bank_cash:,.0f}"],
            textposition='auto',
            textfont=dict(size=11, color='#E6EDF3'),
            width=0.6,
        ))

    return apply_base_layout(
        fig,
        barmode='relative',
        title='Cash Position Waterfall',
        xaxis_title="",
        yaxis_title="Amount (₹)",
        height=400,
    )


def create_cash_waterfall(
    opening: float,
    confirmed_inflows: float,
    confirmed_outflows: float,
    pending_inflows: float = 0,
    pending_outflows: float = 0,
    bank_cash: float = None,
) -> go.Figure:
    """Backward-compatible wrapper for the cash waterfall chart."""
    expected_cash = opening + confirmed_inflows - confirmed_outflows + pending_inflows - pending_outflows
    return create_cash_waterfall_chart(
        opening=opening,
        inflows=confirmed_inflows,
        outflows=confirmed_outflows,
        pending_in=pending_inflows,
        pending_out=pending_outflows,
        expected_cash=expected_cash,
        bank_cash=bank_cash,
    )


def create_variance_breakdown_chart(
    expected: float,
    bank_cash: float,
    confirmed_inflows: float,
    confirmed_outflows: float,
    pending_inflows: float,
    pending_outflows: float,
    adjustments: float = 0,
) -> go.Figure:
    """Create detailed variance breakdown chart."""
    fig = go.Figure()

    components = [
        ("Expected Cash", float(expected), '#58A6FF'),
        ("Confirmed Inflows", float(confirmed_inflows), '#00D4AA'),
        ("Confirmed Outflows", -float(confirmed_outflows), '#FF6B6B'),
        ("Pending Inflows", float(pending_inflows), '#F0B429'),
        ("Pending Outflows", -float(pending_outflows), '#F0B429'),
        ("Adjustments", float(adjustments), '#58A6FF'),
        ("Bank Cash", float(bank_cash), '#8B949E'),
    ]

    for name, value, color in components:
        fig.add_trace(go.Bar(
            name=name,
            x=['Cash Position'],
            y=[value],
            marker_color=color,
            text=[f"₹{value:,.0f}"],
            textposition='auto',
            textfont=dict(size=11, color='#E6EDF3'),
        ))

    return apply_base_layout(
        fig,
        barmode='relative',
        title="Variance Breakdown",
        xaxis_title="",
        yaxis_title="Amount (₹)",
        height=300,
    )


def create_confusion_matrix_chart(
    tp: int, fp: int, fn: int, tn: int,
) -> go.Figure:
    """Create confusion matrix heatmap."""
    z = [[tp, fp], [fn, tn]]
    x = ["Predicted Match", "Predicted No Match"]
    y = ["Actual Match", "Actual No Match"]

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=x,
        y=y,
        colorscale=[
            [0, "#1E2329"],
            [0.25, "#1A3A2A"],
            [0.5, "#00D4AA"],
            [0.75, "#00B88A"],
            [1, "#00D4AA"],
        ],
        text=[[f"TP: {tp}", f"FP: {fp}"], [f"FN: {fn}", f"TN: {tn}"]],
        texttemplate="%{text}",
        textfont=dict(size=14, color="#E6EDF3"),
        hovertemplate="%{y} / %{x}<br>Count: %{z}<extra></extra>",
        showscale=False,
    ))

    return apply_base_layout(
        fig,
        title="Confusion Matrix",
        height=300,
        xaxis_title="Predicted",
        yaxis_title="Actual",
    )


def create_forecast_chart(
    forecast_entries: list,
    horizons: list = None,
) -> go.Figure:
    """
    Create forecast chart with inflows/outflows over time.
    
    Args:
        forecast_entries: List of dicts with keys: forecast_date, amount, horizon_days, event_name
        horizons: List of horizon days [7, 14, 30]
    """
    if horizons is None:
        horizons = [7, 14, 30]
    
    if not forecast_entries:
        fig = go.Figure()
        return apply_base_layout(fig, title="Forecast (No Data)", height=300)
    
    df = pd.DataFrame(forecast_entries)
    df['forecast_date'] = pd.to_datetime(df['forecast_date'])
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df_in = df[df['amount'] > 0].groupby('forecast_date')['amount'].sum().reset_index()
    df_out = df[df['amount'] < 0].groupby('forecast_date')['amount'].sum().reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_in['forecast_date'],
        y=df_in['amount'],
        name='Inflows',
        marker_color='#00D4AA',
        hovertemplate='%{x|%d %b}: ₹%{y:,.0f}<extra></extra>',
    ))
    
    fig.add_trace(go.Bar(
        x=df_out['forecast_date'],
        y=df_out['amount'],
        name='Outflows',
        marker_color='#FF6B6B',
        hovertemplate='%{x|%d %b}: ₹%{y:,.0f}<extra></extra>',
    ))
    
    return apply_base_layout(
        fig,
        barmode='relative',
        title=f"Cash Flow Forecast ({max(horizons)} Days)",
        xaxis_title="Date",
        yaxis_title="Amount (₹)",
        height=400,
    )


def create_forecast_summary_chart(
    forecast_entries: list,
    horizons: list = None,
) -> go.Figure:
    """Create horizontal bar chart for forecast summary by horizon."""
    if horizons is None:
        horizons = [7, 14, 30]
    
    if not forecast_entries:
        fig = go.Figure()
        return apply_base_layout(fig, title="Forecast Summary", height=200)
    
    df = pd.DataFrame(forecast_entries)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')  # Add this line
    df['horizon_days'] = pd.to_numeric(df['horizon_days'], errors='coerce') 
    
    summary_data = []
    for h in horizons:
        h_data = df[df['horizon_days'] <= h]
        inflows = h_data[h_data['amount'] > 0]['amount'].sum() if not h_data.empty else 0
        outflows = abs(h_data[h_data['amount'] < 0]['amount'].sum()) if not h_data.empty else 0
        net = inflows - outflows
        
        summary_data.append({
            'horizon': f'{h}d',
            'inflows': inflows,
            'outflows': outflows,
            'net': net,
        })
    
    df_sum = pd.DataFrame(summary_data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_sum['horizon'],
        x=df_sum['inflows'],
        name='Inflows',
        orientation='h',
        marker_color='#00D4AA',
        text=[f"₹{v:,.0f}" for v in df_sum['inflows']],
        textposition='auto',
    ))
    
    fig.add_trace(go.Bar(
        y=df_sum['horizon'],
        x=-df_sum['outflows'],
        name='Outflows',
        orientation='h',
        marker_color='#FF6B6B',
        text=[f"₹{v:,.0f}" for v in df_sum['outflows']],
        textposition='auto',
    ))
    
    return apply_base_layout(
        fig,
        barmode='relative',
        title="Forecast Summary by Horizon",
        xaxis_title="Amount (₹)",
        yaxis_title="",
        height=250,
    )


def create_resolution_pie_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
) -> go.Figure:
    """Create pie chart for exception resolution breakdown."""
    fig = go.Figure(data=[go.Pie(
        labels=["Resolved", "Escalated", "Unresolved"],
        values=[resolved, escalated, unresolved],
        hole=0.5,
        marker=dict(colors=["#00D4AA", "#F0B429", "#FF6B6B"]),
        textinfo="label+percent+value",
        textfont=dict(size=14, color="#E6EDF3"),
        hovertemplate="%{label}<br>Count: %{value}<br>%{percent}<extra></extra>",
    )])

    return apply_base_layout(
        fig,
        title="Exception Resolution Breakdown",
        height=350,
        showlegend=True,
    )


def create_resolution_breakdown_chart(
    resolved: int,
    escalated: int,
    unresolved: int,
) -> go.Figure:
    """Create horizontal bar chart for resolution breakdown."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=["Resolved", "Escalated", "Unresolved"],
        x=[resolved, escalated, unresolved],
        orientation='h',
        marker_color=["#00D4AA", "#F0B429", "#FF6B6B"],
        text=[str(resolved), str(escalated), str(unresolved)],
        textposition='auto',
        textfont=dict(size=14, color='#E6EDF3'),
    ))

    return apply_base_layout(
        fig,
        title="Exception Resolution Breakdown",
        xaxis_title="Count",
        height=300,
    )


def create_match_table_figure(
    matches_df: pd.DataFrame,
    height: int = 500,
) -> go.Figure:
    """Create a styled table for matches using Plotly table."""
    if matches_df.empty:
        fig = go.Figure()
        return apply_base_layout(fig, title="No Matches Found", height=200)
    
    # Format data for display
    df = matches_df.copy()
    df['score'] = df['score'].apply(lambda x: f"{x:.2%}")
    df['status'] = df['status'].str.replace('_', ' ').str.title()
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["Match ID", "Txn A", "Txn B", "Score", "Method", "Status"],
            fill_color='#1E2329',
            font=dict(color='#E6EDF3', size=12),
            align='left',
            line_color='#2D333B',
        ),
        cells=dict(
            values=[
                range(1, len(matches_df) + 1),
                [f"#{m['canonical_transaction_id']}" for _, m in df.iterrows()],
                [f"#{m['matched_transaction_id']}" for _, m in df.iterrows()],
                df['score'],
                df['method'],
                df['status'].str.replace('_', ' ').str.title(),
            ],
            fill_color='#1E2329',
            font=dict(color='#E6EDF3', size=11),
            align='left',
            line_color='#2D333B',
            height=30,
        ),
    )])
    
    return apply_base_layout(
        go.Figure(),
        title="Reconciliation Matches",
        height=400,
    ).update_layout(margin=dict(l=10, r=10, t=50, b=10))


def create_exception_table(
    exceptions_df: pd.DataFrame,
    height: int = 400,
) -> go.Figure:
    """Create styled exception table."""
    if exceptions_df.empty:
        fig = go.Figure()
        return apply_base_layout(fig, title="No Exceptions", height=200)
    
    df = exceptions_df.copy()
    df['confidence'] = df['confidence'].apply(lambda x: f"{x:.0%}")
    df['status'] = df['status'].str.replace('_', ' ').str.title()
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["Exc ID", "Txn ID", "Type", "Severity", "Status", "Confidence", "Description"],
            fill_color='#1E2329',
            font=dict(color='#E6EDF3', size=12),
            align='left',
            line_color='#2D333B',
        ),
        cells=dict(
            values=[
                exceptions_df['id'].tolist(),
                exceptions_df['transaction_id'].tolist(),
                exceptions_df['type'].str.replace('_', ' ').str.title().tolist(),
                exceptions_df['severity'].str.title().tolist(),
                exceptions_df['status'].str.replace('_', ' ').str.title().tolist(),
                [f"{c:.0%}" for c in exceptions_df['confidence']],
                [d[:50] + "..." if len(d) > 50 else d for d in exceptions_df['description'].tolist()],
            ],
            fill_color='#1E2329',
            font=dict(color='#E6EDF3', size=11),
            align='left',
            line_color='#2D333B',
            height=30,
        ),
    )])
    
    return apply_base_layout(
        fig,
        title="Exception Queue",
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
    )


def create_cash_waterfall_chart(
    opening: float,
    inflows: float = 0,
    outflows: float = 0,
    pending_in: float = 0,
    pending_out: float = 0,
    expected_cash: float = None,
    bank_cash: float = None,
) -> go.Figure:
    """Create a cash position waterfall chart."""
    fig = go.Figure()

    opening = float(opening or 0)
    inflows = float(inflows or 0)
    outflows = float(outflows or 0)
    pending_in = float(pending_in or 0)
    pending_out = float(pending_out or 0)

    fig.add_trace(go.Bar(
        name='Opening Balance',
        x=['Cash Position'],
        y=[opening],
        marker_color='#58A6FF',
        text=[f"₹{opening:,.0f}"],
        textposition='auto',
        textfont=dict(size=11, color='#E6EDF3'),
        width=0.6,
    ))

    if inflows > 0:
        fig.add_trace(go.Bar(
            name='Confirmed Inflows',
            x=['Cash Position'],
            y=[inflows],
            marker_color='#00D4AA',
            text=[f"₹{inflows:,.0f}"],
            textposition='auto',
            textfont=dict(size=11, color='#E6EDF3'),
            width=0.6,
        ))

    if outflows > 0:
        fig.add_trace(go.Bar(
            name='Confirmed Outflows',
            x=['Cash Position'],
            y=[-outflows],
            marker_color='#FF6B6B',
            text=[f"₹{outflows:,.0f}"],
            textposition='auto',
            textfont=dict(size=11, color='#E6EDF3'),
            width=0.6,
        ))

    pending_net = pending_in - pending_out
    if pending_net != 0:
        fig.add_trace(go.Bar(
            name='Pending Net',
            x=['Cash Position'],
            y=[pending_net],
            marker_color='#F0B429',
            text=[f"₹{abs(pending_net):,.0f}"],
            textposition='auto',
            textfont=dict(size=11, color='#E6EDF3'),
            width=0.6,
        ))

    expected_total = float(expected_cash) if expected_cash is not None else opening + inflows - outflows + pending_net
    fig.add_trace(go.Bar(
        name='Expected Cash',
        x=['Cash Position'],
        y=[expected_total],
        marker_color='#8B949E',
        text=[f"₹{expected_total:,.0f}"],
        textposition='auto',
        textfont=dict(size=11, color='#E6EDF3'),
        width=0.6,
    ))

    if bank_cash is not None:
        fig.add_trace(go.Bar(
            name='Bank Cash',
            x=['Cash Position'],
            y=[float(bank_cash)],
            marker_color='#B3B1AD',
            text=[f"₹{float(bank_cash):,.0f}"],
            textposition='auto',
            textfont=dict(size=11, color='#E6EDF3'),
            width=0.6,
        ))

    return apply_base_layout(
        fig,
        barmode='relative',
        title='Cash Position Waterfall',
        xaxis_title='',
        yaxis_title='Amount (₹)',
        height=400,
    )


def create_kpi_indicator(
    label: str,
    value: str,
    delta: str = None,
    delta_color: str = "normal",
) -> str:
    """Generate HTML for a KPI indicator card."""
    delta_html = ""
    if delta:
        delta_color = "#00D4AA" if not delta.startswith("-") else "#FF6B6B"
        delta_html = f'<div style="color:{("#00D4AA" if not delta.startswith("-") else "#FF6B6B")}; font-size:0.875rem; font-weight:500; margin-top:0.25rem;">{delta}</div>'
    
    return f'''
    <div style="
        background: linear-gradient(135deg, #1E2329 0%, #252A32 100%);
        border: 1px solid #2D333B;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    ">
        <div style="color: #8B949E; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
            {label}
        </div>
        <div style="color: #00D4AA; font-size: 2rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">
            {value}
        </div>
        {f'<div style="color: {"#00D4AA" if not delta.startswith("-") else "#FF6B6B"}; font-size: 0.875rem; font-weight: 500; margin-top: 0.25rem;">{delta}</div>' if delta else ''}
    </div>
    '''

# Export all
__all__ = [
    'apply_base_layout',
    'BASE_LAYOUT',
    'create_waterfall_chart',
    'create_cash_waterfall_chart',
    'create_cash_waterfall',
    'create_forecast_chart',
    'create_forecast_summary_chart',
    'create_variance_breakdown_chart',
    'create_confusion_matrix_chart',
    'create_resolution_pie_chart',
    'create_resolution_breakdown_chart',
    'create_match_table_figure',
    'create_exception_table',
    'create_kpi_indicator',
    'THEME',
    'STATUS_COLORS',
    'SOURCE_COLORS',
]