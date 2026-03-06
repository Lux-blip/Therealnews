import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="THEREALNEWS with Lawrence", page_icon="📰", layout="wide")

# Dark mode toggle
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=True)
if dark_mode:
    st.markdown("""
    <style>
        .stApp {background-color: #0e1117; color: #fafafa;}
        h1, h2, h3, .stMarkdown, .stCaption {color: #fafafa !important;}
        .card {background-color: #262730; border: 1px solid #4a4a4a; border-radius: 12px; padding: 16px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);}
        .card img {border-radius: 8px; width: 100%; height: auto; object-fit: cover; margin-bottom: 12px;}
        .title {font-size: 1.5em; font-weight: bold; margin: 8px 0;}
        .meta {color: #bbb; font-size: 0.95em; margin-bottom: 8px;}
        .top-story-header {font-size: 2em; text-align: center; margin: 20px 0; color: #FF4B4B;}
    </style>
    """, unsafe_allow_html=True)

# Header with your requested name
st.markdown("<h1 class='top-story-header'>THEREALNEWS with Lawrence</h1>", unsafe_allow_html=True)
st.caption("Unfiltered Conservative Perspective • Fresh Republican Sources")

# Optional logo (upload logo.png to repo root if you have one)
if os.path.exists("logo.png"):
    st.image("logo.png", width=100, use_column_width=False)

# RSS sources (Republican/conservative only)
RSS_FEEDS = {
    "Fox News": ["https://moxie.foxnews.com/google-publisher/latest.xml", "https://moxie.foxnews.com/google-publisher/world.xml"],
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
                            continue  # skip old stuff for freshness
                        date_str = pub_date.strftime("%b %d %H:%M")
                    else:
                        date_str = "Recent"
                    
                    # Extract image if available (common RSS ways)
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
                        'importance_score': len(entry.get('title', '')) + len(entry.get('summary', '')) * 0.5  # simple proxy: longer = more detail/importance
                    })
            except:
                pass
    
    # Sort overall newest first
    articles.sort(key=lambda x: x['pub_datetime'], reverse=True)
    return articles

all_articles = fetch_all_news()

# Top Stories section (top 4-5 "important" recent ones)
st.subheader("🔥 Top Stories")
top_stories = sorted(all_articles[:20], key=lambda x: x['importance_score'], reverse=True)[:5]  # take recent + score
for art in top_stories:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if art['image']:
            st.image(art['image'], use_column_width=True)
        st.markdown(f'<div class="title">[{art["title"]}]({art["link"]})</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="meta">📰 {art["source"]} • {art["published"]}</div>', unsafe_allow_html=True)
        st.write(art['summary'])
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# Sidebar mode & search
mode = st.sidebar.selectbox("📡 Mode", ["War", "Politics", "Economics"])
search_term = st.sidebar.text_input("🔍 Search headlines", "")

mode_keywords = {
    "Politics": ["trump", "maga", "gop", "republican", "border", "election", "harris", "congress"],
    "Economics": ["economy", "inflation", "jobs", "market", "fed", "tariff", "energy", "oil"],
    "War": ["war", "ukraine", "russia", "israel", "gaza", "iran", "china", "military", "nato", "strike"]
}

filtered = [a for a in all_articles if any(k.lower() in (a['title'].lower() + a['summary'].lower()) for k in mode_keywords.get(mode, []))]
if search_term:
    filtered = [a for a in filtered if search_term.lower() in (a['title'].lower() + a['summary'].lower())]
if not filtered:
    filtered = all_articles[:12]

st.write(f"**{len(filtered)} stories** in **{mode}** mode • From conservative sources only")

# Main feed cards (social style)
for art in filtered:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if art['image']:
            st.image(art['image'], use_column_width=True)
        st.markdown(f'<div class="title">[{art["title"]}]({art["link"]})</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="meta">📰 {art["source"]} • {art["published"]}</div>', unsafe_allow_html=True)
        st.write(art['summary'])
        st.markdown('</div>', unsafe_allow_html=True)

# War mode probabilities (unchanged)
if mode == "War":
    st.divider()
    st.subheader("🔥 War Outlook: What Could Happen Next")
    scenarios = [("Major escalation/new front", 34), ("U.S./Israel strikes Iran", 48), ("Energy prices spike", 57), ("Ceasefire progress", 25), ("Sanctions/cyber retaliation", 61)]
    cols = st.columns(2)
    for i, (event, prob) in enumerate(scenarios):
        with cols[i % 2]:
            st.write(f"**{event}**")
            st.progress(prob / 100)
            st.caption(f"{prob}% estimate")

# Sidebar controls
with st.sidebar:
    if st.button("🔄 Refresh Now"):
        st.cache_data.clear()
        st.rerun()
    st.caption("THEREALNEWS with Lawrence • Republican Feed • Built for you")

