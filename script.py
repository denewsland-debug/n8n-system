import requests
import feedparser
import hashlib
import os
import random
import time

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

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
"https://denewsland.in/category/tech-news/"
]

EXTERNAL_LINKS = [
"https://www.nseindia.com",
"https://www.bseindia.com"
]


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


def generate_article(topic):

	if article is None:
    print("AI failed skip")
    continue

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
पूर्ण हिंदी लेख लिखो।

Topic: {topic}

Rules:
Simple Hindi language
Title Hindi English mix
500-600 words
Discover friendly
"""

    data = {
        "model":"llama3-70b-8192",
        "messages":[{"role":"user","content":prompt}],
        "temperature":0.7
    }

    try:

        r = requests.post(url,headers=headers,json=data,timeout=30)

        result = r.json()

        if "choices" not in result:
            return None

        return result["choices"][0]["message"]["content"]

    except:
        return None


def get_image():

    img_url = "https://source.unsplash.com/1280x720/?news"

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


def build_links():

    internal = random.sample(INTERNAL_LINKS,2)
    external = random.sample(EXTERNAL_LINKS,1)

    html = "<h3>Related</h3>"

    for i in internal:
        html += f"<p><a href='{i}'>{i}</a></p>"

    html += "<h3>Sources</h3>"

    for e in external:
        html += f"<p><a href='{e}'>{e}</a></p>"

    return html


def publish(title,content,image_id):

    url = f"{SITE}/wp-json/wp/v2/posts"

    content += build_links()

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


for feed in RSS_FEEDS:

    news = feedparser.parse(feed)

    for item in news.entries[:1]:

        topic = item.title

        if is_duplicate(topic):
            continue

        article = generate_article(topic)

        if article is None:
            print("AI fail skip")
            continue

        title = article.split("\n")[0]

        image_id = get_image()

        publish(title,article,image_id)

        time.sleep(5)
