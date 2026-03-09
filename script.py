import requests
import feedparser
import hashlib
import os
import random

# CONFIG

SITE = "https://denewsland.in"
USERNAME = "sumitsajwan8954@gmail.co"
APP_PASSWORD = "dv9a 3oA6 INKM fxC4 PVr2 D9K5"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

RSS_FEEDS = [
"https://news.google.com/rss/search?q=india+stock+market",
"https://news.google.com/rss/search?q=technology+india",
"https://news.google.com/rss/search?q=finance+india"
]

INTERNAL_LINKS = [
"https://denewsland.in/category/finance-news/",
"https://denewsland.in/category/market-news/",
"https://denewsland.in/category/tech-news/",
"https://denewsland.in/category/breaking-updates/"
]

# DUPLICATE CHECK

def is_duplicate(text):

    h = hashlib.md5(text.encode()).hexdigest()

    try:
        with open("hash.txt") as f:
            if h in f.read():
                return True
    except:
        pass

    with open("hash.txt","a") as f:
        f.write(h+"\n")

    return False

# AI ARTICLE

def generate_article(topic):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
पूर्ण हिंदी लेख त्यार करो मानव भाषा वाला

Article tyar karo or dhyan rhe ye article or title pichle kisi se match na ho

Topic:
{topic}

Rules:

Language simple Hindi
Title Hindi English mix
Discover friendly
Human readable
600 words article
"""

    data = {
        "model":"llama3-70b-8192",
        "messages":[{"role":"user","content":prompt}]
    }

    r = requests.post(url,headers=headers,json=data)

    result = r.json()

    try:
        return result["choices"][0]["message"]["content"]
    except:
        return None


# IMAGE GENERATOR

def get_image():

    img_url = "https://picsum.photos/1280/720"

    img = requests.get(img_url).content

    upload_url = f"{SITE}/wp-json/wp/v2/media"

    headers = {
        "Content-Disposition":"attachment; filename=news.jpg",
        "Content-Type":"image/jpeg"
    }

    r = requests.post(
        upload_url,
        headers=headers,
        data=img,
        auth=(USERNAME,APP_PASSWORD)
    )

    try:
        return r.json()["id"]
    except:
        return 0


# CATEGORY AUTO

def detect_category(text):

    text = text.lower()

    if "stock" in text or "market" in text:
        return 6

    if "technology" in text or "ai" in text:
        return 10

    if "finance" in text or "bank" in text:
        return 5

    return 3


# PUBLISH POST

def publish(title,content,image_id,category):

    url = f"{SITE}/wp-json/wp/v2/posts"

    data = {
        "title":title,
        "content":content,
        "status":"publish",
        "featured_media":image_id,
        "categories":[category]
    }

    r = requests.post(
        url,
        json=data,
        auth=(USERNAME,APP_PASSWORD)
    )

    print("POST:",r.status_code)


# MAIN ENGINE

for feed in RSS_FEEDS:

    news = feedparser.parse(feed)

    for item in news.entries[:10]:

        topic = item.title

        if is_duplicate(topic):
            continue

        article = generate_article(topic)

        if not article:
            continue

        title = article.split("\n")[0]

        image_id = get_image()

        category = detect_category(topic)

        publish(title,article,image_id,category)
