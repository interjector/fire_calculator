import streamlit as st

# ── Palettes ──────────────────────────────────────────────────────────────────

DARK = dict(
    bg="#060b18", surface="#0c1525", surface2="#101d30",
    border="#182035", border2="#1c2e48",
    t1="#dce8f5", t2="#7a96b4", t3="#3d5068",
    accent="#10b981", accent_dim="rgba(16,185,129,0.07)",
    fire_lean="#3b82f6", fire_barista="#06b6d4",
    fire_regular="#f59e0b", fire_fat="#8b5cf6",
    red="#f87171", amber="#f59e0b",
    paper="#0c1525", plot="#08101e",
    grid="#13203a", tick="#3d5068",
    ct="#7a96b4", hover_bg="#101d30",
    hover_border="#1c2e48", hover_text="#dce8f5",
    leg_bg="rgba(12,21,37,0.94)", leg_border="#182035",
    portfolio_rgb="16,185,129",
    invested_rgb="59,130,246",
    gains_rgb="16,185,129",
    band_rgb="16,185,129",
    on_track_bg="rgba(16,185,129,0.1)", on_track_fg="#10b981", on_track_bd="rgba(16,185,129,0.22)",
    off_track_bg="rgba(239,68,68,0.1)", off_track_fg="#f87171", off_track_bd="rgba(239,68,68,0.22)",
    neutral_bg="rgba(59,130,246,0.1)", neutral_fg="#60a5fa", neutral_bd="rgba(59,130,246,0.22)",
    bar_fill="linear-gradient(90deg, #10b981, #34d399)",
    bar_track="#101d30",
)

LIGHT = dict(
    bg="#f0f4f8", surface="#ffffff", surface2="#f8fafc",
    border="#e2e8f0", border2="#cbd5e1",
    t1="#0f172a", t2="#475569", t3="#94a3b8",
    accent="#059669", accent_dim="rgba(5,150,105,0.06)",
    fire_lean="#2563eb", fire_barista="#0891b2",
    fire_regular="#d97706", fire_fat="#7c3aed",
    red="#dc2626", amber="#d97706",
    paper="#ffffff", plot="#f8fafc",
    grid="#e9eef5", tick="#94a3b8",
    ct="#475569", hover_bg="#ffffff",
    hover_border="#e2e8f0", hover_text="#0f172a",
    leg_bg="rgba(255,255,255,0.97)", leg_border="#e2e8f0",
    portfolio_rgb="5,150,105",
    invested_rgb="37,99,235",
    gains_rgb="5,150,105",
    band_rgb="5,150,105",
    on_track_bg="rgba(5,150,105,0.08)", on_track_fg="#059669", on_track_bd="rgba(5,150,105,0.2)",
    off_track_bg="rgba(220,38,38,0.08)", off_track_fg="#dc2626", off_track_bd="rgba(220,38,38,0.2)",
    neutral_bg="rgba(37,99,235,0.08)", neutral_fg="#2563eb", neutral_bd="rgba(37,99,235,0.2)",
    bar_fill="linear-gradient(90deg, #059669, #34d399)",
    bar_track="#e9eef5",
)


def get_palette():
    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"
    is_dark = st.session_state["theme"] == "dark"
    return (DARK if is_dark else LIGHT), is_dark


