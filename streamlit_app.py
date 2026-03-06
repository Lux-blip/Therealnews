import streamlit as st
import feedparser
from datetime import datetime, timedelta
import random
import time

st.set_page_config(page_title="THEREALNEWS with Lawrence", page_icon="📰", layout="wide")

# ────────────────────────────────────────────────
#  Persistent settings
# ────────────────────────────────────────────────
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True
if 'font_size' not in st.session_state:
    st.session_state.font_size = "Medium"
if 'read_stories' not in st.session_state:
    st.session_state.read_stories = set()
if 'saved_stories' not in st.session_state:
    st.session_state.saved_stories = []
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'favorite_sources' not in st.session_state:
    st.session_state.favorite_sources = set()

# ────────────────────────────────────────────────
#  Dark mode & font size styling
# ────────────────────────────────────────────────
font_sizes = {
    "Small": {"title": "1.2rem", "meta": "0.85rem", "summary": "0.92rem"},
    "Medium": {"title": "1.42rem", "meta": "0.96rem", "summary": "0.98rem"},
    "Large": {"title": "1.6rem", "meta": "1.05rem", "summary": "1.08rem"}
}
fs = font_sizes[st.session_state.font_size]

if st.session_state.dark_mode:
    st.markdown(f"""
        <style>
            [data-testid="stAppViewContainer"] {{ background-color: #0e1117 !important; }}
            section[data-testid="stSidebar"] {{ background-color: #161b22 !important; }}
            .stApp {{ background-color: #0e1117 !important; color: #e0e0ff !important; }}
            .card {{ background: #161b22; border: 1px solid #30363d; color: white; }}
            .gradient-overlay {{ background: linear-gradient(to top, rgba(0,0,0,0.92) 0%, rgba(0,0,0,0.65) 40%, transparent 100%) !important; }}
            .card-title {{ font-size: {fs['title']}; }}
            .card-meta {{ font-size: {fs['meta']}; color: #ccc; }}
            .summary {{ font-size: {fs['summary']}; color: #ddd; }}
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <style>
            .card {{ background: white; border: 1px solid #d0d0d0; }}
            .gradient-overlay {{ background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.4) 100%) !important; }}
            .card-title {{ font-size: {fs['title']}; }}
            .card-meta {{ font-size: {fs['meta']}; }}
            .summary {{ font-size: {fs['summary']}; }}
        </style>
    """, unsafe_allow_html=True)

# ────────────────────────────────────────────────
#  Header & controls
# ────────────────────────────────────────────────
st.markdown('<div style="font-size:3.5rem; font-weight:bold; text-align:center; color:#ff4d4d;">THEREALNEWS</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; font-size:1.45rem; color:#aaa; margin-top:-12px;">with Lawrence</div>', unsafe_allow_html=True)

# Sidebar QoL controls
with st.sidebar:
    st.header("Controls")
    st.session_state.dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode)
    st.session_state.font_size = st.selectbox("Font Size", ["Small", "Medium", "Large"], index=["Small","Medium","Large"].index(st.session_state.font_size))
    st.session_state.auto_refresh = st.checkbox("Auto-refresh every 5 min", value=st.session_state.auto_refresh)
    st.session_state.favorite_sources = set(st.multiselect("Favorite Sources", list(RSS_FEEDS.keys()), default=list(st.session_state.favorite_sources)))

    st.subheader("Saved Stories")
    for saved in st.session_state.saved_stories[:5]:
        st.markdown(f"- [{saved['title'][:60]}...]({saved['link']})")
    if st.button("Clear Saved"):
        st.session_state.saved_stories = []

    st.subheader("Search History")
    for past in st.session_state.search_history[-5:]:
        if st.button(past[:30] + "..." if len(past)>30 else past, key=f"hist_{past}"):
            st.session_state.search_term = past
            st.rerun()

    st.caption("THEREALNEWS with Lawrence • Conservative feed")

# ────────────────────────────────────────────────
#  RSS & fetch (same as before – abbreviated)
# ────────────────────────────────────────────────
RSS_FEEDS = { ... }  # ← paste your full RSS_FEEDS dict here from previous versions

@st.cache_data(ttl=600)
def fetch_all_news():
    # ← paste your full fetch_all_news function here (the safe one with try/except)
    # make sure it returns list of dicts with 'title', 'link', 'summary', 'image', 'source', 'published', 'pub_dt', 'score'
    pass

news = fetch_all_news()

# ────────────────────────────────────────────────
#  Filter by favorites, read, mode, search
# ────────────────────────────────────────────────
if st.session_state.favorite_sources:
    news = [a for a in news if a['source'] in st.session_state.favorite_sources]

news = [a for a in news if a['link'] not in st.session_state.read_stories]

search_term = st.text_input("Search headlines")
if search_term and search_term not in st.session_state.search_history:
    st.session_state.search_history.append(search_term)
    if len(st.session_state.search_history) > 10:
        st.session_state.search_history = st.session_state.search_history[-10:]

if search_term:
    news = [a for a in news if search_term.lower() in (a['title'] + a['summary']).lower()]

mode = st.selectbox("Section", ["All", "War", "Politics", "Economics"])
# ... (add mode keyword filtering as before)

# ────────────────────────────────────────────────
#  Cards with mark read, save, share
# ────────────────────────────────────────────────
for item in news[:12]:  # or implement load more
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        # image + gradient overlay as before
        # ...
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if st.button("Mark Read", key=f"read_{item['link']}"):
                st.session_state.read_stories.add(item['link'])
                st.rerun()
        with col2:
            if st.button("Save", key=f"save_{item['link']}"):
                if item not in st.session_state.saved_stories:
                    st.session_state.saved_stories.append(item)
                st.toast("Saved!")
        with col3:
            if st.button("Share", key=f"share_{item['link']}"):
                st.write(f"Link copied: {item['link']}")
                st.toast("Link copied to clipboard!")

# ────────────────────────────────────────────────
#  Auto-refresh logic
# ────────────────────────────────────────────────
if st.session_state.auto_refresh:
    time.sleep(300)  # 5 min
    st.rerun()

# ────────────────────────────────────────────────
#  Random quote sidebar
# ────────────────────────────────────────────────
quotes = [
    "The only thing we have to fear is fear itself. — FDR (but we prefer Reagan)",
    "Government is not the solution to our problem; government is the problem. — Ronald Reagan",
    "Make America Great Again. — Donald J. Trump",
    # add more...
]
st.sidebar.markdown("**Daily Thought**")
st.sidebar.caption(random.choice(quotes))
