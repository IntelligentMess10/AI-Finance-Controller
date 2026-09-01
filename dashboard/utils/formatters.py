from decimal import Decimal
from typing import Optional, Union
from datetime import date, datetime
import pandas as pd
import streamlit as st

from dashboard.styles.theme import get_status_color, get_source_color, get_direction_color, STATUS_COLORS


def format_inr(amount: Union[int, float, Decimal, str]) -> str:
    """
    Format amount as Indian Rupees with appropriate units.
    
    Args:
        amount: Amount to format (int, float, Decimal, or string)
        
    Returns:
        Formatted string like "₹1.23 Cr", "₹45.67 L", "₹1,234.56"
    """
    if amount is None:
        return "₹0.00"
    
    try:
        if isinstance(amount, str):
            amount = Decimal(str(amount).replace(",", "").replace("₹", "").strip())
        elif isinstance(amount, (int, float)):
            amount = Decimal(str(amount))
        elif not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
    except (ValueError, TypeError, ArithmeticError):
        return "₹0.00"
    
    abs_amount = abs(amount)
    
    if abs_amount >= 10_000_000:  # 1 Crore
        return f"₹{amount / 10_000_000:.2f} Cr"
    elif abs_amount >= 100_000:  # 1 Lakh
        return f"₹{amount / 100_000:.2f} L"
    else:
        return f"₹{amount:,.2f}"


def format_inr_compact(amount: Union[int, float, Decimal, str]) -> str:
    """
    Compact INR formatting for tight spaces.
    """
    if amount is None:
        return "₹0"
    
    try:
        if isinstance(amount, str):
            amount = Decimal(str(amount).replace(",", "").replace("₹", "").strip())
        elif isinstance(amount, (int, float)):
            amount = Decimal(str(amount))
        elif not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
    except (ValueError, TypeError, ArithmeticError):
        return "₹0"
    
    abs_amount = abs(amount)
    
    if abs_amount >= 10_000_000:  # 1 Crore
        return f"₹{amount / 10_000_000:.1f}Cr"
    elif abs_amount >= 100_000:  # 1 Lakh
        return f"₹{amount / 100_000:.1f}L"
    elif abs_amount >= 1_000:
        return f"₹{amount / 1_000:.1f}K"
    else:
        return f"₹{amount:,.0f}"


def format_pct(value: Union[float, Decimal, str], decimals: int = 1) -> str:
    """Format a value as percentage."""
    if value is None:
        return "0%"
    try:
        if isinstance(value, str):
            value = float(value.replace("%", ""))
        elif isinstance(value, Decimal):
            value = float(value)
        return f"{float(value):.{decimals}f}%"
    except (ValueError, TypeError):
        return "0%"


def format_pct_decimal(value: Union[float, Decimal, str], decimals: int = 2) -> str:
    """Format decimal as percentage (0.95 -> 95.00%)."""
    if value is None:
        return "0%"
    try:
        if isinstance(value, str):
            value = float(value.replace("%", ""))
        elif isinstance(value, Decimal):
            value = float(value)
        return f"{value * 100:.{decimals}f}%"
    except (ValueError, TypeError):
        return "0%"


def format_date(dt: Union[date, datetime, str]) -> str:
    """Format date as DD MMM YYYY."""
    if dt is None:
        return "—"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except:
            try:
                dt = datetime.strptime(dt, "%Y-%m-%d")
            except:
                return str(dt)
    if isinstance(dt, datetime):
        dt = dt.date()
    if isinstance(dt, date):
        return dt.strftime("%d %b %Y")
    return str(dt)


def format_datetime(dt: Union[datetime, str]) -> str:
    """Format datetime as DD MMM YYYY HH:MM."""
    if dt is None:
        return "—"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except:
            return str(dt)
    if isinstance(dt, datetime):
        return dt.strftime("%d %b %Y %H:%M")
    return str(dt)


def format_number(value: Union[int, float, Decimal, str], decimals: int = 0) -> str:
    """Format number with commas."""
    if value is None:
        return "0"
    try:
        if isinstance(value, str):
            value = float(value.replace(",", ""))
        elif isinstance(value, Decimal):
            value = float(value)
        return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        return "0"


def status_badge(status: str) -> str:
    """Generate HTML for a status badge."""
    from dashboard.styles.theme import get_status_color, STATUS_COLORS
    
    status_lower = status.lower().replace(" ", "_")
    color = STATUS_COLORS.get(status.lower(), "#8B949E")
    
    # Capitalize and format label
    label = status.replace("_", " ").title()
    
    return f'''
    <span style="
        background: {STATUS_COLORS.get(status.lower(), "#8B949E")};
        color: #E6EDF3;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: capitalize;
        display: inline-block;
    ">
        {status.replace("_", " ").title()}
    </span>'''


def status_badge_component(status: str) -> str:
    """Streamlit-compatible status badge using st.markdown."""
    from dashboard.styles.theme import get_status_color
    
    color = get_status_color(status)
    label = status.replace("_", " ").title()
    
    return f'''
    <span style="
        background: {STATUS_COLORS.get(status.lower(), "#8B949E")};
        color: #E6EDF3;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: capitalize;
        display: inline-block;
    ">
        {status.replace("_", " ").title()}
    </span>'''


def source_badge(source: str) -> str:
    """Generate source badge HTML."""
    from dashboard.styles.theme import get_source_color
    
    color = get_source_color(source)
    label = source.upper()
    
    return f'''
    <span style="
        background: {get_source_color(source)};
        color: #E6EDF3;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
    ">
        {source.upper()}
    </span>'''


