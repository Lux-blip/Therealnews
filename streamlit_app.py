import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="THEREALNEWS with Lawrence", page_icon="📰", layout="wide")

# Dark mode + styling
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

# Session state for likes/dislikes
if 'preferences' not in st.session_state:
    st.session_state.preferences = {}  # link -> score
if 'reset_trigger' not in st.session_state:
    st.session_state.reset_trigger = 0

# Republican RSS sources
RSS_FEEDS = {
    "Fox News": [
        "https://moxie.foxnews.com/google-publisher/latest.xml",
        "https://moxie.foxnews.com/google-publisher/world.xml"
    ],
    "Breitbart": ["https://feeds.feedburner.com/breitbart"],
    "Newsmax": ["https://www.newsmax.com/rss/newsfront/16"],
    "Daily Wire": ["https://www.dailywire.com/feeds/rss.xml"],
    "The Federalist": ["https://thefederalist.com/feed/"],
    "Epoch Times": ["https://www.theepochtimes.com/feed"],
    "OANN": ["https://www.oann.com/category/newsroom/feed/"],
    "Washington Examiner": ["https://www.washingtonexaminer.com/feed"],
    "National Review": ["https://www.nationalreview.com/feed"],
    "The Blaze": ["https://www.theblaze.com/feeds/feed.rss"]
}

@st.cache_data(ttl=600)
def fetch_all_news():
    articles = []
    now = datetime.utcnow()
    one_day_ago = now - timedelta(days=1)
    
    for source, urls in RSS_FEEDS.items():
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:12]:
                    pub_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
                    if pub_parsed:
                        pub_date = datetime(*pub_parsed[:6])
                        if pub_date < one_day_ago:
                            continue
                        date_str = pub_date.strftime("%b %d %H:%M")
                    else:
                        date_str = "Recent"
                    
                    # Extract image
                    img_url = None
                    if 'media_content' in entry:
                        for media in entry.media_content:
                            if media.get('medium') == 'image' and 'url' in media:
                                img_url = media['url']
                                break
                    if not img_url and 'media_thumbnail' in entry and entry.media_thumbnail:
                        img_url = entry.media_thumbnail[0].get('url')
                    if not img_url and 'enclosures' in entry:
                        for enc in entry.enclosures:
                            if 'image' in enc.get('type', ''):
                                img_url = enc.get('href')
                                break
                    
                    articles.append({
                        'title': entry.get('title', 'No Title'),
                        'summary': (entry.get('summary') or entry.get('description', 'No summary'))[:280] + '...',
                        'link': entry.get('link', '#'),
                        'published': date_str,
                        'pub_datetime': pub_date if pub_parsed else now,
                        'source': source,
                        'image': img_url,
                        'importance_score': len(entry.get('title', '')) + len(entry.get('summary', '')) * 0.5
                    })
            except Exception:
                pass
    
    articles.sort(key=lambda x: x['pub_datetime'], reverse=True)
    return articles

all_articles = fetch_all_news()

# Personalized priority
def get_adjusted_priority(article):
    link = article['link']
    score = st.session_state.preferences.get(link, 0)
    base = article['importance_score'] + (score * 1000)
    if score <= -1:
        return -999999  # hide
    return base

# Top Stories
st.subheader("🔥 Top Stories")
sorted_top = sorted(all_articles[:30], key=get_adjusted_priority, reverse=True)[:5]
for art in sorted_top:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if art['image']:
            st.image(art['image'], use_column_width=False)
        st.markdown(f'<div class="title">[{art["title"]}]({art["link"]})</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="meta">📰 {art["source"]} • {art["published"]}</div>', unsafe_allow_html=True)
        st.write(art['summary'])
        
        cols = st.columns([1, 1, 8])
        with cols[0]:
            if st.button("👍 Like", key=f"like_top_{art['link']}"):
                st.session_state.preferences[art['link']] = st.session_state.preferences.get(art['link'], 0) + 1
                st.rerun()
        with cols[1]:
            if st.button("👎 Dislike", key=f"dislike_top_{art['link']}"):
                st.session_state.preferences[art['link']] = st.session_state.preferences.get(art['link'], 0) - 1
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# Sidebar controls
mode = st.sidebar.selectbox("📡 Mode", ["War", "Politics", "Economics"])
search_term = st.sidebar.text_input("🔍 Search", "")

if st.sidebar.button("Reset Algorithm", help="Clear all likes/dislikes"):
    st.session_state.preferences = {}
    st.success("Algorithm reset!")
    st.rerun()

# Filter & sort main feed
mode_keywords = {
    "Politics": ["trump", "maga", "gop", "republican", "border", "election", "harris", "congress"],
    "Economics": ["economy", "inflation", "jobs", "market", "fed", "tariff", "energy", "oil"],
    "War": ["war", "ukraine", "russia", "israel", "gaza", "iran", "china", "military", "nato", "strike"]
}

filtered = [
    a for a in all_articles
    if any(k.lower() in (a['title'].lower() + a['summary'].lower()) for k in mode_keywords.get(mode, []))
]

if search_term:
    filtered = [
        a for a in filtered
        if search_term.lower() in (a['title'].lower() + a['summary'].lower())
    ]

filtered.sort(key=get_adjusted_priority, reverse=True)

st.write(f"**{len(filtered)} stories** in **{mode}** mode • Personalized")

for art in filtered[:15]:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if art['image']:
            st.image(art['image'], use_column_width=False)
        st.markdown(f'<div class="title">[{art["title"]}]({art["link"]})</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="meta">📰 {art["source"]} • {art["published"]}</div>', unsafe_allow_html=True)
        st.write(art['summary'])
        
        cols = st.columns([1, 1, 8])
        with cols[0]:
            st.button("👍 Like", key=f"like_{art['link']}")
        with cols[1]:
            st.button("👎 Dislike", key=f"dislike_{art['link']}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# War mode section
if mode == "War":
    st.divider()
    st.subheader("🔥 War Outlook")
    scenarios = [
        ("Major escalation/new front", 34),
        ("U.S./Israel strikes Iran", 48),
        ("Energy prices spike", 57),
        ("Ceasefire progress", 25),
        ("Sanctions/cyber retaliation", 61)
    ]
    cols = st.columns(2)
    for i, (event, prob) in enumerate(scenarios):
        with cols[i % 2]:
            st.write(f"**{event}**")
            st.progress(prob / 100)
            st.caption(f"{prob}%")

with st.sidebar:
    st.caption("THEREALNEWS with Lawrence • Your Feed")
