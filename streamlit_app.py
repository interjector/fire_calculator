import streamlit as st
from components.theme import get_palette, inject_base_css
from components.nav import render_nav

st.set_page_config(
    page_title="Ember — Financial Independence Calculator",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

p, is_dark = get_palette()
inject_base_css(p, is_dark, hide_sidebar=True)

# ── Landing-page specific CSS ─────────────────────────────────────────────────

st.markdown(f"""
<style>
/* ── Hero ──────────────────────────────────────────────── */
.hero-section {{
    text-align: center;
    padding: 4.5rem 2rem 3.5rem;
    background: radial-gradient(ellipse 120% 60% at 50% 0%, rgba(16,185,129,0.07) 0%, transparent 65%);
    border-radius: 20px;
    margin-bottom: 0.5rem;
}}
.hero-eyebrow {{
    display: inline-block;
    background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.22);
    color: {p['accent']}; font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.14em; text-transform: uppercase;
    padding: 0.3rem 1rem; border-radius: 100px; margin-bottom: 1.6rem;
}}
.hero-title {{
    font-size: 3.6rem; font-weight: 800; letter-spacing: -0.05em; line-height: 1.08;
    color: {p['t1']}; margin: 0 0 1.2rem;
}}
.hero-title .ht-accent {{ color: {p['accent']}; }}
.hero-sub {{
    font-size: 1.2rem; color: {p['t2']};
    max-width: 580px; margin: 0 auto 2.8rem; line-height: 1.7;
    text-align: center !important;
}}

/* ── CTA buttons ───────────────────────────────────────── */
.cta-primary .stButton > button,
.cta-primary [data-testid="baseButton-primary"],
.cta-primary [data-testid="stBaseButton-primary"] {{
    background: {p['accent']} !important;
    color: #ffffff !important; border: none !important;
    padding: 0.8rem 2.4rem !important; font-size: 1rem !important;
    font-weight: 700 !important; border-radius: 11px !important;
    box-shadow: 0 4px 20px rgba(16,185,129,0.28) !important;
    width: 100% !important;
}}
.cta-primary .stButton > button:hover {{
    background: {'#0ea572' if is_dark else '#047857'} !important;
    box-shadow: 0 6px 28px rgba(16,185,129,0.4) !important;
    transform: translateY(-2px) !important; color: #ffffff !important;
}}
.cta-secondary .stButton > button {{
    background: transparent !important;
    border: 1px solid {p['border2']} !important; color: {p['t1']} !important;
    padding: 0.8rem 2.4rem !important; font-size: 1rem !important;
    font-weight: 600 !important; border-radius: 11px !important; width: 100% !important;
}}
.cta-secondary .stButton > button:hover {{
    border-color: {p['accent']} !important; color: {p['accent']} !important;
}}

/* ── How it works ──────────────────────────────────────── */
.hiw-section {{
    background: {p['surface']}; border: 1px solid {p['border']};
    border-radius: 18px; padding: 2.8rem 3rem; margin: 2.5rem 0;
}}
.hiw-section h2 {{
    font-size: 1.9rem; font-weight: 800; color: {p['t1']};
    letter-spacing: -0.04em; margin: 0 0 0.5rem;
}}
.hiw-section .hiw-sub {{
    font-size: 1rem; color: {p['t2']}; line-height: 1.65;
    margin: 0 0 2rem; max-width: 520px;
}}
.hiw-step {{
    display: flex; gap: 1.1rem; align-items: flex-start; margin-bottom: 1.5rem;
}}
.hiw-step:last-child {{ margin-bottom: 0; }}
.hiw-num {{
    width: 36px; height: 36px; border-radius: 10px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; font-weight: 800; color: {p['accent']};
    background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2);
}}
.hiw-title {{ font-size: 0.97rem; font-weight: 700; color: {p['t1']}; margin-bottom: 0.2rem; }}
.hiw-desc {{ font-size: 0.92rem; color: {p['t2']}; line-height: 1.6; }}

.fi-formula {{
    background: {p['surface2']}; border: 1px solid {p['border2']};
    border-radius: 12px; padding: 1.3rem 1.6rem; margin: 1rem 0 1.5rem; text-align: center;
}}
.fi-formula .ff-label {{
    font-size: 0.67rem; font-weight: 700; color: {p['t3']};
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.5rem; display: block;
}}
.fi-formula .ff-eq {{ font-size: 1.1rem; font-weight: 700; color: {p['t1']}; }}
.fi-formula .ff-eq .ffe-accent {{ color: {p['accent']}; }}

.example-table {{ width:100%; font-size:0.9rem; margin-top:0.8rem; }}
.example-table td {{ padding: 0.28rem 0.4rem; }}
.example-table td:first-child {{ color: {p['t3']}; }}
.example-table td:last-child {{ color: {p['accent']}; font-weight: 700; text-align: right; }}

/* ── FIRE type cards ───────────────────────────────────── */
.fire-card {{
    background: {p['surface']}; border: 1px solid {p['border']};
    border-radius: 14px; padding: 1.4rem 1.5rem; height: 100%;
    transition: border-color 0.2s, transform 0.2s;
}}
.fire-card:hover {{ border-color: {p['border2']}; transform: translateY(-2px); }}
.fc-icon {{ font-size: 1.6rem; margin-bottom: 0.7rem; display: block; }}
.fc-name {{ font-size: 1rem; font-weight: 700; color: {p['t1']}; margin-bottom: 0.25rem; }}
.fc-range {{ font-size: 0.82rem; font-weight: 600; margin-bottom: 0.6rem; display: block; }}
.fc-desc {{ font-size: 0.9rem; color: {p['t3']}; line-height: 1.6; }}

/* ── Section header ────────────────────────────────────── */
.section-hdr {{ text-align: center; margin-bottom: 2rem; }}
.section-hdr .sh-eyebrow {{
    font-size: 0.7rem; font-weight: 700; color: {p['accent']};
    letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 0.5rem; display: block;
}}
.section-hdr h2 {{
    font-size: 2rem; font-weight: 800; color: {p['t1']}; letter-spacing: -0.04em; margin: 0 0 0.6rem;
}}
.section-hdr p {{ font-size: 1rem; color: {p['t2']}; max-width: 520px; margin: 0 auto; line-height: 1.65; }}

/* ── Tool cards ────────────────────────────────────────── */
.tool-card {{
    background: {p['surface']}; border: 1px solid {p['border']};
    border-radius: 16px; padding: 1.9rem 1.9rem 1.6rem;
    transition: border-color 0.2s, box-shadow 0.2s;
}}
.tool-card:hover {{ border-color: {p['accent']}; box-shadow: 0 6px 30px rgba(16,185,129,0.07); }}
.tc-icon {{ font-size: 2rem; margin-bottom: 0.85rem; display: block; }}
.tc-name {{ font-size: 1.2rem; font-weight: 700; color: {p['t1']}; margin-bottom: 0.45rem; }}
.tc-desc {{ font-size: 0.95rem; color: {p['t2']}; line-height: 1.65; margin-bottom: 1.3rem; }}
.tool-card .stButton > button {{
    background: transparent !important; border: 1px solid {p['border2']} !important;
    color: {p['t1']} !important; font-size: 0.85rem !important; font-weight: 600 !important;
    border-radius: 7px !important; padding: 0.45rem 1rem !important; width: 100% !important;
}}
.tool-card .stButton > button:hover {{
    border-color: {p['accent']} !important; color: {p['accent']} !important;
}}

/* ── CTA banner ────────────────────────────────────────── */
.cta-banner {{
    background: linear-gradient(135deg, {p['surface']}, {p['surface2']});
    border: 1px solid {p['border']}; border-radius: 18px;
    padding: 3.2rem 2rem; text-align: center; margin: 2.5rem 0;
}}
.cta-banner h2 {{
    font-size: 1.95rem; font-weight: 800; color: {p['t1']};
    letter-spacing: -0.04em; margin: 0 0 0.65rem;
}}
.cta-banner p {{ font-size: 1rem; color: {p['t2']}; margin: 0 0 1.9rem; line-height: 1.65; }}

/* ── Footer ────────────────────────────────────────────── */
.site-footer {{
    border-top: 1px solid {p['border']}; padding: 2rem 0 1rem;
    margin-top: 3rem; text-align: center;
}}
.site-footer p {{ font-size: 0.82rem; color: {p['t3']}; margin: 0; line-height: 1.6; }}
.site-footer a {{ color: {p['accent']}; text-decoration: none; }}

.section-gap {{ height: 3rem; }}
</style>
""", unsafe_allow_html=True)

# ── Navbar ────────────────────────────────────────────────────────────────────

render_nav(p, is_dark)

# ── Hero ──────────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="hero-section">
    <span class="hero-eyebrow">Free &amp; open source</span>
    <h1 class="hero-title">Turn income into<br><span class="ht-accent">independence.</span></h1>
    <p class="hero-sub">
        Ember is a free FIRE planning toolkit. Calculate when you can retire, understand
        the math behind financial independence, and build a plan that fits your life — not
        someone else's.
    </p>
</div>
""", unsafe_allow_html=True)

_, btn_l, btn_r, _ = st.columns([2, 1.2, 1.2, 2])
with btn_l:
    st.markdown('<div class="cta-primary">', unsafe_allow_html=True)
    if st.button("⚡  Calculate my FIRE age", use_container_width=True, type="primary", key="hero_calc"):
        st.switch_page("pages/1_Calculator.py")
    st.markdown("</div>", unsafe_allow_html=True)
with btn_r:
    st.markdown('<div class="cta-secondary">', unsafe_allow_html=True)
    if st.button("📚  How does it work?", use_container_width=True, key="hero_learn"):
        st.switch_page("pages/2_Learn.py")
    st.markdown("</div>", unsafe_allow_html=True)

# ── How FIRE works ────────────────────────────────────────────────────────────

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

left, right = st.columns([1.1, 1], gap="large")

with left:
    st.markdown(f"""
<div class="hiw-section">
    <h2>The math everyone gets wrong</h2>
    <p class="hiw-sub">
        Most people think retiring early is about earning more. It's actually about the
        <em>gap</em> between income and spending — and a single formula.
    </p>
    <div class="hiw-step">
        <div class="hiw-num">1</div>
        <div>
            <div class="hiw-title">Decide how much you need to spend</div>
            <div class="hiw-desc">Your retirement lifestyle determines your target. Spend less,
            reach it faster. This is entirely in your control.</div>
        </div>
    </div>
    <div class="hiw-step">
        <div class="hiw-num">2</div>
        <div>
            <div class="hiw-title">Divide by your safe withdrawal rate</div>
            <div class="hiw-desc">At 4%, you need 25× your annual spending invested. That's
            your FI number — the portfolio at which your money works instead of you.</div>
        </div>
    </div>
    <div class="hiw-step">
        <div class="hiw-num">3</div>
        <div>
            <div class="hiw-title">Close the gap with your savings rate</div>
            <div class="hiw-desc">The higher your savings rate, the faster you accumulate —
            and the less you need, since you're already living on less.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

with right:
    st.markdown(f"""
<div class="hiw-section" style="height:100%">
    <h2>Your FI number</h2>
    <p class="hiw-sub">One formula. Two inputs you control.</p>
    <div class="fi-formula">
        <span class="ff-label">The formula</span>
        <span class="ff-eq">
            Annual Spending &nbsp;÷&nbsp;
            <span class="ffe-accent">Withdrawal Rate</span>
            &nbsp;= &nbsp;<span class="ffe-accent">FI Number</span>
        </span>
    </div>
    <table class="example-table">
        <tr>
            <td>Spend $40K/year at 4%</td>
            <td>→ $1,000,000</td>
        </tr>
        <tr>
            <td>Spend $60K/year at 4%</td>
            <td>→ $1,500,000</td>
        </tr>
        <tr>
            <td>Spend $80K/year at 4%</td>
            <td>→ $2,000,000</td>
        </tr>
        <tr>
            <td>Spend $100K/year at 4%</td>
            <td>→ $2,500,000</td>
        </tr>
    </table>
    <div style="margin-top:1.5rem">
        <div style="display:flex;gap:0.8rem">
            <div style="flex:1;background:{p['surface2']};border:1px solid {p['border']};
                        border-radius:10px;padding:0.9rem 1rem;text-align:center">
                <div style="font-size:1.4rem;font-weight:800;color:{p['accent']};
                            letter-spacing:-0.03em">~7%</div>
                <div style="font-size:0.72rem;color:{p['t3']};letter-spacing:0.06em;
                            text-transform:uppercase;margin-top:0.15rem">
                    historical real return
                </div>
            </div>
            <div style="flex:1;background:{p['surface2']};border:1px solid {p['border']};
                        border-radius:10px;padding:0.9rem 1rem;text-align:center">
                <div style="font-size:1.4rem;font-weight:800;color:{p['fire_lean']};
                            letter-spacing:-0.03em">95%</div>
                <div style="font-size:0.72rem;color:{p['t3']};letter-spacing:0.06em;
                            text-transform:uppercase;margin-top:0.15rem">
                    30-yr success rate
                </div>
            </div>
            <div style="flex:1;background:{p['surface2']};border:1px solid {p['border']};
                        border-radius:10px;padding:0.9rem 1rem;text-align:center">
                <div style="font-size:1.4rem;font-weight:800;color:{p['fire_fat']};
                            letter-spacing:-0.03em">25×</div>
                <div style="font-size:0.72rem;color:{p['t3']};letter-spacing:0.06em;
                            text-transform:uppercase;margin-top:0.15rem">
                    spending at 4% rule
                </div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── FIRE Types ────────────────────────────────────────────────────────────────

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="section-hdr">
    <span class="sh-eyebrow">Every lifestyle has a number</span>
    <h2>Five paths to the same destination</h2>
    <p>Financial independence isn't one-size-fits-all. Your target depends on
       how you want to live — not how anyone else does it.</p>
</div>
""", unsafe_allow_html=True)

fire_types = [
    ("🌱", "Lean FIRE",    p["fire_lean"],    "$25–40K/yr · ~$625K–$1M",
     "Live deliberately on less. Reach FI fast, often in low cost-of-living areas. High freedom, low margin for error."),
    ("☕", "Barista FIRE", p["fire_barista"], "Part-time income · Flexible",
     "Leave your career, work part-time for spending money and benefits while your portfolio compounds to full FI."),
    ("🏠", "Regular FIRE", p["fire_regular"], "$50–80K/yr · $1.25M–$2M",
     "The most common target. Covers a comfortable, full American lifestyle — especially with paid-off housing."),
    ("🌟", "Fat FIRE",     p["fire_fat"],     "$100K+/yr · $2.5M+",
     "Retire without adjusting your lifestyle. Longer to reach, maximum flexibility, large buffer for the unexpected."),
    ("🏄", "Coast FIRE",   p["accent"],       "Stop contributing · Let it grow",
     "You've invested enough that compound growth alone carries you to FI by traditional retirement age. Coast from here."),
]

cols = st.columns(5, gap="small")
for col, (icon, name, color, rng, desc) in zip(cols, fire_types):
    with col:
        st.markdown(f"""
<div class="fire-card">
    <span class="fc-icon">{icon}</span>
    <div class="fc-name">{name}</div>
    <span class="fc-range" style="color:{color}">{rng}</span>
    <p class="fc-desc">{desc}</p>
</div>
""", unsafe_allow_html=True)

# ── Tools ─────────────────────────────────────────────────────────────────────

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="section-hdr">
    <span class="sh-eyebrow">Three free tools</span>
    <h2>Everything in one place</h2>
    <p>Each tool is built for a different part of the journey —
       from first principles to a fully stress-tested retirement plan.</p>
</div>
""", unsafe_allow_html=True)

t1, t2, t3 = st.columns(3, gap="medium")

with t1:
    st.markdown(f"""
<div class="tool-card">
    <span class="tc-icon">⚡</span>
    <div class="tc-name">FIRE Calculator</div>
    <p class="tc-desc">
        Enter your portfolio, contribution rate, and target spending. Get your FIRE age,
        progress toward each FIRE type, scenario comparisons, and a Monte Carlo
        stress test across thousands of market sequences.
    </p>
</div>
""", unsafe_allow_html=True)
    if st.button("Open calculator →", key="tool_calc", use_container_width=True):
        st.switch_page("pages/1_Calculator.py")

with t2:
    st.markdown(f"""
<div class="tool-card">
    <span class="tc-icon">📚</span>
    <div class="tc-name">Learn</div>
    <p class="tc-desc">
        Structured concept guides: the FI number, savings rate math, the 4% rule,
        compound growth, tax-advantaged accounts, and a first-steps checklist.
        Build your foundation before running the numbers.
    </p>
</div>
""", unsafe_allow_html=True)
    if st.button("Start learning →", key="tool_learn", use_container_width=True):
        st.switch_page("pages/2_Learn.py")

with t3:
    st.markdown(f"""
<div class="tool-card">
    <span class="tc-icon">✍️</span>
    <div class="tc-name">Blog</div>
    <p class="tc-desc">
        Long-form articles on FIRE strategy and the math behind it. Start with
        "What is FIRE?", go deeper with the 4% rule, and understand the real
        trade-offs between Lean and Fat FIRE.
    </p>
</div>
""", unsafe_allow_html=True)
    if st.button("Read the blog →", key="tool_blog", use_container_width=True):
        st.switch_page("pages/3_Blog.py")

# ── CTA Banner ────────────────────────────────────────────────────────────────

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="cta-banner">
    <h2>Your number is probably closer than you think.</h2>
    <p>Most people overestimate what they need and underestimate what they already have.
       Run the numbers — it takes two minutes.</p>
</div>
""", unsafe_allow_html=True)

_, cta_col, _ = st.columns([2, 2, 2])
with cta_col:
    st.markdown('<div class="cta-primary">', unsafe_allow_html=True)
    if st.button("⚡  Calculate my FIRE age", use_container_width=True, type="primary", key="final_cta"):
        st.switch_page("pages/1_Calculator.py")
    st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="site-footer">
    <p>Ember &nbsp;·&nbsp; Free FIRE planning tools &nbsp;·&nbsp;
    Not financial advice &nbsp;·&nbsp;
    <a href="https://github.com/interjector/fire_calculator" target="_blank">GitHub</a>
    </p>
</div>
""", unsafe_allow_html=True)
