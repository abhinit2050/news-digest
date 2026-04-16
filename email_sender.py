import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from fetch_news import fetch_news

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

def build_html(articles):
    category_colors = {
        "general": "#1a73e8",
        "business": "#2e7d32",
        "science": "#6a1b9a",
        "sports": "#c62828"
    }

    sections = ""
    current_category = None

    for article in articles:
        category = article["category"]
        color = category_colors.get(category, "#333333")

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
            <h1 style="font-size:24px;color:#1a1a1a;margin-bottom:4px;">📰 Your Morning Digest</h1>
            <p style="font-size:13px;color:#888888;margin-bottom:32px;">Top Indian news across your favourite categories</p>
            {sections}
            <p style="font-size:11px;color:#aaaaaa;margin-top:32px;text-align:center;">Powered by NewsAPI + Groq AI · Delivered fresh every morning</p>
        </div>
    </body>
    </html>
    """
    return html

def send_email(articles):
    html_content = build_html(articles)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📰 Your Morning News Digest"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("Email sent successfully!")

articles = fetch_news()
send_email(articles)