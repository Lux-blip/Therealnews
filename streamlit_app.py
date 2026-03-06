import streamlit as st
import feedparser
from datetime import datetime, timedelta
import random
import time

st.set_page_config(page_title="THEREALNEWS with Lawrence", page_icon="📰", layout="wide")

# Persistent settings
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

# Styling – dark mode forced + responsive font
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
            .card {{ background: #161b22; border: 1px solid #30363d; color: white; border-radius: 10px; overflow: hidden; margin-bottom: 40px; box-shadow: 0 4px 16px rgba(0,0,0,0.4); position: relative; }}
            .card-image-wrapper {{ position: relative; width: 100%; }}
            .card img {{ width: 100%; height: auto; display: block; }}
            .gradient-overlay {{ position: absolute; bottom: 0; left: 0; right: 0; padding: 100px 24px 24px; background: linear-gradient(to top, rgba(0,0,0,0.92) 0%, rgba(0,0,0,0.65) 40%, transparent 100%); color: white; }}
            .card-title {{ font-size: {fs['title']}; font-weight: 700; margin: 0 0 8px 0; line-height: 1.3; }}
            .card-meta {{ font-size: {fs['meta']}; color: #ccc; margin-bottom: 14px; }}
            .summary {{ font-size: {fs['summary']}; color: #ddd; margin: 10px 0 16px 0; }}
            .btn {{ background: #ff4d4d !important; color: white !important; border: none !important; padding: 9px 18px !important; border-radius: 6px !important; font-weight: 600 !important; margin-right: 12px !important; cursor: pointer; font-size: 0.95rem !important; }}
            .btn-like {{ background: #4caf50 !important; }}
            .btn-dislike {{ background: #e53935 !important; }}
            .btn-reset {{ background: #c62828 !important; font-size: 0.88rem !important; padding: 6px 16px !important; margin-top: 8px; }}
            hr {{ border-color: #444; margin: 48px 0 64px 0; }}
            .prob-bar {{ margin: 8px 0; }}
        </style>
    """, unsafe_allow_html=True)

# Header
st.markdown('<div style="font-size:3.5rem; font-weight:bold; text-align:center; color:#ff4d4d;">THEREALNEWS</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; font-size:1.45rem; color:#aaa; margin-top:-12px;">with Lawrence</div>', unsafe_allow_html=True)

# Sidebar controls
with st.sidebar:
    st.header("Personalize")
    st.session_state.dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode)
    st.session_state.font_size = st.selectbox("Text Size", ["Small", "Medium", "Large"], index=["Small","Medium","Large"].index(st.session_state.font_size))
    st.session_state.auto_refresh = st.checkbox("Auto-refresh every 5 min", value=st.session_state.auto_refresh)

    st.subheader("Favorite Sources")
    sources = ["Fox News", "Breitbart", "Newsmax", "Daily Wire", "The Federalist", "Epoch Times", "OANN", "Washington Examiner", "National Review", "The Blaze"]
    selected = st.multiselect("Select sources", sources, default=list(st.session_state.favorite_sources))
    st.session_state.favorite_sources = set(selected)

    st.subheader("Saved Stories")
    for s in st.session_state.saved_stories[:6]:
        st.markdown(f"• [{s['title'][:50]}...]({s['link']})")
    if st.button("Clear Saved"):
        st.session_state.saved_stories = []
        st.rerun()

    st.subheader("Search History")
    for q in st.session_state.search_history[-6:]:
        if st.button(q[:35] + "..." if len(q)>35 else q, key=f"hist_{q}"):
            st.session_state.search_term = q
            st.rerun()

    # Random conservative quote
    quotes = [
        "Freedom is never more than one generation away from extinction. — Ronald Reagan",
        "Government is not the solution to our problem; government is the problem. — Ronald Reagan",
        "The nine most terrifying words in the English language are: I'm from the government and I'm here to help. — Ronald Reagan",
        "Make America Great Again. — Donald J. Trump",
        "We will make America strong again. We will make America proud again. — Donald J. Trump"
    ]
    st.markdown("**Daily Thought**")
    st.caption(random.choice(quotes))

# RSS feeds
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
                    pub_date = datetime(*pub_parsed[:6]) if pub_parsed else now
                    if pub_date < one_day_ago:
                        continue
                    date_str = pub_date.strftime("%b %d %H:%M")

                    img = None
                    if 'media_content' in entry:
                        for m in entry.media_content:
                            if m.get('medium') == 'image' and 'url' in m:
                                img = m['url']
                                break

                    articles.append({
                        'title': entry.get('title', 'No title'),
                        'summary': (entry.get('summary') or entry.get('description', ''))[:240] + '...',
                        'link': entry.get('link', '#'),
                        'published': date_str,
                        'pub_dt': pub_date,
                        'source': source,
                        'image': img,
                        'score': len(entry.get('title','')) + len(entry.get('summary','')) * 0.6
                    })
            except:
                pass

    articles.sort(key=lambda x: x['pub_dt'], reverse=True)
    return articles

news = fetch_all_news()

# Filtering
filtered = news
if st.session_state.favorite_sources:
    filtered = [a for a in filtered if a['source'] in st.session_state.favorite_sources]

filtered = [a for a in filtered if a['link'] not in st.session_state.read_stories]

search_term = st.text_input("Search headlines", value=st.session_state.get('search_term', ''))
if search_term and search_term not in st.session_state.search_history:
    st.session_state.search_history.append(search_term)
    st.session_state.search_term = search_term

if search_term:
    filtered = [a for a in filtered if search_term.lower() in (a['title'] + a['summary']).lower()]

mode = st.selectbox("Section", ["All", "War", "Politics", "Economics"])
if mode != "All":
    keywords = {
        "War": ["war", "ukraine", "russia", "israel", "iran", "gaza", "military", "nato", "conflict", "strike", "defense"],
        "Politics": ["trump", "biden", "harris", "election", "congress", "senate", "republican", "democrat", "border", "maga"],
        "Economics": ["economy", "inflation", "jobs", "market", "fed", "tariff", "oil", "recession", "trade", "spending"]
    }
    filtered = [a for a in filtered if any(k.lower() in (a['title']+a['summary']).lower() for k in keywords.get(mode, []))]

# Display feed
st.subheader(f"{mode} Feed – {len(filtered)} stories")

for item in filtered[:15]:
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
                <p class="summary">{item['summary']}</p>
                <div style="margin-top:12px;">
                    <a href="{item['link']}" target="_blank">
                        <button class="btn">Read Article</button>
                    </a>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────
#  WAR MODE PROBABILITIES – this is the new part
# ────────────────────────────────────────────────
if mode == "War":
    st.markdown("---")
    st.subheader("War Outlook – Estimated Next Moves")
    st.caption("Illustrative probabilities based on current conservative reporting patterns")

    war_probs = [
        ("Major escalation / new front opens", 38),
        ("U.S. or Israel directly strikes Iran", 44),
        ("Sharp spike in energy / oil prices", 59),
        ("Temporary ceasefire or talks gain traction", 22),
        ("Expanded sanctions or cyber retaliation", 63),
        ("Proxy conflict widens (e.g. new region)", 31),
        ("De-escalation via back-channel diplomacy", 18)
    ]

    cols = st.columns(2)
    for i, (event, percent) in enumerate(war_probs):
        with cols[i % 2]:
            st.markdown(f"**{event}**")
            st.progress(percent / 100)
            st.caption(f"{percent}% chance")

# Auto-refresh
if st.session_state.auto_refresh:
    time.sleep(300)  # 5 minutes
    st.rerun()

st.sidebar.caption("THEREALNEWS with Lawrence • Updated March 2026")
