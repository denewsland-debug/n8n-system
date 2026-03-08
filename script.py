import feedparser
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

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

for url in rss_urls:

    feed = feedparser.parse(url)

    for entry in feed.entries[:3]:

        post = WordPressPost()

        post.title = entry.title
        post.content = entry.summary
        post.post_status = "publish"

        wp.call(NewPost(post))
