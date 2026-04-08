import streamlit as st
from components.theme import get_palette, inject_base_css
from components.nav import render_nav

st.set_page_config(
    page_title="FIREpath — Financial Independence, Retire Early",
    page_icon="⚡",
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
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.22);
    color: {p['accent']};
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase;
    padding: 0.3rem 1rem; border-radius: 100px; margin-bottom: 1.6rem;
}}
.hero-title {{
    font-size: 3.6rem; font-weight: 800; letter-spacing: -0.05em; line-height: 1.08;
    color: {p['t1']}; margin: 0 0 1.2rem;
}}
.hero-title .ht-accent {{ color: {p['accent']}; }}
.hero-sub {{
    font-size: 1.1rem; color: {p['t2']};
    max-width: 580px; margin: 0 auto 2.8rem; line-height: 1.7;
}}

/* ── Landing CTA buttons ───────────────────────────────── */
.cta-primary .stButton > button {{
    background: linear-gradient(135deg, {p['accent']}, {'#059669' if is_dark else '#047857'}) !important;
    color: #fff !important; border: none !important;
    padding: 0.75rem 2.2rem !important; font-size: 0.95rem !important;
    font-weight: 700 !important; border-radius: 11px !important;
    box-shadow: 0 4px 20px rgba(16,185,129,0.25) !important;
    letter-spacing: 0.01em !important; width: 100% !important;
}}
.cta-primary .stButton > button:hover {{
    box-shadow: 0 6px 28px rgba(16,185,129,0.38) !important;
    transform: translateY(-2px) !important;
}}
.cta-secondary .stButton > button {{
    background: transparent !important;
    border: 1px solid {p['border2']} !important; color: {p['t2']} !important;
    padding: 0.75rem 2.2rem !important; font-size: 0.95rem !important;
    font-weight: 600 !important; border-radius: 11px !important;
    width: 100% !important;
}}
.cta-secondary .stButton > button:hover {{
    border-color: {p['accent']} !important; color: {p['accent']} !important;
}}

/* ── Stats bar ─────────────────────────────────────────── */
.stats-bar {{
    display: flex; justify-content: center; gap: 0; flex-wrap: wrap;
    border-top: 1px solid {p['border']}; border-bottom: 1px solid {p['border']};
    margin: 2rem 0;
}}
.stat-item {{
    flex: 1; min-width: 160px; max-width: 240px;
    text-align: center; padding: 1.1rem 1.5rem;
    border-right: 1px solid {p['border']};
}}
.stat-item:last-child {{ border-right: none; }}
.stat-val {{
    font-size: 1.45rem; font-weight: 800; color: {p['t1']};
    letter-spacing: -0.03em; display: block;
}}
.stat-lbl {{
    font-size: 0.7rem; font-weight: 500; color: {p['t3']};
    letter-spacing: 0.07em; text-transform: uppercase; margin-top: 0.15rem; display: block;
}}
.stat-item .stat-val.green {{ color: {p['accent']}; }}

/* ── Section headers ───────────────────────────────────── */
.section-hdr {{
    text-align: center; margin-bottom: 2.2rem;
}}
.section-hdr .sh-eyebrow {{
    font-size: 0.68rem; font-weight: 700; color: {p['accent']};
    letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 0.5rem; display: block;
}}
.section-hdr h2 {{
    font-size: 2rem; font-weight: 800; color: {p['t1']};
    letter-spacing: -0.04em; margin: 0 0 0.6rem;
}}
.section-hdr p {{
    font-size: 1rem; color: {p['t2']}; max-width: 520px; margin: 0 auto; line-height: 1.65;
}}

/* ── FIRE type cards ───────────────────────────────────── */
.fire-card {{
    background: {p['surface']}; border: 1px solid {p['border']};
    border-radius: 14px; padding: 1.3rem 1.4rem; height: 100%;
    transition: border-color 0.2s, transform 0.2s;
}}
.fire-card:hover {{ border-color: {p['border2']}; transform: translateY(-2px); }}
.fc-icon {{
    font-size: 1.6rem; margin-bottom: 0.7rem; display: block;
}}
.fc-name {{
    font-size: 0.95rem; font-weight: 700; color: {p['t1']}; margin-bottom: 0.25rem;
}}
.fc-range {{
    font-size: 0.78rem; font-weight: 600; margin-bottom: 0.55rem; display: block;
}}
.fc-desc {{
    font-size: 0.8rem; color: {p['t3']}; line-height: 1.55;
}}

