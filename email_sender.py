import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from supabase import create_client
from fetch_news import fetch_news

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

CATEGORY_COLORS = {
    "general": "#1a73e8",
    "business": "#2e7d32",
    "science & tech": "#6a1b9a",
    "sports": "#c62828",
    "entertainment": "#e65100",
    "politics": "#00838f",
    "international_events": "#4527a0"
}

def get_active_subscribers():
    response = supabase.table("subscribers").select("*").eq("is_active", True).execute()
    return response.data

def get_subscriber_categories(subscriber):
    categories = []
    category_map = {
        "general": "general",
        "business": "business",
        "science_tech": "science & tech",
        "sports": "sports",
        "entertainment": "entertainment",
        "politics": "politics",
        "international_events": "international_events"
    }
    for db_col, feed_name in category_map.items():
        if subscriber.get(db_col):
            categories.append(feed_name)
    return categories

def build_html(articles, name):
    sections = ""
    current_category = None

    for article in articles:
        category = article["category"]
        color = CATEGORY_COLORS.get(category, "#333333")

        if category != current_category:
            if current_category is not None:
                sections += "</div>"
            sections += f"""
            <div style="margin-bottom:32px;">
                <h2 style="color:{color};border-bottom:2px solid {color};padding-bottom:6px;text-transform:uppercase;font-size:14px;letter-spacing:1px;">{category}</h2>
            """
            current_category = category

        sections += f"""
        <div style="margin-bottom:20px;">
            <a href="{article['url']}" style="font-size:16px;font-weight:600;color:#1a1a1a;text-decoration:none;">{article['title']}</a>
            <p style="font-size:14px;color:#555555;margin-top:6px;line-height:1.6;">{article['summary']}</p>
            <a href="{article['url']}" style="font-size:12px;color:#1a73e8;">Read full article →</a>
        </div>
        """

    sections += "</div>"

    html = f"""
    <html>
    <body style="font-family:Arial,sans-serif;max-width:640px;margin:auto;padding:24px;background:#f9f9f9;">
        <div style="background:#ffffff;border-radius:8px;padding:32px;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
            <h1 style="font-size:24px;color:#1a1a1a;margin-bottom:4px;">📰 Good morning, {name}!</h1>
            <p style="font-size:13px;color:#888888;margin-bottom:32px;">Here's your personalised news digest for today</p>
            {sections}
            <p style="font-size:11px;color:#aaaaaa;margin-top:32px;text-align:center;">Powered by NewsAPI + Groq AI · <a href="https://news-digest-ieh6.onrender.com/unsubscribe" style="color:#aaaaaa;">Unsubscribe</a></p>
        </div>
    </body>
    </html>
    """
    return html

def send_email(to_email, name, articles):
    if not articles:
        print(f"No articles for {to_email}, skipping.")
        return

    html_content = build_html(articles, name)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📰 Your Morning News Digest"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(os.getenv("SENDER_EMAIL"), os.getenv("SENDER_PASSWORD"))
        server.sendmail(os.getenv("SENDER_EMAIL"), to_email, msg.as_string())
        print(f"Email sent to {to_email}")

def main():
    print("Fetching all news...")
    all_articles = fetch_news()

    print("Fetching subscribers...")
    subscribers = get_active_subscribers()
    print(f"Found {len(subscribers)} active subscribers")

    for subscriber in subscribers:
        name = subscriber["name"]
        email = subscriber["email"]
        categories = get_subscriber_categories(subscriber)

        print(f"\nSending to {email} — categories: {categories}")

        personalised_articles = [a for a in all_articles if a["category"] in categories]
        send_email(email, name, personalised_articles)

main()