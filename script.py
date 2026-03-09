import requests
import feedparser
import hashlib
import os
import random

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SITE = "https://denewsland.in"
USERNAME = "sumitsajwan8954@gmail.co"
APP_PASSWORD = "dv9a 3oA6 INKM fxC4 PVr2 D9K5"

RSS_FEEDS = [
"https://news.google.com/rss/search?q=india+stock+market",
"https://news.google.com/rss/search?q=technology+news+india",
"https://news.google.com/rss/search?q=business+news+india",
"https://www.livemint.com/rss/markets",
"https://www.livemint.com/rss/technology"
]

INTERNAL_LINKS = [
"https://denewsland.in/category/finance-news/",
"https://denewsland.in/category/market-news/",
"https://denewsland.in/category/tech-news/"
]

EXTERNAL_LINKS = [
"https://www.nseindia.com",
"https://www.bseindia.com",
"https://www.moneycontrol.com"
]

# ---------- duplicate check ----------

def is_duplicate(text):

    h = hashlib.md5(text.encode()).hexdigest()

    try:
        with open("hash.txt","r") as f:
            if h in f.read():
                return True
    except:
        pass

    with open("hash.txt","a") as f:
        f.write(h+"\n")

    return False


# ---------- AI ARTICLE GENERATOR ----------


def generate_article(topic):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
पूर्ण हिंदी लेख त्यार करो मानव भाषा वाला।

Article tyar karo or dhyan rhe ye article or title pichle kisi se match na ho.

Topic:
{topic}

Rules:
Language simple Hindi
Title Hindi + English mix
Discover friendly
Human readable
Article 500+ words
"""

    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    r = requests.post(url, headers=headers, json=data)

    result = r.json()

    print(result)   # debug

    try:
        return result["choices"][0]["message"]["content"]
    except:
        return "AI rewrite failed: " + topic

# ---------- IMAGE GENERATOR ----------

def get_image(title):

    # ---- Image prompt ----

    image_prompt = f"""
Create Google Discover friendly news thumbnail.

Rules:

White + light green background

Single object or logo related to topic

Topic: {title}

Add bold text only 3 words.

Clean minimal design.

No dark colors.

Size 1280x720.

Professional news style.
"""

    # ---- generate image ----

    url = "https://image.pollinations.ai/prompt/"

    img_url = url + image_prompt.replace(" ","%20")

    img = requests.get(img_url).content

    upload_url = f"{SITE}/wp-json/wp/v2/media"

    headers = {
    "Content-Disposition":"attachment; filename=news.jpg"
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


# ---------- PUBLISH POST ----------

def publish(title,content,image_id):

    url = f"{SITE}/wp-json/wp/v2/posts"

    content += "\n\nRelated:\n"

    for link in INTERNAL_LINKS:
        content += link+"\n"

    content += "\nSources:\n"

    for link in EXTERNAL_LINKS:
        content += link+"\n"

    data = {
    "title":title,
    "content":content,
    "status":"publish",
    "featured_media":image_id,
    "categories":[7]
    }

    r = requests.post(
        url,
        json=data,
        auth=(USERNAME,APP_PASSWORD)
    )

    print("POST:",r.status_code)


# ---------- MAIN ENGINE ----------

for feed in RSS_FEEDS:

    news = feedparser.parse(feed)

    for item in news.entries[:5]:

        topic = item.title + " " + item.summary

        if is_duplicate(topic):
            continue

        article = generate_article(topic)

        title = article.split("\n")[0]

        image_id = get_image(title)

        publish(title,article,image_id)
