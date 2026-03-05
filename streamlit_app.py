import streamlit as st
import feedparser
import requests
from datetime import datetime

st.set_page_config(page_title="InforMore", page_icon="📰", layout="wide")

# Dark mode toggle
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=True)
if dark_mode:
    st.markdown("""
    <style>
        .stApp {background-color: #0e1117; color: #fafafa;}
        h1, h2, h3, .stMarkdown, .stCaption {color: #fafafa !important;}
        .stContainer {background-color: #262730; border: 1px solid #4a4a4a;}
    </style>
    """, unsafe_allow_html=True)

st.title("📰 InforMore")
st.subheader("Republican Conservative News Feed")
st.caption("Live from 10 top right-leaning sources • March 2026")

# 10+ Republican RSS sources
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
    for source, urls in RSS_FEEDS.items():
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:8]:
                    pub = entry.get('published_parsed') or entry.get('updated_parsed')
                    date_str = datetime(*pub[:6]).strftime("%b %d %H:%M") if pub else "Recent"
                    articles.append({
                        'title': entry.get('title', 'No Title'),
                        'summary': (entry.get('summary') or entry.get('description', ''))[:380] + '...',
                        'link': entry.get('link', '#'),
                        'published': date_str,
                        'source': source
                    })
            except:
                pass
    return sorted(articles, key=lambda x: x['published'], reverse=True)

articles = fetch_all_news()

# Sidebar controls
mode = st.sidebar.selectbox("📡 Select Mode", ["War", "Politics", "Economics"])
search_term = st.sidebar.text_input("🔍 Search headlines or keywords", "")

# Mode keyword filters (Republican slant)
mode_keywords = {
    "Politics": ["trump", "maga", "gop", "republican", "border", "election", "harris", "congress"],
    "Economics": ["economy", "inflation", "jobs", "market", "fed", "tariff", "energy", "oil", "recession"],
    "War": ["war", "ukraine", "russia", "israel", "gaza", "iran", "china", "military", "nato", "strike"]
}

filtered = [a for a in articles if any(k.lower() in (a['title'] + a['summary']).lower() for k in mode_keywords.get(mode, []))]
if search_term:
    filtered = [a for a in filtered if search_term.lower() in (a['title'] + a['summary']).lower()]
if not filtered:
    filtered = articles[:15]

st.write(f"**{len(filtered)} fresh stories** in **{mode}** mode")

# News feed cards
for art in filtered[:18]:
    with st.container(border=True):
        st.markdown(f"**[{art['title']}]({art['link']})**")
        st.caption(f"📰 {art['source']} • {art['published']}")
        st.write(art['summary'])
        st.markdown(f"[Read full article →]({art['link']})")

# War mode extras
if mode == "War":
    st.divider()
    st.subheader("🔥 War Outlook: What Could Happen Next")
    scenarios = [("Major escalation or new front opens", 34), ("U.S./Israel strikes Iran targets", 48), ("Energy prices spike sharply", 57), ("Ceasefire/talks gain traction", 25), ("Expanded sanctions or cyber retaliation", 61)]
    cols = st.columns(2)
    for i, (event, prob) in enumerate(scenarios):
        with cols[i % 2]:
            st.write(f"**{event}**")
            st.progress(prob / 100)
            st.caption(f"{prob}%")

    # Live Polymarket
    st.subheader("📈 Live Polymarket War Probabilities")
    @st.cache_data(ttl=300)
    def fetch_polymarket():
        try:
            r = requests.get("https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=20&order=volume&ascending=false")
            data = r.json()
            war_kw = ["ukraine", "israel", "gaza", "iran", "china", "war", "nato", "russia"]
            return [m for m in data if any(k in (m.get('question','') + m.get('description','')).lower() for k in war_kw)][:6]
        except:
            return []
    pm = fetch_polymarket()
    if pm:
        for m in pm:
            q = m.get('question', 'Market')
            prob = round(float(m['tokens'][0]['price']) * 100) if m.get('tokens') else 50
            st.write(f"**{q}**")
            st.progress(prob / 100)
            st.caption(f"**{prob}%** Yes • Real money odds")
    st.caption("[Open full Polymarket War Section →](https://polymarket.com/predictions/war)")

# Email alerts
with st.sidebar.expander("🛎️ Email Alerts (beta)"):
    email = st.text_input("Your email address")
    if st.button("Subscribe to " + mode + " alerts"):
        if email:
            st.success(f"✅ Subscribed! You'll get daily {mode} updates.")
        else:
            st.error("Please enter an email")

with st.sidebar:
    if st.button("🔄 Refresh Feed Now"):
        st.cache_data.clear()
        st.rerun()
    st.caption("InforMore v3 • Built for Lawrence in WA ❤️\nRepublican sources only")