/* ── Tool cards ────────────────────────────────────────── */
.tool-card {{
    background: {p['surface']}; border: 1px solid {p['border']};
    border-radius: 16px; padding: 1.8rem 1.8rem 1.5rem;
    transition: border-color 0.2s, box-shadow 0.2s;
}}
.tool-card:hover {{
    border-color: {p['accent']};
    box-shadow: 0 6px 30px rgba(16,185,129,0.07);
}}
.tc-icon {{ font-size: 2rem; margin-bottom: 0.8rem; display: block; }}
.tc-name {{ font-size: 1.15rem; font-weight: 700; color: {p['t1']}; margin-bottom: 0.4rem; }}
.tc-desc {{ font-size: 0.85rem; color: {p['t2']}; line-height: 1.6; margin-bottom: 1.2rem; }}
.tool-card .stButton > button {{
    background: transparent !important; border: 1px solid {p['border2']} !important;
    color: {p['t2']} !important; font-size: 0.78rem !important; font-weight: 600 !important;
    border-radius: 7px !important; padding: 0.4rem 1rem !important; width: 100% !important;
}}
.tool-card .stButton > button:hover {{
    border-color: {p['accent']} !important; color: {p['accent']} !important;
}}

/* ── What is FIRE two-col section ──────────────────────── */
.what-section {{
    background: {p['surface']}; border: 1px solid {p['border']};
    border-radius: 18px; padding: 2.5rem 2.5rem; margin: 2rem 0;
}}
.what-section h2 {{
    font-size: 1.85rem; font-weight: 800; color: {p['t1']};
    letter-spacing: -0.04em; margin: 0 0 1rem;
}}
.what-section p {{ font-size: 0.9rem; color: {p['t2']}; line-height: 1.7; margin-bottom: 0.8rem; }}
.fi-formula {{
    background: {p['surface2']}; border: 1px solid {p['border2']};
    border-radius: 12px; padding: 1.2rem 1.5rem; margin: 1.2rem 0;
    text-align: center;
}}
.fi-formula .ff-label {{
    font-size: 0.65rem; font-weight: 700; color: {p['t3']};
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.4rem; display: block;
}}
.fi-formula .ff-eq {{
    font-size: 1.05rem; font-weight: 700; color: {p['t1']};
}}
.fi-formula .ff-eq .ffe-accent {{ color: {p['accent']}; }}
.fi-stat-row {{
    display: flex; gap: 1rem; margin-top: 1.5rem;
}}
.fi-stat {{
    flex: 1; background: {p['surface2']}; border: 1px solid {p['border']};
    border-radius: 10px; padding: 0.85rem 1rem; text-align: center;
}}
.fi-stat .fis-val {{
    font-size: 1.3rem; font-weight: 800; color: {p['t1']}; letter-spacing: -0.03em; display: block;
}}
.fi-stat .fis-lbl {{
    font-size: 0.67rem; color: {p['t3']}; letter-spacing: 0.07em;
    text-transform: uppercase; margin-top: 0.15rem; display: block;
}}

/* ── CTA banner ────────────────────────────────────────── */
.cta-banner {{
    background: linear-gradient(135deg, {p['surface']}, {p['surface2']});
    border: 1px solid {p['border']}; border-radius: 18px;
    padding: 3rem 2rem; text-align: center; margin: 2.5rem 0;
}}
.cta-banner h2 {{
    font-size: 1.9rem; font-weight: 800; color: {p['t1']};
    letter-spacing: -0.04em; margin: 0 0 0.6rem;
}}
.cta-banner p {{ font-size: 0.95rem; color: {p['t2']}; margin: 0 0 1.8rem; line-height: 1.6; }}

/* ── Footer ────────────────────────────────────────────── */
.site-footer {{
    border-top: 1px solid {p['border']}; padding: 2rem 0 1rem;
    margin-top: 3rem; text-align: center;
}}
.site-footer p {{
    font-size: 0.78rem; color: {p['t3']}; margin: 0; line-height: 1.6;
}}
.site-footer a {{ color: {p['accent']}; text-decoration: none; }}

/* ── Section divider ───────────────────────────────────── */
.section-gap {{ height: 3rem; }}
</style>
""", unsafe_allow_html=True)

# ── Navbar ────────────────────────────────────────────────────────────────────

render_nav(p, is_dark)

# ── Hero ──────────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="hero-section">
    <span class="hero-eyebrow">Free &amp; Open Source Tools</span>
    <h1 class="hero-title">Your Path to<br><span class="ht-accent">Financial Freedom</span></h1>
    <p class="hero-sub">
        Interactive calculators, in-depth articles, and a clear roadmap for your journey to
        Financial Independence, Retire Early.
    </p>
</div>
""", unsafe_allow_html=True)

