import requests
import feedparser
import hashlib
import os
import random

SITE = "https://denewsland.in"
USERNAME = "sumitsajwan8954@gmail.co"
APP_PASSWORD = "dv9a 3oA6 INKM fxC4 PVr2 D9K5"
AI_KEY = os.getenv("AI_API_KEY")

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=india+stock+market",
    "https://news.google.com/rss/search?q=technology+india",
]

INTERNAL_LINKS = [
    "https://denewsland.in/category/finance-news/",
    "https://denewsland.in/category/market-news/",
    "https://denewsland.in/category/tech-news/",
]

# ---------- duplicate check ----------

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


# ---------- AI article generator ----------

def generate_article(topic):

    prompt = f"""
पूर्ण हिंदी लेख त्यार करो मानव भाषा वाला।

Topic: {topic}

600 शब्द का सरल हिंदी लेख लिखो।
Title, Meta description और 3 headings बनाओ।
"""

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    r = requests.post(url, headers=headers, json=data)

    try:

        result = r.json()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]

        else:
            print("AI API error:", result)
            return topic

    except Exception as e:

        print("AI failure:", e)
        return topic


# ---------- image generator ----------

def get_image():

    img_url = "https://source.unsplash.com/1280x720/?finance,stock"

    img = requests.get(img_url).content

    upload_url = f"{SITE}/wp-json/wp/v2/media"

    headers = {
        "Content-Disposition": "attachment; filename=news.jpg"
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


# ---------- publish post ----------

def publish(title,content,image_id):

    url = f"{SITE}/wp-json/wp/v2/posts"

    data = {
        "title":title,
        "content":content,
        "status":"publish",
        "featured_media":image_id
    }

    r = requests.post(
        url,
        json=data,
        auth=(USERNAME,APP_PASSWORD)
    )

    print("POST:",r.status_code)


# ---------- main engine ----------

for feed in RSS_FEEDS:

    news = feedparser.parse(feed)

    for item in news.entries[:5]:

        topic = item.title

        if is_duplicate(topic):
            continue

        article = generate_article(topic)

        title = article.split("\n")[0]

        image_id = get_image()

        publish(title,article,image_id)
