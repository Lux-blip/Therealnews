import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="THEREALNEWS with Lawrence", page_icon="📰", layout="wide")

# Newspaper-inspired styling
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=False)
if dark_mode:
    bg_color = "#0e1117"
    card_bg = "#1e1e2e"
    text_color = "#e0e0ff"
    accent = "#c62828"
    gradient = "linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.4) 100%)"
else:
    bg_color = "#f8f5f0"           # light paper/off-white
    card_bg = "#ffffff"
    text_color = "#1a1a1a"
    accent = "#b71c1c"
    gradient = "linear-gradient(to top, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.35) 100%)"

st.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
            font-family: 'Georgia', 'Times New Roman', serif;
        }}
        h1, h2, h3 {{
            font-family: 'Georgia', serif;
            color: {accent} !important;
        }}
        .newspaper-title {{
            font-size: 3.2rem;
            font-weight: bold;
            text-align: center;
            margin: 20px 0 8px;
            letter-spacing: -1px;
            color: {accent};
        }}
        .card {{
            background-color: {card_bg};
            border: 1px solid #d0d0d0;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 28px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.12);
            position: relative;
        }}
        .card img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        .card-gradient {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 24px 20px 16px;
            background: {gradient};
            color: white;
        }}
        .card-title {{
            font-size: 1.35rem;
            font-weight: 700;
            margin: 0 0 6px 0;
            line-height: 1.25;
        }}
        .card-meta {{
            font-size: 0.92rem;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        .action-btn {{
            background-color: {accent} !important;
            color: white !important;
            border: none !important;
            padding: 8px 16px !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            margin-right: 10px !important;
        }}
        .like-btn {{
            background-color: #388e3c !important;
        }}
        .dislike-btn {{
            background-color: #d32f2f !important;
        }}
        .reset-btn {{
            background-color: #c62828 !important;
            font-size: 0.85rem !important;
            padding: 6px 14px !important;
        }}
    </style>
""", unsafe_allow_html=True)

# Header — newspaper style
st.markdown('<div class="newspaper-title">THEREALNEWS</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; font-size:1.3rem; margin-top:-10px; color:#555;">with Lawrence</p>', unsafe_allow_html=True)
st.caption("Unfiltered • Conservative • Republican Perspective", help="Curated from trusted right-leaning sources")

# Session state
if 'preferences' not in st.session_state:
    st.session_state.preferences = {}
if 'reset_trigger' not in st.session_state:
    st.session_state.reset_trigger = 0

# (Keep your RSS_FEEDS dict here – same as before)

@st.cache_data(ttl=600)
def fetch_all_news():
    # (Keep your full fetch_all_news function from the previous working version)
    # Make sure it returns articles with 'image', 'title', 'summary', 'link', 'source', 'published', 'pub_datetime', 'importance_score'
    pass  # ← paste your fetch function body here

all_articles = fetch_all_news()

def get_adjusted_priority(article):
    link = article['link']
    score = st.session_state.preferences.get(link, 0)
    base = article['importance_score'] + score * 1200
    if score <= -1:
        return -999999
    return base

# Top Stories
st.subheader("Top Stories")
sorted_top = sorted(all_articles[:30], key=get_adjusted_priority, reverse=True)[:4]

for art in sorted_top:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        if art['image']:
            st.image(art['image'], use_column_width=True)
        else:
            st.markdown('<div style="height:180px; background:#444;"></div>', unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="card-gradient">
                <div class="card-title"><a href="{art['link']}" target="_blank" style="color:white; text-decoration:none;">{art['title']}</a></div>
                <div class="card-meta">📰 {art['source']} • {art['published']}</div>
                
                <div style="margin-top:12px;">
                    <button class="action-btn like-btn" onclick="parent.window.location.href='{art['link']}'">Read Article</button>
                    <button class="action-btn like-btn">👍 Like</button>
                    <button class="action-btn dislike-btn">👎 Dislike</button>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# Sidebar
mode = st.sidebar.selectbox("Section", ["War", "Politics", "Economics"])
search_term = st.sidebar.text_input("Search headlines")

if st.sidebar.button("Reset Algorithm", help="Clear likes & dislikes", key="reset_alg"):
    st.session_state.preferences = {}
    st.success("Preferences reset")
    st.rerun()

# Main feed (same filtering + personalization logic as before)
# ... (add your mode_keywords, filtering, sorting code here)

# Example main feed card loop (adapt to your filtered list)
for art in filtered[:12]:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        if art['image']:
            st.image(art['image'], use_column_width=True)
        
        st.markdown(f"""
            <div class="card-gradient">
                <div class="card-title"><a href="{art['link']}" target="_blank" style="color:white; text-decoration:none;">{art['title']}</a></div>
                <div class="card-meta">📰 {art['source']} • {art['published']}</div>
                <p style="margin:8px 0 12px 0; color:#eee;">{art['summary']}</p>
                
                <div>
                    <button class="action-btn like-btn" onclick="parent.window.location.href='{art['link']}'">Read Article</button>
                    <button class="action-btn like-btn">👍 Like</button>
                    <button class="action-btn dislike-btn">👎 Dislike</button>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Keep War mode probabilities section if mode == "War"
