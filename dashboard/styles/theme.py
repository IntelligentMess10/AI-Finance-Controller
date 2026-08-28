"""
Theme configuration for AI Finance Controller Dashboard.
Bloomberg terminal inspired dark theme.
"""

THEME = {
    # Background colors
    "bg_primary": "#0E1117",      # Main background
    "bg_secondary": "#1E2329",    # Card backgrounds
    "bg_tertiary": "#252A32",     # Elevated surfaces
    
    # Border colors
    "border": "#2D333B",
    "border_light": "#3D4444",
    
    # Text colors
    "text_primary": "#E6EDF3",    # Primary text
    "text_secondary": "#8B949E",  # Muted text
    "text_muted": "#6A737D",      # Very muted text
    
    # Accent colors
    "accent": "#00D4AA",          # Teal - primary actions, positive
    "accent_hover": "#00E6BB",
    "accent_dim": "#008F7A",
    
    "warning": "#F0B429",         # Amber - warnings, pending
    "warning_hover": "#FFC44A",
    
    "danger": "#FF6B6B",          # Red - errors, negative
    "danger_hover": "#FF8A8A",
    
    "info": "#58A6FF",            # Blue - info, inflows
    "info_hover": "#7BB3FF",
    
    # Status colors
    "success": "#00D4AA",
    "warning": "#F0B429",
    "danger": "#FF6B6B",
    "info": "#58A6FF",
    
    # Chart colors
    "chart_colors": [
        "#00D4AA",  # Teal
        "#58A6FF",  # Blue
        "#F0B429",  # Amber
        "#FF6B6B",  # Red
        "#A371F7",  # Purple
        "#FF9F1C",  # Orange
        "#39FF14",  # Neon Green
        "#FF6E6E",  # Light Red
    ],
    
    # Typography
    "font_mono": "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
    "font_sans": "'Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', sans-serif",
    
    # Spacing
    "spacing_xs": "0.25rem",
    "spacing_sm": "0.5rem",
    "spacing_md": "1rem",
    "spacing_lg": "1.5rem",
    "spacing_xl": "2rem",
    
    # Border radius
    "radius_sm": "4px",
    "radius_md": "8px",
    "radius_lg": "12px",
    "radius_xl": "16px",
    
    # Shadows
    "shadow_sm": "0 1px 2px rgba(0,0,0,0.3)",
    "shadow_md": "0 4px 6px rgba(0,0,0,0.3)",
    "shadow_lg": "0 10px 25px rgba(0,0,0,0.4)",
    
    # Transitions
    "transition_fast": "150ms ease",
    "transition_normal": "250ms ease",
    "transition_slow": "350ms ease",
}