def inject_base_css(p, dark, hide_sidebar=False):
    scrollbar = "rgba(255,255,255,0.08)" if dark else "rgba(0,0,0,0.12)"
    sidebar_css = """
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
""" if hide_sidebar else ""
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}
.stApp {{ background-color: {p['bg']} !important; }}
[data-testid="stSidebarNav"] {{ display: none !important; }}
{sidebar_css}
/* ── Sidebar ─────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background-color: {p['surface']} !important;
    border-right: 1px solid {p['border']} !important;
}}
[data-testid="stSidebar"] > div:first-child {{ padding-top: 1rem !important; }}
.section-label {{
    color: {p['t3']};
    font-size: 0.59rem; font-weight: 700; letter-spacing: 0.13em; text-transform: uppercase;
    padding: 1rem 0 0.4rem; display: block;
    border-bottom: 1px solid {p['border']}; margin-bottom: 0.55rem;
}}
.theme-toggle-btn button {{
    background: {p['surface2']} !important; border: 1px solid {p['border2']} !important;
    color: {p['t2']} !important; border-radius: 8px !important;
    font-size: 0.75rem !important; font-weight: 600 !important;
    width: 100% !important; padding: 0.45rem 0 !important; transition: all 0.15s !important;
}}
.theme-toggle-btn button:hover {{
    border-color: {p['accent']} !important; color: {p['accent']} !important;
}}
/* ── Inputs ──────────────────────────────────────────── */
[data-testid="stSidebar"] .stNumberInput > div > div > input,
[data-testid="stSidebar"] .stTextInput > div > div > input {{
    background-color: {p['surface2']} !important; border: 1px solid {p['border2']} !important;
    color: {p['t1']} !important; border-radius: 6px !important; font-size: 0.83rem !important;
}}
[data-testid="stSidebar"] .stNumberInput > div > div > input:focus,
[data-testid="stSidebar"] .stTextInput > div > div > input:focus {{
    border-color: {p['accent']} !important; box-shadow: 0 0 0 2px {p['accent_dim']} !important;
    outline: none !important;
}}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stCheckbox label,
[data-testid="stSidebar"] .stRadio label {{
    color: {p['t2']} !important; font-size: 0.77rem !important; font-weight: 500 !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background-color: {p['surface2']} !important; border-color: {p['border2']} !important;
    color: {p['t1']} !important; border-radius: 6px !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] span {{ color: {p['t1']} !important; }}
[data-testid="stSidebar"] .streamlit-expanderHeader {{
    background-color: {p['surface2']} !important; border: 1px solid {p['border']} !important;
    border-radius: 7px !important; color: {p['t2']} !important;
    font-size: 0.77rem !important; font-weight: 600 !important;
}}
[data-testid="stSidebar"] .streamlit-expanderContent {{
    background-color: {p['surface']} !important; border: 1px solid {p['border']} !important;
    border-top: none !important; border-radius: 0 0 7px 7px !important;
}}
/* ── Main area ───────────────────────────────────────── */
.main .block-container {{
    padding-top: 1.5rem !important; padding-left: 2rem !important;
    padding-right: 2rem !important; max-width: 1420px !important;
}}
/* ── Metrics ─────────────────────────────────────────── */
[data-testid="stMetric"] {{
    background: {p['surface']} !important; border: 1px solid {p['border']} !important;
    border-radius: 12px !important; padding: 1.1rem 1.3rem !important;
}}
[data-testid="stMetricLabel"] > div {{
    color: {p['t3']} !important; font-size: 0.63rem !important; font-weight: 700 !important;
    letter-spacing: 0.11em !important; text-transform: uppercase !important;
}}
[data-testid="stMetricValue"] {{
    color: {p['t1']} !important; font-size: 1.7rem !important;
    font-weight: 700 !important; letter-spacing: -0.03em !important;
}}
[data-testid="stMetricDelta"] {{ font-size: 0.73rem !important; }}
/* ── Tabs ────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: transparent !important; border-bottom: 1px solid {p['border']} !important; gap: 0 !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important; color: {p['t3']} !important;
    font-size: 0.79rem !important; font-weight: 500 !important; padding: 0.55rem 0.9rem !important;
    border: none !important; border-bottom: 2px solid transparent !important; border-radius: 0 !important;
}}
.stTabs [aria-selected="true"] {{
    color: {p['t1']} !important; border-bottom-color: {p['accent']} !important; background: transparent !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 1.2rem !important; }}
/* ── Buttons ─────────────────────────────────────────── */
.stButton > button {{
    border-radius: 7px !important; font-size: 0.79rem !important;
    font-weight: 600 !important; letter-spacing: 0.02em !important; transition: all 0.15s ease !important;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {p['accent']}, {'#059669' if dark else '#047857'}) !important;
    border: none !important; color: #fff !important; box-shadow: 0 3px 10px {p['accent_dim']} !important;
}}
.stButton > button[kind="primary"]:hover {{
    box-shadow: 0 5px 16px {p['accent_dim']} !important; transform: translateY(-1px) !important;
}}
.stButton > button[kind="secondary"] {{
    background: transparent !important; border: 1px solid {p['border2']} !important; color: {p['t2']} !important;
}}
.stButton > button[kind="secondary"]:hover {{
    border-color: {p['accent']} !important; color: {p['accent']} !important;
}}
/* ── DataFrames ──────────────────────────────────────── */
[data-testid="stDataFrame"] {{
    border: 1px solid {p['border']} !important; border-radius: 10px !important; overflow: hidden !important;
}}
/* ── Alerts / Scrollbar / Global ─────────────────────── */
.stAlert {{ border-radius: 9px !important; }}
.stRadio label {{ color: {p['t2']} !important; font-size: 0.79rem !important; }}
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {scrollbar}; border-radius: 3px; }}
h1, h2, h3, h4 {{ color: {p['t1']} !important; }}
p {{ color: {p['t2']} !important; }}
hr {{ border-color: {p['border']} !important; margin: 0.5rem 0 !important; }}
/* ── Calculator-specific components ─────────────────── */
.app-title {{ font-size: 1.25rem; font-weight: 800; color: {p['t1']}; letter-spacing: -0.04em; }}
.app-tagline {{ font-size: 0.73rem; color: {p['t3']}; margin-left: 0.55rem; }}
.status-pill {{
    display: inline-flex; align-items: center; gap: 0.3rem;
    padding: 0.28rem 0.75rem; border-radius: 100px;
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.02em;
}}
.pill-green  {{ background:{p['on_track_bg']};  color:{p['on_track_fg']};  border:1px solid {p['on_track_bd']}; }}
.pill-red    {{ background:{p['off_track_bg']}; color:{p['off_track_fg']}; border:1px solid {p['off_track_bd']}; }}
.pill-blue   {{ background:{p['neutral_bg']};   color:{p['neutral_fg']};   border:1px solid {p['neutral_bd']}; }}
.section-title {{
    display: block; font-size: 0.59rem; font-weight: 700; color: {p['t3']};
    letter-spacing: 0.13em; text-transform: uppercase;
    padding-bottom: 0.55rem; border-bottom: 1px solid {p['border']}; margin: 1.6rem 0 0.9rem;
}}
.progress-wrap {{
    background: {p['surface']}; border: 1px solid {p['border']}; border-radius: 11px;
    padding: 1rem 1.3rem; margin: 0.9rem 0;
}}
.progress-track {{ background: {p['bar_track']}; border-radius: 100px; height: 7px; overflow: hidden; margin: 0.45rem 0; }}
.progress-fill {{ height: 100%; border-radius: 100px; background: {p['bar_fill']}; }}
.target-card {{
    background: {p['surface']}; border: 1px solid {p['border']}; border-radius: 11px; padding: 0.95rem 1.1rem;
}}
.target-card.selected {{ border-color: {p['accent']}; }}
.tc-label {{ font-size: 0.59rem; font-weight: 700; color: {p['t3']}; letter-spacing: 0.11em; text-transform: uppercase; }}
.tc-amount {{ font-size: 1.18rem; font-weight: 700; color: {p['t1']}; letter-spacing: -0.025em; margin: 0.22rem 0 0.08rem; }}
.tc-sub {{ font-size: 0.69rem; color: {p['t3']}; }}
.tc-bar-track {{ background: {p['bar_track']}; border-radius: 100px; height: 3px; margin: 0.55rem 0 0.28rem; }}
.scenario-hint {{ font-size: 0.77rem; color: {p['t2']}; margin-bottom: 0.9rem; line-height: 1.55; }}
.chart-label {{
    font-size: 0.65rem; font-weight: 700; color: {p['t3']};
    letter-spacing: 0.09em; text-transform: uppercase; margin-bottom: 0.3rem; padding-top: 0.2rem;
}}
</style>""", unsafe_allow_html=True)
