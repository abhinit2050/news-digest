import requests
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY);

CATEGORIES = ["general", "business", "science", "sports"]
ARTICLES_PER_CATEGORY = 3

def summarise_article(title, description):
    prompt = f"Summarise this news article in 2 sentences, simply and clearly:\nTitle: {title}\nDescription: {description}"
    
    chat = groq_client.chat.completions.create(
       model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return chat.choices[0].message.content;

def fetch_news():
    all_articles = []
    
    for category in CATEGORIES:
        url = "https://newsapi.org/v2/everything"
        params = {
            "apiKey": API_KEY,
            "q": f"india {category}",
            "language": "en",
            "pageSize": ARTICLES_PER_CATEGORY,
            "sortBy": "publishedAt"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "ok":
            print(f"\n--- {category.upper()} ---")
            for article in data["articles"]:
                title = article["title"]
                description = article.get("description", "")
                summary = summarise_article(title, description)
                print(f"\nTitle: {title}")
                print(f"Summary: {summary}")
                all_articles.append({
                    "category": category,
                    "title": title,
                    "summary": summary,
                    "url": article["url"]
                })
        else:
            print(f"Error fetching {category}: {data}")
    
    return all_articles

fetch_news()