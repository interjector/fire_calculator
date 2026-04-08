import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from components.theme import get_palette, inject_base_css
from components.nav import render_nav

st.set_page_config(
    page_title="Learn — FIREpath",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

p, is_dark = get_palette()
inject_base_css(p, is_dark, hide_sidebar=True)

st.markdown(f"""
<style>
/* ── Learn page layout ─────────────────────────────────── */
.learn-hero {{
    padding: 2rem 0 2.5rem;
    border-bottom: 1px solid {p['border']};
    margin-bottom: 2.5rem;
}}
.learn-hero h1 {{
    font-size: 2.4rem; font-weight: 800; color: {p['t1']};
    letter-spacing: -0.05em; margin: 0 0 0.6rem;
}}
.learn-hero p {{
    font-size: 1rem; color: {p['t2']}; max-width: 560px; line-height: 1.65; margin: 0;
}}

/* ── Concept cards ──────────────────────────────────────── */
.concept-card {{
    background: {p['surface']}; border: 1px solid {p['border']};
    border-radius: 14px; padding: 1.6rem 1.8rem; margin-bottom: 1rem;
    border-left: 3px solid transparent;
}}
.concept-card.accent-green {{ border-left-color: {p['accent']}; }}
.concept-card.accent-blue  {{ border-left-color: {p['fire_lean']}; }}
.concept-card.accent-amber {{ border-left-color: {p['fire_regular']}; }}
.concept-card.accent-purple {{ border-left-color: {p['fire_fat']}; }}

.cc-eyebrow {{
    font-size: 0.63rem; font-weight: 700; letter-spacing: 0.13em;
    text-transform: uppercase; margin-bottom: 0.45rem; display: block;
}}
.cc-title {{
    font-size: 1.15rem; font-weight: 700; color: {p['t1']};
    letter-spacing: -0.02em; margin-bottom: 0.5rem;
}}
.cc-body {{ font-size: 0.88rem; color: {p['t2']}; line-height: 1.7; }}
.cc-body strong {{ color: {p['t1']}; }}
.cc-body code {{
    background: {p['surface2']}; border: 1px solid {p['border2']};
    border-radius: 4px; padding: 0.1rem 0.4rem;
    font-size: 0.83rem; color: {p['accent']};
}}

/* ── Formula block ──────────────────────────────────────── */
.formula-block {{
    background: {p['surface2']}; border: 1px solid {p['border2']};
    border-radius: 10px; padding: 1rem 1.4rem; margin: 0.9rem 0;
    text-align: center;
}}
.formula-block .fb-eq {{
    font-size: 1rem; font-weight: 700; color: {p['t1']};
}}
.formula-block .fb-eq .fba {{ color: {p['accent']}; }}

/* ── Comparison table ───────────────────────────────────── */
.compare-table {{
    width: 100%; border-collapse: collapse;
    font-size: 0.83rem; margin: 1rem 0;
}}
.compare-table th {{
    text-align: left; padding: 0.6rem 0.9rem;
    font-size: 0.63rem; font-weight: 700; color: {p['t3']};
    letter-spacing: 0.1em; text-transform: uppercase;
    border-bottom: 1px solid {p['border']};
}}
.compare-table td {{
    padding: 0.7rem 0.9rem; color: {p['t2']};
    border-bottom: 1px solid {p['border']};
    vertical-align: top;
}}
.compare-table tr:last-child td {{ border-bottom: none; }}
.compare-table td:first-child {{ font-weight: 600; color: {p['t1']}; }}
.ct-badge {{
    display: inline-block; padding: 0.15rem 0.55rem;
    border-radius: 100px; font-size: 0.7rem; font-weight: 600;
}}

/* ── Checklist ──────────────────────────────────────────── */
.checklist-item {{
    display: flex; gap: 0.8rem; align-items: flex-start;
    padding: 0.75rem 0; border-bottom: 1px solid {p['border']};
}}
.checklist-item:last-child {{ border-bottom: none; }}
.cli-icon {{
    width: 24px; height: 24px; border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; flex-shrink: 0; margin-top: 0.05rem;
}}
.cli-title {{ font-size: 0.88rem; font-weight: 600; color: {p['t1']}; margin-bottom: 0.15rem; }}
.cli-desc {{ font-size: 0.8rem; color: {p['t3']}; line-height: 1.5; }}

/* ── Section heading ────────────────────────────────────── */
.learn-section-hdr {{
    font-size: 0.62rem; font-weight: 700; color: {p['t3']};
    letter-spacing: 0.13em; text-transform: uppercase;
    padding-bottom: 0.5rem; border-bottom: 1px solid {p['border']};
    margin: 2.2rem 0 1.1rem; display: block;
}}
</style>
""", unsafe_allow_html=True)

render_nav(p, is_dark)

# ── Hero ──────────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="learn-hero">
    <h1>📚 Learn FIRE</h1>
    <p>Core concepts, essential math, and a clear path forward.
       Everything you need to understand and pursue financial independence.</p>
</div>
""", unsafe_allow_html=True)

# ── Section 1: Foundations ────────────────────────────────────────────────────

st.markdown('<span class="learn-section-hdr">Foundations</span>', unsafe_allow_html=True)

col_a, col_b = st.columns(2, gap="medium")

with col_a:
    st.markdown(f"""
<div class="concept-card accent-green">
    <span class="cc-eyebrow" style="color:{p['accent']}">Core Concept</span>
    <div class="cc-title">Your FI Number</div>
    <div class="cc-body">
        <p>Financial Independence is reached when your invested assets generate enough returns to
        cover your living expenses — indefinitely. The <strong>FI Number</strong> is the portfolio
        size that makes this possible.</p>
        <div class="formula-block">
            <span class="fb-eq">
                FI Number = Annual Spending ÷ <span class="fba">Withdrawal Rate</span>
            </span>
        </div>
        <p>At a 4% withdrawal rate, you need <strong>25× your annual spending</strong>.</p>
        <table style="width:100%;font-size:0.8rem;margin-top:0.7rem">
            <tr>
                <td style="color:{p['t3']};padding:0.2rem 0">$40K/year spending</td>
                <td style="color:{p['accent']};font-weight:700;text-align:right">→ $1,000,000</td>
            </tr>
            <tr>
                <td style="color:{p['t3']};padding:0.2rem 0">$60K/year spending</td>
                <td style="color:{p['accent']};font-weight:700;text-align:right">→ $1,500,000</td>
            </tr>
            <tr>
                <td style="color:{p['t3']};padding:0.2rem 0">$100K/year spending</td>
                <td style="color:{p['accent']};font-weight:700;text-align:right">→ $2,500,000</td>
            </tr>
        </table>
    </div>
</div>
""", unsafe_allow_html=True)

with col_b:
    st.markdown(f"""
<div class="concept-card accent-blue">
    <span class="cc-eyebrow" style="color:{p['fire_lean']}">The Most Important Variable</span>
    <div class="cc-title">Savings Rate</div>
    <div class="cc-body">
        <p>Your <strong>savings rate</strong> — the percentage of income you invest — is the single
        biggest driver of your FIRE timeline. It controls both how fast your portfolio grows
        <em>and</em> how small your FI number is (since spending less means needing less).</p>
        <table style="width:100%;font-size:0.8rem;margin-top:0.7rem;border-top:1px solid {p['border']}">
            <tr>
                <th style="color:{p['t3']};font-size:0.65rem;letter-spacing:0.08em;
                           text-transform:uppercase;padding:0.5rem 0.3rem;text-align:left">
                    Savings Rate
                </th>
                <th style="color:{p['t3']};font-size:0.65rem;letter-spacing:0.08em;
                           text-transform:uppercase;padding:0.5rem 0.3rem;text-align:right">
                    Years to FI
                </th>
            </tr>
            <tr>
                <td style="color:{p['t2']};padding:0.35rem 0.3rem">10%</td>
                <td style="color:{p['t2']};padding:0.35rem 0.3rem;text-align:right">~43 years</td>
            </tr>
            <tr>
                <td style="color:{p['t2']};padding:0.35rem 0.3rem">25%</td>
                <td style="color:{p['t2']};padding:0.35rem 0.3rem;text-align:right">~32 years</td>
            </tr>
            <tr>
                <td style="color:{p['t2']};padding:0.35rem 0.3rem">40%</td>
                <td style="color:{p['fire_lean']};font-weight:600;padding:0.35rem 0.3rem;text-align:right">~22 years</td>
            </tr>
            <tr>
                <td style="color:{p['t2']};padding:0.35rem 0.3rem">60%</td>
                <td style="color:{p['accent']};font-weight:700;padding:0.35rem 0.3rem;text-align:right">~12 years</td>
            </tr>
        </table>
        <p style="margin-top:0.7rem;font-size:0.8rem;color:{p['t3']}">
            Assumes 7% real returns. Even modest increases in savings rate dramatically
            compress the timeline.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Section 2: The Math ───────────────────────────────────────────────────────

st.markdown('<span class="learn-section-hdr">The Math</span>', unsafe_allow_html=True)

col_c, col_d = st.columns(2, gap="medium")

with col_c:
    st.markdown(f"""
<div class="concept-card accent-amber">
    <span class="cc-eyebrow" style="color:{p['fire_regular']}">Withdrawal Strategy</span>
    <div class="cc-title">The 4% Rule</div>
    <div class="cc-body">
        <p>The <strong>4% rule</strong> comes from the 1998 Trinity Study, which analyzed every
        rolling 30-year period of US stock market history. Key finding: a portfolio of 60% stocks
        / 40% bonds using a 4% initial withdrawal rate (inflation-adjusted each year) survived
        <strong>95%+ of all 30-year periods</strong>.</p>
        <p>How it works in practice:</p>
        <ul style="margin:0.5rem 0 0.5rem 1.2rem;line-height:1.8">
            <li>Year 1: withdraw 4% of starting portfolio</li>
            <li>Each subsequent year: adjust for inflation only</li>
            <li>Portfolio growth replenishes withdrawals in most years</li>
        </ul>
        <div style="background:{p['surface2']};border:1px solid {p['border2']};
                    border-radius:8px;padding:0.8rem 1rem;margin-top:0.8rem">
            <div style="font-size:0.67rem;color:{p['t3']};letter-spacing:0.09em;
                        text-transform:uppercase;margin-bottom:0.3rem">Adjusting for early retirement</div>
            <div style="font-size:0.8rem;color:{p['t2']}">
                Retiring at 65? 4% is fine. Retiring at 40? Consider 3.25–3.5% — the longer
                horizon increases sequence-of-returns risk.
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

with col_d:
    st.markdown(f"""
<div class="concept-card accent-green">
    <span class="cc-eyebrow" style="color:{p['accent']}">Time Value of Money</span>
    <div class="cc-title">Compound Growth</div>
    <div class="cc-body">
        <p>Compound interest is the mechanism that makes FIRE possible. Your portfolio earns
        returns not just on contributions, but on all previous returns — growth that accelerates
        exponentially over time.</p>
        <div class="formula-block">
            <span class="fb-eq">
                FV = PV × (1 + r)<sup>n</sup>
            </span>
        </div>
        <p>At 7% annual real return, money doubles roughly every <strong>10 years</strong>.
        This means time in the market matters enormously:</p>
        <table style="width:100%;font-size:0.8rem;margin-top:0.7rem">
            <tr>
                <td style="color:{p['t3']};padding:0.2rem 0">$100K invested, 10 yrs</td>
                <td style="color:{p['t1']};font-weight:700;text-align:right">→ ~$197K</td>
            </tr>
            <tr>
                <td style="color:{p['t3']};padding:0.2rem 0">$100K invested, 20 yrs</td>
                <td style="color:{p['t1']};font-weight:700;text-align:right">→ ~$387K</td>
            </tr>
            <tr>
                <td style="color:{p['t3']};padding:0.2rem 0">$100K invested, 30 yrs</td>
                <td style="color:{p['accent']};font-weight:700;text-align:right">→ ~$761K</td>
            </tr>
        </table>
        <p style="margin-top:0.8rem;font-size:0.8rem;color:{p['t3']}">
            This is why starting early (or finding your Coast FIRE number) is so powerful —
            early dollars compound far longer.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Section 3: Accounts ───────────────────────────────────────────────────────

st.markdown('<span class="learn-section-hdr">Tax-Advantaged Accounts</span>', unsafe_allow_html=True)

st.markdown(f"""
<div class="concept-card accent-purple">
    <span class="cc-eyebrow" style="color:{p['fire_fat']}">Tax Strategy</span>
    <div class="cc-title">Account Types Overview</div>
    <div class="cc-body">
        <p>Where you hold your investments matters almost as much as what you invest in.
        Tax-advantaged accounts can add hundreds of thousands of dollars to your lifetime
        returns by reducing or eliminating taxes on growth.</p>
        <table class="compare-table" style="margin-top:1rem">
            <tr>
                <th>Account</th>
                <th>2026 Limit</th>
                <th>Tax Treatment</th>
                <th>Best For</th>
            </tr>
            <tr>
                <td>401(k) / 403(b)</td>
                <td>$23,500</td>
                <td>Pre-tax contributions, taxed on withdrawal</td>
                <td>High earners reducing current tax bill</td>
            </tr>
            <tr>
                <td>Roth IRA</td>
                <td>$7,000</td>
                <td>After-tax contributions, <strong style="color:{p['accent']}">tax-free growth</strong></td>
                <td>Early retirees; lower tax years</td>
            </tr>
            <tr>
                <td>Traditional IRA</td>
                <td>$7,000</td>
                <td>Pre-tax (if deductible), taxed on withdrawal</td>
                <td>Supplementing 401(k)</td>
            </tr>
            <tr>
                <td>HSA</td>
                <td>$4,300 / $8,550</td>
                <td><strong style="color:{p['accent']}">Triple tax-advantaged</strong></td>
                <td>Healthcare + stealth retirement account</td>
            </tr>
            <tr>
                <td>Taxable Brokerage</td>
                <td>Unlimited</td>
                <td>Long-term capital gains rates</td>
                <td>Funds needed before age 59½</td>
            </tr>
        </table>
        <div style="background:{p['surface2']};border:1px solid {p['border2']};border-radius:8px;
                    padding:0.8rem 1rem;margin-top:1rem">
            <div style="font-size:0.67rem;color:{p['t3']};letter-spacing:0.09em;
                        text-transform:uppercase;margin-bottom:0.3rem">FIRE Account Priority</div>
            <div style="font-size:0.82rem;color:{p['t2']}">
                1. 401(k) to employer match → 2. HSA (if eligible) → 3. Roth IRA →
                4. Max 401(k) → 5. Taxable brokerage
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Section 4: FIRE Types ─────────────────────────────────────────────────────

st.markdown('<span class="learn-section-hdr">FIRE Types at a Glance</span>', unsafe_allow_html=True)

st.markdown(f"""
<div class="concept-card accent-blue">
    <span class="cc-eyebrow" style="color:{p['fire_lean']}">Choose Your Path</span>
    <div class="cc-title">The Five FIRE Types</div>
    <div class="cc-body">
        <table class="compare-table">
            <tr>
                <th>Type</th>
                <th>Annual Spending</th>
                <th>Portfolio Needed</th>
                <th>Key Trade-off</th>
            </tr>
            <tr>
                <td>🌱 Lean FIRE</td>
                <td>$25–40K</td>
                <td style="color:{p['fire_lean']};font-weight:600">$625K – $1M</td>
                <td>Fastest path, least cushion</td>
            </tr>
            <tr>
                <td>☕ Barista FIRE</td>
                <td>Flexible</td>
                <td style="color:{p['fire_barista']};font-weight:600">50–75% of FI number</td>
                <td>Needs part-time income + benefits</td>
            </tr>
            <tr>
                <td>🏠 Regular FIRE</td>
                <td>$50–80K</td>
                <td style="color:{p['fire_regular']};font-weight:600">$1.25M – $2M</td>
                <td>Most common, balanced trade-off</td>
            </tr>
            <tr>
                <td>🌟 Fat FIRE</td>
                <td>$100K+</td>
                <td style="color:{p['fire_fat']};font-weight:600">$2.5M+</td>
                <td>Maximum freedom, longest timeline</td>
            </tr>
            <tr>
                <td>🏄 Coast FIRE</td>
                <td>Any</td>
                <td style="color:{p['accent']};font-weight:600">Age-dependent</td>
                <td>Stop saving; compound growth does the work</td>
            </tr>
        </table>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Section 5: First Steps ────────────────────────────────────────────────────

st.markdown('<span class="learn-section-hdr">Getting Started</span>', unsafe_allow_html=True)

steps = [
    ("📊", p["accent"],        "rgba(16,185,129,0.1)",
     "Track your spending",
     "You can't optimize what you don't measure. Spend one month logging every dollar. "
     "You'll likely find 20–30% that doesn't align with your values."),
    ("💰", p["fire_lean"],     "rgba(59,130,246,0.1)",
     "Calculate your savings rate",
     "Savings rate = (Income − Spending) ÷ Income. A 20% rate is a starting point; "
     "30–50% is where FIRE timelines start to compress meaningfully."),
    ("🎯", p["fire_regular"],  "rgba(245,158,11,0.1)",
     "Pick your FIRE type and calculate your FI number",
     "Use the FIRE Calculator to model your specific situation. Try different FIRE types "
     "and see how they change your timeline."),
    ("🏦", p["fire_fat"],      "rgba(139,92,246,0.1)",
     "Max tax-advantaged accounts first",
     "401(k) to match, then HSA, then Roth IRA, then max 401(k). This sequence minimizes "
     "your lifetime tax bill on the same investments."),
    ("📈", p["accent"],        "rgba(16,185,129,0.1)",
     "Invest in low-cost index funds",
     "The research is overwhelming: low-cost broad-market index funds (VTI, VTSAX, "
     "FZROX) outperform actively managed funds in the long run. Keep costs below 0.1%."),
    ("🔁", p["fire_lean"],     "rgba(59,130,246,0.1)",
     "Automate and revisit annually",
     "Set up automatic contributions so you can't spend before investing. Review your "
     "plan once a year — adjust as income, expenses, and goals change."),
]

for icon, color, bg, title, desc in steps:
    st.markdown(f"""
<div class="checklist-item">
    <div class="cli-icon" style="background:{bg};color:{color}">{icon}</div>
    <div>
        <div class="cli-title">{title}</div>
        <div class="cli-desc">{desc}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── CTA ───────────────────────────────────────────────────────────────────────

st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="background:{p['surface']};border:1px solid {p['border']};border-radius:16px;
            padding:2rem;text-align:center;margin-top:1rem">
    <div style="font-size:1.3rem;font-weight:800;color:{p['t1']};letter-spacing:-0.03em;margin-bottom:0.5rem">
        Ready to run the numbers?
    </div>
    <div style="font-size:0.9rem;color:{p['t2']};margin-bottom:0">
        Put the concepts to work — model your personal path to financial independence.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
_, cta_col, _ = st.columns([2, 2, 2])
with cta_col:
    if st.button("⚡  Open the FIRE Calculator", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Calculator.py")

st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
_, blog_col, _ = st.columns([2, 2, 2])
with blog_col:
    if st.button("✍️  Read the Blog →", use_container_width=True):
        st.switch_page("pages/3_Blog.py")
