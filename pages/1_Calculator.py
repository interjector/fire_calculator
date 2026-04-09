import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fire_calculator import FIRECalculator
import numpy as np
import requests
from datetime import datetime
from components.theme import get_palette, inject_base_css
from components.nav import render_nav

st.set_page_config(
    page_title="FIRE Calculator — Ember",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

p, is_dark = get_palette()
inject_base_css(p, is_dark)

FC = dict(
    lean=p["fire_lean"], barista=p["fire_barista"],
    regular=p["fire_regular"], fat=p["fire_fat"],
)

# ── Navbar ────────────────────────────────────────────────────────────────────

render_nav(p, is_dark)

# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt(val):
    if val is None:
        return "—"
    if abs(val) >= 1_000_000:
        return f"${val / 1_000_000:.2f}M"
    if abs(val) >= 1_000:
        return f"${val / 1_000:.0f}K"
    return f"${val:,.0f}"

def chart_layout(p, height=440, y_prefix="$", right_margin=180, top_margin=28):
    return dict(
        paper_bgcolor=p["paper"],
        plot_bgcolor=p["plot"],
        font=dict(family="Inter, sans-serif", color=p["ct"], size=11),
        xaxis=dict(
            gridcolor=p["grid"], linecolor=p["grid"],
            tickfont=dict(color=p["tick"], size=10),
            title_font=dict(color=p["tick"], size=11),
            showgrid=True, zeroline=False,
        ),
        yaxis=dict(
            gridcolor=p["grid"], linecolor=p["grid"],
            tickfont=dict(color=p["tick"], size=10),
            title_font=dict(color=p["tick"], size=11),
            tickprefix=y_prefix, tickformat=",.0f",
            showgrid=True, zeroline=False,
        ),
        legend=dict(
            bgcolor=p["leg_bg"], bordercolor=p["leg_border"], borderwidth=1,
            font=dict(color=p["ct"], size=10),
            itemsizing="constant",
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=p["hover_bg"], bordercolor=p["hover_border"],
            font=dict(color=p["hover_text"], size=11),
        ),
        height=height,
        margin=dict(l=10, r=right_margin, t=top_margin, b=10),
    )

def make_fig(p, height=440, y_prefix="$", right_margin=180, top_margin=28):
    fig = go.Figure()
    fig.update_layout(**chart_layout(p, height, y_prefix, right_margin, top_margin))
    return fig

# ── Sidebar ───────────────────────────────────────────────────────────────────

def slabel(text):
    st.sidebar.markdown(f'<span class="section-label">{text}</span>', unsafe_allow_html=True)

with st.sidebar:
    icon = "☀️  Switch to Light" if is_dark else "🌙  Switch to Dark"
    st.markdown('<div class="theme-toggle-btn">', unsafe_allow_html=True)
    if st.button(icon, use_container_width=True):
        st.session_state["theme"] = "light" if is_dark else "dark"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

slabel("Your Situation")
current_age = st.sidebar.number_input("Current Age", min_value=18, max_value=80, value=32)
current_portfolio_taxable = st.sidebar.number_input(
    "Taxable Portfolio ($)", min_value=0, value=75000, step=5000)
current_portfolio_tax_deferred = st.sidebar.number_input(
    "Tax-Deferred Portfolio ($)", min_value=0, value=50000, step=5000)
annual_contribution = st.sidebar.number_input(
    "Annual Contribution ($)", min_value=0, value=36000, step=1000)
expected_annual_spending = st.sidebar.number_input(
    "Retirement Spending / Year ($)", min_value=1000, value=80000, step=1000)

slabel("Strategy")
_fire_map = {"Lean": "lean", "Barista": "barista", "Regular": "regular", "Fat": "fat"}
fire_type_display = st.sidebar.selectbox("FIRE Type", list(_fire_map.keys()), index=2)
fire_type = _fire_map[fire_type_display]
desired_retirement_age = st.sidebar.number_input(
    "Target Retirement Age (optional)", min_value=int(current_age), max_value=80,
    value=None, placeholder="—")
life_expectancy = st.sidebar.number_input(
    "Life Expectancy", min_value=int(current_age) + 5, max_value=120, value=90)

slabel("Market Assumptions")
growth_rate = st.sidebar.slider(
    "Annual Growth Rate", min_value=1.0, max_value=15.0, value=7.0,
    step=0.5, format="%.1f%%") / 100
inflation_rate = st.sidebar.slider(
    "Inflation Rate", min_value=0.0, max_value=10.0, value=3.0,
    step=0.5, format="%.1f%%") / 100
withdrawal_rate = st.sidebar.slider(
    "Safe Withdrawal Rate", min_value=2.0, max_value=8.0, value=4.0,
    step=0.25, format="%.2f%%") / 100

slabel("Social Security")
social_security_income = st.sidebar.number_input(
    "Expected Annual SS ($)", min_value=0, value=0, step=1000)
social_security_age = st.sidebar.number_input(
    "SS Start Age", min_value=62, max_value=70, value=67)

slabel("Events")

with st.sidebar.expander("Windfalls (optional)"):
    num_windfalls = st.number_input("Number of windfalls", min_value=0, max_value=5, value=0)
    windfalls = []
    for i in range(int(num_windfalls)):
        c1, c2 = st.columns(2)
        with c1:
            w_age = st.number_input("Age", min_value=int(current_age), max_value=100,
                                    value=int(current_age) + 5, key=f"wa_{i}")
        with c2:
            w_amt = st.number_input("Amount ($)", min_value=0, value=50000,
                                    step=5000, key=f"wamt_{i}")
        windfalls.append({"age": w_age, "amount": w_amt})

with st.sidebar.expander("Large Expense (optional)"):
    has_large_expense = st.checkbox("Include large expense")
    large_expense = {}
    if has_large_expense:
        expense_type_label = st.radio("Type", ["Single year", "Multi-year"], horizontal=True)
        funding_strategy = st.selectbox(
            "Funding strategy",
            ["Portfolio Withdrawal", "Reduce Contributions", "Mixed Approach"])
        fs_key = funding_strategy.lower().replace(" ", "_")

        if expense_type_label == "Single year":
            le_age = st.number_input("At age", min_value=int(current_age), max_value=100,
                                     value=int(current_age) + 10)
            le_amount = st.number_input("Amount ($)", min_value=0, value=50000, step=5000)
            large_expense = {"type": "single", "target_age": le_age,
                             "amount": le_amount, "funding_strategy": fs_key}
            if funding_strategy == "Mixed Approach":
                large_expense["max_contribution_reduction"] = st.number_input(
                    "Max contribution reduction ($)", min_value=0,
                    max_value=int(annual_contribution),
                    value=min(le_amount, int(annual_contribution)), step=1000)
            elif funding_strategy == "Reduce Contributions" and le_amount > annual_contribution:
                st.caption(f"Excess ${le_amount - annual_contribution:,} withdrawn from portfolio")
        else:
            c1, c2 = st.columns(2)
            with c1:
                le_start = st.number_input("Start age", min_value=int(current_age), max_value=100,
                                           value=int(current_age) + 10)
            with c2:
                le_end = st.number_input("End age", min_value=int(le_start), max_value=100,
                                         value=int(le_start) + 2)
            le_annual = st.number_input("Annual amount ($)", min_value=0, value=30000, step=1000)
            large_expense = {"type": "multi", "start_age": le_start,
                             "end_age": max(le_end, le_start), "annual_amount": le_annual,
                             "funding_strategy": fs_key}
            if funding_strategy == "Mixed Approach":
                large_expense["max_annual_contribution_reduction"] = st.number_input(
                    "Max annual contrib reduction ($)", min_value=0,
                    max_value=int(annual_contribution),
                    value=min(le_annual, int(annual_contribution)), step=1000)

# ── Calculation ───────────────────────────────────────────────────────────────

try:
    calc = FIRECalculator(
        current_age=int(current_age),
        current_portfolio_taxable=float(current_portfolio_taxable),
        current_portfolio_tax_deferred=float(current_portfolio_tax_deferred),
        annual_contribution=float(annual_contribution),
        expected_annual_spending=float(expected_annual_spending),
        growth_rate=growth_rate,
        inflation_rate=inflation_rate,
        withdrawal_rate=withdrawal_rate,
        social_security_income=float(social_security_income),
        social_security_age=int(social_security_age),
        desired_retirement_age=int(desired_retirement_age) if desired_retirement_age else None,
        life_expectancy=int(life_expectancy),
        fire_type=fire_type,
        windfalls=windfalls,
        large_expense=large_expense,
    )
    target_portfolio = calc.calculate_target_portfolio()
    years_to_fire    = calc.calculate_years_to_fire()
    fire_age         = (int(current_age) + years_to_fire) if years_to_fire is not None else None
    projections      = calc.generate_yearly_projections()
    fire_targets     = calc.calculate_all_fire_targets()
    proj_df          = pd.DataFrame(projections)

    cons_calc = FIRECalculator(
        int(current_age), float(current_portfolio_taxable), float(current_portfolio_tax_deferred),
        float(annual_contribution), float(expected_annual_spending),
        growth_rate=0.05, inflation_rate=0.04, withdrawal_rate=withdrawal_rate,
        life_expectancy=int(life_expectancy), fire_type=fire_type,
    )
    opt_calc = FIRECalculator(
        int(current_age), float(current_portfolio_taxable), float(current_portfolio_tax_deferred),
        float(annual_contribution), float(expected_annual_spending),
        growth_rate=0.09, inflation_rate=0.02, withdrawal_rate=withdrawal_rate,
        life_expectancy=int(life_expectancy), fire_type=fire_type,
    )
    cons_df = pd.DataFrame(cons_calc.generate_yearly_projections())
    opt_df  = pd.DataFrame(opt_calc.generate_yearly_projections())

except Exception as e:
    st.error(f"Calculation error: {e}")
    st.stop()

current_total = float(current_portfolio_taxable) + float(current_portfolio_tax_deferred)
ages          = proj_df["age"].tolist()
port_vals     = proj_df["portfolio_value"].tolist()

# ── Header ────────────────────────────────────────────────────────────────────

hcol, scol = st.columns([5, 1])
with hcol:
    st.markdown(
        '<div style="padding:0.15rem 0 1.3rem">'
        '<span class="app-title">FIRE Calculator</span>'
        '<span class="app-tagline">Financial Independence, Retire Early</span>'
        '</div>',
        unsafe_allow_html=True,
    )
with scol:
    if desired_retirement_age and fire_age:
        if fire_age <= int(desired_retirement_age):
            diff = int(desired_retirement_age) - fire_age
            pill = f'<span class="status-pill pill-green">On Track &nbsp;·&nbsp; {diff}y early</span>'
        else:
            diff = fire_age - int(desired_retirement_age)
            pill = f'<span class="status-pill pill-red">Behind &nbsp;·&nbsp; {diff}y late</span>'
    elif fire_age:
        pill = f'<span class="status-pill pill-blue">FIRE @ {fire_age}</span>'
    else:
        pill = '<span class="status-pill pill-red">FIRE not in range</span>'
    st.markdown(f'<div style="text-align:right;padding-top:0.35rem">{pill}</div>',
                unsafe_allow_html=True)

# ── Metrics ───────────────────────────────────────────────────────────────────

m1, m2, m3, m4 = st.columns(4)
with m1:
    if fire_age:
        delta = None
        if desired_retirement_age:
            diff = int(desired_retirement_age) - fire_age
            delta = f"{abs(diff)}y {'early' if diff >= 0 else 'late'}"
        st.metric("FIRE Age", str(fire_age), delta=delta)
    else:
        st.metric("FIRE Age", "Not Achieved")
with m2:
    st.metric("Years to FIRE", f"{years_to_fire:.1f}" if years_to_fire else "—")
with m3:
    st.metric("Target Portfolio", fmt(target_portfolio))
with m4:
    pct = min(current_total / target_portfolio * 100, 100) if target_portfolio else 0
    st.metric("Current Portfolio", fmt(current_total), delta=f"{pct:.0f}% of target")

# ── Progress bar ──────────────────────────────────────────────────────────────

pct_val = min(current_total / target_portfolio * 100, 100) if target_portfolio else 0
st.markdown(f"""
<div class="progress-wrap">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <span style="font-size:0.59rem;font-weight:700;color:{p['t3']};letter-spacing:0.11em;text-transform:uppercase">
      Progress to {fire_type_display} FIRE
    </span>
    <span style="font-size:0.8rem;font-weight:700;color:{p['t1']}">{pct_val:.1f}%</span>
  </div>
  <div class="progress-track">
    <div class="progress-fill" style="width:{pct_val:.2f}%"></div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:0.25rem">
    <span style="font-size:0.67rem;color:{p['t3']}">Current: {fmt(current_total)}</span>
    <span style="font-size:0.67rem;color:{p['t3']}">Target: {fmt(target_portfolio)}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── FIRE Target Cards ─────────────────────────────────────────────────────────

st.markdown('<span class="section-title">FIRE Targets</span>', unsafe_allow_html=True)
_target_meta = [
    ("lean",    "Lean FIRE",    "Frugal lifestyle"),
    ("regular", "Regular FIRE", "Comfortable lifestyle"),
    ("fat",     "Fat FIRE",     "Elevated lifestyle"),
]
tcols = st.columns(3)
for col, (ftype, fname, fdesc) in zip(tcols, _target_meta):
    with col:
        ftarget   = fire_targets[ftype]["target_portfolio"]
        fprogress = min(current_total / ftarget * 100, 100) if ftarget else 0
        sel       = "selected" if ftype == fire_type else ""
        bar_color = p["accent"] if ftype == fire_type else FC[ftype]
        achieved_rows = proj_df[proj_df["portfolio_value"] >= ftarget]
        age_label = f"Age {achieved_rows.iloc[0]['age']:.0f}" if not achieved_rows.empty else "Beyond range"
        st.markdown(f"""
        <div class="target-card {sel}">
          <div class="tc-label">{fname}</div>
          <div class="tc-amount">{fmt(ftarget)}</div>
          <div class="tc-sub">{fdesc}&nbsp;·&nbsp;${fire_targets[ftype]['annual_spending']:,.0f}/yr</div>
          <div class="tc-bar-track">
            <div style="width:{fprogress:.1f}%;height:100%;border-radius:100px;background:{bar_color}"></div>
          </div>
          <div style="display:flex;justify-content:space-between">
            <span style="font-size:0.66rem;color:{p['t3']}">{fprogress:.0f}% funded</span>
            <span style="font-size:0.66rem;color:{p['t3']}">{age_label}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────

tab_proj, tab_scen, tab_mc, tab_data = st.tabs([
    "Portfolio Projection", "Scenario Analysis", "Monte Carlo", "Yearly Data"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 · Portfolio Projection
# ══════════════════════════════════════════════════════════════════════════════

with tab_proj:

    st.markdown('<p class="chart-label">Projected Portfolio Growth</p>', unsafe_allow_html=True)
    fig_main = make_fig(p, height=460, right_margin=220, top_margin=20)

    cons_vals = cons_df["portfolio_value"].tolist()
    opt_vals  = opt_df["portfolio_value"].tolist()
    band_color = f"rgba({p['band_rgb']},0.08)"

    fig_main.add_trace(go.Scatter(
        x=ages + ages[::-1],
        y=opt_vals + cons_vals[::-1],
        fill="toself", fillcolor=band_color, line=dict(width=0),
        name="Conservative–Optimistic Range", hoverinfo="skip", showlegend=True,
    ))

    fig_main.add_trace(go.Scatter(
        x=ages, y=port_vals,
        mode="lines", name="Your Portfolio",
        line=dict(color=p["accent"], width=2.5),
        hovertemplate="Age %{x}<br>$%{y:,.0f}<extra></extra>",
    ))

    _fire_lines = [
        ("lean",    "Lean",    p["fire_lean"]),
        ("regular", "Regular", p["fire_regular"]),
        ("fat",     "Fat",     p["fire_fat"]),
    ]
    for ftype, fname, color in _fire_lines:
        ftarget = fire_targets[ftype]["target_portfolio"]
        is_sel  = ftype == fire_type
        suffix  = "← Selected" if is_sel else ""
        lbl     = f"{fname} FIRE  ·  {fmt(ftarget)}  ·  {suffix}"

        fig_main.add_hline(
            y=ftarget, line_dash="solid" if is_sel else "dash",
            line_color=color, line_width=2 if is_sel else 1,
        )
        fig_main.add_trace(go.Scatter(
            x=[None], y=[None], mode="lines", name=lbl,
            line=dict(color=color, width=2 if is_sel else 1, dash="solid" if is_sel else "dash"),
        ))
        fig_main.add_annotation(
            x=max(ages), y=ftarget, text=f"  {fname}",
            showarrow=False, xanchor="left",
            font=dict(color=color, size=9), xref="x", yref="y",
        )

    if fire_age is not None:
        fig_main.add_vline(
            x=fire_age, line_dash="dot",
            line_color=f"rgba({p['portfolio_rgb']},0.45)", line_width=1.5,
        )
        fig_main.add_vrect(
            x0=fire_age, x1=max(ages),
            fillcolor=f"rgba({p['portfolio_rgb']},0.025)", layer="below", line_width=0,
        )
        fig_main.add_annotation(
            x=fire_age, y=max(port_vals) * 0.97, text=f"FIRE @ {fire_age}",
            showarrow=False, font=dict(color=p["accent"], size=9),
            bgcolor=p["surface"], borderpad=3,
        )
        fire_row = proj_df[proj_df["age"] == fire_age]
        if not fire_row.empty:
            fig_main.add_trace(go.Scatter(
                x=[fire_age], y=[fire_row.iloc[0]["portfolio_value"]],
                mode="markers",
                marker=dict(color=p["accent"], size=11, symbol="star",
                            line=dict(color=p["surface"], width=1.5)),
                name="FIRE Achieved",
                hovertemplate=f"<b>FIRE @ {fire_age}</b><br>${fire_row.iloc[0]['portfolio_value']:,.0f}<extra></extra>",
                showlegend=False,
            ))

    fig_main.update_layout(
        xaxis_title="Age", yaxis_title="Portfolio Value",
        legend=dict(orientation="v", yanchor="top", y=0.99, xanchor="left", x=1.01),
        margin=dict(l=10, r=220, t=20, b=10),
    )
    st.plotly_chart(fig_main, use_container_width=True)

    st.markdown('<p class="chart-label" style="margin-top:1.5rem">Capital Invested vs Investment Gains</p>',
                unsafe_allow_html=True)

    running_invested = current_total
    invested_cumul, gains_cumul = [], []
    for row in projections:
        running_invested += row["annual_contribution"]
        invested_cumul.append(running_invested)
        gains_cumul.append(max(0.0, row["portfolio_value"] - running_invested))

    fig_cig = make_fig(p, height=280, right_margin=160, top_margin=10)
    fig_cig.add_trace(go.Scatter(
        x=ages, y=invested_cumul, stackgroup="one", name="Capital Invested",
        line=dict(width=0.5, color=FC["lean"]),
        fillcolor=f"rgba({p['invested_rgb']},0.30)",
        hovertemplate="Age %{x}<br>Invested: $%{y:,.0f}<extra></extra>",
    ))
    fig_cig.add_trace(go.Scatter(
        x=ages, y=gains_cumul, stackgroup="one", name="Investment Gains",
        line=dict(width=0.5, color=p["accent"]),
        fillcolor=f"rgba({p['gains_rgb']},0.30)",
        hovertemplate="Age %{x}<br>Gains: $%{y:,.0f}<extra></extra>",
    ))

    if invested_cumul and gains_cumul:
        final_invested = invested_cumul[-1]
        final_gains    = gains_cumul[-1]
        final_total    = final_invested + final_gains
        gains_pct      = (final_gains / final_total * 100) if final_total else 0
        fig_cig.add_annotation(
            x=ages[-1], y=final_total, text=f"  {gains_pct:.0f}% gains",
            showarrow=False, xanchor="left", font=dict(color=p["accent"], size=9),
        )

    if fire_age:
        fig_cig.add_vline(
            x=fire_age, line_dash="dot",
            line_color=f"rgba({p['portfolio_rgb']},0.35)", line_width=1,
        )

    fig_cig.update_layout(
        xaxis_title="Age", yaxis_title="Cumulative Value",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=10, r=160, t=10, b=10),
    )
    st.plotly_chart(fig_cig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 · Scenario Analysis
# ══════════════════════════════════════════════════════════════════════════════

with tab_scen:
    st.markdown('<p class="scenario-hint">Model alternative paths and see how they shift your FIRE timeline.</p>',
                unsafe_allow_html=True)
    scenario_type = st.radio(
        "Scenario", ["No Contributions", "Part-Time Work", "Barista FIRE"],
        horizontal=True, label_visibility="collapsed",
    )
    st.markdown(f'<hr style="border-color:{p["border"]};margin:0.6rem 0 1.1rem">', unsafe_allow_html=True)

    def scenario_comparison_chart(df_base, df_alt, color_base, color_alt,
                                  label_base, label_alt, period_start=None, period_end=None,
                                  period_color_rgb="59,130,246", period_label=""):
        fig_s = make_fig(p, height=400, right_margin=160, top_margin=20)
        fig_s.add_trace(go.Scatter(
            x=df_base["age"], y=df_base["portfolio_value"],
            mode="lines", name=label_base, line=dict(color=color_base, width=2),
            hovertemplate="Age %{x}<br>$%{y:,.0f}<extra></extra>",
        ))
        fig_s.add_trace(go.Scatter(
            x=df_alt["age"], y=df_alt["portfolio_value"],
            mode="lines", name=label_alt, line=dict(color=color_alt, width=2.5),
            fill="tozeroy", fillcolor=f"rgba({period_color_rgb},0.05)",
            hovertemplate="Age %{x}<br>$%{y:,.0f}<extra></extra>",
        ))

        if period_start and period_end:
            fig_s.add_vrect(
                x0=period_start, x1=period_end,
                fillcolor=f"rgba({period_color_rgb},0.07)", layer="below", line_width=0,
            )
            fig_s.add_annotation(
                x=(period_start + period_end) / 2,
                y=max(df_alt["portfolio_value"]) * 0.96,
                text=period_label, showarrow=False,
                font=dict(color=f"rgba({period_color_rgb},0.8)", size=9),
            )

        fig_s.add_hline(
            y=target_portfolio, line_dash="dot",
            line_color=f"rgba({p['portfolio_rgb']},0.35)", line_width=1,
        )
        fig_s.add_annotation(
            x=max(df_alt["age"]), y=target_portfolio,
            text=f"  Target: {fmt(target_portfolio)}",
            showarrow=False, xanchor="left",
            font=dict(color=p["accent"], size=9),
        )

        fire_ages = {}
        for df_s, color, lbl in [(df_base, color_base, label_base), (df_alt, color_alt, label_alt)]:
            a_rows = df_s[df_s["fire_achieved"] == True]
            if not a_rows.empty:
                fa = a_rows.iloc[0]["age"]
                fire_ages[lbl] = fa
                fv = a_rows.iloc[0]["portfolio_value"]
                fig_s.add_trace(go.Scatter(
                    x=[fa], y=[fv], mode="markers",
                    marker=dict(color=color, size=11, symbol="star",
                                line=dict(color=p["surface"], width=1.5)),
                    name=f"FIRE @ {fa:.0f} ({lbl})",
                    hovertemplate=f"<b>FIRE @ {fa:.0f}</b><br>${fv:,.0f}<extra></extra>",
                ))
                fig_s.add_vline(
                    x=fa, line_dash="dot", line_color=f"{color}55", line_width=1,
                )

        fig_s.update_layout(xaxis_title="Age", yaxis_title="Portfolio Value")
        return fig_s, fire_ages

    if scenario_type == "No Contributions":
        st.markdown('<p class="scenario-hint">What happens if you stop contributing today?</p>',
                    unsafe_allow_html=True)
        if st.button("Run Scenario", key="btn_nc", type="primary"):
            nc = calc.generate_no_contribution_projections(int(life_expectancy) - int(current_age))
            st.session_state["scen_nc"] = nc

        if "scen_nc" in st.session_state:
            nc_df = pd.DataFrame(st.session_state["scen_nc"])
            fig_s, fa = scenario_comparison_chart(
                proj_df, nc_df, p["accent"], p["fire_regular"],
                "With Contributions", "No Contributions",
                period_color_rgb=p["fire_regular"].lstrip("#"),
            )
            st.plotly_chart(fig_s, use_container_width=True)
            if fa.get("With Contributions") and fa.get("No Contributions"):
                diff_nc = fa["No Contributions"] - fa["With Contributions"]
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("With Contributions — FIRE Age", str(fa["With Contributions"]))
                with c2:
                    st.metric("No Contributions — FIRE Age", str(fa["No Contributions"]),
                              delta=f"{diff_nc:+.0f} years", delta_color="inverse")

    elif scenario_type == "Part-Time Work":
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            pt_start = st.number_input("Start age", min_value=int(current_age), max_value=100,
                                       value=int(current_age) + 10, key="pt_start")
        with c2:
            pt_end = st.number_input("End age", min_value=int(current_age), max_value=100,
                                     value=int(current_age) + 17, key="pt_end")
        with c3:
            pt_inc = st.number_input("Annual income ($)", min_value=0, value=30000,
                                     step=5000, key="pt_inc")
        with c4:
            pt_spend = st.number_input("Annual spending ($)", min_value=0,
                                       value=int(expected_annual_spending * 0.8),
                                       step=5000, key="pt_spend")
        if st.button("Run Scenario", key="btn_pt", type="primary"):
            pt = calc.generate_part_time_projections(
                pt_spend, pt_inc, pt_start, pt_end, int(life_expectancy) - int(current_age))
            st.session_state["scen_pt"] = {"data": pt, "start": pt_start, "end": pt_end}

        if "scen_pt" in st.session_state:
            pt_df = pd.DataFrame(st.session_state["scen_pt"]["data"])
            pts, pte = st.session_state["scen_pt"]["start"], st.session_state["scen_pt"]["end"]
            rgb_pt = p["fire_lean"].lstrip("#")
            fig_pt, fa_pt = scenario_comparison_chart(
                proj_df, pt_df, p["fire_lean"], p["accent"],
                "Current Plan", "Part-Time Plan", pts, pte, rgb_pt, "Part-Time Period",
            )
            st.plotly_chart(fig_pt, use_container_width=True)
            if fa_pt.get("Current Plan") and fa_pt.get("Part-Time Plan"):
                diff_pt = fa_pt["Part-Time Plan"] - fa_pt["Current Plan"]
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Current Plan — FIRE Age", str(fa_pt["Current Plan"]))
                with c2:
                    st.metric("Part-Time Plan — FIRE Age", str(fa_pt["Part-Time Plan"]),
                              delta=f"{diff_pt:+.0f} years",
                              delta_color="normal" if diff_pt < 0 else "inverse")

    elif scenario_type == "Barista FIRE":
        st.markdown('<p class="scenario-hint">Work a lower-stress job with healthcare benefits while your portfolio compounds to full FIRE.</p>',
                    unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            bar_start = st.number_input("Start age", min_value=int(current_age), max_value=100,
                                        value=int(current_age) + 8, key="bar_start")
        with c2:
            bar_end = st.number_input("Healthcare ends", min_value=int(current_age), max_value=100,
                                      value=65, key="bar_end")
        with c3:
            bar_inc = st.number_input("Annual income ($)", min_value=0, value=25000,
                                      step=5000, key="bar_inc")
        with c4:
            bar_spend = st.number_input("Annual spending ($)", min_value=0,
                                        value=int(expected_annual_spending * 0.85),
                                        step=5000, key="bar_spend")
        if st.button("Run Scenario", key="btn_bar", type="primary"):
            bar = calc.generate_part_time_projections(
                bar_spend, bar_inc, bar_start, bar_end, int(life_expectancy) - int(current_age))
            st.session_state["scen_bar"] = {"data": bar, "start": bar_start, "end": bar_end}

        if "scen_bar" in st.session_state:
            bar_df = pd.DataFrame(st.session_state["scen_bar"]["data"])
            bs, be = st.session_state["scen_bar"]["start"], st.session_state["scen_bar"]["end"]
            rgb_bar = p["fire_fat"].lstrip("#")
            fig_bar, fa_bar = scenario_comparison_chart(
                proj_df, bar_df, p["fire_lean"], p["fire_fat"],
                "Current Plan", "Barista FIRE Plan", bs, be, rgb_bar, "Barista Period",
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            if fa_bar.get("Current Plan") and fa_bar.get("Barista FIRE Plan"):
                diff_bar = fa_bar["Barista FIRE Plan"] - fa_bar["Current Plan"]
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Current Plan — FIRE Age", str(fa_bar["Current Plan"]))
                with c2:
                    st.metric("Barista FIRE — FIRE Age", str(fa_bar["Barista FIRE Plan"]),
                              delta=f"{diff_bar:+.0f} years",
                              delta_color="normal" if diff_bar < 0 else "inverse")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 · Monte Carlo
# ══════════════════════════════════════════════════════════════════════════════

with tab_mc:
    st.markdown('<p class="scenario-hint">Simulate thousands of market scenarios using randomised annual returns to stress-test your plan.</p>',
                unsafe_allow_html=True)
    mc1, mc2 = st.columns(2)
    with mc1:
        num_sims = st.number_input("Simulations", min_value=100, max_value=10000,
                                   value=1000, step=100)
    with mc2:
        sim_years = st.number_input("Years to simulate", min_value=5, max_value=50,
                                    value=min(30, int(life_expectancy) - int(current_age)))

    if st.button("Run Monte Carlo", type="primary"):
        with st.spinner("Running simulations…"):
            mc_res = calc.run_monte_carlo_simulation(int(num_sims), int(sim_years))
        st.session_state["mc_res"] = mc_res

    if "mc_res" in st.session_state:
        mc = st.session_state["mc_res"]
        if "error" in mc:
            st.error(mc["error"])
        else:
            r1, r2, r3, r4 = st.columns(4)
            with r1:
                sr = mc["success_rate"]
                sr_color = p["accent"] if sr >= 80 else (p["fire_regular"] if sr >= 60 else p["red"])
                st.markdown(f"""
                <div style="background:{p['surface']};border:1px solid {p['border']};border-radius:12px;
                     padding:1.1rem 1.3rem;border-left:3px solid {sr_color}">
                  <div style="font-size:0.63rem;font-weight:700;color:{p['t3']};letter-spacing:0.11em;text-transform:uppercase">
                    Success Rate
                  </div>
                  <div style="font-size:1.9rem;font-weight:700;color:{sr_color};letter-spacing:-0.03em;margin-top:0.2rem">
                    {sr:.1f}%
                  </div>
                  <div style="font-size:0.68rem;color:{p['t3']};margin-top:0.1rem">
                    portfolios beat target
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with r2:
                st.metric("Median Outcome", fmt(mc["final_values"]["median"]))
            with r3:
                st.metric("Mean Outcome", fmt(mc["final_values"]["mean"]))
            with r4:
                st.metric("Target Portfolio", fmt(mc["target_portfolio"]))

            st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
            st.markdown('<p class="chart-label">Outcome Distribution Over Time</p>', unsafe_allow_html=True)
            yrs = list(range(mc["years"] + 1))
            fig_mc = make_fig(p, height=380, right_margin=140, top_margin=15)

            fig_mc.add_trace(go.Scatter(
                x=yrs + yrs[::-1],
                y=mc["percentiles"]["p90"] + mc["percentiles"]["p10"][::-1],
                fill="toself", fillcolor=f"rgba({p['invested_rgb']},0.08)",
                line=dict(width=0), name="10th – 90th Pct", hoverinfo="skip",
            ))
            fig_mc.add_trace(go.Scatter(
                x=yrs + yrs[::-1],
                y=mc["percentiles"]["p75"] + mc["percentiles"]["p25"][::-1],
                fill="toself", fillcolor=f"rgba({p['invested_rgb']},0.18)",
                line=dict(width=0), name="25th – 75th Pct", hoverinfo="skip",
            ))
            for pct_key, pct_label, alpha in [
                ("p90", "90th Pct", "0.55"), ("p75", "75th Pct", "0.7"),
                ("p50", "Median", "1.0"), ("p25", "25th Pct", "0.7"), ("p10", "10th Pct", "0.55"),
            ]:
                is_median = pct_key == "p50"
                fig_mc.add_trace(go.Scatter(
                    x=yrs, y=mc["percentiles"][pct_key], mode="lines", name=pct_label,
                    line=dict(
                        color=f"rgba({p['invested_rgb']},{alpha})" if not is_median else p["fire_lean"],
                        width=2.5 if is_median else 1,
                        dash="solid" if is_median else "dot",
                    ),
                    hovertemplate=f"{pct_label}: $%{{y:,.0f}}<extra></extra>",
                ))

            fig_mc.add_hline(
                y=mc["target_portfolio"], line_dash="dot",
                line_color=f"rgba({p['portfolio_rgb']},0.6)", line_width=1.5,
            )
            fig_mc.add_annotation(
                x=mc["years"], y=mc["target_portfolio"],
                text=f"  Target: {fmt(mc['target_portfolio'])}",
                showarrow=False, xanchor="left", font=dict(color=p["accent"], size=9),
            )
            fig_mc.update_layout(xaxis_title="Years from Now", yaxis_title="Portfolio Value")
            st.plotly_chart(fig_mc, use_container_width=True)

            st.markdown('<p class="chart-label" style="margin-top:1.2rem">Final Portfolio Value by Percentile</p>',
                        unsafe_allow_html=True)
            pct_labels = ["P10", "P25", "P50", "P75", "P90"]
            pct_finals = [
                mc["percentiles"]["p10"][-1], mc["percentiles"]["p25"][-1],
                mc["percentiles"]["p50"][-1], mc["percentiles"]["p75"][-1],
                mc["percentiles"]["p90"][-1],
            ]
            bar_colors = [p["accent"] if v >= mc["target_portfolio"] else p["red"] for v in pct_finals]
            fig_bar_mc = make_fig(p, height=240, right_margin=20, top_margin=10)
            fig_bar_mc.add_trace(go.Bar(
                x=pct_labels, y=pct_finals, marker_color=bar_colors,
                text=[fmt(v) for v in pct_finals], textposition="outside",
                textfont=dict(color=p["t2"], size=10),
                hovertemplate="%{x}: $%{y:,.0f}<extra></extra>",
                name="Final Value", showlegend=False,
            ))
            fig_bar_mc.add_hline(
                y=mc["target_portfolio"], line_dash="dot",
                line_color=f"rgba({p['portfolio_rgb']},0.6)", line_width=1.5,
            )
            fig_bar_mc.update_layout(
                yaxis_title="Final Portfolio Value", bargap=0.35,
                margin=dict(l=10, r=20, t=10, b=10),
            )
            st.plotly_chart(fig_bar_mc, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 · Yearly Data
# ══════════════════════════════════════════════════════════════════════════════

with tab_data:
    disp = proj_df[[
        "age", "portfolio_value", "target_portfolio",
        "inflation_adjusted_spending", "annual_contribution",
        "sustainable_withdrawal", "surplus_deficit", "fire_achieved",
    ]].copy()
    disp.columns = ["Age", "Portfolio", "Target", "Spending",
                    "Contribution", "Max Withdrawal", "Surplus/Deficit", "FIRE"]
    for col in ["Portfolio", "Target", "Spending", "Contribution",
                "Max Withdrawal", "Surplus/Deficit"]:
        disp[col] = disp[col].apply(lambda x: f"${x:,.0f}")
    disp["FIRE"] = disp["FIRE"].apply(lambda x: "✓" if x else "")
    st.dataframe(disp, use_container_width=True, hide_index=True)

# ── Feedback ──────────────────────────────────────────────────────────────────

st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)
st.markdown(f'<hr style="border-color:{p["border"]}">', unsafe_allow_html=True)

def _bot_check():
    if "bot_q" not in st.session_state:
        import random
        a, b = random.randint(1, 10), random.randint(1, 10)
        st.session_state["bot_q"] = f"{a} + {b}"
        st.session_state["bot_a"] = a + b
    return st.session_state["bot_q"], st.session_state["bot_a"]

def _submit_feedback(text, ftype, email=None):
    data = {"timestamp": datetime.now().isoformat(), "type": ftype,
            "feedback": text, "email": email or "anonymous", "app": "FIRE Calculator"}
    url = st.secrets.get("FEEDBACK_WEBHOOK_URL", "")
    if url:
        try:
            r = requests.get(url, params=data, timeout=10)
            return r.status_code == 200, "Feedback submitted — thank you!"
        except Exception as e:
            return False, str(e)
    if "fb_log" not in st.session_state:
        st.session_state["fb_log"] = []
    st.session_state["fb_log"].append(data)
    return True, "Received (dev mode)"

with st.expander("Share Feedback"):
    fb_type = st.selectbox("Type", ["Feature Request", "Bug Report", "General", "UI/UX"])
    fb_text = st.text_area("Feedback", placeholder="What could be better?", height=90)
    fb_email = st.text_input("Email (optional)", placeholder="you@example.com")
    q, ans = _bot_check()
    fb_check = st.number_input(f"Quick check: {q} =", min_value=0, max_value=100, value=0)
    if st.button("Submit", type="primary"):
        if not fb_text.strip():
            st.error("Please enter some feedback.")
        elif fb_check != ans:
            st.error("Incorrect answer — try again.")
        else:
            ok, msg = _submit_feedback(fb_text, fb_type, fb_email)
            if ok:
                st.success(msg)
                del st.session_state["bot_q"], st.session_state["bot_a"]
                st.rerun()
            else:
                st.error(msg)
