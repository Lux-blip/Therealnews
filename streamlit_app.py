import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="THEREALNEWS with Lawrence", page_icon="📰", layout="wide")

# Dark mode + card styling (smaller images, like/dislike buttons)
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=True)
if dark_mode:
    st.markdown("""
    <style>
        .stApp {background-color: #0e1117; color: #fafafa;}
        h1, h2, h3 {color: #fafafa !important;}
        .card {background-color: #262730; border: 1px solid #4a4a4a; border-radius: 12px; padding: 16px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);}
        .card img {border-radius: 8px; width: 300px; max-width: 100%; height: auto; object-fit: cover; margin-bottom: 12px; display: block; margin-left: auto; margin-right: auto;}
        .title {font-size: 1.4em; font-weight: bold; margin: 8px 0;}
        .meta {color: #bbb; font-size: 0.95em; margin-bottom: 8px;}
        .top-story-header {font-size: 2em; text-align: center; margin: 20px 0; color: #FF4B4B;}
        .like-btn {background-color: #4CAF50 !important; color: white !important; border: none !important; padding: 6px 12px !important; border-radius: 6px !important; margin-right: 8px !important;}
        .dislike-btn {background-color: #f44336 !important; color: white !important; border: none !important; padding: 6px 12px !important; border-radius: 6px !important;}
        .reset-btn {background-color: #FF0000 !important; color: white !important; font-size: 0.8em !important; padding: 4px 10px !important; border-radius: 6px !important;}
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown("<h1 class='top-story-header'>THEREALNEWS with Lawrence</h1>", unsafe_allow_html=True)
st.caption("Your Personalized Conservative Feed • Republican Sources Only")

# Init session state for likes/dislikes & reset
if 'preferences' not in st.session_state:
    st.session_state.preferences = {}  # link -> score (+1 like, -1 dislike)
if 'reset_trigger' not in st.session_state:
    st.session_state.reset_trigger = 0

# RSS sources
RSS_FEEDS = { ... }  # Keep your full RSS_FEEDS dict here from previous code

@st.cache_data(ttl=600) def fetch_all_news():
    # Same as before - fetch, extract image, add pub_datetime, importance_score
    # (copy the full fetch_all_news function from your last working version)
    # For brevity: assume it returns list of dicts with 'link', 'title', 'summary', 'image', 'source', 'published', 'pub_datetime', 'importance_score'

all_articles = fetch_all_news()

# Apply user preferences to boost/hide
def get_adjusted_priority(article):
    link = article['link']
    score = st.session_state.preferences.get(link, 0)
    base = article['importance_score'] + (score * 1000)  # Like boosts a lot, dislike lowers
    if score <= -1:
        return -999999  # Hide disliked heavily
    return base

# Top Stories (boosted by prefs)
st.subheader("🔥 Top Stories")
sorted_top = sorted(all_articles[:30], key=get_adjusted_priority, reverse=True)[:5]
for art in sorted_top:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if art['image']:
            st.image(art['image'], use_column_width=False)  # smaller via CSS
        st.markdown(f'<div class="title">[{art["title"]}]({art["link"]})</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="meta">📰 {art["source"]} • {art["published"]}</div>', unsafe_allow_html=True)
        st.write(art['summary'])
        
        # Like / Dislike
        cols = st.columns([1,1,8])
        with cols[0]:
            if st.button("👍 Like", key=f"like_{art['link']}", help="Show more like this", use_container_width=True):
                st.session_state.preferences[art['link']] = st.session_state.preferences.get(art['link'], 0) + 1
                st.rerun()
        with cols[1]:
            if st.button("👎 Dislike", key=f"dislike_{art['link']}", help="Show less like this", use_container_width=True):
                st.session_state.preferences[art['link']] = st.session_state.preferences.get(art['link'], 0) - 1
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# Sidebar: Mode, Search, Reset
mode = st.sidebar.selectbox("📡 Mode", ["War", "Politics", "Economics"])
search_term = st.sidebar.text_input("🔍 Search", "")

# Reset button - small & red
if st.sidebar.button("Reset Algorithm", key="reset_alg", help="Clear all likes/dislikes", use_container_width=False):
    st.session_state.preferences = {}
    st.session_state.reset_trigger += 1
    st.success("Algorithm reset! Preferences cleared.")
    st.rerun()

# Filter main feed (with prefs applied)
mode_keywords = { ... }  # your keywords

filtered = [a for a in all_articles if any(k.lower() in (a['title'].lower() + a['summary'].lower()) for k in mode_keywords.get(mode, []))]
if search_term:
    filtered = [a for a in filtered if search_term.lower() in (a['title'].lower() + a['summary'].lower())]

# Sort main feed with prefs
filtered.sort(key=get_adjusted_priority, reverse=True)

st.write(f"**{len(filtered)} stories** in **{mode}** mode • Personalized by your likes/dislikes")

for art in filtered[:15]:  # limit to avoid overload
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if art['image']:
            st.image(art['image'], use_column_width=False)
        st.markdown(f'<div class="title">[{art["title"]}]({art["link"]})</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="meta">📰 {art["source"]} • {art["published"]}</div>', unsafe_allow_html=True)
        st.write(art['summary'])
        
        cols = st.columns([1,1,8])
        with cols[0]:
            st.button("👍 Like", key=f"like_main_{art['link']}", help="Boost this type")
        with cols[1]:
            st.button("👎 Dislike", key=f"dislike_main_{art['link']}", help="Reduce this type")
        
        st.markdown('</div>', unsafe_allow_html=True)

# War mode extras (keep as-is)

with st.sidebar:
    st.caption("THEREALNEWS with Lawrence • Your Feed • Likes shape what you see more")
