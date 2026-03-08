import feedparser
import requests
import random
import os
import re
import hashlib
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods.media import UploadFile

# ==============================
# WORDPRESS LOGIN
# ==============================

wp = Client(
"https://denewsland.in/xmlrpc.php",
"sumitsajwan8954@gmail.co",
"dv9a 3oA6 INKM fxC4 PVr2 D9K5"
)

# ==============================
# GROQ API
# ==============================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ==============================
# RSS SOURCES (Mint + News)
# ==============================

rss_urls = [
"https://news.google.com/rss/search?q=india+finance",
"https://news.google.com/rss/search?q=stock+market+india",
"https://news.google.com/rss/search?q=technology+news+india",
"https://news.google.com/rss/search?q=breaking+news+india",
"https://www.livemint.com/rss/markets",
"https://www.livemint.com/rss/technology",
"https://www.livemint.com/rss/news"
]

# ==============================
# DUPLICATE CHECK
# ==============================

def is_duplicate(text):

    hash_val = hashlib.md5(text.encode()).hexdigest()

    try:
        with open("hashes.txt","r") as f:
            hashes = f.read()

            if hash_val in hashes:
                return True

    except:
        pass

    with open("hashes.txt","a") as f:
        f.write(hash_val+"\n")

    return False

# ==============================
# AI REWRITE
# ==============================

def ai_rewrite(text):

    prompt = f"""
पूर्ण हिंदी लेख तैयार करो मानव भाषा वाला।

Article tyar karo or dhyan rhe ye article or title pichle kisi se match na ho।

Information angle se tyar karna।

Topic:
{text}

Rules:

Language simple Hindi ho
Title shock + money angle + emoji
Exactly 3 headings
5 internal links add karo
3 authority external links add karo
600+ words
"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type":"application/json"
        },
        json={
            "model":"llama3-70b-8192",
            "messages":[{"role":"user","content":prompt}]
        }
    )

    data = response.json()

    return data["choices"][0]["message"]["content"]

# ==============================
# TITLE EXTRACT
# ==============================

def extract_title(article):

    m = re.search(r"Title:\s*(.*)",article)

    if m:
        return m.group(1)

    return "Market Update"

# ==============================
# CTR TITLE OPTIMIZER
# ==============================

def optimize_title(title):

    return f"🚨 {title} – Investors Alert!"

# ==============================
# CATEGORY DETECT
# ==============================

def detect_category(title):

    t = title.lower()

    if "tech" in t:
        return "Tech News"

    if "stock" in t or "market" in t:
        return "Market News"

    if "breaking" in t:
        return "Breaking Updates"

    return "Finance News"

# ==============================
# DISCOVER THUMBNAIL
# ==============================

def discover_thumbnail(title):

    words = title.split()

    text = "+".join(words[:3])

    return f"https://dummyimage.com/1280x720/ffffff/0a7f3f.png&text={text}"

# ==============================
# IMAGE UPLOAD
# ==============================

def upload_image(url):

    img = requests.get(url).content

    data = {
        'name':'thumb.jpg',
        'type':'image/jpeg',
        'bits':img
    }

    res = wp.call(UploadFile(data))

    return res['id']

# ==============================
# SCHEMA MARKUP
# ==============================

def add_schema(article,title):

    schema = f"""
<script type="application/ld+json">
{{
 "@context":"https://schema.org",
 "@type":"NewsArticle",
 "headline":"{title}"
}}
</script>
"""

    return article + schema

# ==============================
# MAIN LOOP
# ==============================

for url in rss_urls:

    feed = feedparser.parse(url)

    for entry in feed.entries[:3]:

        if is_duplicate(entry.summary):
            continue

        article = ai_rewrite(entry.summary)

        title = extract_title(article)

        title = optimize_title(title)

        category = detect_category(title)

        article = add_schema(article,title)

        img_url = discover_thumbnail(title)

        img_id = upload_image(img_url)

        post = WordPressPost()

        post.title = title
        post.content = article
        post.thumbnail = img_id
        post.post_status = "publish"
        post.terms_names = {'category':[category]}

        wp.call(NewPost(post))
				# ===== POST URL =====

url = f"https://denewsland.in/?p={post_id}"

# ===== GOOGLE SITEMAP PING =====

requests.get(
"https://www.google.com/ping?sitemap=https://denewsland.in/sitemap_index.xml"
)

# ===== BING INDEXNOW =====

indexnow_url = "https://api.indexnow.org/indexnow"

payload = {
"host": "denewsland.in",
"key": "Denewsland8954275500",
"urlList": [url]
}

requests.post(indexnow_url, json=payload)

# ===== DISCOVER REFRESH SIGNAL =====

requests.get(url)
