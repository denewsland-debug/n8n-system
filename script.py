import os
import feedparser
import requests
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

GROQ_API_KEY = "YOUR_GROQ_API_KEY"

rss_urls = [
"https://news.google.com/rss/search?q=india+finance",
"https://news.google.com/rss/search?q=stock+market+india",
"https://news.google.com/rss/search?q=technology+news+india"
]

wp = Client(
"https://denewsland.in/xmlrpc.php",
"sumitsajwan8954@gmail.co",
"dv9a 3oA6 INKM fxC4 PVr2 D9K5"
)

def rewrite_hindi(text):

    prompt = f"Rewrite this news in simple Hindi for Indian readers:\n\n{text}"

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-70b-8192",
            "messages":[
                {"role":"user","content":prompt}
            ]
        }
    )

    result = response.json()

    return result["choices"][0]["message"]["content"]


for url in rss_urls:

    feed = feedparser.parse(url)

    for entry in feed.entries[:3]:

        article = rewrite_hindi(entry.summary)

        post = WordPressPost()

        post.title = entry.title
        post.content = article
        post.post_status = "publish"

        wp.call(NewPost(post))
