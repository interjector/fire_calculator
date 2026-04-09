import streamlit as st


def _nav_css(p, dark):
    return f"""<style>
.nav-brand {{
    font-size: 1.05rem; font-weight: 800; letter-spacing: -0.04em;
    margin: 0; padding-top: 0.25rem; display: flex; align-items: center; gap: 0.35rem;
}}
.nav-brand .nb-fire {{ color: {p['accent']}; }}
.nav-brand .nb-path {{ color: {p['t1']}; }}

[data-testid="stPageLink"] {{ margin: 0 !important; padding: 0 !important; }}
[data-testid="stPageLink"] p {{
    font-size: 0.83rem !important; font-weight: 500 !important;
    color: {p['t2']} !important; text-align: center;
    padding: 0.32rem 0.6rem; border-radius: 6px; transition: all 0.15s; margin: 0;
}}
[data-testid="stPageLink"] p:hover {{
    color: {p['t1']} !important; background: {p['surface2']} !important;
}}

.nav-rule {{ border: none; border-top: 1px solid {p['border']}; margin: 0.45rem 0 1.8rem 0; }}

.nav-theme-btn .stButton > button {{
    background: {p['surface2']} !important; border: 1px solid {p['border2']} !important;
    color: {p['t2']} !important; border-radius: 8px !important;
    font-size: 0.72rem !important; font-weight: 600 !important;
    padding: 0.28rem 0.6rem !important; width: 100% !important;
    transition: all 0.15s !important;
}}
.nav-theme-btn .stButton > button:hover {{
    border-color: {p['accent']} !important; color: {p['accent']} !important;
}}
</style>"""


def render_nav(p, is_dark):
    st.markdown(_nav_css(p, is_dark), unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6 = st.columns([3, 0.85, 1.15, 0.8, 0.75, 1.1])
    with c1:
        st.markdown(
            '<p class="nav-brand">'
            '🔥 <span class="nb-fire">Ember</span>'
            '</p>',
            unsafe_allow_html=True,
        )
    with c2:
        st.page_link("streamlit_app.py", label="Home")
    with c3:
        st.page_link("pages/1_Calculator.py", label="Calculator")
    with c4:
        st.page_link("pages/2_Learn.py", label="Learn")
    with c5:
        st.page_link("pages/3_Blog.py", label="Blog")
    with c6:
        icon = "☀️  Light" if is_dark else "🌙  Dark"
        st.markdown('<div class="nav-theme-btn">', unsafe_allow_html=True)
        if st.button(icon, key="theme_nav", use_container_width=True):
            st.session_state["theme"] = "light" if is_dark else "dark"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="nav-rule">', unsafe_allow_html=True)