# Status color mapping
STATUS_COLORS = {
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

# Direction colors
DIRECTION_COLORS = {
    "inflow": "#00D4AA",
    "outflow": "#FF6B6B",
}

# Source colors
SOURCE_COLORS = {
    "bank": "#58A6FF",
    "ledger": "#00D4AA",
    "processor": "#F0B429",
}

def get_status_color(status: str) -> str:
    """Get color for a status string."""
    return STATUS_COLORS.get(status.lower(), "#8B949E")

def get_source_color(source: str) -> str:
    """Get color for a source."""
    return SOURCE_COLORS.get(source.lower(), "#8B949E")

def get_direction_color(direction: str) -> str:
    """Get color for transaction direction."""
    return DIRECTION_COLORS.get(direction.lower(), "#8B949E")


def generate_css() -> str:
    """Generate CSS string for Streamlit injection."""
    return f"""
<style>
    /* Main background */
    .stApp {{
        background-color: {THEME["bg_primary"]};
    }}
    
    .main {{
        background-color: {THEME["bg_primary"]};
    }}
    
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}
    
    /* Metric Cards */
    .metric-card {{
        background: linear-gradient(135deg, {THEME["bg_secondary"]} 0%, {THEME["bg_tertiary"]} 100%);
        border: 1px solid {THEME["border"]};
        border-radius: {THEME["radius_md"]};
        padding: {THEME["spacing_lg"]};
        box-shadow: {THEME["shadow_md"]};
        transition: all {THEME["transition_normal"]};
    }}
    
    .metric-card:hover {{
        border-color: {THEME["border_light"]};
        box-shadow: {THEME["shadow_lg"]};
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {THEME["accent"]};
        font-family: {THEME["font_mono"]};
    }}
    
    .metric-label {{
        font-size: 0.875rem;
        color: {THEME["text_muted"]};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    /* Status Badges */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: capitalize;
    }}
    
    .status-matched {{ background: #1A3A2A; color: #00D4AA; }}
    .status-probable_match {{ background: #3A2E1A; color: #F0B429; }}
    .status-exception {{ background: #3A1A1A; color: #FF6B6B; }}
    .status-unresolved {{ background: #2D2D3A; color: #8B949E; }}
    .status-escalated {{ background: #3A2E1A; color: #F0B429; }}
    .status-open {{ background: #1A2A3A; color: #58A6FF; }}
    .status-investigating {{ background: #3A2E1A; color: #F0B429; }}
    .status-resolved {{ background: #1A3A2A; color: #00D4AA; }}
    .status-escalated {{ background: #3A2E1A; color: #F0B429; }}
    .status-unresolved {{ background: #2D2D3A; color: #8B949E; }}
    
    /* Evidence Panel */
    .evidence-panel {{
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 1rem;
    }}
    
    /* Section Header */
    .section-header {{
        color: #E6EDF3;
        font-weight: 600;
        font-size: 1.125rem;
        margin-bottom: 1rem;
    }}
    
    /* Buttons */
    .stButton > button {{
        background: {THEME["bg_secondary"]};
        border: 1px solid {THEME["border"]};
        color: {THEME["text_primary"]};
        border-radius: {THEME["radius_md"]};
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all {THEME["transition_fast"]};
    }}
    
    .stButton > button:hover {{
        background: {THEME["bg_tertiary"]};
        border-color: {THEME["accent"]};
    }}
    
    .stButton > button[kind="primary"] {{
        background: {THEME["accent"]};
        border-color: {THEME["accent"]};
        color: {THEME["bg_primary"]};
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background: {THEME["accent_hover"]};
        border-color: {THEME["accent_hover"]};
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: {THEME["bg_secondary"]};
        border-radius: 6px 6px 0 0;
        padding: 0.5rem 1rem;
        color: {THEME["text_secondary"]};
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {THEME["bg_tertiary"]};
        color: {THEME["accent"]};
        border-bottom: 2px solid {THEME["accent"]};
    }}
    
    /* Tables */
    .stDataFrame {{
        background: {THEME["bg_secondary"]};
    }}
    
    .stDataFrame th {{
        background: {THEME["bg_tertiary"]} !important;
        color: {THEME["text_primary"]} !important;
    }}
    
    .stDataFrame td {{
        background: {THEME["bg_secondary"]} !important;
        color: {THEME["text_primary"]} !important;
    }}
    
    /* Selectbox */
    .stSelectbox > div > div {{
        background: {THEME["bg_secondary"]};
        border-color: {THEME["border"]};
    }}
    
    /* Slider */
    .stSlider [data-baseweb="slider"] {{
        color: {THEME["accent"]};
    }}
    
    /* Metric Cards */
    [data-testid="metric-container"] {{
        background: linear-gradient(135deg, {THEME["bg_secondary"]} 0%, {THEME["bg_tertiary"]} 100%);
        border: 1px solid {THEME["border"]};
        border-radius: {THEME["radius_md"]};
        padding: {THEME["spacing_lg"]};
        box-shadow: {THEME["shadow_md"]};
    }}
    
    [data-testid="metric-container"] > div:first-child {{
        color: {THEME["text_muted"]} !important;
        font-size: 0.875rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    [data-testid="metric-container"] > div:last-child {{
        color: {THEME["accent"]} !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        font-family: {THEME["font_mono"]} !important;
    }}
    
    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {THEME["bg_primary"]};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {THEME["border"]};
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {THEME["border_light"]};
    }}
    
    /* Plotly Charts */
    .js-plotly-plot {{
        background: {THEME["bg_primary"]} !important;
    }}
    
    .plotly-graph-div {{
        background: {THEME["bg_primary"]} !important;
    }}
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div {{
        background: {THEME["bg_secondary"]} !important;
        border-color: {THEME["border"]} !important;
        color: {THEME["text_primary"]} !important;
    }}
    
    .stSelectbox [data-baseweb="select"] > div {{
        background: {THEME["bg_secondary"]} !important;
    }}
    
    /* Metric Cards Custom */
    .kpi-card {{
        background: linear-gradient(135deg, {THEME["bg_secondary"]} 0%, {THEME["bg_tertiary"]} 100%);
        border: 1px solid {THEME["border"]};
        border-radius: {THEME["radius_md"]};
        padding: {THEME["spacing_lg"]};
        box-shadow: {THEME["shadow_md"]};
        transition: all {THEME["transition_normal"]};
    }}
    
    .kpi-card:hover {{
        border-color: {THEME["border_light"]};
        box-shadow: {THEME["shadow_lg"]};
        transform: translateY(-2px);
    }}
    
    .kpi-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {THEME["accent"]};
        font-family: {THEME["font_mono"]};
    }}
    
    .kpi-label {{
        font-size: 0.875rem;
        color: {THEME["text_muted"]};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }}
</style>
"""

# For backward compatibility
THEME_COLORS = THEME