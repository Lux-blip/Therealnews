import streamlit as st
import feedparser
from datetime import datetime, timedelta

st.set_page_config(page_title="THEREALNEWS with Lawrence", page_icon="📰", layout="wide")

# Force dark mode + newspaper-inspired dark styling
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background-color: #0e1117 !important;
            color: #e0e0ff !important;
        }
        .stApp {
            background-color: #0e1117 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #161b22 !important;
        }
        .title-main {
            font-size: 3.5rem;
            font-weight: bold;
            text-align: center;
            color: #ff4d4d;
            margin: 24px 0 4px 0;
            letter-spacing: -1.2px;
        }
        .subtitle {
            text-align: center;
            font-size: 1.45rem;
            color: #aaa;
            margin-top: -12px;
            margin-bottom: 20px;
        }
        .card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 40px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.4);
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
            padding: 100px 24px 24px;
            background: linear-gradient(to top, rgba(0,0,0,0.92) 0%, rgba(0,0,0,0.65) 40%, rgba(0,0,0,0.25) 70%, transparent 100%);
            color: white;
        }
        .card-title {
            font-size: 1.42rem;
            font-weight: 700;
            margin: 0 0 8px 0;
            line-height: 1.3;
        }
        .card-meta {
            font-size: 0.96rem;
            color: #ccc;
            margin-bottom: 14px;
        }
        .btn {
            background: #ff4d4d !important;
            color: white !important;
            border: none !important;
            padding: 9px 18px !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            margin-right: 12px !important;
            cursor: pointer;
            font-size: 0.95rem !important;
        }
        .btn-like { background: #4caf50 !important; }
        .btn-dislike { background: #e53935 !important; }
        .btn-reset {
            background: #c62828 !important;
            font-size: 0.88rem !important;
            padding: 6px 16px !important;
            margin-top: 8px;
        }
        hr {
            border-color: #444;
            margin: 48px 0 64px 0;
        }
        .stInfo, .stSuccess {
            background-color: #21262d !important;
            color: #e0e0ff !important;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="title-main">THEREALNEWS</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">with Lawrence</div>', unsafe_allow_html=True)
st.caption("Conservative • Republican-leaning sources • Unfiltered perspective")

# Session state for likes/dislikes
if 'prefs' not in st.session_state:
    st.session_state.prefs = {}

# RSS sources
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

news = fetch_all_news()

# Sidebar
mode = st.sidebar.selectbox("Section", ["All", "War", "Politics", "Economics"])

if st.sidebar.button("Reset likes/dislikes", help="Clear personalization"):
    st.session_state.prefs = {}
    st.success("Preferences cleared")
    st.rerun()

# Priority function
def priority(article):
    val = st.session_state.prefs.get(article['link'], 0)
    return article['score'] + val * 1500 if val >= 0 else -999999

# Top Stories
st.subheader("Top Stories")
top_items = sorted(news[:40], key=priority, reverse=True)[:4]

for item in top_items:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.markdown('<div class="card-image-wrapper">', unsafe_allow_html=True)
        if item['image']:
            st.image(item['image'], use_column_width=True)
        else:
            st.markdown('<div style="height:220px; background:#1e1e2e;"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="gradient-overlay">
                <div class="card-title">
                    <a href="{item['link']}" target="_blank" style="color:white; text-decoration:none;">
                        {item['title']}
                    </a>
                </div>
                <div class="card-meta">📰 {item['source']} • {item['published']}</div>
                <div style="margin-top:14px;">
                    <a href="{item['link']}" target="_blank">
                        <button class="btn">Read Article</button>
                    </a>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Main feed
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
    st.info("No recent stories in this section – try another mode or refresh later.")

for item in items:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.markdown('<div class="card-image-wrapper">', unsafe_allow_html=True)
        if item['image']:
            st.image(item['image'], use_column_width=True)
        else:
            st.markdown('<div style="height:220px; background:#1e1e2e;"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="gradient-overlay">
                <div class="card-title">
                    <a href="{item['link']}" target="_blank" style="color:white; text-decoration:none;">
                        {item['title']}
                    </a>
                </div>
                <div class="card-meta">📰 {item['source']} • {item['published']}</div>
                <p style="margin:10px 0 16px 0; color:#ddd; font-size:0.98rem;">{item['summary']}</p>
                <div>
                    <a href="{item['link']}" target="_blank">
                        <button class="btn">Read Article</button>
                    </a>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# War mode probabilities
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

st.sidebar.caption("THEREALNEWS with Lawrence • Conservative feed • Dark mode forced")
