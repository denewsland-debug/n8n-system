import feedparser
import requests
import os
import random

# ==============================
# WORDPRESS LOGIN (REST API)
# ==============================

site = "https://denewsland.in"
username = "sumitsajwan8954@gmail.co"
app_password = "dv9a 3oA6 INKM fxC4 PVr2 D9K5"

# ==============================
# GROQ AI
# ==============================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ==============================
# RSS SOURCES
# ==============================

rss_urls = [
"https://news.google.com/rss/search?q=india+finance",
"https://news.google.com/rss/search?q=stock+market+india",
"https://news.google.com/rss/search?q=technology+news+india",
"https://www.livemint.com/rss/markets",
"https://www.livemint.com/rss/technology",
"https://www.livemint.com/rss/news"
]

# ==============================
# INTERNAL LINKS
# ==============================

internal_links = [
"https://denewsland.in/category/finance-news/",
"https://denewsland.in/category/market-news/",
"https://denewsland.in/category/tech-news/",
"https://denewsland.in/category/breaking-updates/",
"https://denewsland.in/"
]

# ==============================
# AI REWRITE
# ==============================
def ai_rewrite(text):

    prompt = f"""
    इस news को simple human Hindi में rewrite करो।
    Title strong होना चाहिए।
		Human Language 
		Title Discover Friendly 
		3 external link 
		4 internal link 
    Article readable होना चाहिए।

    Topic:
    {text}
    """

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role":"user","content":prompt}
        ]
    }

    r = requests.post(url,headers=headers,json=data)

    try:
        result = r.json()
        return result["choices"][0]["message"]["content"]

    except:
        print("AI Error:", r.text)
        return text

# ==============================
# FEATURED IMAGE
# ==============================

def upload_image():

    img_url = "https://source.unsplash.com/featured/?news"

    img = requests.get(img_url).content

    media_url = f"{site}/wp-json/wp/v2/media"

    headers = {
        "Content-Disposition": "attachment; filename=news.jpg"
    }

    r = requests.post(
        media_url,
        headers=headers,
        data=img,
        auth=(username,app_password)
    )

    return r.json()["id"]

# ==============================
# POST PUBLISH
# ==============================

def publish_post(title,content,image_id):

    url = f"{site}/wp-json/wp/v2/posts"

    data = {
        "title":title,
        "content":content,
        "status":"publish",
        "featured_media":image_id
    }

    r = requests.post(
        url,
        auth=(username,app_password),
        json=data
    )

    print(r.status_code)

# ==============================
# MAIN ENGINE
# ==============================

for rss in rss_urls:

    feed = feedparser.parse(rss)

    for post in feed.entries[:5]:

        text = post.title + " " + post.summary

        article = ai_rewrite(text)

        title = article.split("\n")[0]

        image_id = upload_image()

        content = article

        content += "\n\nExternal Source: " + post.link

        for link in random.sample(internal_links,3):
            content += "\n" + link

        publish_post(title,content,image_id)