# CTA buttons
_, btn_l, btn_r, _ = st.columns([2, 1.2, 1.2, 2])
with btn_l:
    st.markdown('<div class="cta-primary">', unsafe_allow_html=True)
    if st.button("⚡  Try the Calculator", use_container_width=True, type="primary", key="hero_calc"):
        st.switch_page("pages/1_Calculator.py")
    st.markdown("</div>", unsafe_allow_html=True)
with btn_r:
    st.markdown('<div class="cta-secondary">', unsafe_allow_html=True)
    if st.button("📚  Start Learning", use_container_width=True, key="hero_learn"):
        st.switch_page("pages/2_Learn.py")
    st.markdown("</div>", unsafe_allow_html=True)

# ── Stats bar ─────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="stats-bar">
    <div class="stat-item">
        <span class="stat-val green">5</span>
        <span class="stat-lbl">FIRE Types Modelled</span>
    </div>
    <div class="stat-item">
        <span class="stat-val green">∞</span>
        <span class="stat-lbl">Monte Carlo Simulations</span>
    </div>
    <div class="stat-item">
        <span class="stat-val green">3</span>
        <span class="stat-lbl">Scenario Analyses</span>
    </div>
    <div class="stat-item">
        <span class="stat-val green">$0</span>
        <span class="stat-lbl">Cost, Always</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── What is FIRE ──────────────────────────────────────────────────────────────

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

left, right = st.columns([1.1, 1])
with left:
    st.markdown(f"""
<div class="what-section">
    <h2>What is FIRE?</h2>
    <p>
        FIRE — Financial Independence, Retire Early — is the practice of accumulating enough
        invested assets that your returns cover your living expenses indefinitely. Once you cross
        that line, work becomes optional.
    </p>
    <p>
        The central concept is your <strong style="color:{p['t1']}">FI Number</strong>: the portfolio
        size at which you're financially free. It's calculated from two things you control: how much
        you spend, and the safe withdrawal rate you plan on.
    </p>
    <div class="fi-formula">
        <span class="ff-label">Your FI Number</span>
        <span class="ff-eq">
            Annual Spending &nbsp;÷&nbsp;
            <span class="ffe-accent">Withdrawal Rate</span>
            &nbsp;= &nbsp;<span class="ffe-accent">Target Portfolio</span>
        </span>
    </div>
    <p>
        At a 4% withdrawal rate, you need 25× your annual spending. Spend $60K/year?
        Your FI number is $1.5M. The calculator models your specific path to that number.
    </p>
    <div class="fi-stat-row">
        <div class="fi-stat">
            <span class="fis-val" style="color:{p['accent']}">25×</span>
            <span class="fis-lbl">at 4% withdrawal</span>
        </div>
        <div class="fi-stat">
            <span class="fis-val" style="color:{p['fire_lean']}">~7%</span>
            <span class="fis-lbl">historical real return</span>
        </div>
        <div class="fi-stat">
            <span class="fis-val" style="color:{p['fire_fat']}">95%</span>
            <span class="fis-lbl">30-yr success rate</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

with right:
    st.markdown(f"""
<div class="what-section" style="height:100%">
    <h2>The Three Phases</h2>
    <p>
        Every FIRE journey moves through three phases — and knowing where you are changes
        how you should think about the next step.
    </p>
    <div style="margin-top:1.2rem">
        <div style="display:flex;gap:1rem;align-items:flex-start;margin-bottom:1.4rem">
            <div style="width:32px;height:32px;border-radius:8px;background:rgba(16,185,129,0.12);
                        display:flex;align-items:center;justify-content:center;
                        font-size:1rem;flex-shrink:0">1</div>
            <div>
                <div style="font-size:0.9rem;font-weight:700;color:{p['t1']}">Accumulation</div>
                <div style="font-size:0.82rem;color:{p['t3']};line-height:1.55;margin-top:0.2rem">
                    You earn more than you spend and invest the difference. Compound returns
                    start doing the heavy lifting.
                </div>
            </div>
        </div>
        <div style="display:flex;gap:1rem;align-items:flex-start;margin-bottom:1.4rem">
            <div style="width:32px;height:32px;border-radius:8px;background:rgba(59,130,246,0.12);
                        display:flex;align-items:center;justify-content:center;
                        font-size:1rem;flex-shrink:0">2</div>
            <div>
                <div style="font-size:0.9rem;font-weight:700;color:{p['t1']}">Transition</div>
                <div style="font-size:0.82rem;color:{p['t3']};line-height:1.55;margin-top:0.2rem">
                    Your portfolio generates real income. Many people shift to part-time work,
                    explore Barista FIRE, or change careers.
                </div>
            </div>
        </div>
        <div style="display:flex;gap:1rem;align-items:flex-start">
            <div style="width:32px;height:32px;border-radius:8px;background:rgba(139,92,246,0.12);
                        display:flex;align-items:center;justify-content:center;
                        font-size:1rem;flex-shrink:0">3</div>
            <div>
                <div style="font-size:0.9rem;font-weight:700;color:{p['t1']}">Financial Independence</div>
                <div style="font-size:0.82rem;color:{p['t3']};line-height:1.55;margin-top:0.2rem">
                    Investment income covers expenses. Work is optional. You choose how you spend
                    your time — not your employer.
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
    <span class="sh-eyebrow">Choose Your Path</span>
    <h2>Five Flavors of FIRE</h2>
    <p>The FIRE spectrum covers everything from radical frugality to lifestyle abundance.
       Pick the one that fits the life you want to live.</p>
</div>
""", unsafe_allow_html=True)

fire_types = [
    ("🌱", "Lean FIRE",    p["fire_lean"],    "$25–40K/yr · ~$625K–$1M",
     "Live frugally and reach FI fast. Common in low cost-of-living areas or abroad. Fastest path, thinnest margin."),
    ("☕", "Barista FIRE", p["fire_barista"], "Part-time income · Flexible target",
     "Leave your career, work part-time for income and benefits, let your portfolio compound to full FI."),
    ("🏠", "Regular FIRE", p["fire_regular"], "$50–80K/yr · ~$1.25M–$2M",
     "The most common target. Covers most American lifestyles comfortably — especially with paid-off housing."),
    ("🌟", "Fat FIRE",     p["fire_fat"],     "$100K+/yr · $2.5M+",
     "Retire without changing your lifestyle. Maximum flexibility, longest accumulation, largest cushion."),
    ("🏄", "Coast FIRE",   p["accent"],       "Stop contributing · Time does the work",
     "You've invested enough that compound growth alone will carry you to FI by traditional retirement age."),
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

# ── Tools showcase ────────────────────────────────────────────────────────────

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="section-hdr">
    <span class="sh-eyebrow">Everything You Need</span>
    <h2>The FIREpath Toolkit</h2>
    <p>Three integrated tools — built to take you from first principles to a concrete, stress-tested plan.</p>
</div>
""", unsafe_allow_html=True)

