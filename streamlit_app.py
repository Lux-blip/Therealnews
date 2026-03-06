import streamlit as st
import feedparser
from datetime import datetime, timedelta

st.set_page_config(page_title="THEREALNEWS with Lawrence", page_icon="📰", layout="wide")

# ────────────────────────────────────────────────
#  Styling – newspaper + gradient cards
# ────────────────────────────────────────────────
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f5f0;
        color: #1a1a1a;
        font-family: Georgia, 'Times New Roman', serif;
    }
    .title-main {
        font-size: 3.4rem;
        font-weight: bold;
        text-align: center;
        color: #b71c1c;
        margin: 20px 0 0 0;
        letter-spacing: -1px;
    }
    .subtitle {
        text-align: center;
        font-size: 1.4rem;
        color: #444;
        margin-top: -12px;
    }
    .card {
        background: white;
        border: 1px solid #d0d0d0;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 36px !important;
        box-shadow: 0 3px 12px rgba(0,0,0,0.1);
        position: relative;
    }
    .card-image-wrapper {
        position: relative;
        width: 100%;
    }
    .card img {
        width: 100%;
        height: auto;
        display: block;
    }
    .gradient-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 90px 20px 20px;
        background: linear-gradient(to top, rgba(0,0,0,0.88) 0%, rgba(0,0,0,0.4) 70%, transparent 100%);
        color: white;
    }
    .card-title {
        font-size: 1.38rem;
        font-weight: 700;
        margin: 0 0 6px 0;
        line-height: 1.28;
    }
    .card-meta {
        font-size: 0.94rem;
        opacity: 0.92;
        margin-bottom: 12px;
    }
    .btn {
        background: #b71c1c !important;
        color: white !important;
        border: none !important;
        padding: 8px 16px !important;
        border-radius: 5px !important;
        font-weight: 600 !important;
        margin-right: 10px !important;
        cursor: pointer;
    }
    .btn-like { background: #2e7d32 !important; }
    .btn-dislike { background: #c62828 !important; }
    .btn-reset { 
        background: #d32f2f !important; 
        font-size: 0.9rem !important;
        padding: 6px 14px !important;
    }
    hr {
        border-color: #aaa;
        margin: 48px 0 64px 0;
    }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
#  Header
# ────────────────────────────────────────────────
st.markdown('<div class="title-main">THEREALNEWS</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">with Lawrence</div>', unsafe_allow_html=True)
st.caption("Conservative perspective • Republican-leaning sources", help="Fox, Breitbart, Newsmax, Daily Wire, OANN, Epoch Times, etc.")

# ────────────────────────────────────────────────
#  Session state for likes/dislikes
# ────────────────────────────────────────────────
if 'prefs' not in st.session_state:
    st.session_state.prefs = {}          # link → +1 like / -1 dislike

# ────────────────────────────────────────────────
#  RSS sources (Republican / conservative)
# ────────────────────────────────────────────────
RSS_FEEDS = {
    "Fox News": [
        "https://moxie.foxnews.com/google-publisher/latest.xml",
        "https://moxie.foxnews.com/google-publisher/politics.xml",
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

# ────────────────────────────────────────────────
#  Fetch function – always returns list
# ────────────────────────────────────────────────
@st.cache_data(ttl=600)
def fetch_all_news():
    articles = []
    now = datetime.utcnow()
    one_day_ago = now - timedelta(days=1)

    for source, urls in RSS_FEEDS.items():
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:10]:
                    pub_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
                    pub_date = None
                    date_str = "Recent"

                    if pub_parsed:
                        try:
                            pub_date = datetime(*pub_parsed[:6])
                            if pub_date < one_day_ago:
                                continue
                            date_str = pub_date.strftime("%b %d %H:%M")
                        except:
                            pass

                    # Image
                    img = None
                    if 'media_content' in entry:
                        for m in entry.media_content:
                            if m.get('medium') == 'image' and 'url' in m:
                                img = m['url']
                                break
                    if not img and 'media_thumbnail' in entry and entry.media_thumbnail:
                        img = entry.media_thumbnail[0].get('url')

                    articles.append({
                        'title': entry.get('title', 'No title'),
                        'summary': (entry.get('summary') or entry.get('description', ''))[:240] + '...',
                        'link': entry.get('link', '#'),
                        'published': date_str,
                        'pub_dt': pub_date if pub_date else now,
                        'source': source,
                        'image': img,
                        'score': len(entry.get('title','')) + len(entry.get('summary','')) * 0.6
                    })
            except:
                pass

    articles.sort(key=lambda x: x['pub_dt'], reverse=True)
    return articles

# Load news
news = fetch_all_news()

# ────────────────────────────────────────────────
#  Sidebar controls
# ────────────────────────────────────────────────
mode = st.sidebar.selectbox("Section", ["All", "War", "Politics", "Economics"])

if st.sidebar.button("Reset likes/dislikes", help="Clear personalization", key="reset"):
    st.session_state.prefs = {}
    st.success("Preferences cleared")
    st.rerun()

# ────────────────────────────────────────────────
#  Simple personalization
# ────────────────────────────────────────────────
def priority(article):
    link = article['link']
    val = st.session_state.prefs.get(link, 0)
    return article['score'] + val * 1500 if val >= 0 else -999999

# ────────────────────────────────────────────────
#  Top Stories
# ────────────────────────────────────────────────
st.subheader("Top Stories")
top_items = sorted(news[:40], key=priority, reverse=True)[:4]

for item in top_items:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if item['image']:
            st.image(item['image'], use_column_width=True)
        else:
            st.markdown('<div style="height:160px; background:#555;"></div>', unsafe_allow_html=True)

        st.markdown(f"""
            <div class="gradient-bottom">
                <div class="card-title">
                    <a href="{item['link']}" target="_blank" style="color:white; text-decoration:none;">
                        {item['title']}
                    </a>
                </div>
                <div class="card-meta">📰 {item['source']} • {item['published']}</div>
                <div style="margin-top:12px;">
                    <a href="{item['link']}" target="_blank">
                        <button class="btn">Read Article</button>
                    </a>
                    <button class="btn btn-like" onclick="alert('Liked!')">👍 Like</button>
                    <button class="btn btn-dislike" onclick="alert('Disliked!')">👎 Dislike</button>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ────────────────────────────────────────────────
#  Main feed
# ────────────────────────────────────────────────
st.subheader(f"{mode} Feed")

keywords = {
    "War": ["war", "ukraine", "russia", "israel", "iran", "gaza", "military", "nato", "conflict"],
    "Politics": ["trump", "biden", "harris", "election", "congress", "senate", "republican", "democrat", "border"],
    "Economics": ["economy", "inflation", "jobs", "market", "fed", "tariff", "oil", "recession"]
}

items = news
if mode != "All":
    items = [a for a in news if any(k.lower() in (a['title']+a['summary']).lower() for k in keywords.get(mode, []))]

items = sorted(items, key=priority, reverse=True)[:12]

if not items:
    st.info("No recent stories in this section right now – try another mode or refresh later.")

for item in items:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if item['image']:
            st.image(item['image'], use_column_width=True)
        else:
            st.markdown('<div style="height:160px; background:#555;"></div>', unsafe_allow_html=True)

        st.markdown(f"""
            <div class="gradient-bottom">
                <div class="card-title">
                    <a href="{item['link']}" target="_blank" style="color:white; text-decoration:none;">
                        {item['title']}
                    </a>
                </div>
                <div class="card-meta">📰 {item['source']} • {item['published']}</div>
                <p style="margin:8px 0 12px 0; color:#eee; font-size:0.97rem;">{item['summary']}</p>
                <div>
                    <a href="{item['link']}" target="_blank">
                        <button class="btn">Read Article</button>
                    </a>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────
#  War probabilities
# ────────────────────────────────────────────────
if mode == "War":
    st.markdown("---")
    st.subheader("War Outlook – Estimated Next Moves")
    probs = [
        ("Major escalation or new front", 38),
        ("U.S. or Israel strikes Iran assets", 44),
        ("Energy / oil prices spike sharply", 59),
        ("Temporary ceasefire talks advance", 22),
        ("Expanded sanctions or cyber response", 63)
    ]
    cols = st.columns(2)
    for i, (txt, pct) in enumerate(probs):
        with cols[i % 2]:
            st.write(f"**{txt}**")
            st.progress(pct / 100)
            st.caption(f"{pct}%")

st.sidebar.caption("THEREALNEWS with Lawrence • Conservative feed")
