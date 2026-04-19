import feedparser
import os
import json
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime, timezone
import time

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

FEEDS = {
    "general": [
        "https://feeds.feedburner.com/ndtvnews-top-stories",
        "https://www.thehindu.com/news/national/feeder/default.rss",
    ],
    "business": [
        "https://www.livemint.com/rss/money",
        "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
    ],
    "science & tech": [
        "https://inc42.com/feed/",
        "https://techcrunch.com/feed/",
        "https://www.thehindu.com/sci-tech/feeder/default.rss",
    ],
    "sports": [
        "https://www.thehindu.com/sport/feeder/default.rss",
        "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
    ]
}

ARTICLES_TO_FETCH = 10
ARTICLES_TO_KEEP = 2

def pick_best_articles(articles, category):
    numbered = ""
    for i, a in enumerate(articles):
        numbered += f"{i+1}. {a['title']}\n"

    prompt = f"""You are a news curator for an Indian reader interested in {category} news.
Here are {len(articles)} recent articles. Pick the {ARTICLES_TO_KEEP} most important and interesting ones.

Rules:
- If there was a major event, ensure that the news with the result of the event, if any, is selected
- No two articles should be about the same event, match or topic
- Prefer variety and diversity of stories
- Prioritise stories that are significant and not repetitive

Return ONLY a JSON array of the numbers you picked. Example: [2, 7]
Do not explain. Just return the JSON array.

Articles:
{numbered}"""

    chat = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    response = chat.choices[0].message.content.strip()
    indices = json.loads(response)
    return [articles[i - 1] for i in indices]

def summarise_article(title, description):
    prompt = f"Summarise this news article in 2 sentences, simply and clearly:\nTitle: {title}\nDescription: {description}"

    chat = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return chat.choices[0].message.content

def fetch_news():
    all_articles = []

    for category, feed_urls in FEEDS.items():
        print(f"\n--- {category.upper()} ---")

        for feed_url in feed_urls:
            feed = feedparser.parse(feed_url)
            candidates = []

            for entry in feed.entries[:ARTICLES_TO_FETCH]:
                title = entry.get("title", "")
                description = entry.get("summary", "")
                url = entry.get("link", "")

                if not title or not description or len(description.strip()) < 20:
                    continue
                
                published = entry.get("published_parsed") or entry.get("updated_parsed")
                if published:
                    published_dt = datetime(*published[:6], tzinfo=timezone.utc)
                    age_hours = (datetime.now(timezone.utc) - published_dt).total_seconds() / 3600
                    if age_hours > 24:
                        continue


                candidates.append({
                    "category": category,
                    "title": title,
                    "description": description,
                    "url": url
                })

            if not candidates:
                continue

            best = pick_best_articles(candidates, category)

            for article in best:
                summary = summarise_article(article["title"], article["description"])
                print(f"\nTitle: {article['title']}")
                print(f"Summary: {summary}")

                all_articles.append({
                    "category": category,
                    "title": article["title"],
                    "summary": summary,
                    "url": article["url"]
                })

    return all_articles 