t1, t2, t3 = st.columns(3, gap="medium")

with t1:
    st.markdown(f"""
<div class="tool-card">
    <span class="tc-icon">⚡</span>
    <div class="tc-name">FIRE Calculator</div>
    <p class="tc-desc">
        Model your path to financial independence. Input your portfolio, contributions, and
        target spending to see your FIRE age, scenario comparisons, and a full Monte Carlo
        stress test.
    </p>
</div>
""", unsafe_allow_html=True)
    if st.button("Open Calculator →", key="tool_calc", use_container_width=True):
        st.switch_page("pages/1_Calculator.py")

with t2:
    st.markdown(f"""
<div class="tool-card">
    <span class="tc-icon">📚</span>
    <div class="tc-name">Learn</div>
    <p class="tc-desc">
        Build your foundation. Structured guides on the FI number, savings rates, tax-advantaged
        accounts, FIRE types, and the math that makes it all work.
    </p>
</div>
""", unsafe_allow_html=True)
    if st.button("Start Learning →", key="tool_learn", use_container_width=True):
        st.switch_page("pages/2_Learn.py")

with t3:
    st.markdown(f"""
<div class="tool-card">
    <span class="tc-icon">✍️</span>
    <div class="tc-name">Blog</div>
    <p class="tc-desc">
        In-depth articles on FIRE strategy, withdrawal rules, and lifestyle design.
        Start with the fundamentals and go as deep as you want.
    </p>
</div>
""", unsafe_allow_html=True)
    if st.button("Read the Blog →", key="tool_blog", use_container_width=True):
        st.switch_page("pages/3_Blog.py")

# ── CTA Banner ────────────────────────────────────────────────────────────────

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="cta-banner">
    <h2>Ready to find your number?</h2>
    <p>It takes two minutes. Enter your current portfolio, contribution rate, and
       target spending — and see exactly when financial freedom is within reach.</p>
</div>
""", unsafe_allow_html=True)

_, cta_col, _ = st.columns([2, 2, 2])
with cta_col:
    st.markdown('<div class="cta-primary">', unsafe_allow_html=True)
    if st.button("⚡  Calculate My FIRE Age", use_container_width=True, type="primary", key="final_cta"):
        st.switch_page("pages/1_Calculator.py")
    st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="site-footer">
    <p>FIREpath &nbsp;·&nbsp; Free, open-source FIRE planning tools &nbsp;·&nbsp;
    Not financial advice &nbsp;·&nbsp;
    <a href="https://github.com" target="_blank">GitHub</a>
    </p>
</div>
""", unsafe_allow_html=True)
