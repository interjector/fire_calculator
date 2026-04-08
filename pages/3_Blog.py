import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from components.theme import get_palette, inject_base_css
from components.nav import render_nav

st.set_page_config(
    page_title="Blog — FIREpath",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

p, is_dark = get_palette()
inject_base_css(p, is_dark, hide_sidebar=True)

st.markdown(f"""
<style>
/* ── Blog layout ───────────────────────────────────────── */
.blog-hero {{
    padding: 2rem 0 2.5rem;
    border-bottom: 1px solid {p['border']};
    margin-bottom: 2.5rem;
}}
.blog-hero h1 {{
    font-size: 2.4rem; font-weight: 800; color: {p['t1']};
    letter-spacing: -0.05em; margin: 0 0 0.6rem;
}}
.blog-hero p {{
    font-size: 1rem; color: {p['t2']}; max-width: 560px; line-height: 1.65; margin: 0;
}}

/* ── Post cards ────────────────────────────────────────── */
.post-card {{
    background: {p['surface']}; border: 1px solid {p['border']};
    border-radius: 16px; padding: 1.8rem;
    transition: border-color 0.2s, box-shadow 0.2s;
    cursor: pointer; height: 100%;
}}
.post-card:hover {{
    border-color: {p['border2']};
    box-shadow: 0 6px 30px rgba(0,0,0,0.08);
}}
.pc-tag {{
    display: inline-block; background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.2); color: {p['accent']};
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
    padding: 0.2rem 0.65rem; border-radius: 100px; margin-bottom: 0.8rem;
}}
.pc-title {{
    font-size: 1.15rem; font-weight: 700; color: {p['t1']};
    letter-spacing: -0.02em; line-height: 1.3; margin-bottom: 0.55rem;
}}
.pc-desc {{ font-size: 0.85rem; color: {p['t2']}; line-height: 1.65; margin-bottom: 1.2rem; }}
.pc-meta {{
    display: flex; gap: 0.8rem; align-items: center;
    font-size: 0.72rem; color: {p['t3']};
}}
.pc-meta-dot {{ color: {p['border2']}; }}

/* ── Article view ──────────────────────────────────────── */
.article-back {{
    display: inline-flex; align-items: center; gap: 0.4rem;
    font-size: 0.8rem; font-weight: 500; color: {p['t3']};
    margin-bottom: 1.5rem; cursor: pointer; transition: color 0.15s;
}}
.article-back:hover {{ color: {p['t1']}; }}

.article-header {{ margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid {p['border']}; }}
.article-tag {{
    display: inline-block; background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.2); color: {p['accent']};
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
    padding: 0.2rem 0.65rem; border-radius: 100px; margin-bottom: 0.9rem;
}}
.article-title {{
    font-size: 2rem; font-weight: 800; color: {p['t1']};
    letter-spacing: -0.04em; line-height: 1.15; margin-bottom: 0.7rem;
}}
.article-desc {{
    font-size: 1rem; color: {p['t2']}; line-height: 1.65;
    max-width: 680px; margin-bottom: 1rem;
}}
.article-meta {{
    display: flex; gap: 1rem; font-size: 0.75rem; color: {p['t3']};
}}

/* ── Article body markdown overrides ──────────────────── */
.article-body {{ max-width: 740px; }}
.article-body h2 {{
    font-size: 1.35rem !important; font-weight: 700 !important;
    color: {p['t1']} !important; letter-spacing: -0.025em !important;
    margin-top: 2rem !important; margin-bottom: 0.5rem !important;
    padding-top: 1.5rem; border-top: 1px solid {p['border']};
}}
.article-body h2:first-of-type {{ border-top: none; padding-top: 0; margin-top: 0 !important; }}
.article-body p {{
    font-size: 0.93rem !important; color: {p['t2']} !important; line-height: 1.75 !important;
    margin-bottom: 0.9rem !important;
}}
.article-body strong {{ color: {p['t1']} !important; font-weight: 600 !important; }}
.article-body ul, .article-body ol {{
    padding-left: 1.4rem; margin-bottom: 0.9rem;
}}
.article-body li {{
    font-size: 0.93rem !important; color: {p['t2']} !important;
    line-height: 1.7 !important; margin-bottom: 0.3rem;
}}
.article-body blockquote {{
    border-left: 3px solid {p['accent']}; padding: 0.5rem 0 0.5rem 1.2rem;
    margin: 1rem 0; background: {p['surface2']}; border-radius: 0 8px 8px 0;
}}
.article-body blockquote p {{
    font-size: 0.95rem !important; font-style: italic;
    color: {p['t1']} !important; margin: 0 !important;
}}
.article-body table {{
    width: 100%; border-collapse: collapse; margin: 1rem 0;
    font-size: 0.85rem;
}}
.article-body th {{
    text-align: left; padding: 0.6rem 0.9rem;
    font-size: 0.65rem; font-weight: 700; color: {p['t3']};
    letter-spacing: 0.08em; text-transform: uppercase;
    border-bottom: 1px solid {p['border']};
    background: {p['surface2']};
}}
.article-body td {{
    padding: 0.65rem 0.9rem; color: {p['t2']} !important;
    border-bottom: 1px solid {p['border']};
}}
.article-body tr:last-child td {{ border-bottom: none; }}
.article-body hr {{
    border: none !important; border-top: 1px solid {p['border']} !important;
    margin: 1.8rem 0 !important;
}}
.article-body code {{
    background: {p['surface2']}; border: 1px solid {p['border2']};
    border-radius: 4px; padding: 0.1rem 0.4rem;
    font-size: 0.83rem; color: {p['accent']};
}}
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

POSTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "content", "posts")

def parse_frontmatter(text):
    """Parse YAML-style frontmatter from a markdown file."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip()
    return meta, parts[2].strip()

def load_posts():
    posts = []
    if not os.path.isdir(POSTS_DIR):
        return posts
    for fname in sorted(os.listdir(POSTS_DIR)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(POSTS_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            raw = f.read()
        meta, body = parse_frontmatter(raw)
        posts.append({
            "slug": meta.get("slug", fname.replace(".md", "")),
            "title": meta.get("title", fname.replace(".md", "").replace("-", " ").title()),
            "date": meta.get("date", ""),
            "read_time": meta.get("read_time", ""),
            "description": meta.get("description", ""),
            "tags": [t.strip() for t in meta.get("tags", "").split(",") if t.strip()],
            "body": body,
        })
    return posts

# ── Load posts ────────────────────────────────────────────────────────────────

all_posts = load_posts()
post_map  = {post["slug"]: post for post in all_posts}

# ── Session state ─────────────────────────────────────────────────────────────

if "blog_post" not in st.session_state:
    st.session_state["blog_post"] = None

# ── Navbar ────────────────────────────────────────────────────────────────────

render_nav(p, is_dark)

# ══════════════════════════════════════════════════════════════════════════════
# ARTICLE VIEW
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state["blog_post"] and st.session_state["blog_post"] in post_map:
    post = post_map[st.session_state["blog_post"]]

    if st.button("← Back to all posts", key="back_btn"):
        st.session_state["blog_post"] = None
        st.rerun()

    # Article header
    tag_display = post["tags"][0].replace("-", " ").title() if post["tags"] else "Article"
    st.markdown(f"""
<div class="article-header">
    <span class="article-tag">{tag_display}</span>
    <div class="article-title">{post['title']}</div>
    <p class="article-desc">{post['description']}</p>
    <div class="article-meta">
        <span>{post['date']}</span>
        <span>·</span>
        <span>{post['read_time']}</span>
    </div>
</div>
""", unsafe_allow_html=True)

    # Article body
    _, content_col, _ = st.columns([0.05, 11, 1])
    with content_col:
        st.markdown('<div class="article-body">', unsafe_allow_html=True)
        st.markdown(post["body"])
        st.markdown("</div>", unsafe_allow_html=True)

    # End-of-article nav
    st.markdown(f'<hr style="border-color:{p["border"]};margin:2.5rem 0 1.5rem">', unsafe_allow_html=True)

    # Next post suggestion
    slugs = [p_["slug"] for p_ in all_posts]
    cur_idx = slugs.index(post["slug"]) if post["slug"] in slugs else -1
    next_post = all_posts[cur_idx + 1] if cur_idx >= 0 and cur_idx + 1 < len(all_posts) else None

    nav_l, nav_r = st.columns(2)
    with nav_l:
        if st.button("← Back to all posts", key="back_btn2"):
            st.session_state["blog_post"] = None
            st.rerun()
    with nav_r:
        if next_post:
            if st.button(f"Next: {next_post['title']} →", key="next_post_btn", use_container_width=True):
                st.session_state["blog_post"] = next_post["slug"]
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# POST LIST VIEW
# ══════════════════════════════════════════════════════════════════════════════

else:
    st.markdown(f"""
<div class="blog-hero">
    <h1>✍️ Blog</h1>
    <p>In-depth articles on FIRE strategy, withdrawal rules, tax planning,
       and the lifestyle design behind financial independence.</p>
</div>
""", unsafe_allow_html=True)

    if not all_posts:
        st.info("No posts found. Add markdown files to `content/posts/`.")
    else:
        # Render posts in a grid (2 columns for wider screens, 1 for first if odd)
        for i in range(0, len(all_posts), 2):
            batch = all_posts[i:i+2]
            cols = st.columns(len(batch), gap="medium")
            for col, post in zip(cols, batch):
                with col:
                    tag_display = post["tags"][0].replace("-", " ").title() if post["tags"] else "Article"
                    st.markdown(f"""
<div class="post-card">
    <span class="pc-tag">{tag_display}</span>
    <div class="pc-title">{post['title']}</div>
    <p class="pc-desc">{post['description']}</p>
    <div class="pc-meta">
        <span>{post['date']}</span>
        <span class="pc-meta-dot">·</span>
        <span>{post['read_time']}</span>
    </div>
</div>
""", unsafe_allow_html=True)
                    if st.button("Read article →", key=f"read_{post['slug']}", use_container_width=True):
                        st.session_state["blog_post"] = post["slug"]
                        st.rerun()

    # Divider + learn CTA
    st.markdown(f'<div style="height:2rem"></div>', unsafe_allow_html=True)
    st.markdown(f"""
<div style="background:{p['surface']};border:1px solid {p['border']};border-radius:16px;
            padding:1.8rem;text-align:center">
    <div style="font-size:1.1rem;font-weight:700;color:{p['t1']};margin-bottom:0.4rem">
        Want the short version?
    </div>
    <div style="font-size:0.88rem;color:{p['t2']};margin-bottom:1rem">
        The Learn section has structured concept cards and reference tables — faster to scan
        than a full article.
    </div>
</div>
""", unsafe_allow_html=True)
    st.markdown('<div style="height:0.4rem"></div>', unsafe_allow_html=True)
    _, learn_col, _ = st.columns([2, 2, 2])
    with learn_col:
        if st.button("📚  Go to Learn →", use_container_width=True):
            st.switch_page("pages/2_Learn.py")