def format_pct(value: Union[float, Decimal, str], decimals: int = 1) -> str:
    """Format as percentage."""
    if value is None:
        return "0%"
    try:
        if isinstance(value, str):
            value = float(value.replace("%", ""))
        elif isinstance(value, Decimal):
            value = float(value)
        return f"{float(value):.{decimals}f}%"
    except (ValueError, TypeError):
        return "0%"


def format_pct_decimal(value: Union[float, Decimal, str], decimals: int = 2) -> str:
    """Format decimal as percentage (0.95 -> 95.00%)."""
    if value is None:
        return "0%"
    try:
        if isinstance(value, str):
            value = float(value.replace("%", ""))
        elif isinstance(value, Decimal):
            value = float(value)
        return f"{value * 100:.{decimals}f}%"
    except (ValueError, TypeError):
        return "0%"


def truncate(text: str, length: int = 50, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix


def status_badge_html(status: str) -> str:
    """Generate HTML for status badge."""
    from dashboard.styles.theme import STATUS_COLORS
    
    color = STATUS_COLORS.get(status.lower(), "#8B949E")
    label = status.replace("_", " ").title()
    
    return f'''
    <span style="
        background: {STATUS_COLORS.get(status.lower(), "#8B949E")};
        color: #E6EDF3;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: capitalize;
        display: inline-block;
    ">
        {status.replace("_", " ").title()}
    </span>'''


def format_delta(current: float, previous: float, is_currency: bool = False) -> str:
    """Format delta between two values."""
    if previous == 0:
        return "—"
    
    delta = current - previous
    pct_change = (delta / abs(previous)) * 100 if previous != 0 else 0
    
    if is_currency:
        from dashboard.utils.formatters import format_inr
        delta_str = format_inr(delta)
        pct_str = f"({pct_change:+.1f}%)"
        return f"{format_inr(delta)} {pct_str}"
    else:
        delta_str = f"{delta:+,.2f}"
        pct_str = f"({pct_change:+.1f}%)"
        return f"{delta_str} {pct_str}"


def render_status_badge(status: str) -> str:
    """Render status badge using Streamlit markdown."""
    status_lower = status.lower().replace(" ", "_")
    color_map = {
        "matched": "#00D4AA",
        "probable_match": "#F0B429",
        "exception": "#FF6B6B",
        "unresolved": "#8B949E",
        "escalated": "#F0B429",
        "open": "#58A6FF",
        "investigating": "#F0B429",
        "resolved": "#00D4AA",
        "escalated": "#F0B429",
        "unresolved": "#8B949E",
    }
    color = None
    for key, color_val in {
        "matched": "#00D4AA",
        "probable_match": "#F0B429",
        "exception": "#FF6B6B",
        "unresolved": "#8B949E",
        "escalated": "#F0B429",
        "open": "#58A6FF",
        "investigating": "#F0B429",
        "resolved": "#00D4AA",
        "escalated": "#F0B429",
        "unresolved": "#8B949E",
    }.items():
        if key in status.lower():
            color = color_val
            break
    else:
        color = "#8B949E"
    
    label = status.replace("_", " ").title()
    return f'''
    <span style="
        background: {color};
        color: #E6EDF3;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: capitalize;
        display: inline-block;
    ">
        {status.replace("_", " ").title()}
    </span>'''


def render_status_badge(status: str) -> str:
    """Streamlit markdown compatible status badge."""
    from dashboard.styles.theme import get_status_color
    
    color = get_status_color(status)
    label = status.replace("_", " ").title()
    
    return f'<span style="background:{color}; color:#E6EDF3; padding:0.25rem 0.75rem; border-radius:9999px; font-size:0.75rem; font-weight:600; text-transform:capitalize; display:inline-block;">{status.replace("_", " ").title()}</span>'


def render_kpi_card(label: str, value: str, delta: str = None, delta_color: str = "normal") -> str:
    """Render a KPI card HTML."""
    delta_html = ""
    if delta:
        delta_color = "#00D4AA" if delta_color == "normal" else "#FF6B6B" if delta_color == "inverse" else "#F0B429"
        delta_html = f'<div style="color:{delta_color}; font-size:0.875rem; font-weight:500; margin-top:0.25rem;">{delta}</div>'
    
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
        {f'<div style="color:{("#00D4AA" if not delta.startswith("-") else "#FF6B6B")}; font-size:0.875rem; font-weight:500; margin-top:0.25rem;">{delta}</div>' if delta else ''}
    </div>'''


def render_kpi_card(label: str, value: str, delta: str = None, delta_type: str = "normal") -> None:
    """Render KPI card using Streamlit."""
    delta_color = "normal"
    if delta and delta.startswith("-"):
        delta_type = "inverse"
    elif delta and delta.startswith("+"):
        delta_type = "normal"
    else:
        delta_type = "normal"
    
    st.markdown(render_kpi_card(label, value, delta, delta_type), unsafe_allow_html=True)


if __name__ == "__main__":
    # Quick tests
    print(format_inr(34028.11))
    print(format_inr(70629.43))
    print(format_inr(383151.38))
    print(format_inr(10000000))
    print(format_inr(5000000))
    print(format_inr(50000))
    print(format_inr(-50000))
    print(format_pct(0.95))
    print(format_pct_decimal(0.95))
    print(format_date("2026-07-14"))
    print(format_date("2026-07-14T10:30:00"))
    print(status_badge("matched"))
    print(status_badge("probable_match"))
    print(status_badge("exception"))
    print(format_delta(100, 100))
    print(format_delta(110, 100))
    print(format_delta(90, 100, is_currency=True))